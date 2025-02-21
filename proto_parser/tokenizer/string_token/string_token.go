package string_token

import (
	"context"
	"errors"
	"fmt"
	"strings"

	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/hex_token"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/octal_token"
	"github.com/shaldengeki/monorepo/proto_parser/tokenizer/whitespace_token"
)

func IsStringQuote(s string) bool {
	return s == "\"" || s == "'"
}

func IsRegularStringRune(r rune, openingQuote string) bool {
	return !strings.ContainsRune("\n\x00\\"+openingQuote, r)
}

func ParseRegularString(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	currIdx := start
	for idx, r := range string(body[start:]) {
		currIdx = idx + start
		if !IsRegularStringRune(r, openingQuote) {
			break
		}
	}

	if currIdx == start {
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not parseable as a regular string", body, currIdx)}
	}

	return string(body[start:currIdx]), currIdx, nil
}

func IsSimpleEscapeRune(s string) bool {
	return strings.Contains("abfnrtv\\'\"?", s)
}

func ParseSimpleEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	if start >= len(body) {
		return "", 0, fmt.Errorf("Cannot parse simple escape in position %d in body of length %d", start, len(body))
	}

	stringToScan := string(body[start:])
	if len(stringToScan) < 2 || string(stringToScan[0]) != "\\" || !IsSimpleEscapeRune(string(stringToScan[1])) {
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not parseable as a simple escape", body, start)}
	}

	return string(stringToScan[0:2]), start + 2, nil
}

func ParseHexEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	if start >= len(body) {
		return "", 0, fmt.Errorf("Cannot parse hex escape in position %d in body of length %d", start, len(body))
	}
	if string(body[start]) != "\\" {
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not parseable as a hex escape", body, start)}
	}

	currIdx := 1
	stringToScan := string(body[start+currIdx:])

	for idx, r := range stringToScan {
		currIdx = idx + 1
		if idx == 0 {
			if !hex_token.IsHexLeadingRune(r) {
				return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d does not start with x or X", stringToScan, idx)}
			}
		} else if !hex_token.IsHexRune(r) {
			break
		}
	}

	if currIdx <= 2 {
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not a valid hex value", stringToScan, currIdx)}
	}

	return string(body[start : start+currIdx]), start + currIdx, nil
}

func ParseOctalEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	if start >= len(body) {
		return "", 0, fmt.Errorf("Cannot parse octal escape in position %d in body of length %d", start, len(body))
	}
	if string(body[start]) != "\\" {
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not parseable as a octal escape", body, start)}
	}

	currIdx := 1
	stringToScan := string(body[start+currIdx:])

	for idx, r := range stringToScan {
		currIdx = idx + 1
		if !octal_token.IsOctalRune(r) {
			break
		}
	}

	if currIdx <= 1 {
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not a valid octal value", stringToScan, currIdx)}
	}

	return string(body[start : start+currIdx]), start + currIdx, nil
}

func ParseUnicodeEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	if start >= len(body) {
		return "", 0, fmt.Errorf("Cannot parse unicode escape in position %d in body of length %d", start, len(body))
	}

	currIdx := start

	if string(body[currIdx]) != "\\" {
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not parseable as a unicode escape", body, currIdx)}
	}
	currIdx += 1

	stringToScan := ""
	if string(body[currIdx]) == "u" {
		// Four digits
		stringToScan = string(body[currIdx+1 : currIdx+5])
		currIdx += 5
	} else if string(body[currIdx]) == "U" {
		// Eight digits
		stringToScan = string(body[currIdx+1 : currIdx+9])
		currIdx += 9
	} else {
		// Invalid
		return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not parseable as a unicode escape", body, currIdx)}
	}

	// Every character should be a hex digit
	for _, r := range stringToScan {
		if !hex_token.IsHexRune(r) {
			return "", 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d is not parseable as a unicode escape (non-hex digit)", stringToScan, currIdx)}
		}
	}

	return string(body[start:currIdx]), currIdx, nil
}

