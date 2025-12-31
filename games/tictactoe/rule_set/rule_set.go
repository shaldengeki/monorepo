package rule_set

import (
	"context"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
)

type RuleSet interface {
	InitialState(ctx context.Context) (*proto.GameState, error)
	ValidateState(ctx context.Context, gameState proto.GameState) (violations []string, err error)
	ApplyMove(ctx context.Context, priorState proto.GameState, move *proto.BoardMarker) (*proto.GameState, error)
	MoveFinishesGame(ctx context.Context, move *proto.BoardMarker, board *proto.Board) (bool, error)
	CurrentPlayer(ctx context.Context, currentState *proto.GameState) (*proto.Player, error)
}
