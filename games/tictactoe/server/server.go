package server

import (
	"context"
	"errors"
	"fmt"

	"github.com/shaldengeki/monorepo/games/tictactoe/game_state_provider"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
)

type gameServer struct {
	server.UnimplementedGameServerServer

	gameStateProvider game_state_provider.GameStateProvider
}

func (s *gameServer) GetState(ctx context.Context, request *server.GetStateRequest) (*server.GetStateResponse, error) {
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

func (s *gameServer) ValidateState(ctx context.Context, request *server.ValidateStateRequest) (*server.ValidateStateResponse, error) {
	if request.GameState == nil {
		return &server.ValidateStateResponse{}, nil
	}

	violations := []string{}

	if request.GameState.Turn < 1 {
		violations = append(violations, "Turn count should be >= 1")
	}

	if request.GameState.Round < 1 {
		violations = append(violations, "Round count should be >= 1")
	}

	scoreViolations, err := s.ValidateStateScores(ctx, request.GameState.Scores)
	if err != nil {
		return nil, fmt.Errorf("Could not validate scores in state: %w", err)
	}
	for _, v := range scoreViolations {
		violations = append(violations, v)
	}

	boardViolations, err := s.ValidateStateBoard(ctx, request.GameState.Board)
	if err != nil {
		return nil, fmt.Errorf("Could not validate board in state: %w", err)
	}
	for _, v := range boardViolations {
		violations = append(violations, v)
	}

	return &server.ValidateStateResponse{ValidationErrors: violations}, nil
}

func (s *gameServer) ValidateStateScores(ctx context.Context, scores []*proto.Score) ([]string, error) {
	violations := []string{}

	hasPoints := false
	for _, score := range scores {
		if score.Score < 0 {
			violations = append(violations, fmt.Sprintf("Player %s score must be >= 0", score.Player))
		} else if score.Score > 0 {
			if hasPoints {
				violations = append(violations, "Only one player may have points")
				break
			}
			hasPoints = true
		}
	}

	return violations, nil
}

func New(gameStateProvider game_state_provider.GameStateProvider) *gameServer {
	return &gameServer{gameStateProvider: gameStateProvider}
}
