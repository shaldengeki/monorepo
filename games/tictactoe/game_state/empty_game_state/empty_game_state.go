package empty_game_state

import (
	"context"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state"
)

type EmptyGameState struct {
	game_state.GameState
}

func (s EmptyGameState) GetState(ctx context.Context, gameId string) (*proto.GameState, error) {
	gs := proto.GameState{}
	return &gs, nil
}

func (s EmptyGameState) SetState(ctx context.Context, gameId string, newState proto.GameState) error {
	return nil
}

func NewEmptyGameState() game_state.GameState {
	return EmptyGameState{}
}

