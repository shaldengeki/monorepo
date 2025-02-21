package string_token

import (
	"context"
	"errors"
	"fmt"

	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func IsStringQuote(s string) bool {
	return s == "\"" || s == "'"
}

func ParseRegularString(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	return "", 0, &tokenErrors.TokenNotParseableError{Message: "TODO"}
}

func ParseSimpleEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	return "", 0, &tokenErrors.TokenNotParseableError{Message: "TODO"}
}

func ParseHexEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	return "", 0, &tokenErrors.TokenNotParseableError{Message: "TODO"}
}

func ParseOctalEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	return "", 0, &tokenErrors.TokenNotParseableError{Message: "TODO"}
}

func ParseUnicodeEscapeSequence(ctx context.Context, start int, body string, openingQuote string) (string, int, error) {
	return "", 0, &tokenErrors.TokenNotParseableError{Message: "TODO"}
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
		ParseRegularString,
		ParseSimpleEscapeSequence,
		ParseHexEscapeSequence,
		ParseOctalEscapeSequence,
		ParseUnicodeEscapeSequence,
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
	if string(body[idx]) != openingQuote {
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
	tokens := []*pbtoken.StringSingleToken{}

	for {
		tkn, newIdx, err := ParseStringSingleToken(ctx, idx, body)
		if err == nil {
			tokens = append(tokens, &tkn)
			idx = newIdx

			if idx >= len(body) {
				break
			}
			continue
		}

		if errors.As(err, &unparseableError) {
			return pbtoken.Token{}, 0, &tokenErrors.TokenNotParseableError{Message: fmt.Sprintf("body %s, start %d is not a parseable as a string literal: %w", body, start, err)}
		} else {
			return pbtoken.Token{}, start, fmt.Errorf("Unexpected error when parsing string literal tokens at position %d: %w\nfor body: %s", idx, err, body)
		}
	}

	return pbtoken.Token{
		Token: &pbtoken.Token_StringToken{
			StringToken: &pbtoken.StringToken{
				StringLiterals: tokens,
			},
		},
	}, idx, nil
}
