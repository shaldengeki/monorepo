package grpc

import (
	"context"
	"errors"
	"fmt"

	"github.com/shaldengeki/monorepo/games/tictactoe/game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/server"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
)

type grpcServer struct {
	pbserver.UnimplementedGameServiceServer

	gameServer server.GameServer
	gameStateProvider game_state.GameState
	gameCount int
}

func (s *grpcServer) CreateGame(ctx context.Context, request *pbserver.CreateGameRequest) (*pbserver.CreateGameResponse, error) {
	gameId := fmt.Sprintf("%d", s.gameCount)
	err := s.gameStateProvider.SetState(ctx, gameId, proto.GameState{Turn: 0, Round: 1, Finished: false, Board: &proto.Board{Rows: 3, Columns: 3}, Players: []*proto.Player{{Id: "1", Symbol: "X"}, {Id: "2", Symbol: "O"}}})
	if err != nil {
		return nil, fmt.Errorf("could not create game with id %d: %w", gameId, err)
	}

	s.gameCount += 1

	return &pbserver.CreateGameResponse{
		GameId: gameId,
	}, nil
}

func (s *grpcServer) GetState(ctx context.Context, request *pbserver.GetStateRequest) (*pbserver.GetStateResponse, error) {
	if request.GameId == "" {
		return nil, errors.New("Game ID not provided")
	}

	state, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil {
		return nil, fmt.Errorf("Could not fetch game state: %v", err)
	}

	r := pbserver.GetStateResponse{GameState: state}
	return &r, nil
}

func (s *grpcServer) ValidateState(ctx context.Context, request *pbserver.ValidateStateRequest) (*pbserver.ValidateStateResponse, error) {
	if request.GameState == nil {
		return &pbserver.ValidateStateResponse{}, nil
	}

	violations, err := s.gameServer.ValidateGameState(ctx, *request.GameState)
	if err != nil {
		return nil, fmt.Errorf("could not validate state: %w", err)
	}

	return &pbserver.ValidateStateResponse{ValidationErrors: violations}, nil
}

func (s *grpcServer) MakeMove(ctx context.Context, request *pbserver.MakeMoveRequest) (*pbserver.MakeMoveResponse, error) {
	if request == nil {
		return &pbserver.MakeMoveResponse{ValidationErrors: []string{"move must be non-empty"}}, nil
	}

	// First, validate the move prospectively.
	validationErrors, err := s.gameServer.ValidateMarker(ctx, request.Move)
	if err != nil {
		return nil, fmt.Errorf("could not validate move request: %w", err)
	}
	if len(validationErrors) > 0 {
		return &pbserver.MakeMoveResponse{ValidationErrors: validationErrors}, nil
	}

	// TODO: this won't work with any sort of concurrency; we'll need some sort of locking.

	// Next, fetch this game's state.
	priorState, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil || priorState == nil {
		return nil, fmt.Errorf("could not get game state to make move for game %s: prior state %v, err %w", request.GameId, priorState, err)
	}

	// Next, apply the move.
	updatedGameState, err := s.gameServer.ApplyMove(ctx, *priorState, request.Move)
	if err != nil {
		return nil, fmt.Errorf("could not apply move to prior state for game %s: %w", request.GameId, err)
	}

	// Next, validate the resulting state.
	updatedValidationErrors, err := s.gameServer.ValidateGameState(ctx, *updatedGameState)
	if err != nil {
		return nil, fmt.Errorf("could not validate updated game state: %w", err)
	}
	if len(updatedValidationErrors) > 0 {
		return &pbserver.MakeMoveResponse{ValidationErrors: updatedValidationErrors}, nil
	}

	// Finally, commit the result.
	err = s.gameStateProvider.SetState(ctx, request.GameId, *updatedGameState)
	if err != nil {
		return nil, fmt.Errorf("could not set updated state for game %s: %w", request.GameId, err)
	}

	return &pbserver.MakeMoveResponse{GameState: updatedGameState}, nil
}

func New(gameState game_state.GameState) grpcServer {
	return grpcServer{gameStateProvider: gameState, gameServer: server.New(gameState)}
}
