package grpc

import (
	"testing"
	pb "github.com/shaldengeki/monorepo/games/tictactoe/proto"
	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/empty_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/read_only_in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/static_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/rule_set/default_rule_set"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestValidateState(t *testing.T) {
	gameState := empty_game_state.NewEmptyGameState()
	ruleSet := default_rule_set.NewDefaultRuleSet()
	grpcServer := New(gameState, ruleSet)

	t.Run("ValidWithEmptyState", func(t *testing.T) {
		request := pbserver.ValidateStateRequest{}

		res, err := grpcServer.ValidateState(t.Context(), &request)
		require.NoError(t, err)
		assert.Empty(t, res.ValidationErrors)
	})

	t.Run("Turn", func(t *testing.T) {
		// Turn = 1
		request := pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: 1}}
		res, err := grpcServer.ValidateState(t.Context(), &request)
		require.NoError(t, err)
		assert.Empty(t, res.ValidationErrors)

		// Turn = 0
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 0, Round: 1}}
		res, err = grpcServer.ValidateState(t.Context(), &request)
		require.NoError(t, err)
		assert.NotEmpty(t, res.ValidationErrors)

		// Turn > # players
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 3, Round: 1, Players: []*pb.Player{{Symbol: "X"}, {Symbol: "O"}}}}
		res, err = grpcServer.ValidateState(t.Context(), &request)
		require.NoError(t, err)
		assert.NotEmpty(t, res.ValidationErrors)

	})

	t.Run("Round", func(t *testing.T) {
		// Round = 1
		request := pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: 1}}
		res, err := grpcServer.ValidateState(t.Context(), &request)
		require.NoError(t, err)
		assert.Empty(t, res.ValidationErrors)

		// Round = 0
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 1, Round: 0}}
		res, err = grpcServer.ValidateState(t.Context(), &request)
		require.NoError(t, err)
		assert.NotEmpty(t, res.ValidationErrors)
	})
	// bool finished = 3;
	// repeated Score scores = 4;
	// Board board = 5;
	// repeated Player players = 6;
}

