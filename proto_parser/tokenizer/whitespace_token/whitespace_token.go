package whitespace_token

import (
	"context"
	"fmt"
	"strings"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func ParseWhitespaceToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse position %d in body of length %d", start, len(body))
	}

	stringToScan := string(body[start:])
	removedBody := strings.TrimLeft(stringToScan, " \n\t")
	whitespaceLength := len(stringToScan) - len(removedBody)

	if whitespaceLength == 0 {
		return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("character %s is not whitespace", string(body[start]))}
	}

	return pbtoken.Token{
		Token: &pbtoken.Token_WhitespaceToken{
			WhitespaceToken: &pbtoken.WhitespaceToken{
				Spaces: string(body[start:start+whitespaceLength]),
			},
		},
	}, start + whitespaceLength, nil
}
