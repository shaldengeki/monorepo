package server

import (
	"context"
	"log"
	"sync"
	"sync/atomic"
	// "github.com/shaldengeki/monorepo/games/tictactoe/game_state_provider"
)

type MoveRequest struct {
	Move   Move
	Client *Client
}

type gameServer struct {
	// gameStateProvider game_state_provider.GameStateProvider
	board               *Board
	moveRequests        chan MoveRequest
	shutdownBegan       atomic.Bool
	backgroundJobCtx    context.Context
	backgroundJobCancel context.CancelFunc
	backgroundJobWg     *sync.WaitGroup
	processMovesCtx     context.Context
	processMovesCancel  context.CancelFunc
}

func (s *gameServer) Run() {
	go s.processMoves()
	go s.boardToDiskHandler.RunForever()
}

func (s *gameServer) processMoves() {
	s.backgroundJobWg.Add(1)
	defer s.backgroundJobWg.Done()

	for {
		select {
		case <-s.processMovesCtx.Done():
			log.Printf("processMoves: context done")
			return
		case moveReq := <-s.moveRequests:
			if s.processMovesCtx.Err() != nil {
				log.Printf("processMoves: context done")
				return
			}

			moveResult := s.board.ValidateAndApplyMove__NOTTHREADSAFE(moveReq.Move)
			if !moveResult.Valid {
				moveReq.Client.SendInvalidMove(moveReq.Move.MoveToken)
				continue
			}

			if moveResult.WinningMove {
				log.Printf("Received the winning move!")
				s.gameOver.Store(true)
				s.processMovesCancel()
			}

			s.boardToDiskHandler.AddMove(&moveReq.Move)

			if moveResult.CapturedPiece.Piece.IsEmpty() {
				moveMetadata := MoveMetadata{
					DidCapture: false,
					Internal:   false,
				}
				if len(moveResult.MovedPieces) > 0 {
					moveMetadata.PieceType = moveResult.MovedPieces[0].Piece.Type
				}
				moveReq.Client.SendValidMove(moveReq.Move.MoveToken,
					moveResult.Seqnum,
					moveMetadata,
					0)
			} else {
				moveMetadata := MoveMetadata{
					DidCapture:        true,
					Internal:          false,
					CapturedPieceType: moveResult.CapturedPiece.Piece.Type,
				}
				if len(moveResult.MovedPieces) > 0 {
					moveMetadata.PieceType = moveResult.MovedPieces[0].Piece.Type
				}
				moveReq.Client.SendValidMove(moveReq.Move.MoveToken,
					moveResult.Seqnum,
					moveMetadata,
					moveResult.CapturedPiece.Piece.ID)
			}

		case adoptionReq := <-s.adoptionRequests:
			adoptionResult, err := s.board.Adopt(&adoptionReq)
			if err != nil || adoptionResult == nil {
				continue
			}
			s.boardToDiskHandler.AddAdoption(&adoptionReq)

			go func() {
				affectedZones := s.clientManager.AffectedZonesForAdoption(&adoptionReq)
				interestedClients := s.clientManager.GetClientsForZones(affectedZones)
				m := &protocol.ServerMessage{
					Payload: &protocol.ServerMessage_Adoption{
						Adoption: &protocol.ServerAdoption{
							AdoptedIds: adoptionResult.AdoptedPieces,
						},
					},
				}
				message, err := proto.Marshal(m)
				if err != nil {
					log.Printf("Error marshalling adoption: %v", err)
					return
				}

				for client := range interestedClients {
					client.SendAdoption(message)
				}
				s.clientManager.ReturnClientMap(interestedClients)
			}()

		case bulkCaptureReq := <-s.bulkCaptureRequests:
			bulkCaptureMsg, err := s.board.DoBulkCapture(&bulkCaptureReq)
			if err != nil || bulkCaptureMsg == nil {
				continue
			}
			s.boardToDiskHandler.AddBulkCapture(&bulkCaptureReq)

			go func() {
				m := &protocol.ServerMessage{
					Payload: &protocol.ServerMessage_BulkCapture{
						BulkCapture: bulkCaptureMsg,
					},
				}
				message, err := proto.Marshal(m)
				if err != nil {
					log.Printf("Error marshalling bulk capture: %v", err)
					return
				}
				affectedZones := s.clientManager.AffectedZonesForBulkCapture(&bulkCaptureReq)
				interestedClients := s.clientManager.GetClientsForZones(affectedZones)
				for client := range interestedClients {
					client.SendBulkCapture(message)
				}
				s.clientManager.ReturnClientMap(interestedClients)
			}()
		}
	}
}

// func (s *gameServer) GetState(ctx context.Context, request *server.GetStateRequest) (*server.GetStateResponse, error) {
// 	if request.GameId == "" {
// 		return nil, errors.New("Game ID not provided")
// 	}

