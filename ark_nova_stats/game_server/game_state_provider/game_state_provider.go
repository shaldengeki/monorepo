package game_state_provider

import (
	"context"

	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/game_state"
)

type GameStateProvider interface {
	GetState(context context.Context, gameId int64) (*game_state.GameState, error)
}

type EmptyGameStateProvider struct {
	GameStateProvider
}

func (s EmptyGameStateProvider) GetState(ctx context.Context, gameId int64) (*game_state.GameState, error) {
	gs := game_state.GameState{}
	return &gs, nil
}

func NewEmptyGameStateProvider() GameStateProvider {
	return EmptyGameStateProvider{}
}

type StaticGameState struct {
	GameStateProvider

	staticState *game_state.GameState
}

func (s StaticGameState) GetState(ctx context.Context, gameId int64) (*game_state.GameState, error) {
	return s.staticState, nil
}

func NewStaticGameState(state *game_state.GameState) GameStateProvider {
	return StaticGameState{staticState: state}
}
