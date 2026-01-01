package main

import (
	"log"
	"net"

	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	servergrpc "github.com/shaldengeki/monorepo/games/tictactoe/server/grpc"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/rule_set/default_rule_set"

	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", "0.0.0.0:5003")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pbserver.RegisterGameServiceServer(
		grpcServer,
		servergrpc.New(
			in_memory_game_state.New(nil),
			default_rule_set.New(),
		),
	)
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Fatal error when serving request: %v", err)
	}
}
