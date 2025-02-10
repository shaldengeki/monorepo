package main

import (
	"context"
	"io"
	"log"
	"os"
	tokenizer "github.com/shaldengeki/monorepo/proto_parser/tokenizer"
)

func main() {
	ctx := context.Background()
	logger := log.Default()

	protoText, err := io.ReadAll(os.Stdin)
	if err != nil {
		logger.Fatalf("Could not read stdin: %v", err)
	}

	tokens, err := tokenizer.ParseTokens(ctx, string(protoText))
	if err != nil {
		logger.Fatalf("Could not parse tokens: %v", err)
	}
	logger.Printf("Tokens: %v", tokens)

	return
}
