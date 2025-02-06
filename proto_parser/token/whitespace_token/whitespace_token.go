package whitespace_token

import (
	"context"
	"fmt"
	"strings"
	token "github.com/shaldengeki/monorepo/proto_parser/token"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func ParseWhitespaceToken(ctx context.Context, start int, body string) (pbtoken.WhitespaceToken, int, error) {
	if start >= len(body) {
		return pbtoken.WhitespaceToken{}, 0, fmt.Errorf("Cannot parse position %i in body of length %i", start, len(body))
	}
	if !strings.ContainsAny(string(body[start]), " \n\t") {
		return pbtoken.WhitespaceToken{}, 0, token.TokenNotParseableError(fmt.Sprintf("character %s is not whitespace", string(body[start])))
	}

	stringToScan := string(body[start:])
	removedBody := strings.TrimLeft(stringToScan, " \n\t")
	whitespaceLength := len(stringToScan) - len(removedBody)

	return pbtoken.WhitespaceToken{
		Spaces: string(body[start:start+whitespaceLength]),
	}, start + whitespaceLength, nil
}
