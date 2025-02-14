package identifier_token

import (
	"context"
	"fmt"
	"strings"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func IsIdentifierLeadingRune(r rune) bool {
	return strings.ContainsRune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", r)
}

func IsIdentifierRune(r rune) bool {
	return strings.ContainsRune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789", r)
}

func ParseIdentifierToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse identifier in position %d in body of length %d", start, len(body))
	}

	if !IsIdentifierLeadingRune(rune(body[start])) {
		return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as an identifier", body)}
	}

	stringToScan := string(body[start:])
	endIdx := 0
	for idx, r := range stringToScan {
		if !IsIdentifierRune(r) {
			break
		}
		endIdx = idx
	}

	return pbtoken.Token{
		Token: &pbtoken.Token_IdentifierToken{
			IdentifierToken: &pbtoken.IdentifierToken{
				Identifier: string(body[:endIdx + 1]),
			},
		},
	}, start + endIdx + 1, nil
}
