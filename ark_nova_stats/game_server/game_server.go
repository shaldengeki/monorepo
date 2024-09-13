package game_server

import (
	"context"
	"errors"
	"log"
	"net"

	proto "github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto"

	"google.golang.org/grpc"
)

type gameServer struct {
	proto.UnimplementedGameServerServer
}

func (s *gameServer) GetState(_ context.Context, request *proto.GetStateRequest) (*proto.GetStateResponse, error) {
	if request.GameId == 0 {
		return nil, errors.New("Game ID not provided")
	}

	r := proto.GetStateResponse{}
	return &r, nil
}

func newServer() *gameServer {
	return &gameServer{}
}

func main() {
	lis, err := net.Listen("tcp", "localhost:5003")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	proto.RegisterGameServerServer(grpcServer, newServer())
	grpcServer.Serve(lis)
}

/*
	TODO:
		- set up a fixture for a sample game state
		- implement GetState, returning the fixture
		- wrangle into a test for GetState
		- implement skeleton for ValidateState
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
