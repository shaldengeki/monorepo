package game_state_provider

import (
	"context"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
)

type GameStateProvider interface {
	GetState(context context.Context, gameId string) (*proto.GameState, error)
}

type EmptyGameStateProvider struct {
	GameStateProvider
}

func (s EmptyGameStateProvider) GetState(ctx context.Context, gameId string) (*proto.GameState, error) {
	gs := proto.GameState{}
	return &gs, nil
}

func NewEmptyGameStateProvider() GameStateProvider {
	return EmptyGameStateProvider{}
}

type StaticGameStateProvider struct {
	GameStateProvider

	staticState *proto.GameState
}

func (s StaticGameStateProvider) GetState(ctx context.Context, gameId string) (*proto.GameState, error) {
	return s.staticState, nil
}

func NewStaticGameStateProvider(state *proto.GameState) GameStateProvider {
	return StaticGameStateProvider{staticState: state}
}
