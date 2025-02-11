package parser

import (
	"context"
	"errors"
	"fmt"

	pbnode "github.com/shaldengeki/monorepo/proto_parser/proto/node"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	parserErrors "github.com/shaldengeki/monorepo/proto_parser/parser/errors"
)


func Parse(ctx context.Context, tokens []pbtoken.Token) (pbnode.NodeTree, error) {
	pos := 0
	nodeTree := pbnode.NodeTree{}

	if len(tokens) == 0 {
		return nodeTree, nil
	}

	parseFuncs := []func(context.Context, int, []pbtoken.Token)(pbnode.Node, int, error){}

	var unparseableError *parserErrors.NodeNotParseableError
	for {
		priorPos := pos
		for _, f := range parseFuncs {
			node, idx, err := f(ctx, pos, tokens)
			if err == nil {
				nodeTree.Nodes = append(nodeTree.Nodes, &node)
				pos = idx
				break
			}
			if !errors.As(err, &unparseableError) {
				return pbnode.NodeTree{}, fmt.Errorf("Unexpected error when parsing nodes at position %d: %w\nfor tokens: %s", pos, err, tokens)
			}
		}
		if pos >= len(tokens) {
			break
		}

		if pos == priorPos {
			return pbnode.NodeTree{}, fmt.Errorf("Token at position %d was unparseable in list: %v", pos, tokens)
		}
	}
	return nodeTree, nil
}