func ParseStringSingleToken(ctx context.Context, start int, body string) (pbtoken.StringSingleToken, int, error) {
	openingQuote := string(body[start])
	if !IsStringQuote(openingQuote) {
		return pbtoken.StringSingleToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d does not start with a string quote", body, start)}
	}
	start += 1

	if start >= len(body) {
		return pbtoken.StringSingleToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is just a single quote", body, start)}
	}

	parseFuncs := []func(context.Context, int, string, string) (string, int, error){
		ParseSimpleEscapeSequence,
		ParseHexEscapeSequence,
		ParseOctalEscapeSequence,
		ParseUnicodeEscapeSequence,
		ParseRegularString,
	}

	idx := start
	var unparseableError *tokenErrors.TokenNotParseableError

	for {
		prevIdx := idx
		for _, f := range parseFuncs {
			_, newIdx, err := f(ctx, idx, body, openingQuote)
			if err == nil {
				idx = newIdx
				break
			}
			if !errors.As(err, &unparseableError) {
				return pbtoken.StringSingleToken{}, 0, fmt.Errorf("Unexpected error when parsing single string tokens at position %d: %w\nfor body: %s", idx, err, body)
			}
		}
		if idx == prevIdx || idx >= len(body) {
			break
		}
	}

	// We should now be pointing at an end quote, matching the leading quote.
	if idx >= len(body) || string(body[idx]) != openingQuote {
		return pbtoken.StringSingleToken{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, position %d does not end with a string quote matching leading quote %s", body, idx, openingQuote)}
	}

	quoteType := pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_UNKNOWN
	if openingQuote == "\"" {
		quoteType = pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_DOUBLE
	} else if openingQuote == "'" {
		quoteType = pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_SINGLE
	}

	return pbtoken.StringSingleToken{
		QuotationMarkType: quoteType,
		Value:             string(body[start:idx]),
	}, idx + 1, nil
}

func ParseStringToken(ctx context.Context, start int, body string) (pbtoken.Token, int, error) {
	if start >= len(body) {
		return pbtoken.Token{}, 0, fmt.Errorf("Cannot parse string literal in position %d in body of length %d", start, len(body))
	}

	var unparseableError *tokenErrors.TokenNotParseableError

	idx := start
	lastIdx := idx
	lastStringTokenIdx := start
	tokens := []*pbtoken.StringSingleToken{}
	var lastErr error

	for {
		tkn, newIdx, parseErr := ParseStringSingleToken(ctx, idx, body)
		if parseErr == nil {
			tokens = append(tokens, &tkn)
			idx = newIdx
			lastStringTokenIdx = idx

			if idx >= len(body) {
				break
			}
			continue
		}

		if !errors.As(parseErr, &unparseableError) {
			return pbtoken.Token{}, 0, fmt.Errorf("Unexpected error when parsing string literal tokens at position %d: %w\nfor body: %s", idx, parseErr, body)
		}
		lastErr = parseErr

		// See if this is whitespace.
		_, newIdx, whitespaceErr := whitespace_token.ParseWhitespaceToken(ctx, idx, body)
		if whitespaceErr == nil {
			idx = newIdx

			if idx >= len(body) {
				break
			}
		} else if !errors.As(whitespaceErr, &unparseableError) {
			return pbtoken.Token{}, 0, fmt.Errorf("Unexpected error when parsing string literal tokens (whitespace) at position %d: %w\nfor body: %s", idx, whitespaceErr, body)
		}

		// Not a string.
		if lastIdx == idx {
			break
		}
		lastIdx = idx
	}

	if len(tokens) == 0 {
		return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is not parseable as a string literal: %w", body, start, lastErr)}
	}

	return pbtoken.Token{
		Token: &pbtoken.Token_StringToken{
			StringToken: &pbtoken.StringToken{
				StringLiterals: tokens,
			},
		},
	}, lastStringTokenIdx, nil
}
