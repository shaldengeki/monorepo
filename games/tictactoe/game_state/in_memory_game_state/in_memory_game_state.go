package in_memory_game_state

import (
	"context"
	"fmt"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state"
)

type InMemoryGameState struct {
	game_state.GameState

    gameStates map[string]*proto.GameState
}

func (s InMemoryGameState) GetState(ctx context.Context, gameId string) (*proto.GameState, error) {
	state, found := s.gameStates[gameId]
	if !found {
		return nil, fmt.Errorf("could not find game state for id %s", gameId)
	}

	return state, nil
}

func (s InMemoryGameState) SetState(ctx context.Context, gameId string, newState proto.GameState) error {
	s.gameStates[gameId] = &newState
	return nil
}

func NewInMemoryGameState(initialState map[string]*proto.GameState) game_state.GameState {
	return InMemoryGameState{gameStates: initialState}
}
