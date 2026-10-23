package default_rule_set

import (
	"context"
	"fmt"

	"github.com/shaldengeki/monorepo/games/checkers/proto"
	"github.com/shaldengeki/monorepo/games/checkers/rule_set"
)

type DefaultRuleSet struct {
	rule_set.RuleSet
}

func (self DefaultRuleSet) InitialState(ctx context.Context) (*proto.GameState, error) {
	return &proto.GameState{
		Turn: 0,
		Round: 1,
		Finished: false,
		Board: &proto.Board{
			Rows: 8,
			Columns: 8,
			// TODO: fill this out.
			Markers: []*proto.BoardMarker{
				{Row: 0, Column: 0, Type: proto.BoardMarkerType_BOARD_MARKER_TYPE_PAWN, Player: &proto.Player{Id: "1"}},
			},
		},
		PlayerStates: []*proto.PlayerGameState{
			{Player: &proto.Player{Id: "1"}},
			{Player: &proto.Player{Id: "2"}},
		},
	}, nil
}

func (self DefaultRuleSet) ValidateState(ctx context.Context, gameState proto.GameState) (violations []string, err error) {
	if gameState.Turn < 1 {
		violations = append(violations, "Turn count should be >= 1")
	} else if gameState.PlayerStates != nil && int(gameState.Turn) > len(gameState.PlayerStates) {
		violations = append(violations, "Turn count must be <= # of players")
	}

	if gameState.Round < 1 {
		violations = append(violations, "Round count should be >= 1")
	}

	scoreViolations, err := self.ValidateStatePlayerStates(ctx, gameState.PlayerStates)
	if err != nil {
		return nil, fmt.Errorf("Could not validate player states in state: %w", err)
	}
	for _, v := range scoreViolations {
		violations = append(violations, v)
	}

	boardViolations, err := self.ValidateStateBoard(ctx, gameState.Board, gameState.Finished)
	if err != nil {
		return nil, fmt.Errorf("Could not validate board in state: %w", err)
	}
	for _, v := range boardViolations {
		violations = append(violations, v)
	}

	return violations, nil
}

func (self DefaultRuleSet) ValidateStatePlayerStates(ctx context.Context, playerStates []*proto.PlayerGameState) ([]string, error) {
	violations := []string{}

	hasPoints := false
	for _, playerState := range playerStates {
		if playerState.Score < 0 {
			violations = append(violations, fmt.Sprintf("Player %s score must be >= 0", playerState.Player.Id))
		} else if playerState.Score > 0 {
			if hasPoints {
				violations = append(violations, "Only one player may have points")
				break
			}
			hasPoints = true
		}
	}

	return violations, nil
}

func (self DefaultRuleSet) ValidateStateBoard(ctx context.Context, board *proto.Board, finished bool) ([]string, error) {
	violations := []string{}

	if board == nil {
		return violations, nil
	}

	boardViolations, err := self.ValidateBoard(ctx, board)
	if err != nil {
		return nil, fmt.Errorf("Could not validate board: %w", err)
	}
	for _, v := range boardViolations {
		violations = append(violations, v)
	}

	return violations, nil
}

func (self DefaultRuleSet) ValidateBoard(ctx context.Context, board *proto.Board) ([]string, error) {
	violations := []string{}

	if board.Rows < 1 {
		violations = append(violations, "Board must have >= 1 row")
	}

	if board.Columns < 1 {
		violations = append(violations, "Board must have >= 1 column")
	}

	positions := map[string]string{}
	for _, marker := range board.Markers {
		markerViolations, err := self.ValidateMarker(ctx, marker)
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
			violations = append(violations, fmt.Sprintf("More than one marker found at %s, pre-existing marker %s, conflicts with %s", coord, before, marker.Player.Id))
		} else {
			positions[coord] = marker.Player.Id
		}
	}

	return violations, nil
}

func (self DefaultRuleSet) ValidateMarker(ctx context.Context, marker *proto.BoardMarker) ([]string, error) {
	violations := []string{}

	if marker.Row < 0 {
		violations = append(violations, "Marker row must be >= 0")
	}

	if marker.Column < 0 {
		violations = append(violations, "Marker column must be >= 0")
	}

	// TODO: Allow a user to not pass the type, and inherit pre-existing value.
	if marker.Type == proto.BoardMarkerType_BOARD_MARKER_TYPE_UNKNOWN {
		violations = append(violations, "Marker type must be set")
	}

	if marker.Player == nil {
		violations = append(violations, "Marker player must be set")
	} else if marker.Player.Id == "" {
		violations = append(violations, "Marker player ID must be set")
	}

	return violations, nil
}

