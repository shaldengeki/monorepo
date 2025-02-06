package whitespace_token

import (
	"context"
	"fmt"
	"strings"
	token "github.com/shaldengeki/monorepo/proto_parser/token"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func ParseWhitespaceToken(ctx context.Context, start int, body string) (pbtoken.Token, error) {
	if start >= len(body) {
		return pbtoken.Token{}, fmt.Errorf("Cannot parse position %i in body of length %i", start, len(body))
	}
	if !strings.ContainsAny(string(body[start]), " \n\t") {
		return pbtoken.Token{}, token.TokenNotParseableError(fmt.Sprintf("character %s is not whitespace", string(body[start])))
	}
	return pbtoken.Token{}, nil
}
