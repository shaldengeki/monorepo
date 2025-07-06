package server

import (
	"context"
	"errors"
	"fmt"

	"github.com/shaldengeki/monorepo/games/tictactoe/game_state_provider"

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

	if request.GameState.Turn < 1 {
		return &server.ValidateStateResponse{ValidationErrors: []string{"Turn count should be >= 1"}}, nil
	}

	if request.GameState.Round < 1 {
		return &server.ValidateStateResponse{ValidationErrors: []string{"Round count should be >= 1"}}, nil
	}

	return &server.ValidateStateResponse{}, nil
}

func New(gameStateProvider game_state_provider.GameStateProvider) *gameServer {
	return &gameServer{gameStateProvider: gameStateProvider}
}
