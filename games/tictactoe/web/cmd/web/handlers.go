package main

import (
	"context"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"path/filepath"
	"strconv"

	"github.com/bazelbuild/rules_go/go/runfiles"
	pb "github.com/shaldengeki/monorepo/games/tictactoe/proto"
	serverpb "github.com/shaldengeki/monorepo/games/tictactoe/proto/server"
	"github.com/shaldengeki/monorepo/games/tictactoe/server/grpc"
	"github.com/shaldengeki/monorepo/games/tictactoe/game_state/in_memory_game_state"
	"github.com/shaldengeki/monorepo/games/tictactoe/rule_set/default_rule_set"
)

var gameStateServer = grpc.New(
	in_memory_game_state.New(map[string]*pb.GameState{}),
	default_rule_set.New(),
)

func resolveTemplatePath(p string) (string, error) {
	return runfiles.Rlocation(filepath.Join("_main", "games", "tictactoe", "web", "ui", p))
}

func resolveTemplatePaths(templates []string) ([]string, error) {
	resolvedTemplatePaths := make([]string, len(templates))
	for i, tmpl := range templates {
		res, err := resolveTemplatePath(tmpl)
		if err != nil {
			return []string{}, err
		}
		resolvedTemplatePaths[i] = res
	}
	return resolvedTemplatePaths, nil
}

func home(w http.ResponseWriter, r *http.Request) {
	resolvedTemplatePaths, err := resolveTemplatePaths([]string{
		"html/base.tmpl",
		"html/partials/nav.tmpl",
		"html/pages/home.tmpl",
	})
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	ts, err := template.ParseFiles(resolvedTemplatePaths...)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	err = ts.ExecuteTemplate(w, "base", nil)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}
}

func gameView(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil || id < 1 {
		http.NotFound(w, r)
		return
	}
	fmt.Fprintf(w, "Display a specific game with ID %d...", id)
}

func gameCreate(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Display a form for creating a new game..."))
}

func gameCreatePost(w http.ResponseWriter, r *http.Request) {
	resp, err := gameStateServer.CreateGame(context.Background(), &serverpb.CreateGameRequest{})
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}
	output := fmt.Sprintf("Before: %v | After: %v", resp, gameStateServer)

	w.WriteHeader(http.StatusCreated)
	w.Write([]byte(output))
}
