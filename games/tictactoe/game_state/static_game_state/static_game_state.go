package static_game_state

import (
	"context"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state"
)

type StaticGameState struct {
	game_state.GameState

	staticState *proto.GameState
}

func (s StaticGameState) GetState(ctx context.Context, gameId string) (*proto.GameState, error) {
	return s.staticState, nil
}

func (s StaticGameState) SetState(ctx context.Context, gameId string, newState proto.GameState) error {
	return nil
}

func NewStaticGameState(state *proto.GameState) game_state.GameState {
	return StaticGameState{staticState: state}
}
