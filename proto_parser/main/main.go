package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"os"
	pbnode "github.com/shaldengeki/monorepo/proto_parser/proto/node"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer"
	"github.com/shaldengeki/monorepo/proto_parser/parser"
)

func ParseProtoText(ctx context.Context, protoText string) (pbnode.NodeTree, error) {
	logger := log.Default()

	tokens, err := tokenizer.Tokenize(ctx, string(protoText))
	if err != nil {
		return pbnode.NodeTree{}, fmt.Errorf("Could not tokenize proto text %s: %w", string(protoText), err)
	}
	logger.Printf("Tokens: %v", tokens)

	nodeTree, err := parser.Parse(ctx, tokens)
	if err != nil {
		return pbnode.NodeTree{}, fmt.Errorf("Could not parse tokens %v into node tree: %w", tokens, err)
		logger.Fatalf("Could not parse into node tree: %v", err)
	}

	return nodeTree, nil
}

func main() {
	ctx := context.Background()
	logger := log.Default()

	protoText, err := io.ReadAll(os.Stdin)
	if err != nil {
		logger.Fatalf("Could not read stdin: %v", err)
	}

	nodeTree, err := ParseProtoText(ctx, string(protoText))
	if err != nil {
		logger.Fatalf("Could not parse proto text %s: %v", string(protoText), err)
	}

	logger.Printf("Node tree: %v", nodeTree)

	return
}
