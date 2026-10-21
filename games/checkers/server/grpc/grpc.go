package grpc

import (
	"context"
	"errors"
	"fmt"

	"github.com/shaldengeki/monorepo/games/checkers/game_state"
	"github.com/shaldengeki/monorepo/games/checkers/rule_set"
	pbserver "github.com/shaldengeki/monorepo/games/checkers/proto/server"
)

type grpcServer struct {
	pbserver.UnimplementedGameServiceServer

	ruleSet rule_set.RuleSet
	gameStateProvider game_state.GameState
	gameCount int
}

func (s *grpcServer) CreateGame(ctx context.Context, request *pbserver.CreateGameRequest) (*pbserver.CreateGameResponse, error) {
	gameId := fmt.Sprintf("%d", s.gameCount)
	initialState, err := s.ruleSet.InitialState(ctx)
	if err != nil {
		return nil, fmt.Errorf("could not set up initial game state: %w", err)
	}

	err = s.gameStateProvider.SetState(ctx, gameId, *initialState)
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

	violations, err := s.ruleSet.ValidateState(ctx, *request.GameState)
	if err != nil {
		return nil, fmt.Errorf("could not validate state: %w", err)
	}

	return &pbserver.ValidateStateResponse{ValidationErrors: violations}, nil
}

func (s *grpcServer) MakeMove(ctx context.Context, request *pbserver.MakeMoveRequest) (*pbserver.MakeMoveResponse, error) {
	if request == nil {
		return &pbserver.MakeMoveResponse{ValidationErrors: []string{"move must be non-empty"}}, nil
	}

	// TODO: this won't work with any sort of concurrency; we'll need some sort of locking.

	// Fetch this game's state.
	priorState, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil || priorState == nil {
		return nil, fmt.Errorf("could not get game state to make move for game %s: prior state %v, err %w", request.GameId, priorState, err)
	}

	// Validate the move prospectively.
	occupiedSpaces := map[uint32]map[uint32]string{}
	for _, marker := range priorState.Board.Markers {
		if _, found := occupiedSpaces[marker.Row]; !found {
			occupiedSpaces[marker.Row] = map[uint32]string{}
		}
		occupiedSpaces[marker.Row][marker.Column] = marker.Player.Id
	}
	validationErrors, err := s.ruleSet.ValidateJumps(ctx, request.Jumps, occupiedSpaces, priorState.Board)
	if err != nil {
		return nil, fmt.Errorf("could not validate jump: %w", err)
	}
	if len(validationErrors) > 0 {
		return &pbserver.MakeMoveResponse{ValidationErrors: validationErrors}, nil
	}

	// Next, apply the move.
	updatedGameState, err := s.ruleSet.ApplyMove(ctx, *priorState, request.Jumps)
	if err != nil {
		return nil, fmt.Errorf("could not apply move to prior state for game %s: %w", request.GameId, err)
	}

	// Next, validate the resulting state.
	updatedValidationErrors, err := s.ruleSet.ValidateState(ctx, *updatedGameState)
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

func New(gameState game_state.GameState, ruleSet rule_set.RuleSet) *grpcServer {
	return &grpcServer{gameStateProvider: gameState, ruleSet: ruleSet}
}
