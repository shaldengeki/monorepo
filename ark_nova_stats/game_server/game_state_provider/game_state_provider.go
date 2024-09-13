package game_state_provider

import (
	"context"

	proto "github.com/shaldengeki/monorepo/ark_nova_stats/proto"
)

type GameStateProvider interface {
	GetState(_ context.Context, gameId int) (*proto.GameState, error)
}
