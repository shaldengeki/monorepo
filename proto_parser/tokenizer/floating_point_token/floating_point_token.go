package floating_point_token

import (
	"context"
	"fmt"
	"strings"

	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/decimal_token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func IsExponentRune(r rune) bool {
	return strings.ContainsRune("eE", r)
}

func IsExponentValueRune(r rune) bool {
	return decimal_token.IsDecimalRune(r) || strings.ContainsRune("-+", r)
}

func ParseFloatingPointToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse floating point in position %d in body of length %d", start, len(body))
	}

	negative := false
	if string(body[start]) == "-" {
		negative = true
		start += 1
	}
	if start >= len(body) {
		return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as a floating point literal", body)}
	}

	if start+3 <= len(body) && string(body[start:start+3]) == "inf" {
		return pbtoken.Token{
			Token: &pbtoken.Token_FloatingPointToken{
				FloatingPointToken: &pbtoken.FloatingPointToken{
					FloatingPointType: &pbtoken.FloatingPointToken_Inf{
						Inf: true,
					},
					Negative: negative,
				},
			},
		}, start + 3, nil
	} else if start+3 <= len(body) && string(body[start:start+3]) == "nan" {
		return pbtoken.Token{
			Token: &pbtoken.Token_FloatingPointToken{
				FloatingPointToken: &pbtoken.FloatingPointToken{
					FloatingPointType: &pbtoken.FloatingPointToken_Nan{
						Nan: true,
					},
					Negative: negative,
				},
			},
		}, start + 3, nil
	}

	// decimals "." [ decimals ] [ exponent ] | decimals exponent | "."decimals [ exponent ]
	hasDecimalPoint := false
	hasExponent := false
	stringToScan := string(body[start:])
	endIdx := 0
	for idx, r := range stringToScan {
		if !hasDecimalPoint && strings.ContainsRune(".", r) {
			hasDecimalPoint = true
			endIdx = idx
			continue
		}

		if !hasExponent && IsExponentRune(r) {
			hasExponent = true
			endIdx = idx
			continue
		}

		if hasExponent && IsExponentValueRune(r) {
			endIdx = idx
			continue
		}

		if !decimal_token.IsDecimalRune(r) {
			break
		}
		endIdx = idx
	}

	if endIdx == 0 {
		return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is not a parseable as a floating point literal", body, start)}
	}

	if !hasDecimalPoint && !hasExponent {
		return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is not a parseable as a floating point literal", body, start)}
	}

	return pbtoken.Token{
		Token: &pbtoken.Token_FloatingPointToken{
			FloatingPointToken: &pbtoken.FloatingPointToken{
				Negative: negative,
				FloatingPointType: &pbtoken.FloatingPointToken_Literal{
					Literal: string(stringToScan[:endIdx+1]),
				},
			},
		},
	}, start + endIdx + 1, nil
}
