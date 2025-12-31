package server

import (
	"context"
	"errors"
	"fmt"

	"github.com/shaldengeki/monorepo/games/tictactoe/game_state"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
	"github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
)

type gameServer struct {
	server.UnimplementedGameServiceServer

	gameStateProvider game_state.GameState
	gameCount int
}

func (s *gameServer) CreateGame(ctx context.Context, request *server.CreateGameRequest) (*server.CreateGameResponse, error) {
	gameId := fmt.Sprintf("%d", s.gameCount)
	err := s.gameStateProvider.SetState(ctx, gameId, proto.GameState{Turn: 0, Round: 1, Finished: false, Board: &proto.Board{Rows: 3, Columns: 3}, Players: []*proto.Player{{Id: "1", Symbol: "X"}, {Id: "2", Symbol: "O"}}})
	if err != nil {
		return nil, fmt.Errorf("could not create game with id %d: %w", gameId, err)
	}

	s.gameCount += 1

	return &server.CreateGameResponse{
		GameId: gameId,
	}, nil
}

func (s *gameServer) GetState(ctx context.Context, request *server.GetStateRequest) (*server.GetStateResponse, error) {
	if request.GameId == "" {
		return nil, errors.New("Game ID not provided")
	}

	state, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil {
		return nil, fmt.Errorf("Could not fetch game state: %v", err)
	}

	r := server.GetStateResponse{GameState: state}
	return &r, nil
}

func (s *gameServer) ValidateState(ctx context.Context, request *server.ValidateStateRequest) (*server.ValidateStateResponse, error) {
	if request.GameState == nil {
		return &server.ValidateStateResponse{}, nil
	}

	violations, err := s.ValidateGameState(ctx, *request.GameState)
	if err != nil {
		return nil, fmt.Errorf("could not validate state: %w", err)
	}

	return &server.ValidateStateResponse{ValidationErrors: violations}, nil
}

func (s *gameServer) ValidateGameState(ctx context.Context, gameState proto.GameState) (violations []string, err error) {
	if gameState.Turn < 1 {
		violations = append(violations, "Turn count should be >= 1")
	} else if gameState.Players != nil && int(gameState.Turn) > len(gameState.Players) {
		violations = append(violations, "Turn count must be <= # of players")
	}

	if gameState.Round < 1 {
		violations = append(violations, "Round count should be >= 1")
	}

	scoreViolations, err := s.ValidateStateScores(ctx, gameState.Scores)
	if err != nil {
		return nil, fmt.Errorf("Could not validate scores in state: %w", err)
	}
	for _, v := range scoreViolations {
		violations = append(violations, v)
	}

	boardViolations, err := s.ValidateStateBoard(ctx, gameState.Board, gameState.Finished)
	if err != nil {
		return nil, fmt.Errorf("Could not validate board in state: %w", err)
	}
	for _, v := range boardViolations {
		violations = append(violations, v)
	}

	return violations, nil
}

func (s *gameServer) ValidateStateScores(ctx context.Context, scores []*proto.Score) ([]string, error) {
	violations := []string{}

	hasPoints := false
	for _, score := range scores {
		if score.Score < 0 {
			violations = append(violations, fmt.Sprintf("Player %s score must be >= 0", score.Player))
		} else if score.Score > 0 {
			if hasPoints {
				violations = append(violations, "Only one player may have points")
				break
			}
			hasPoints = true
		}
	}

	return violations, nil
}

func (s *gameServer) ValidateStateBoard(ctx context.Context, board *proto.Board, finished bool) ([]string, error) {
	violations := []string{}

	if board == nil {
		return violations, nil
	}

	boardViolations, err := s.ValidateBoard(ctx, board)
	if err != nil {
		return nil, fmt.Errorf("Could not validate board: %w", err)
	}
	for _, v := range boardViolations {
		violations = append(violations, v)
	}

	return violations, nil
}

