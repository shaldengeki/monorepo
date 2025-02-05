package token

import (
	"context"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func ParseTokens(ctx context.Context, body string) ([]pbtoken.Token, error) {
	return []pbtoken.Token{}, nil
}
