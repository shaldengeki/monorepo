package token

import (
	"context"
	"errors"
	"fmt"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	"github.com/shaldengeki/monorepo/proto_parser/token/whitespace_token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/token/errors"
)


func ParseTokens(ctx context.Context, body string) ([]pbtoken.Token, error) {
	pos := 0
	tokens := []pbtoken.Token{}

	if len(body) == 0 {
		return tokens, nil
	}

	parseFuncs := []func(context.Context, int, string)(pbtoken.Token, int, error){
		whitespace_token.ParseWhitespaceToken,
	}

	var unparseableError *tokenErrors.TokenNotParseableError
	for {
		for _, f := range parseFuncs {
			tkn, idx, err := f(ctx, pos, body)
			if err == nil {
				tokens = append(tokens, tkn)
				pos = pos + idx
				break
			}
			if !errors.As(err, &unparseableError) {
				return []pbtoken.Token{}, fmt.Errorf("Unexpected error when parsing tokens at position %d: %w\nfor body: %s", pos, err, body)
			}
		}
		if pos >= len(body) {
			break
		}
	}
	return tokens, nil
}
