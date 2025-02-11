package syntax_node

import (
	"context"
	"fmt"
	"strings"
	parserErrors "github.com/shaldengeki/monorepo/proto_parser/parser/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	pbnode "github.com/shaldengeki/monorepo/proto_parser/proto/node"
)

func ParseSyntaxNode(ctx context.Context, start int, tokens []pbtoken.Token) (pbnode.Node, int, error) {
	if start >= len(tokens) {
		return pbnode.Node{}, 0, fmt.Errorf("Cannot parse syntax node in position %d in tokens of length %d", start, len(tokens))
	}

	return pbnode.Node{
		Node: &pbnode.Node_SyntaxNode{
			SyntaxNode: &pbtoken.SyntaxNode{
				Syntax: "test",
			},
		},
	}, start + 1, nil
}
