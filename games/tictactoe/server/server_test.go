package server

import (
	"context"
	"testing"
	pb "github.com/shaldengeki/monorepo/games/tictactoe/proto"
	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/empty_game_state"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestValidateState(t *testing.T) {
	ctx := context.Background()
	emptyProvider := empty_game_state.NewEmptyGameState()
	server := New(emptyProvider)

	t.Run("ValidWithEmptyState", func(t *testing.T) {
		request := pbserver.ValidateStateRequest{}

		res, err := server.ValidateState(ctx, &request)
		require.NoError(t, err)
		assert.Empty(t, res.ValidationErrors)
	})

	t.Run("Turn", func(t *testing.T) {
		// Turn = 1
		request := pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: 1}}
		res, err := server.ValidateState(ctx, &request)
		require.NoError(t, err)
		assert.Empty(t, res.ValidationErrors)

		// Turn = <= 0
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 0, Round: 1}}
		res, err = server.ValidateState(ctx, &request)
		require.NoError(t, err)
		assert.NotEmpty(t, res.ValidationErrors)
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: -1, Round: 1}}
		res, err = server.ValidateState(ctx, &request)
		require.NoError(t, err)
		assert.NotEmpty(t, res.ValidationErrors)
	})

	t.Run("Round", func(t *testing.T) {
		// Round = 1
		request := pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: 1}}
		res, err := server.ValidateState(ctx, &request)
		require.NoError(t, err)
		assert.Empty(t, res.ValidationErrors)

		// Round = <= 0
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: 0}}
		res, err = server.ValidateState(ctx, &request)
		require.NoError(t, err)
		assert.NotEmpty(t, res.ValidationErrors)
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: -1}}
		res, err = server.ValidateState(ctx, &request)
		require.NoError(t, err)
		assert.NotEmpty(t, res.ValidationErrors)
	})
	// bool finished = 3;
	// repeated Score scores = 4;
	// Board board = 5;
}

func TestMakeMove(t *testing.T) {
	assert.NotNil(t, nil)
}
