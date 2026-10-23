package grpc

import (
	"testing"
	pb "github.com/shaldengeki/monorepo/games/checkers/proto"
	pbserver "github.com/shaldengeki/monorepo/games/checkers/proto/server"
	"github.com/shaldengeki/monorepo/games/checkers/game_state/empty_game_state"
	"github.com/shaldengeki/monorepo/games/checkers/game_state/in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/checkers/game_state/read_only_in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/checkers/game_state/static_game_state"
	"github.com/shaldengeki/monorepo/games/checkers/rule_set/default_rule_set"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func copyState(state *pb.GameState) *pb.GameState {
	players := make([]*pb.Player, len(state.Players))
	playerMap := map[string]*pb.Player{}
	for idx, player := range state.Players {
		players[idx] = &pb.Player{Id: player.Id}
		playerMap[player.Id] = players[idx]
	}

	scores := make([]*pb.Score, len(state.Scores))
	for idx, score := range state.Scores {
		scores[idx] = &pb.Score{
			Player: playerMap[score.Player.Id],
			Score: score.Score,
		}
	}

	markers := make([]*pb.BoardMarker, len(state.Board.Markers))
	for idx, marker := range state.Board.Markers {
		markers[idx] = &pb.BoardMarker{
			Row: marker.Row,
			Column: marker.Column,
			Type: marker.Type,
			Player: playerMap[marker.Player.Id],
		}
	}

	board := &pb.Board{
		Rows: state.Board.Rows,
		Columns: state.Board.Columns,
		Markers: markers,
	}

	return &pb.GameState{
		Turn: state.Turn,
		Round: state.Round,
		Finished: state.Finished,
		Scores: scores,
		Board: board,
		Players: players,
	}
}

func TestValidateState(t *testing.T) {
	gameState := empty_game_state.New()
	ruleSet := default_rule_set.New()
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
		request = pbserver.ValidateStateRequest{GameState: &pb.GameState{Turn: 3, Round: 1, Players: []*pb.Player{{Id: "X"}, {Id: "O"}}}}
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
		gameState := empty_game_state.New()
		ruleSet := default_rule_set.New()
		grpcServer := New(gameState, ruleSet)

		t.Run("NilRequestReturnsValidationError", func(t *testing.T) {
			res, err := grpcServer.MakeMove(t.Context(), nil)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("InvalidMoveReturnsInfraError", func(t *testing.T) {
			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 1, Column: 1, Player: &pb.Player{Id: ""}},
					{Row: 1, Column: 1, Player: &pb.Player{Id: ""}},
				},
			}
			_, err := grpcServer.MakeMove(t.Context(), &request)
			require.Error(t, err)
		})
	})

	t.Run("WithState", func(t *testing.T) {
		state := pb.GameState{
			Round: 1,
			Players: []*pb.Player{
				{Id: "O"},
				{Id: "X"},
			},
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				//
				//  O
				// X O
				Markers: []*pb.BoardMarker{
					{
						Row: 0,
						Column: 0,
						Player: &pb.Player{Id: "X"},
						Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
					},
					{
						Row: 0,
						Column: 2,
						Player: &pb.Player{Id: "O"},
						Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
					},
					{
						Row: 1,
						Column: 1,
						Player: &pb.Player{Id: "O"},
						Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
					},
				},
			},
		}

		ruleSet := default_rule_set.New()

		t.Run("NilRequestReturnsValidationError", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			res, err := grpcServer.MakeMove(t.Context(), nil)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("InvalidMoveReturnsValidationError", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 1, Column: 1, Player: &pb.Player{Id: ""}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("MoveIntoSameSpaceReturnsValidationError", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 0, Column: 2, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
					{Row: 0, Column: 2, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("NonExistentPieceReturnsValidationError", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 1, Column: 0, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
					{Row: 0, Column: 1, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("CollidingMoveReturnsValidationError", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 0, Column: 2, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
					{Row: 1, Column: 1, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("EmptyJumpsReturnsValidationError", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)

			request = pbserver.MakeMoveRequest{}
			res, err = grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("InvalidJumpDirectionReturnsValidationError", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 1, Column: 1, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
					{Row: 2, Column: 0, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)

			request = pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 1, Column: 1, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
					{Row: 1, Column: 0, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err = grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})


		t.Run("JumpIntoOriginalSpaceReturnsSuccess", func(t *testing.T) {
			state := pb.GameState{
				Round: 1,
				Players: []*pb.Player{
					{Id: "O"},
					{Id: "X"},
				},
				Board: &pb.Board{
					Rows: 5,
					Columns: 5,
					//   
					//  X X
					// O  
					//  X X
					//
					Markers: []*pb.BoardMarker{
						{
							Row: 2,
							Column: 0,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING,
						},
						{
							Row: 1,
							Column: 1,
							Player: &pb.Player{Id: "X"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 1,
							Column: 3,
							Player: &pb.Player{Id: "X"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 3,
							Column: 1,
							Player: &pb.Player{Id: "X"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 3,
							Column: 3,
							Player: &pb.Player{Id: "X"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
					},
				},
			}
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 2, Column: 0, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 4, Column: 2, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 2, Column: 4, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 0, Column: 2, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 2, Column: 0, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.Empty(t, res.ValidationErrors)
		})

		t.Run("JumpOverAlreadyJumpedOverPieceReturnsValidationError", func(t *testing.T) {
			state := pb.GameState{
				Round: 1,
				Players: []*pb.Player{
					{Id: "O"},
					{Id: "X"},
				},
				Board: &pb.Board{
					Rows: 5,
					Columns: 5,
					//   
					//  O O
					// X  
					//  O O
					//
					Markers: []*pb.BoardMarker{
						{
							Row: 2,
							Column: 0,
							Player: &pb.Player{Id: "X"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING,
						},
						{
							Row: 1,
							Column: 1,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 1,
							Column: 3,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 3,
							Column: 1,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 3,
							Column: 3,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
					},
				},
			}
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 2, Column: 0, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 4, Column: 2, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 2, Column: 4, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 0, Column: 2, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 2, Column: 0, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
					{Row: 4, Column: 2, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_KING},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("SingleMoveIntoEmptySpaceReturnsSuccess", func(t *testing.T) {
			gameState := static_game_state.New(copyState(&state))
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				Jumps: []*pb.BoardMarker{
					{Row: 1, Column: 1, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
					{Row: 2, Column: 2, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.Empty(t, res.ValidationErrors)
		})

		t.Run("InvalidSetStateReturnsValidationError", func(t *testing.T) {
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
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
					},
				},
				Players: []*pb.Player{
					{Id: "O"},
					{Id: "X"},
				},
			}
			readOnlyStateMap := map[string]*pb.GameState{
				"game_id_1": &readOnlyState,
			}
			gameState := read_only_in_memory_game_state.New(readOnlyStateMap)
			ruleSet := default_rule_set.New()
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Jumps: []*pb.BoardMarker{
					{Row: 2, Column: 2, Player: &pb.Player{Id: "X"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
				},
			}
			res, err := grpcServer.MakeMove(t.Context(), &request)
			require.NoError(t, err)
			assert.NotEmpty(t, res.ValidationErrors)
		})

		t.Run("SuccessfulSetReturnsSuccess", func(t *testing.T) {
			// This test mutates game state, so we set up a separate set of structs.
			inMemoryState := pb.GameState{
				Round: 1,
				Turn: 1,
				Players: []*pb.Player{
					{Id: "O"},
					{Id: "X"},
				},
				Board: &pb.Board{
					Rows: 3,
					Columns: 3,
					Markers: []*pb.BoardMarker{
						{
							Row: 2,
							Column: 0,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 1,
							Column: 1,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 0,
							Column: 0,
							Player: &pb.Player{Id: "X"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
					},
				},
			}
			inMemoryStateMap := map[string]*pb.GameState{
				"game_id_1": &inMemoryState,
			}
			gameState := in_memory_game_state.New(inMemoryStateMap)
			ruleSet := default_rule_set.New()
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Jumps: []*pb.BoardMarker{
					{Row: 0, Column: 0, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN, Player: &pb.Player{Id: "X"}},
					{Row: 2, Column: 2, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN, Player: &pb.Player{Id: "X"}},
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
			assert.Equal(t, 2, int(board.Markers[0].Row))
			assert.Equal(t, 0, int(board.Markers[0].Column))
			assert.Equal(t, "O", board.Markers[0].Player.Id)
			assert.Equal(t, 2, int(board.Markers[1].Row))
			assert.Equal(t, 2, int(board.Markers[1].Column))
			assert.Equal(t, "X", board.Markers[1].Player.Id)

			request = pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Jumps: []*pb.BoardMarker{
					{Row: 2, Column: 0, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
					{Row: 1, Column: 1, Player: &pb.Player{Id: "O"}, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN},
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
					{Id: "O"},
					{Id: "X"},
				},
				Board: &pb.Board{
					Rows: 3,
					Columns: 3,
					Markers: []*pb.BoardMarker{
						{
							Row: 0,
							Column: 0,
							Player: &pb.Player{Id: "O"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
						{
							Row: 1,
							Column: 1,
							Player: &pb.Player{Id: "X"},
							Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN,
						},
					},
				},
			}
			inMemoryStateMap := map[string]*pb.GameState{
				"game_id_1": &inMemoryState,
			}
			gameState := in_memory_game_state.New(inMemoryStateMap)
			ruleSet := default_rule_set.New()
			grpcServer := New(gameState, ruleSet)

			request := pbserver.MakeMoveRequest{
				GameId: "game_id_1",
				Jumps: []*pb.BoardMarker{
					{Row: 0, Column: 0, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN, Player: &pb.Player{Id: "O"}},
					{Row: 2, Column: 2, Type: pb.BoardMarkerType_BOARD_MARKER_TYPE_PAWN, Player: &pb.Player{Id: "O"}},
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
			assert.Equal(t, "O", scores[0].Player.Id)
			assert.Equal(t, 1, int(scores[0].Score))
		})
	})
}
