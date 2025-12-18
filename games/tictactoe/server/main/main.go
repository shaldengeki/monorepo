package main

import (
	"log"
	"net"

	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/in_memory_game_state"

	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", "0.0.0.0:5003")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pbserver.RegisterGameServiceServer(grpcServer, server.New(in_memory_game_state.NewInMemoryGameState(nil)))
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Fatal error when serving request: %v", err)
	}
}
