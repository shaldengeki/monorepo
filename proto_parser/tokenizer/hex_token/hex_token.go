package hex_token

import (
	"context"
	"fmt"
	"strings"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

func IsHexLeadingRune(r rune) bool {
	return strings.ContainsRune("xX", r)
}

func IsHexRune(r rune) bool {
	return strings.ContainsRune("0123456789ABCDEFabcdef", r)
}

func ParseHexToken(ctx context.Context, start int, body string) (pbtoken.HexToken, int, error) {
	if start >= len(body) {
		return pbtoken.HexToken{}, 0, fmt.Errorf("Cannot parse hex in position %d in body of length %d", start, len(body))
	}

	negative := false
	if string(body[start]) == "-" {
		negative = true
		start += 1
	}
	if start >= len(body) {
		return pbtoken.HexToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as a hex", body)}
	}

	if string(body[start]) != "0" {
		return pbtoken.HexToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as a hex", body)}
	}

	if !IsHexLeadingRune(rune(body[start+1])) {
		return pbtoken.HexToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as a hex", body)}
	}

	stringToScan := string(body[start+2:])
	endIdx := start + 2
	for _, r := range stringToScan {
		if !IsHexRune(r) {
			break
		}
		endIdx += 1
	}
	if endIdx == start + 2 {
		return pbtoken.HexToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("prefix of %s is not a parseable as a hex", body)}
	}

	return pbtoken.HexToken{
		Negative: negative,
		Literal: string(body[start:endIdx]),
	}, endIdx, nil
}
