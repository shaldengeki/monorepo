package boolean_token

import (
	"context"
	"fmt"

	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func ParseBooleanToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse boolean in position %d in body of length %d", start, len(body))
	}

	if start+4 <= len(body) && string(body[start:start+4]) == "true" {
		return pbtoken.Token{
			Token: &pbtoken.Token_BooleanToken{
				BooleanToken: &pbtoken.BooleanToken{
					Value: true,
				},
			},
		}, start + 4, nil
	} else if start+5 <= len(body) && string(body[start:start+5]) == "false" {
		return pbtoken.Token{
			Token: &pbtoken.Token_BooleanToken{
				BooleanToken: &pbtoken.BooleanToken{
					Value: false,
				},
			},
		}, start + 5, nil
	}

	return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is not a parseable as a boolean literal", body, start)}
}
