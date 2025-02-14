package decimal_token

import (
	"context"
	"fmt"
	"strings"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func IsDecimalLeadingRune(r rune) bool {
	return strings.ContainsRune("123456789", r)
}

func IsDecimalRune(r rune) bool {
	return strings.ContainsRune("0123456789", r)
}

func ParseDecimalToken(ctx context.Context, start int, body string) (pbtoken.DecimalToken, int, error) {
	if start >= len(body) {
		return pbtoken.DecimalToken{}, 0, fmt.Errorf("Cannot parse identifier in position %d in body of length %d", start, len(body))
	}

	negative := false
	if string(body[start]) == "-" {
		negative = true
		start += 1
	}

	if !IsDecimalLeadingRune(rune(body[start])) {
		return pbtoken.DecimalToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as an identifier", body)}
	}

	stringToScan := string(body[start:])
	endIdx := 0
	for idx, r := range stringToScan {
		if !IsDecimalRune(r) {
			break
		}
		endIdx = idx
	}

	return pbtoken.DecimalToken{
		Negative: negative,
		Literal: string(stringToScan[:endIdx + 1]),
	}, start + endIdx + 1, nil
}
