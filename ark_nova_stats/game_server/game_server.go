package game_server

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/game_state_provider"

	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/game_state"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/player_game_state"
	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto/server"

	"google.golang.org/grpc"
)

type gameServer struct {
	server.UnimplementedGameServerServer

	gameStateProvider game_state_provider.GameStateProvider
}

func (s *gameServer) GetState(ctx context.Context, request *server.GetStateRequest) (*server.GetStateResponse, error) {
	if request.GameId == 0 {
		return nil, errors.New("Game ID not provided")
	}

	state, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil {
		return nil, errors.New(fmt.Sprintf("Could not fetch game state: %v", err))
	}

	r := server.GetStateResponse{GameState: state}
	return &r, nil
}

func (s *gameServer) CalculateBreakMax(players int) int {
	return 1 + 4*players
}

func (s *gameServer) ValidateBreak(ctx context.Context, gameState *game_state.GameState) []string {
	if gameState.BreakCount < 0 {
		return []string{"Break count should be >= 0"}
	}

	if gameState.BreakMax < 1 {
		return []string{"Break max should be >= 1"}
	}

	if gameState.BreakMax < gameState.BreakCount {
		return []string{"Break count should be <= break max"}
	}

	if int(gameState.BreakMax) != s.CalculateBreakMax(len(gameState.PlayerGameStates)) {
		return []string{"Break max is incorrect for this number of players"}
	}

	return []string{}
}

func (s *gameServer) ValidateDisplay(ctx context.Context, gameState *game_state.GameState) []string {
	if gameState.DisplayState != nil && gameState.DisplayState.Cards != nil {
		if len(gameState.DisplayState.Cards) > 6 {
			return []string{"Display must contain at most six cards"}
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerGameState(ctx context.Context, playerGameState *player_game_state.PlayerGameState) []string {
	if playerGameState.PlayerId <= 0 {
		return []string{"Player ID not set"}
	}

	if playerGameState.Reputation < 0 {
		return []string{"Player reputation must be >= 0"}
	}

	return []string{}
}


func (s *gameServer) ValidateState(ctx context.Context, request *server.ValidateStateRequest) (*server.ValidateStateResponse, error) {
	if request.GameState == nil {
		return &server.ValidateStateResponse{}, nil
	}

	if request.GameState.Round < 1 {
		return &server.ValidateStateResponse{ValidationErrors: []string{"Round count should be >= 1"}}, nil
	}

	errs := s.ValidateBreak(ctx, request.GameState)
	if len(errs) > 0 {
		return &server.ValidateStateResponse{ValidationErrors: errs}, nil
	}

	errs = s.ValidateDisplay(ctx, request.GameState)
	if len(errs) > 0 {
		return &server.ValidateStateResponse{ValidationErrors: errs}, nil
	}

	if request.GameState.PlayerGameStates == nil || len(request.GameState.PlayerGameStates) < 1 {
		return &server.ValidateStateResponse{ValidationErrors: []string{"At least one player game state must be passed"}}, nil
	}

	for _, playerGameState := range request.GameState.PlayerGameStates {
		errs = s.ValidatePlayerGameState(ctx, playerGameState)
		if len(errs) > 0 {
			return &server.ValidateStateResponse{ValidationErrors: errs}, nil
		}
	}

	return &server.ValidateStateResponse{}, nil
}

func New(gameStateProvider game_state_provider.GameStateProvider) *gameServer {
	return &gameServer{gameStateProvider: gameStateProvider}
}

func main() {
	lis, err := net.Listen("tcp", "localhost:5003")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	server.RegisterGameServerServer(grpcServer, New(nil))
	grpcServer.Serve(lis)
}

/*
	TODO:
		- write tests for invalid states within each board component, like:
			- invalid buildings (off grid, two of one, enclosure over-occupied, etc)
			- invalid partner zoos (two of one)
			- invalid animals (too many for the enclosures we have)
		- implement ValidateState, passing each test

		future directions:
		- spin up game server
			- spin up game server, backed by postgres
			- create database tables
			- backfill with BGA game logs
				- Add a CreateTable rpc
				- In Python, add worker logic to call CreateTable with game logs
			- in stats db, call GetState and render endgame state
		- support play
			- add protos for taking actions
			- add TakeAction rpc and implement it, returning GameState
*/
