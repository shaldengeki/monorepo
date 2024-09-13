package game_server

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/game_state_provider"

	proto "github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto"
	stateProto "github.com/shaldengeki/monorepo/ark_nova_stats/proto"

	"google.golang.org/grpc"
)

type gameServer struct {
	proto.UnimplementedGameServerServer

	gameStateProvider game_state_provider.GameStateProvider
}

func (s *gameServer) GetState(ctx context.Context, request *proto.GetStateRequest) (*proto.GetStateResponse, error) {
	if request.GameId == 0 {
		return nil, errors.New("Game ID not provided")
	}

	state, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil {
		return nil, errors.New(fmt.Sprintf("Could not fetch game state: %v", err))
	}

	r := proto.GetStateResponse{GameState: state}
	return &r, nil
}

func (s *gameServer) ValidateMapState(ctx context.Context, gameState *stateProto.GameState) []string {
	// TODO: implement this.
	return []string{}
}

func (s *gameServer) ValidateState(ctx context.Context, request *proto.ValidateStateRequest) (*proto.ValidateStateResponse, error) {
	if request.GameState == nil {
		return &proto.ValidateStateResponse{}, nil
	}

	if request.GameState.Round < 1 {
		return &proto.ValidateStateResponse{ValidationErrors: []string{"Round count should be >= 1"}}, nil
	}

	if request.GameState.BreakCount < 0 {
		return &proto.ValidateStateResponse{ValidationErrors: []string{"Break count should be >= 0"}}, nil
	}

	if request.GameState.BreakMax < 1 {
		return &proto.ValidateStateResponse{ValidationErrors: []string{"Break max should be >= 1"}}, nil
	}

	errs := s.ValidateMapState(ctx, request.GameState)
	if len(errs) > 0 {
		return &proto.ValidateStateResponse{ValidationErrors: errs}, nil
	}

	return &proto.ValidateStateResponse{}, nil
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
	proto.RegisterGameServerServer(grpcServer, New(nil))
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