func (s *gameServer) ValidateBoard(ctx context.Context, board *proto.Board) ([]string, error) {
	violations := []string{}

	if board.Rows < 1 {
		violations = append(violations, "Board must have >= 1 row")
	}

	if board.Columns < 1 {
		violations = append(violations, "Board must have >= 1 column")
	}

	positions := map[string]string{}
	for _, marker := range board.Markers {
		markerViolations, err := s.ValidateMarker(ctx, marker)
		if err != nil {
			return nil, fmt.Errorf("Could not validate marker: %w", err)
		}
		for _, v := range markerViolations {
			violations = append(violations, v)
		}

		coord := fmt.Sprintf("%d,%d", marker.Row, marker.Column)
		if marker.Row >= board.Rows {
			violations = append(violations, fmt.Sprintf("Marker at %s is past board edge with %d rows", coord, board.Rows))
		}
		if marker.Column >= board.Columns {
			violations = append(violations, fmt.Sprintf("Marker at %s is past board edge with %d columns", coord, board.Columns))
		}

		if before, ok := positions[coord]; ok {
			violations = append(violations, fmt.Sprintf("More than one marker found at %s, pre-existing marker %s, conflicts with %s", coord, before, marker.Symbol))
		} else {
			positions[coord] = marker.Symbol
		}
	}

	return violations, nil
}

func (s *gameServer) ValidateMarker(ctx context.Context, marker *proto.BoardMarker) ([]string, error) {
	violations := []string{}

	if marker.Row < 0 {
		violations = append(violations, "Marker row must be >= 0")
	}

	if marker.Column < 0 {
		violations = append(violations, "Marker column must be >= 0")
	}

	if marker.Symbol == "" {
		violations = append(violations, "Marker symbol must be set")
	} else if len(marker.Symbol) > 1 {
		violations = append(violations, "Marker symbol must only be a single character")
	}

	return violations, nil
}

func (s *gameServer) MakeMove(ctx context.Context, request *server.MakeMoveRequest) (*server.MakeMoveResponse, error) {
	if request == nil {
		return &server.MakeMoveResponse{ValidationErrors: []string{"move must be non-empty"}}, nil
	}

	// First, validate the move prospectively.
	validationErrors, err := s.ValidateMarker(ctx, request.Move)
	if err != nil {
		return nil, fmt.Errorf("could not validate move request: %w", err)
	}
	if len(validationErrors) > 0 {
		return &server.MakeMoveResponse{ValidationErrors: validationErrors}, nil
	}

	// TODO: this won't work with any sort of concurrency; we'll need some sort of locking.

	// Next, fetch this game's state.
	priorState, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil || priorState == nil {
		return nil, fmt.Errorf("could not get game state to make move for game %s: prior state %v, err %w", request.GameId, priorState, err)
	}

	// Next, apply the move.
	updatedGameState, err := s.ApplyMove(ctx, *priorState, request.Move)
	if err != nil {
		return nil, fmt.Errorf("could not apply move to prior state for game %s: %w", request.GameId, err)
	}

	// Next, validate the resulting state.
	updatedValidationErrors, err := s.ValidateGameState(ctx, *updatedGameState)
	if err != nil {
		return nil, fmt.Errorf("could not validate updated game state: %w", err)
	}
	if len(updatedValidationErrors) > 0 {
		return &server.MakeMoveResponse{ValidationErrors: updatedValidationErrors}, nil
	}

	// Finally, commit the result.
	err = s.gameStateProvider.SetState(ctx, request.GameId, *updatedGameState)
	if err != nil {
		return nil, fmt.Errorf("could not set updated state for game %s: %w", request.GameId, err)
	}

	return &server.MakeMoveResponse{GameState: updatedGameState}, nil
}

func (s *gameServer) CurrentPlayer(ctx context.Context, currentState *proto.GameState) (*proto.Player, error) {
	if currentState == nil {
		return nil, fmt.Errorf("cannot determine current player for nil game state")
	}

	if len(currentState.Players) == 0 {
		return nil, fmt.Errorf("cannot determine current player for empty player set")
	}

	// First, handle the start of game.
	if currentState.Turn == 0 {
		return currentState.Players[0], nil
	}

	// Use the turn count to determine which player is current.
	playerIdx := int(currentState.Turn) % len(currentState.Players)
	return currentState.Players[playerIdx], nil
}

