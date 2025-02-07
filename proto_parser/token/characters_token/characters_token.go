package characters_token

import (
	"context"
	"fmt"
	"strings"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/token/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func ParseCharactersToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse position %d in body of length %d", start, len(body))
	}

	stringToScan := string(body[start:])
	idx := 0
	for _, c := range stringToScan {
		if strings.ContainsRune(" \n\t", c) {
			break
		}
		idx += 1
	}

	if idx == 0 {
		return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("character %s is not a non-whitespace character", string(body[start]))}
	}

	return pbtoken.Token{
		Token: &pbtoken.Token_CharactersToken{
			CharactersToken: &pbtoken.CharactersToken{
				Characters: string(body[start:start+idx]),
			},
		},
	}, start + idx, nil
}
