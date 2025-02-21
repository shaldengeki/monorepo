package string_token

import (
	"context"
	"errors"
	"fmt"

	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func ParseStringSingleToken(ctx context.Context, start int, body string) (pbtoken.StringSingleToken, int, error) {
	return pbtoken.StringSingleToken{}, start, fmt.Errorf("TODO")
}

func ParseStringToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse string literal in position %d in body of length %d", start, len(body))
	}

	var unparseableError *tokenErrors.TokenNotParseableError

	idx := start
	tokens := []*pbtoken.StringSingleToken{}

	for {
		tkn, newIdx, err := ParseStringSingleToken(ctx, idx, body)
		if err == nil {
			tokens = append(tokens, &tkn)
			idx = newIdx

			if idx >= len(body) {
				break
			}
			continue
		}

		if errors.As(err, &unparseableError) {
			return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is not a parseable as an string literal", body, start)}
		} else {
			return pbtoken.Token{}, start, fmt.Errorf("Unexpected error when parsing string literal tokens at position %d: %w\nfor body: %s", idx, err, body)
		}
	}

	return pbtoken.Token{
		Token: &pbtoken.Token_StringToken{
			StringToken: &pbtoken.StringToken{
				StringLiterals: tokens,
			},
		},
	}, idx, nil
}
