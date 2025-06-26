package main

import (
	"context"
	"io"
	"log"
	"os"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer"
	"github.com/shaldengeki/monorepo/proto_parser/parser"
)

func main() {
	ctx := context.Background()
	logger := log.Default()

	protoText, err := io.ReadAll(os.Stdin)
	if err != nil {
		logger.Fatalf("Could not read stdin: %v", err)
	}

	tokens, err := tokenizer.Tokenize(ctx, string(protoText))
	if err != nil {
		logger.Fatalf("Could not parse tokens: %v", err)
	}
	logger.Printf("Tokens: %v", tokens)

	nodeTree, err := parser.Parse(ctx, tokens)
	if err != nil {
		logger.Fatalf("Could not parse into node tree: %v", err)
	}
	logger.Printf("Node tree: %v", nodeTree)

	return
}
