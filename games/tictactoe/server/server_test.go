package server

import (
	"context"
	"testing"
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
