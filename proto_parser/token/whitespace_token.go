package token

import (
	"context"
	"fmt"
	"strings"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func ParseWhitespaceToken(ctx context.Context, start int, body string) (pbtoken.WhitespaceToken, error) {
	if !strings.ContainsAny(string(body[start]), " \n\t") {
		return pbtoken.WhitespaceToken{}, TokenNotParseableError(fmt.Sprintf("character %s is not whitespace", string(body[start])))
	}
	return pbtoken.WhitespaceToken{}, nil
}