func (self DefaultRuleSet) PlayerIdAtPosition(ctx context.Context, startingLocations map[uint32]map[uint32]string, row uint32, column uint32) string {
	startingColumns, found := startingLocations[row]
	if !found {
		return ""
	}

	startingLocationPlayerId, found := startingColumns[column]
	if !found {
		return ""
	}

	return startingLocationPlayerId
}

func (self DefaultRuleSet) AllowedJumps(ctx context.Context, marker *proto.BoardMarker, startingLocations map[uint32]map[uint32]string, board *proto.Board) (map[uint32]map[uint32]bool, error) {
	allowedJumps := map[uint32]map[uint32]bool{}
	directions := [][]int{{-1, -1}, {-1, 1}, {1, -1}, {1, 1}}
	for _, direction := range directions {
		rowDelta, columnDelta := direction[0], direction[1]
		landingRow, landingColumn := direction[0] + int(marker.Row), direction[1] + int(marker.Column)

		// If this position is landable, add it and move on.
		if landingRow < 0 || uint32(landingRow) >= board.Rows || landingColumn < 0 || uint32(landingColumn) >= board.Columns {
			continue
		}
		landingRowTyped, landingColumnTyped := uint32(landingRow), uint32(landingColumn)

		// Next, check to see if this spot is open. If it is, it's the only allowed jump in this direction.
		playerAtPosition := self.PlayerIdAtPosition(ctx, startingLocations, landingRowTyped, landingColumnTyped)
		if playerAtPosition == "" {
			if _, found := allowedJumps[landingRowTyped]; !found {
				allowedJumps[landingRowTyped] = map[uint32]bool{}
			}
			allowedJumps[landingRowTyped][landingColumnTyped] = true
			continue
		}

		// Check to see if we can jump over a piece in this direction.
		if playerAtPosition == marker.Player.Id {
			continue
		}

		landingRow += rowDelta
		landingColumn += columnDelta
		if landingRow < 0 || uint32(landingRow) >= board.Rows || landingColumn < 0 || uint32(landingColumn) >= board.Columns {
			continue
		}
		landingRowTyped, landingColumnTyped = uint32(landingRow), uint32(landingColumn)

		playerAtPosition = self.PlayerIdAtPosition(ctx, startingLocations, landingRowTyped, landingColumnTyped)
		if playerAtPosition == "" {
			if _, found := allowedJumps[landingRowTyped]; !found {
				allowedJumps[landingRowTyped] = map[uint32]bool{}
			}
			allowedJumps[landingRowTyped][landingColumnTyped] = true
			continue
		}
	}

	return allowedJumps, nil
}

func (self DefaultRuleSet) JumpIsRegularMove(ctx context.Context, before *proto.BoardMarker, after *proto.BoardMarker) bool {
	rowDelta := int(before.Row) - int(after.Row)
	if rowDelta != 1 && rowDelta != -1 {
		return false
	}

	colDelta := int(before.Column) - int(after.Column)
	if colDelta != 1 && colDelta != -1 {
		return false
	}

	return true

}
func (self DefaultRuleSet) FindJumpedOverPiece(ctx context.Context, before *proto.BoardMarker, after *proto.BoardMarker, startingLocations map[uint32]map[uint32]string) *proto.BoardMarker {
	rowDelta := int(after.Row) - int(before.Row)
	if rowDelta != 2 && rowDelta != -2 {
		return nil
	}

	colDelta := int(after.Column) - int(before.Column)
	if colDelta != 2 && colDelta != -2 {
		return nil
	}

	jumpedOverRow := uint32(int(before.Row) + rowDelta / 2)
	locationCols, found := startingLocations[jumpedOverRow]
	if !found {
		return nil
	}

	jumpedOverColumn := uint32(int(before.Column) + colDelta / 2)
	jumpedOverId, found := locationCols[jumpedOverColumn]
	if !found {
		return nil
	}

	if jumpedOverId == before.Player.Id {
		return nil
	}

	return &proto.BoardMarker{
		Row: jumpedOverRow,
		Column: jumpedOverColumn,
		Player: &proto.Player{Id: jumpedOverId},
	}
}

