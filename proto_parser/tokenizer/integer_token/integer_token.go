package integer_token

import (
	"context"
	"errors"
	"fmt"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/decimal_token"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/octal_token"
)

func ParseIntegerToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse integer in position %d in body of length %d", start, len(body))
	}

	var unparseableError *tokenErrors.TokenNotParseableError

	decToken, idx, err := decimal_token.ParseDecimalToken(ctx, start, body)
	if err == nil {
		return pbtoken.Token{
			Token: &pbtoken.Token_IntegerToken{
				IntegerToken: &pbtoken.IntegerToken{
					IntegerType: &pbtoken.IntegerToken_DecimalToken{
						DecimalToken: &decToken,
					},
				},
			},
		}, idx, nil
	}
	if !errors.As(err, &unparseableError) {
		return pbtoken.Token{}, start, fmt.Errorf("Unexpected error when parsing decimal tokens at position %d: %w\nfor body: %s", start, err, body)
	}

	octalToken, idx, err := octal_token.ParseOctalToken(ctx, start, body)
	if err == nil {
		return pbtoken.Token{
			Token: &pbtoken.Token_IntegerToken{
				IntegerToken: &pbtoken.IntegerToken{
					IntegerType: &pbtoken.IntegerToken_OctalToken{
						OctalToken: &octalToken,
					},
				},
			},
		}, idx, nil
	}
	if !errors.As(err, &unparseableError) {
		return pbtoken.Token{}, start, fmt.Errorf("Unexpected error when parsing octal tokens at position %d: %w\nfor body: %s", start, err, body)
	}

	return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is not a parseable as an integer literal", body, start)}
}