func (s *gameServer) ApplyMove(ctx context.Context, priorState proto.GameState, move *proto.BoardMarker) (*proto.GameState, error) {
	if priorState.Finished {
		return nil, fmt.Errorf("game is already finished, can't make more moves")
	}

	if len(priorState.Players) == 0 {
		return nil, fmt.Errorf("cannot make moves in a game with no players")
	}

	currentPlayer, err := s.CurrentPlayer(ctx, &priorState)
	if err != nil {
		return nil, fmt.Errorf("could not determine current player when applying move on prior state %v: %w", priorState, err)
	}

	if move.Symbol != currentPlayer.Symbol {
		return nil, fmt.Errorf("it is not %s's turn to play (it is %s's)", move.Symbol, currentPlayer.Symbol)
	}

	for _, otherMarker := range priorState.Board.Markers {
		if move.Row == otherMarker.Row && move.Column == otherMarker.Column {
			return nil, fmt.Errorf("another player (%s) has already claimed row %d, col %d", otherMarker.Symbol, otherMarker.Row, otherMarker.Column)
		}
	}
	newState := priorState
	newState.Board.Markers = append(newState.Board.Markers, move)
	newState.Turn += 1

	if (int(newState.Turn) - 1) % len(newState.Players) == 0 {
		newState.Round += 1
		newState.Turn = 1
	}

	finished, err := s.MoveFinishesGame(ctx, move, newState.Board)
	if err != nil {
		return nil, fmt.Errorf("could not check if move finished game with state %v: %w", newState, err)
	}

	if finished {
		newState.Finished = true

		var finishingPlayer *proto.Player
		for _, player := range newState.Players {
			if player.Symbol == move.Symbol {
				finishingPlayer = player
			}
		}

		if finishingPlayer == nil {
			return nil, fmt.Errorf("could not find player who played finishing move %v", &move)
		}

		newState.Scores = append(newState.Scores, &proto.Score{Player: finishingPlayer, Score: 1})
	}

	return &newState, nil
}

func (s *gameServer) MoveFinishesGame(ctx context.Context, move *proto.BoardMarker, board *proto.Board) (bool, error) {
	if board == nil {
		return false, fmt.Errorf("cannot check if move finished game for state with nil board")
	}

	if board.Markers == nil {
		return false, fmt.Errorf("cannot check if move finished game for state with nil markers")
	}

	// Count the number of markers in the current entry's row, column, and diagonal, if square.
	// If it equals the length of the board in that dimension, they've won.
	// Start with 1 in every count, to account for the current move.
	numRow := 1
	numColumn := 1
	numDiagPositive := 1
	numDiagNegative := 1
	for _, marker := range board.Markers {
		if marker.Symbol != move.Symbol {
			continue
		}

		// Skip the current move.
		if marker.Row == move.Row && marker.Column == move.Column {
			continue
		}

		if marker.Row == move.Row {
			numRow += 1
		} else if marker.Column == move.Column {
			numColumn += 1
		}
		if board.Rows == board.Columns {
			if (marker.Column - move.Column) == (marker.Row - move.Row) && (marker.Column - move.Column) >= 0 {
				numDiagPositive += 1
			}
			if (marker.Column - move.Column) == (marker.Row - move.Row) && (marker.Column - move.Column) <= 0 {
				numDiagNegative += 1
			}
		}
	}
	if numRow == int(board.Rows) || numColumn == int(board.Columns) {
		return true, nil
	}
	if board.Rows == board.Columns && (numDiagPositive == int(board.Rows) || numDiagNegative == int(board.Rows)) {
		return true, nil
	}

	return false, nil
}

func New(gameStateProvider game_state.GameState) *gameServer {
	return &gameServer{gameStateProvider: gameStateProvider}
}