func (self DefaultRuleSet) ValidateJumps(ctx context.Context, jumps []*proto.BoardMarker, startingLocations map[uint32]map[uint32]string, board *proto.Board) ([]string, error) {
	// TODO: enforce that the player can't move backwards unless it's a king.
	if len(jumps) < 2 {
		return []string{"Must have at least two locations in jumps"}, nil
	}

	_, found := startingLocations[jumps[0].Row][jumps[0].Column]
	if !found {
		return []string{fmt.Sprintf("there is no piece at (%d,%d) to jump with, locations are %v", jumps[0].Row, jumps[0].Column, startingLocations)}, nil
	}
	delete(startingLocations[jumps[0].Row], jumps[0].Column)

	violations := []string{}
	currentLocation := jumps[0]
	regularMoves := 0
	jumpMoves := 0
	for _, jump := range jumps[1:] {
		jumpErrors, err := self.ValidateMarker(ctx, jump)
		if err != nil {
			return violations, fmt.Errorf("validating marker for jump: %w", err)
		}

		violations = append(violations, jumpErrors...)

		allowedJumps, err := self.AllowedJumps(ctx, currentLocation, startingLocations, board)
		if err != nil {
			return violations, fmt.Errorf("calculating allowed jumps: %w", err)
		}
		allowedCols, foundRow := allowedJumps[jump.Row]
		if !foundRow {
			violations = append(violations, fmt.Sprintf("not allowed to jump from (%d,%d) to (%d,%d)", currentLocation.Row, currentLocation.Column, jump.Row, jump.Column))
		} else if _, foundCol := allowedCols[jump.Column]; !foundCol {
			violations = append(violations, fmt.Sprintf("not allowed to jump from (%d,%d) to (%d,%d)", currentLocation.Row, currentLocation.Column, jump.Row, jump.Column))
		}

		// Check if we're just moving.
		if self.JumpIsRegularMove(ctx, currentLocation, jump) {
			regularMoves += 1
		} else if jumpedOverPiece := self.FindJumpedOverPiece(ctx, currentLocation, jump, startingLocations); jumpedOverPiece != nil {
			jumpMoves += 1
			// Check if we're landing in a location with an un-jumped marker.
			if otherMarker, found := startingLocations[jump.Row][jump.Column]; found {
				violations = append(violations, fmt.Sprintf("another player (%s) has already claimed row %d, col %d", otherMarker, jump.Row, jump.Column))
			}

			delete(startingLocations[jumpedOverPiece.Row], jumpedOverPiece.Column)

		} else {
			violations = append(violations, fmt.Sprintf("jump from (%d,%d) to (%d,%d) is not a valid move", currentLocation.Row, currentLocation.Column, jump.Row, jump.Column))
		}
		currentLocation = jump
	}

	if regularMoves > 1 {
		violations = append(violations, "cannot make more than one regular move")
		if jumpMoves > 0 {
			violations = append(violations, "cannot make a regular move and a jump-over-piece move")
		}
	}

	if jumpMoves > 1 && jumps[0].Type != proto.BoardMarkerType_BOARD_MARKER_TYPE_KING {
		violations = append(violations, "only kings can make more than one jump-over-piece move")
	}

	return violations, nil
}

