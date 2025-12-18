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

	// Next, fetch this game's state.
	priorState, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil {
		return nil, fmt.Errorf("could not get game state to make move for game %s: %w", request.GameId, err)
	}

	// Next, apply the move.
	updatedGameState, err := s.ApplyMove(ctx, priorState, request.Move)
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

func (s *gameServer) ApplyMove(ctx context.Context, priorState *proto.GameState, move *proto.BoardMarker) (*proto.GameState, error) {
	// TODO
	return priorState, nil
}

func New(gameStateProvider game_state.GameState) *gameServer {
	return &gameServer{gameStateProvider: gameStateProvider}
}
