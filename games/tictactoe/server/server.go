package server

import (
	"context"
	"errors"
	"fmt"

	"github.com/shaldengeki/monorepo/games/tictactoe/game_state"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
)

type GameServer struct {
	server.UnimplementedGameServiceServer

	gameStateProvider game_state.GameState
	gameCount int
}

func (s *GameServer) CreateGame(ctx context.Context, request *server.CreateGameRequest) (*server.CreateGameResponse, error) {
	gameId := fmt.Sprintf("%d", s.gameCount)
	err := s.gameStateProvider.SetState(ctx, gameId, proto.GameState{Turn: 0, Round: 1, Finished: false, Board: &proto.Board{Rows: 3, Columns: 3}, Players: []*proto.Player{{Id: "1", Symbol: "X"}, {Id: "2", Symbol: "O"}}})
	if err != nil {
		return nil, fmt.Errorf("could not create game with id %d: %w", gameId, err)
	}

	s.gameCount += 1

	return &server.CreateGameResponse{
		GameId: gameId,
	}, nil
}

func (s *GameServer) GetState(ctx context.Context, request *server.GetStateRequest) (*server.GetStateResponse, error) {
	if request.GameId == "" {
		return nil, errors.New("Game ID not provided")
	}

	state, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil {
		return nil, fmt.Errorf("Could not fetch game state: %v", err)
	}

	r := server.GetStateResponse{GameState: state}
	return &r, nil
}

func (s *GameServer) ValidateState(ctx context.Context, request *server.ValidateStateRequest) (*server.ValidateStateResponse, error) {
	if request.GameState == nil {
		return &server.ValidateStateResponse{}, nil
	}

	violations, err := s.ValidateGameState(ctx, *request.GameState)
	if err != nil {
		return nil, fmt.Errorf("could not validate state: %w", err)
	}

	return &server.ValidateStateResponse{ValidationErrors: violations}, nil
}

func (s *GameServer) MakeMove(ctx context.Context, request *server.MakeMoveRequest) (*server.MakeMoveResponse, error) {
	if request == nil {
		return &server.MakeMoveResponse{ValidationErrors: []string{"move must be non-empty"}}, nil
	}

	// First, validate the move prospectively.
	validationErrors, err := s.ValidateMarker(ctx, request.Move)
	if err != nil {
		return nil, fmt.Errorf("could not validate move request: %w", err)
	}
	if len(validationErrors) > 0 {
		return &server.MakeMoveResponse{ValidationErrors: validationErrors}, nil
	}

	// TODO: this won't work with any sort of concurrency; we'll need some sort of locking.

	// Next, fetch this game's state.
	priorState, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil || priorState == nil {
		return nil, fmt.Errorf("could not get game state to make move for game %s: prior state %v, err %w", request.GameId, priorState, err)
	}

	// Next, apply the move.
	updatedGameState, err := s.ApplyMove(ctx, *priorState, request.Move)
	if err != nil {
		return nil, fmt.Errorf("could not apply move to prior state for game %s: %w", request.GameId, err)
	}

	// Next, validate the resulting state.
	updatedValidationErrors, err := s.ValidateGameState(ctx, *updatedGameState)
	if err != nil {
		return nil, fmt.Errorf("could not validate updated game state: %w", err)
	}
	if len(updatedValidationErrors) > 0 {
		return &server.MakeMoveResponse{ValidationErrors: updatedValidationErrors}, nil
	}

	// Finally, commit the result.
	err = s.gameStateProvider.SetState(ctx, request.GameId, *updatedGameState)
	if err != nil {
		return nil, fmt.Errorf("could not set updated state for game %s: %w", request.GameId, err)
	}

	return &server.MakeMoveResponse{GameState: updatedGameState}, nil
}

func New(gameStateProvider game_state.GameState) GameServer {
	return GameServer{gameStateProvider: gameStateProvider}
}
