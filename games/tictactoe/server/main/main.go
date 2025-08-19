package main

import (
	"log"
	"net"

	pbserver "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/server"

	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", "0.0.0.0:5003")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pbserver.RegisterGameServerServer(grpcServer, server.New(nil))
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Fatal error when serving request: %v", err)
	}
}
