package server

import (
	"context"
	"testing"
	pb "github.com/shaldengeki/monorepo/games/tictactoe/proto"
	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state_provider"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestValidateState_WithEmptyState_ReturnsValid(t *testing.T) {
	ctx := context.Background()

	emptyProvider := game_state_provider.NewEmptyGameStateProvider()
	server := New(emptyProvider)
	request := pbserver.ValidateStateRequest{}
	
	res, err := server.ValidateState(ctx, &request)
	require.NoError(t, err)
	assert.Empty(t, res.ValidationErrors)
}

// int32 turn = 1;
func TestValidateState_Turn(t *testing.T) {
	ctx := context.Background()

	emptyProvider := game_state_provider.NewEmptyGameStateProvider()
	server := New(emptyProvider)

	// Turn = 1
	request := pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: 1, Board: &pb.Board{Rows: 1, Columns: 1}}}
	res, err := server.ValidateState(ctx, &request)
	require.NoError(t, err)
	assert.Empty(t, res.ValidationErrors)


	// Turn = <= 0
	request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 0, Round: 1, Board: &pb.Board{Rows: 1, Columns: 1}}}
	res, err = server.ValidateState(ctx, &request)
	require.NoError(t, err)
	assert.NotEmpty(t, res.ValidationErrors)
	request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: -1, Round: 1, Board: &pb.Board{Rows: 1, Columns: 1}}}
	res, err = server.ValidateState(ctx, &request)
	require.NoError(t, err)
	assert.NotEmpty(t, res.ValidationErrors)
}

// int32 round = 2;
// bool finished = 3;
// repeated Score scores = 4;
// Board board = 5;
