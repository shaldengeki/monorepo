package main

import (
	"context"
	"errors"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/shaldengeki/monorepo/games/tictactoe/server"
)

var addr = flag.String("addr", "0.0.0.0:5003", "HTTP service address")

func main() {
	flag.Parse()

	s := server.New()
	s.Run()

	mux := http.NewServeMux()
	mux.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		s.ServeWs(w, r)
	})

	httpServer := &http.Server{
		Addr:    *addr,
		Handler: mux,
	}

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	done := make(chan bool, 1)

	go func() {
		sig := <-sigs
		log.Printf("Received signal: %s. Initiating graceful shutdown...", sig)

		shutdownCtx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
		defer cancel()
		if err := httpServer.Shutdown(shutdownCtx); err != nil {
			log.Printf("Failed to shutdown HTTP server: %v", err)
		}
		log.Printf("Graceful shutdown complete")
		done <- true
	}()

	log.Printf("Starting server on %s", *addr)

	go func() {
		err := httpServer.ListenAndServe()
		if err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("Server stopped: %v", err)
		}
	}()

	log.Printf("Waiting for shutdown signal")
	<-done
}
