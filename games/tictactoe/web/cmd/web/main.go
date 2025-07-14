package main

import (
	"log"
	"net/http"
	"path/filepath"

	"github.com/bazelbuild/rules_go/go/runfiles"
)

func main() {
	mux := http.NewServeMux()
	mainCssPath, err := runfiles.Rlocation(filepath.Join("_main", "games", "tictactoe", "web", "ui", "static", "css", "main.css"))
	if err != nil {
		log.Fatal(err)
	}
	staticPath := filepath.Dir(filepath.Dir(mainCssPath))

	fileServer := http.FileServer(http.Dir(staticPath))
	mux.Handle("GET /static/", http.StripPrefix("/static", fileServer))

	mux.HandleFunc("GET /{$}", home)
	mux.HandleFunc("GET /game/view/{id}", gameView)
	mux.HandleFunc("GET /game/create", gameCreate)
	mux.HandleFunc("POST /game/create", gameCreatePost)

	log.Print("Starting server on :4000")
	err = http.ListenAndServe(":4000", mux)
	log.Fatal(err)
}
