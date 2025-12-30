package server

import (
	"context"
	"testing"
	pb "github.com/shaldengeki/monorepo/games/tictactoe/proto"
	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/empty_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/read_only_in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/static_game_state"
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
	ctx := context.Background()

	t.Run("EmptyState", func(t *testing.T) {
		emptyProvider := empty_game_state.NewEmptyGameState()
		server := New(emptyProvider)

		t.Run("NilRequestReturnsValidationError", func(t *testing.T) {
			res, err := server.MakeMove(ctx, nil)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("InvalidMoveReturnsValidationError", func(t *testing.T) {
			request := pbserver.MakeMoveRequest{
				Move: &pb.BoardMarker{
					Row: -1,
				},
			}
			res, err := server.MakeMove(ctx, &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("ValidMoveReturnsInfraError", func(t *testing.T) {
			request := pbserver.MakeMoveRequest{
				Move: &pb.BoardMarker{
					Row: 1,
					Column: 1,
					Symbol: "X",
				},
			}
			_, err := server.MakeMove(ctx, &request)
			assert.Error(t, err)
		})
	})

	t.Run("WithState", func(t *testing.T) {
		state := pb.GameState{
			Round: 1,
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				Markers: []*pb.BoardMarker{
					{
						Row: 1,
						Column: 1,
						Symbol: "O",
					},
				},
			},
		}
		staticProvider := static_game_state.NewStaticGameState(&state)
		staticServer := New(staticProvider)

		t.Run("NilRequestReturnsValidationError", func(t *testing.T) {
			res, err := staticServer.MakeMove(ctx, nil)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("InvalidMoveReturnsValidationError", func(t *testing.T) {
			request := pbserver.MakeMoveRequest{
				Move: &pb.BoardMarker{
					Row: -1,
				},
			}
			res, err := staticServer.MakeMove(ctx, &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("CollidingMoveReturnsInfraError", func(t *testing.T) {
			request := pbserver.MakeMoveRequest{
				Move: &pb.BoardMarker{
					Row: 1,
					Column: 1,
					Symbol: "X",
				},
			}
			_, err := staticServer.MakeMove(ctx, &request)
			assert.Error(t, err)
		})

		t.Run("InvalidSetStateReturnsInfraError", func(t *testing.T) {
			// This test mutates game state, so we set up a separate set of structs.
			readOnlyState := pb.GameState{
				Round: 1,
				Board: &pb.Board{
					Rows: 3,
					Columns: 3,
					Markers: []*pb.BoardMarker{
						{
							Row: 1,
							Column: 1,
							Symbol: "O",
						},
					},
				},
			}
			readOnlyStateMap := map[string]*pb.GameState{
				"game_id_1": &readOnlyState,
			}
			readOnlyProvider := read_only_in_memory_game_state.NewReadOnlyInMemoryGameState(readOnlyStateMap)
			readOnlyServer := New(readOnlyProvider)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Move: &pb.BoardMarker{
					Row: 2,
					Column: 2,
					Symbol: "X",
				},
			}
			_, err := readOnlyServer.MakeMove(ctx, &request)
			assert.Error(t, err)
		})

		t.Run("SuccessfulSetReturnsSuccess", func(t *testing.T) {
			// This test mutates game state, so we set up a separate set of structs.
			inMemoryState := pb.GameState{
				Round: 1,
				Board: &pb.Board{
					Rows: 3,
					Columns: 3,
					Markers: []*pb.BoardMarker{
						{
							Row: 1,
							Column: 1,
							Symbol: "O",
						},
					},
				},
			}
			inMemoryStateMap := map[string]*pb.GameState{
				"game_id_1": &inMemoryState,
			}
			inMemoryProvider := in_memory_game_state.NewInMemoryGameState(inMemoryStateMap)
			inMemoryServer := New(inMemoryProvider)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Move: &pb.BoardMarker{
					Row: 2,
					Column: 2,
					Symbol: "X",
				},
			}
			_, err := inMemoryServer.MakeMove(ctx, &request)
			require.NoError(t, err)
			assert.Empty(t, "TODO")
		})
	})

}
