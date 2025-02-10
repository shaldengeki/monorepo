package main

import (
	"context"
	"io"
	"log"
	"os"
	"github.com/shaldengeki/monorepo/proto_parser/token"
)

func main() {
	ctx := context.Background()
	logger := log.Default()

	protoText, err := io.ReadAll(os.Stdin)
	if err != nil {
		logger.Fatalf("Could not read stdin: %v", err)
	}

	tokens, err := token.ParseTokens(ctx, string(protoText))
	if err != nil {
		logger.Fatalf("Could not parse tokens: %v", err)
	}
	logger.Printf("Tokens: %v", tokens)

	return
}
