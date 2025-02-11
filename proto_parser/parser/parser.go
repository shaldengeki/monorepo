package parser

import (
	"context"
	pbnode "github.com/shaldengeki/monorepo/proto_parser/proto/node"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)


func Parse(ctx context.Context, tokens []pbtoken.Token) (pbnode.NodeTree, error) {
	return pbnode.NodeTree{}, nil
}
