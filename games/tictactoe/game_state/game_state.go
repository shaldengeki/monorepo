package game_state

import (
	"context"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
)

type GameState interface {
	GetState(ctx context.Context, gameId string) (*proto.GameState, error)
	SetState(ctx context.Context, gameId string, newState proto.GameState) error
}
