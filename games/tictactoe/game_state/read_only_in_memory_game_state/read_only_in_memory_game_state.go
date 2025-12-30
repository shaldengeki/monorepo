package read_only_in_memory_game_state

import (
	"context"
	"fmt"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/in_memory_game_state"
)

type ReadOnlyInMemoryGameState struct {
	game_state.GameState
	inMemoryProvider in_memory_game_state.InMemoryGameState
}

func (s ReadOnlyInMemoryGameState) GetState(ctx context.Context, gameId string) (*proto.GameState, error) {
	return s.inMemoryProvider.GetState(ctx, gameId)
}

func (s ReadOnlyInMemoryGameState) SetState(ctx context.Context, gameId string, newState proto.GameState) error {
	return fmt.Errorf("cannot set state in read-only game state provider")
}

func NewReadOnlyInMemoryGameState(initialState map[string]*proto.GameState) game_state.GameState {
	inMemoryProvider := in_memory_game_state.NewInMemoryGameState(initialState).(in_memory_game_state.InMemoryGameState)
	return ReadOnlyInMemoryGameState{
		inMemoryProvider: inMemoryProvider,
	}
}
