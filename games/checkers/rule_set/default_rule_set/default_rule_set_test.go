package default_rule_set

import (
	"testing"
	pb "github.com/shaldengeki/monorepo/games/checkers/proto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestValidateState(t *testing.T) {
	ruleSet := New()

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
		state = pb.GameState{Turn: 3, Round: 1, Players: []*pb.Player{{}, {}}}
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
	ruleSet := New()

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
				{Id: "1"},
				{Id: "2"},
			},
			Board: &pb.Board{
				Rows: 8,
				Columns: 8,
				Markers: []*pb.BoardMarker{},
			},
		}
		player, err := ruleSet.CurrentPlayer(t.Context(), &state)
		require.NoError(t, err)
		assert.Equal(t, "1", player.Id)
	})

	t.Run("Middle", func(t *testing.T) {
		state := pb.GameState{
			Round: 2,
			Turn: 1,
			Players: []*pb.Player{
				{Id: "1"},
				{Id: "2"},
			},
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				Markers: []*pb.BoardMarker{
					{
						Row: 1,
						Column: 1,
					},
					{
						Row: 2,
						Column: 1,
					},
					{
						Row: 0,
						Column: 1,
					},
				},
			},
		}
		player, err := ruleSet.CurrentPlayer(t.Context(), &state)
		require.NoError(t, err)
		assert.Equal(t, "2", player.Id)
	})
}

func TestApplyMove(t *testing.T) {
	ruleSet := New()

	t.Run("WrongPlayer", func(t *testing.T) {
		// Wrong first player.
		state := pb.GameState{
			Round: 1,
			Turn: 0,
			Players: []*pb.Player{
				{Id: "1"},
				{Id: "2"},
			},
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				// TODO: Set up an initial board.
				Markers: []*pb.BoardMarker{},
			},
		}
		jumps := []*pb.BoardMarker{
			{Row: 2, Column: 2, Player: &pb.Player{Id: "2"}},
			{Row: 2, Column: 2, Player: &pb.Player{Id: "2"}},
		}
		_, err := ruleSet.ApplyMove(t.Context(), state, jumps)
		assert.Error(t, err)

		// Wrong player, further in.
		state = pb.GameState{
			Round: 2,
			Turn: 1,
			Players: []*pb.Player{
				{Id: "1"},
				{Id: "2"},
			},
			Board: &pb.Board{
				Rows: 3,
				Columns: 3,
				Markers: []*pb.BoardMarker{
					{
						Row: 1,
						Column: 1,
					},
					{
						Row: 2,
						Column: 1,
					},
					{
						Row: 0,
						Column: 1,
					},
				},
			},
		}
		jumps = []*pb.BoardMarker{
			{Row: 2, Column: 2},
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
			},
			{
				Row: 1,
				Column: 0,
			},
			{
				Row: 1,
				Column: 2,
			},
			{
				Row: 1,
				Column: 1,
			},
			{
				Row: 2,
				Column: 2,
			},
			{
				Row: 0,
				Column: 0,
			},
		},
	}
	ruleSet := New()

	t.Run("NonFinishingMove", func(t *testing.T) {
		move := pb.BoardMarker{
			Row: 2,
			Column: 0,
		}
		finished, err := ruleSet.MoveFinishesGame(t.Context(), &move, &board)
		require.NoError(t, err)
		assert.False(t, finished)
	})
	t.Run("FinishingMove", func(t *testing.T) {
		move := pb.BoardMarker{
			Row: 0,
			Column: 2,
		}
		finished, err := ruleSet.MoveFinishesGame(t.Context(), &move, &board)
		require.NoError(t, err)
		assert.True(t, finished)
	})
}
