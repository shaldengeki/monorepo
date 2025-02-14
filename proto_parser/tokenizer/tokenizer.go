package tokenizer

import (
	"context"
	"errors"
	"fmt"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/identifier_token"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/whitespace_token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)


func Tokenize(ctx context.Context, body string) ([]pbtoken.Token, error) {
	pos := 0
	tokens := []pbtoken.Token{}

	if len(body) == 0 {
		return tokens, nil
	}

	// To add support for a new parseable token, add a function into this list.
	// The function should return TokenNotParseableError when the current string doesn't match the token type (but could be a valid token),
	// and any other error when the string is definitely invalid.
	parseFuncs := []func(context.Context, int, string)(pbtoken.Token, int, error){
		whitespace_token.ParseWhitespaceToken,
		identifier_token.ParseIdentifierToken,
	}

	var unparseableError *tokenErrors.TokenNotParseableError
	for {
		for _, f := range parseFuncs {
			tkn, idx, err := f(ctx, pos, body)
			if err == nil {
				tokens = append(tokens, tkn)
				pos = idx
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
