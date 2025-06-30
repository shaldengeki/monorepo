package main

import (
	"log"
	"net"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server"
	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto/server"

	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", "localhost:5003")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	server.RegisterGameServerServer(grpcServer, game_server.New(nil))
	grpcServer.Serve(lis)
}
