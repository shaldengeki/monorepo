package octal_token

import (
	"context"
	"fmt"
	"strings"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func IsOctalLeadingRune(r rune) bool {
	return strings.ContainsRune("0", r)
}

func IsOctalRune(r rune) bool {
	return strings.ContainsRune("01234567", r)
}

func ParseOctalToken(ctx context.Context, start int, body string) (pbtoken.OctalToken, int, error) {
	if start >= len(body) {
		return pbtoken.OctalToken{}, 0, fmt.Errorf("Cannot parse octal in position %d in body of length %d", start, len(body))
	}

	negative := false
	if string(body[start]) == "-" {
		negative = true
		start += 1
	}
	if start >= len(body) {
		return pbtoken.OctalToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as an octal", body)}
	}

	if !IsOctalLeadingRune(rune(body[start])) {
		return pbtoken.OctalToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as an octal", body)}
	}

	stringToScan := string(body[start:])
	endIdx := 0
	for idx, r := range stringToScan {
		if !IsOctalRune(r) {
			break
		}
		endIdx = idx
	}

	return pbtoken.OctalToken{
		Negative: negative,
		Literal: string(stringToScan[:endIdx + 1]),
	}, start + endIdx + 1, nil
}
