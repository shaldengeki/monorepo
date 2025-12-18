package game_state

import (
	"context"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
)

type GameState interface {
	GetState(context context.Context, gameId string) (*proto.GameState, error)
}