func TestMakeMove(t *testing.T) {
	t.Run("EmptyState", func(t *testing.T) {
		gameState := empty_game_state.NewEmptyGameState()
		ruleSet := default_rule_set.NewDefaultRuleSet()
		grpcServer := New(gameState, ruleSet)

		t.Run("NilRequestReturnsValidationError", func(t *testing.T) {
			res, err := grpcServer.MakeMove(t.Context(), nil)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("InvalidMoveReturnsValidationError", func(t *testing.T) {
			request := pbserver.MakeMoveRequest{
				Move: &pb.BoardMarker{
					Row: 1,
					Column: 1,
					Symbol: "",
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
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
			_, err := grpcServer.MakeMove(t.Context(), &request)
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
		gameState := static_game_state.NewStaticGameState(&state)
		ruleSet := default_rule_set.NewDefaultRuleSet()
		grpcServer := New(gameState, ruleSet)

		t.Run("NilRequestReturnsValidationError", func(t *testing.T) {
			res, err := grpcServer.MakeMove(t.Context(), nil)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("InvalidMoveReturnsValidationError", func(t *testing.T) {
			request := pbserver.MakeMoveRequest{
				Move: &pb.BoardMarker{
					Row: 1,
					Column: 1,
					Symbol: "",
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
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
			_, err := grpcServer.MakeMove(t.Context(), &request)
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
				Players: []*pb.Player{
					{Id: "1", Symbol: "O"},
					{Id: "2", Symbol: "X"},
				},
			}
			readOnlyStateMap := map[string]*pb.GameState{
				"game_id_1": &readOnlyState,
			}
			gameState := read_only_in_memory_game_state.NewReadOnlyInMemoryGameState(readOnlyStateMap)
			ruleSet := default_rule_set.NewDefaultRuleSet()
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Move: &pb.BoardMarker{
					Row: 2,
					Column: 2,
					Symbol: "X",
				},
			}
			_, err := grpcServer.MakeMove(t.Context(), &request)
			assert.Error(t, err)
		})

		t.Run("SuccessfulSetReturnsSuccess", func(t *testing.T) {
			// This test mutates game state, so we set up a separate set of structs.
			inMemoryState := pb.GameState{
				Round: 1,
				Turn: 1,
				Players: []*pb.Player{
					{Id: "1", Symbol: "O"},
					{Id: "2", Symbol: "X"},
				},
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
			gameState := in_memory_game_state.NewInMemoryGameState(inMemoryStateMap)
			ruleSet := default_rule_set.NewDefaultRuleSet()
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Move: &pb.BoardMarker{
					Row: 2,
					Column: 2,
					Symbol: "X",
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			require.NotNil(t, res)
			assert.Empty(t, res.ValidationErrors)

			require.NotNil(t, res.GameState)
			finalState := res.GameState
			assert.Equal(t, 2, int(finalState.Turn))
			assert.Equal(t, 1, int(finalState.Round))
			assert.False(t, finalState.Finished)
			assert.Empty(t, finalState.Scores)

			require.NotNil(t, finalState.Board)
			board := finalState.Board
			require.Len(t, board.Markers, 2)
			assert.Equal(t, 1, int(board.Markers[0].Row))
			assert.Equal(t, 1, int(board.Markers[0].Column))
			assert.Equal(t, "O", board.Markers[0].Symbol)
			assert.Equal(t, 2, int(board.Markers[1].Row))
			assert.Equal(t, 2, int(board.Markers[1].Column))
			assert.Equal(t, "X", board.Markers[1].Symbol)

			request = pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Move: &pb.BoardMarker{
					Row: 0,
					Column: 0,
					Symbol: "O",
				},
			}
			res, err = grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			require.NotNil(t, res)
			assert.Empty(t, res.ValidationErrors)

			require.NotNil(t, res.GameState)
			finalState = res.GameState
			assert.Equal(t, 1, int(finalState.Turn))
			assert.Equal(t, 2, int(finalState.Round))
			assert.False(t, finalState.Finished)
			assert.Empty(t, finalState.Scores)
		})

		t.Run("GameEnd", func(t *testing.T) {
			// This test mutates game state, so we set up a separate set of structs.
			inMemoryState := pb.GameState{
				Round: 2,
				Turn: 2,
				Players: []*pb.Player{
					{Id: "1", Symbol: "O"},
					{Id: "2", Symbol: "X"},
				},
				Board: &pb.Board{
					Rows: 3,
					Columns: 3,
					Markers: []*pb.BoardMarker{
						{
							Row: 0,
							Column: 0,
							Symbol: "O",
						},
						{
							Row: 1,
							Column: 0,
							Symbol: "X",
						},
						{
							Row: 0,
							Column: 1,
							Symbol: "O",
						},
						{
							Row: 1,
							Column: 1,
							Symbol: "X",
						},
					},
				},
			}
			inMemoryStateMap := map[string]*pb.GameState{
				"game_id_1": &inMemoryState,
			}
			gameState := in_memory_game_state.NewInMemoryGameState(inMemoryStateMap)
			ruleSet := default_rule_set.NewDefaultRuleSet()
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Move: &pb.BoardMarker{
					Row: 0,
					Column: 2,
					Symbol: "O",
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			require.NotNil(t, res)
			assert.Empty(t, res.ValidationErrors)

			require.NotNil(t, res.GameState)
			finalState := res.GameState
			assert.Equal(t, 1, int(finalState.Turn))
			assert.Equal(t, 3, int(finalState.Round))
			assert.True(t, finalState.Finished)

			require.NotEmpty(t, finalState.Scores)
			scores := finalState.Scores
			require.Len(t, scores, 1)
			assert.Equal(t, "O", scores[0].Player.Symbol)
			assert.Equal(t, 1, int(scores[0].Score))
		})
	})
}
