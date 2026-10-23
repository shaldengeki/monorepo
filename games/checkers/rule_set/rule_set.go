package rule_set

import (
	"context"

	"github.com/shaldengeki/monorepo/games/checkers/proto"
)

type RuleSet interface {
	InitialState(ctx context.Context) (*proto.GameState, error)
	ValidateMarker(ctx context.Context, marker *proto.BoardMarker) ([]string, error)
	ValidateState(ctx context.Context, gameState proto.GameState) (violations []string, err error)
	ValidateJumps(ctx context.Context, jumps []*proto.BoardMarker, startingLocations map[uint32]map[uint32]string, board *proto.Board, playerStates []*proto.PlayerGameState) ([]string, error)
	ApplyMove(ctx context.Context, priorState proto.GameState, jumps []*proto.BoardMarker) (*proto.GameState, error)
	MoveFinishesGame(ctx context.Context, board *proto.Board) (bool, error)
	CurrentPlayer(ctx context.Context, currentState *proto.GameState) (*proto.Player, error)
}