// 	state, err := s.gameStateProvider.GetState(ctx, request.GameId)
// 	if err != nil {
// 		return nil, fmt.Errorf("Could not fetch game state: %v", err)
// 	}

// 	r := server.GetStateResponse{GameState: state}
// 	return &r, nil
// }

// func (s *gameServer) ValidateState(ctx context.Context, request *server.ValidateStateRequest) (*server.ValidateStateResponse, error) {
// 	if request.GameState == nil {
// 		return &server.ValidateStateResponse{}, nil
// 	}

// 	violations := []string{}

// 	if request.GameState.Turn < 1 {
// 		violations = append(violations, "Turn count should be >= 1")
// 	}

// 	if request.GameState.Round < 1 {
// 		violations = append(violations, "Round count should be >= 1")
// 	}

// 	scoreViolations, err := s.ValidateStateScores(ctx, request.GameState.Scores)
// 	if err != nil {
// 		return nil, fmt.Errorf("Could not validate scores in state: %w", err)
// 	}
// 	for _, v := range scoreViolations {
// 		violations = append(violations, v)
// 	}

// 	boardViolations, err := s.ValidateStateBoard(ctx, request.GameState.Board, request.GameState.Finished)
// 	if err != nil {
// 		return nil, fmt.Errorf("Could not validate board in state: %w", err)
// 	}
// 	for _, v := range boardViolations {
// 		violations = append(violations, v)
// 	}

// 	return &server.ValidateStateResponse{ValidationErrors: violations}, nil
// }

// func (s *gameServer) ValidateStateScores(ctx context.Context, scores []*proto.Score) ([]string, error) {
// 	violations := []string{}

// 	hasPoints := false
// 	for _, score := range scores {
// 		if score.Score < 0 {
// 			violations = append(violations, fmt.Sprintf("Player %s score must be >= 0", score.Player))
// 		} else if score.Score > 0 {
// 			if hasPoints {
// 				violations = append(violations, "Only one player may have points")
// 				break
// 			}
// 			hasPoints = true
// 		}
// 	}

// 	return violations, nil
// }

// func (s *gameServer) ValidateStateBoard(ctx context.Context, board *proto.Board, finished bool) ([]string, error) {
// 	violations := []string{}

// 	boardViolations, err := s.ValidateBoard(ctx, board)
// 	if err != nil {
// 		return nil, fmt.Errorf("Could not validate board: %w", err)
// 	}
// 	for _, v := range boardViolations {
// 		violations = append(violations, v)
// 	}

// 	return violations, nil
// }

// func (s *gameServer) ValidateBoard(ctx context.Context, board *proto.Board) ([]string, error) {
// 	violations := []string{}

// 	if board.Rows < 1 {
// 		violations = append(violations, "Board must have >= 1 row")
// 	}

// 	if board.Columns < 1 {
// 		violations = append(violations, "Board must have >= 1 column")
// 	}

// 	positions := map[string]string{}
// 	for _, marker := range board.Markers {
// 		markerViolations, err := s.ValidateMarker(ctx, marker)
// 		if err != nil {
// 			return nil, fmt.Errorf("Could not validate marker: %w", err)
// 		}
// 		for _, v := range markerViolations {
// 			violations = append(violations, v)
// 		}

// 		coord := fmt.Sprintf("%d,%d", marker.Row, marker.Column)
// 		if marker.Row >= board.Rows {
// 			violations = append(violations, fmt.Sprintf("Marker at %s is past board edge with %d rows", coord, board.Rows))
// 		}
// 		if marker.Column >= board.Columns {
// 			violations = append(violations, fmt.Sprintf("Marker at %s is past board edge with %d columns", coord, board.Columns))
// 		}

// 		if before, ok := positions[coord]; ok {
// 			violations = append(violations, fmt.Sprintf("More than one marker found at %s, pre-existing marker %s, conflicts with %s", coord, before, marker.Symbol))
// 		} else {
// 			positions[coord] = marker.Symbol
// 		}
// 	}

// 	return violations, nil
// }

// func (s *gameServer) ValidateMarker(ctx context.Context, marker *proto.BoardMarker) ([]string, error) {
// 	violations := []string{}

// 	if marker.Row < 0 {
// 		violations = append(violations, "Marker row must be >= 0")
// 	}

// 	if marker.Column < 0 {
// 		violations = append(violations, "Marker column must be >= 0")
// 	}

// 	if marker.Symbol == "" {
// 		violations = append(violations, "Marker symbol must be set")
// 	} else if len(marker.Symbol) > 1 {
// 		violations = append(violations, "Marker symbol must only be a single character")
// 	}

// 	return violations, nil
// }

func New() *gameServer {
	return &gameServer{}
}
