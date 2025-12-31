package default_rule_set

import (
	"testing"
	pb "github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestValidateState(t *testing.T) {
	ruleSet := NewDefaultRuleSet()

	t.Run("InvalidWithEmptyState", func(t *testing.T) {
		state := pb.GameState{}

		violations, err := ruleSet.ValidateState(t.Context(), state)
		require.NoError(t, err)
		assert.NotEmpty(t, violations)
	})

	t.Run("Turn", func(t *testing.T) {
		// Turn = 1
		state := pb.GameState{Turn: 1, Round: 1}
		violations, err := ruleSet.ValidateState(t.Context(), state)
		require.NoError(t, err)
		assert.Empty(t, violations)

		// Turn = 0
		state = pb.GameState{Turn: 0, Round: 1}
		violations, err = ruleSet.ValidateState(t.Context(), state)
		require.NoError(t, err)
		assert.NotEmpty(t, violations)

		// Turn > # players
		state = pb.GameState{Turn: 3, Round: 1, Players: []*pb.Player{{Symbol: "X"}, {Symbol: "O"}}}
		violations, err = ruleSet.ValidateState(t.Context(), state)
		require.NoError(t, err)
		assert.NotEmpty(t, violations)
	})

	t.Run("Round", func(t *testing.T) {
		// Round = 1
		state := pb.GameState{Turn: 1, Round: 1}
		violations, err := ruleSet.ValidateState(t.Context(), state)
		require.NoError(t, err)
		assert.Empty(t, violations)

		// Round = 0
		state = pb.GameState{Turn: 1, Round: 0}
		violations, err = ruleSet.ValidateState(t.Context(), state)
		require.NoError(t, err)
		assert.NotEmpty(t, violations)
	})
	// bool finished = 3;
	// repeated Score scores = 4;
	// Board board = 5;
	// repeated Player players = 6;
}

func TestCurrentPlayer(t *testing.T) {
	ruleSet := NewDefaultRuleSet()

	t.Run("Nil", func(t *testing.T) {
		_, err := ruleSet.CurrentPlayer(t.Context(), nil)
		require.Error(t, err)
	})

	t.Run("EmptyPlayers", func(t *testing.T) {
		_, err := ruleSet.CurrentPlayer(t.Context(), &pb.GameState{Players: []*pb.Player{}})
		require.Error(t, err)
	})

	t.Run("Start", func(t *testing.T) {
		state := pb.GameState{
			Round: 1,
			Turn: 0,
			Players: []*pb.Player{
				{Id: "1", Symbol: "O"},
				{Id: "2", Symbol: "X"},
			},
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				Markers: []*pb.BoardMarker{},
			},
		}
		player, err := ruleSet.CurrentPlayer(t.Context(), &state)
		require.NoError(t, err)
		assert.Equal(t, "1", player.Id)
		assert.Equal(t, "O", player.Symbol)
	})

	t.Run("Middle", func(t *testing.T) {
		state := pb.GameState{
			Round: 2,
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
					{
						Row: 2,
						Column: 1,
						Symbol: "X",
					},
					{
						Row: 0,
						Column: 1,
						Symbol: "O",
					},
				},
			},
		}
		player, err := ruleSet.CurrentPlayer(t.Context(), &state)
		require.NoError(t, err)
		assert.Equal(t, "2", player.Id)
		assert.Equal(t, "X", player.Symbol)
	})
}

func TestApplyMove(t *testing.T) {
	ruleSet := NewDefaultRuleSet()

	t.Run("WrongPlayer", func(t *testing.T) {
		// Wrong first player.
		state := pb.GameState{
			Round: 1,
			Turn: 0,
			Players: []*pb.Player{
				{Id: "1", Symbol: "O"},
				{Id: "2", Symbol: "X"},
			},
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				Markers: []*pb.BoardMarker{},
			},
		}
		move := pb.BoardMarker{
			Row: 2,
			Column: 2,
			Symbol: "X",
		}
		_, err := ruleSet.ApplyMove(t.Context(), state, &move)
		assert.Error(t, err)

		// Wrong player, further in.
		state = pb.GameState{
			Round: 2,
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
					{
						Row: 2,
						Column: 1,
						Symbol: "X",
					},
					{
						Row: 0,
						Column: 1,
						Symbol: "O",
					},
				},
			},
		}
		move = pb.BoardMarker{
			Row: 2,
			Column: 2,
			Symbol: "O",
		}
		_, err = ruleSet.ApplyMove(t.Context(), state, &move)
		assert.Error(t, err)
	})

	t.Run("ZeroPlayers", func(t *testing.T) {
		state := pb.GameState{
			Round: 1,
			Turn: 0,
			Players: []*pb.Player{},
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				Markers: []*pb.BoardMarker{},
			},
		}
		move := pb.BoardMarker{
			Row: 2,
			Column: 2,
			Symbol: "X",
		}
		_, err := ruleSet.ApplyMove(t.Context(), state, &move)
		assert.Error(t, err)
	})
}

func TestMoveFinishesGame(t *testing.T) {
	// XO
	// XXO
	//   O
	board := pb.Board{
		Rows: 3,
		Columns: 3,
		Markers: []*pb.BoardMarker{
			{
				Row: 0,
				Column: 1,
				Symbol: "O",
			},
			{
				Row: 1,
				Column: 0,
				Symbol: "X",
			},
			{
				Row: 1,
				Column: 2,
				Symbol: "O",
			},
			{
				Row: 1,
				Column: 1,
				Symbol: "X",
			},
			{
				Row: 2,
				Column: 2,
				Symbol: "O",
			},
			{
				Row: 0,
				Column: 0,
				Symbol: "X",
			},
		},
	}
	ruleSet := NewDefaultRuleSet()

	t.Run("NonFinishingMove", func(t *testing.T) {
		move := pb.BoardMarker{
			Row: 2,
			Column: 0,
			Symbol: "O",
		}
		finished, err := ruleSet.MoveFinishesGame(t.Context(), &move, &board)
		require.NoError(t, err)
		assert.False(t, finished)
	})
	t.Run("FinishingMove", func(t *testing.T) {
		move := pb.BoardMarker{
			Row: 0,
			Column: 2,
			Symbol: "O",
		}
		finished, err := ruleSet.MoveFinishesGame(t.Context(), &move, &board)
		require.NoError(t, err)
		assert.True(t, finished)
	})
}