func (self DefaultRuleSet) ApplyMove(ctx context.Context, priorState proto.GameState, jumps []*proto.BoardMarker) (*proto.GameState, error) {
	if priorState.Finished {
		return nil, fmt.Errorf("game is already finished, can't make more moves")
	}

	if len(priorState.PlayerStates) == 0 {
		return nil, fmt.Errorf("cannot make moves in a game with no players")
	}

	currentPlayer, err := self.CurrentPlayer(ctx, &priorState)
	if err != nil {
		return nil, fmt.Errorf("could not determine current player when applying move on prior state %v: %w", priorState, err)
	}

	if len(jumps) < 2 {
		return nil, fmt.Errorf("jump must have at least starting and ending location")
	}

	jumpedMarkerLocations := map[uint32]map[uint32]bool{}
	occupiedSpaces := map[uint32]map[uint32]string{}
	for _, marker := range priorState.Board.Markers {
		if _, found := occupiedSpaces[marker.Row]; !found {
			occupiedSpaces[marker.Row] = map[uint32]string{}
		}
		occupiedSpaces[marker.Row][marker.Column] = marker.Player.Id
	}

	startingId, found := occupiedSpaces[jumps[0].Row][jumps[0].Column]
	if !found {
		return nil, fmt.Errorf("there is no piece at (%d,%d) to jump with", jumps[0].Row, jumps[0].Column)
	}

	if startingId != currentPlayer.Id {
		return nil, fmt.Errorf("current player is %s, can't jump piece at (%d,%d) owned by %s", currentPlayer.Id, jumps[0].Row, jumps[0].Column, jumps[0].Player.Id)
	}

	delete(occupiedSpaces[jumps[0].Row], jumps[0].Column)

	currentLocation := jumps[0]
	for _, jump := range jumps[1:] {
		// TODO: walk through jumps, identifying which pieces were jumped over, and accumulating jumped-over pieces.
		if jump.Player.Id != currentPlayer.Id {
			return nil, fmt.Errorf("it is not %s's turn to play (it is %s's)", jump.Player.Id, currentPlayer.Id)
		}

		// Check if we're jumping over a piece; accumulate in jumpedMarkerLocations if so.
		if jumpedOverPiece := self.FindJumpedOverPiece(ctx, currentLocation, jump, occupiedSpaces); jumpedOverPiece != nil {
			if _, found := jumpedMarkerLocations[jumpedOverPiece.Row]; !found {
				jumpedMarkerLocations[jumpedOverPiece.Row] = map[uint32]bool{}
			}
			jumpedMarkerLocations[jumpedOverPiece.Row][jumpedOverPiece.Column] = true

			// Also, remove from occupiedSpaces.
			delete(occupiedSpaces[jumpedOverPiece.Row], jumpedOverPiece.Column)
		}

		currentLocation = jump
	}

	updatedMarkers := []*proto.BoardMarker{}
	for _, marker := range priorState.Board.Markers {
		// This marker wasn't affected if it didn't move and wasn't jumped over.
		wasJumped := false
		cols, rowFound := jumpedMarkerLocations[marker.Row]
		if rowFound {
			_, wasJumped = cols[marker.Column]
		}
		movingPiece := marker.Row == jumps[0].Row && marker.Column == jumps[0].Column

		if !movingPiece && !wasJumped {
			updatedMarkers = append(updatedMarkers, marker)
		}
	}
	// Append moving piece at the end.
	updatedMarkers = append(updatedMarkers, jumps[len(jumps)-1])

	newState := priorState
	newState.Board.Markers = updatedMarkers
	newState.Turn += 1

	if (int(newState.Turn) - 1) % len(newState.PlayerStates) == 0 {
		newState.Round += 1
		newState.Turn = 1
	}

	finished, err := self.MoveFinishesGame(ctx, newState.Board)
	if err != nil {
		return nil, fmt.Errorf("could not check if move finished game with state %v: %w", newState, err)
	}

	lastJump := jumps[len(jumps)-1]
	if finished {
		newState.Finished = true

		var finishingPlayer *proto.Player
		for _, playerState := range newState.PlayerStates {
			if playerState.Player.Id == lastJump.Player.Id {
				playerState.Score = 1
				finishingPlayer = playerState.Player
			}
		}

		if finishingPlayer == nil {
			return nil, fmt.Errorf("could not find player who played finishing move %v", &lastJump)
		}
	}

	return &newState, nil
}

func (self DefaultRuleSet) MoveFinishesGame(ctx context.Context, board *proto.Board) (bool, error) {
	if board == nil {
		return false, fmt.Errorf("cannot check if move finished game for state with nil board")
	}

	if board.Markers == nil {
		return false, fmt.Errorf("cannot check if move finished game for state with nil markers")
	}

	// Check whether only one player has pieces on the board.
	singleAllowedPlayerId := ""
	for _, marker := range board.Markers {
		if singleAllowedPlayerId == "" {
			singleAllowedPlayerId = marker.Player.Id
		}
		if marker.Player.Id != singleAllowedPlayerId {
			return false, nil
		}
	}

	return true, nil
}

func (self DefaultRuleSet) CurrentPlayer(ctx context.Context, currentState *proto.GameState) (*proto.Player, error) {
	if currentState == nil {
		return nil, fmt.Errorf("cannot determine current player for nil game state")
	}

	if len(currentState.PlayerStates) == 0 {
		return nil, fmt.Errorf("cannot determine current player for empty player set")
	}

	// First, handle the start of game.
	if currentState.Turn == 0 {
		return currentState.PlayerStates[0].Player, nil
	}

	// Use the turn count to determine which player is current.
	playerIdx := int(currentState.Turn) % len(currentState.PlayerStates)
	return currentState.PlayerStates[playerIdx].Player, nil
}

func New() rule_set.RuleSet {
	return DefaultRuleSet{}
}
