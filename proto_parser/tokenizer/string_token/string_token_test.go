package string_token

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseStringToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseStringToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseStringToken_WithNoQuotes_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseStringToken(ctx, 0, "foo")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseStringToken_WithUnmatchedQuotes_ReturnsError(t *testing.T) {
	ctx := context.Background()
	invalidCases := []string{
		"'foo\"",
		"\"foo'",
		"'",
		"\"",
	}
	for _, invalidCase := range invalidCases {
		_, _, err := ParseStringToken(ctx, 0, invalidCase)
		require.Error(t, err)
		var errType *tokenErrors.TokenNotParseableError
		assert.ErrorAs(t, err, &errType)
	}
}

func TestParseStringToken_WithEmptySingleQuotes_ReturnsEmptyLiteral(t *testing.T) {
	ctx := context.Background()
	body := "''"
	res, idx, err := ParseStringToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetStringToken())
	assert.Equal(t, 1, len(res.GetStringToken().StringLiterals))
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_SINGLE, res.GetStringToken().StringLiterals[0].QuotationMarkType)
	assert.Equal(t, "", res.GetStringToken().StringLiterals[0].Value)
	assert.Equal(t, len(body), idx)
}

func TestParseStringToken_WithEmptyDoubleQuotes_ReturnsEmptyLiteral(t *testing.T) {
	ctx := context.Background()
	body := "\"\""
	res, idx, err := ParseStringToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetStringToken())
	assert.Equal(t, 1, len(res.GetStringToken().StringLiterals))
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_DOUBLE, res.GetStringToken().StringLiterals[0].QuotationMarkType)
	assert.Equal(t, "", res.GetStringToken().StringLiterals[0].Value)
	assert.Equal(t, len(body), idx)
}

func TestParseStringToken_WithSingleQuotedString_ReturnsSingleString(t *testing.T) {
	ctx := context.Background()
	body := "'test asdf)S(Dn8fys0f(*NSD))' foo bar"
	res, idx, err := ParseStringToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetStringToken())
	assert.Equal(t, 1, len(res.GetStringToken().StringLiterals))
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_SINGLE, res.GetStringToken().StringLiterals[0].QuotationMarkType)
	assert.Equal(t, "test asdf)S(Dn8fys0f(*NSD))", res.GetStringToken().StringLiterals[0].Value)
	assert.Equal(t, 29, idx)
}

func TestParseStringToken_WithDoubleQuotedString_ReturnsSingleString(t *testing.T) {
	ctx := context.Background()
	body := "\"test asdf)S(Dn8fys0f(*NSD))\" foo bar"
	res, idx, err := ParseStringToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetStringToken())
	assert.Equal(t, 1, len(res.GetStringToken().StringLiterals))
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_DOUBLE, res.GetStringToken().StringLiterals[0].QuotationMarkType)
	assert.Equal(t, "test asdf)S(Dn8fys0f(*NSD))", res.GetStringToken().StringLiterals[0].Value)
	assert.Equal(t, 29, idx)
}

func TestParseStringToken_WithCharEscapes_ReturnsCharEscapes(t *testing.T) {
	ctx := context.Background()
	body := "\"\r\n\" foo bar"
	res, idx, err := ParseStringToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetStringToken())
	assert.Equal(t, 1, len(res.GetStringToken().StringLiterals))
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_DOUBLE, res.GetStringToken().StringLiterals[0].QuotationMarkType)
	assert.Equal(t, "\r\n", res.GetStringToken().StringLiterals[0].Value)
	assert.Equal(t, 4, idx)
}

func TestParseStringToken_WithMixedEscapesAndCharacters_ReturnsMixture(t *testing.T) {
	ctx := context.Background()
	body := "\"test asd\nf)S(Dn8fy\r0Afs0f(*NSD))\" foo bar"
	res, idx, err := ParseStringToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetStringToken())
	assert.Equal(t, 1, len(res.GetStringToken().StringLiterals))
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_DOUBLE, res.GetStringToken().StringLiterals[0].QuotationMarkType)
	assert.Equal(t, "test asd\nf)S(Dn8fy\x0Afs0f(*NSD))", res.GetStringToken().StringLiterals[0].Value)
	assert.Equal(t, 34, idx)
}

func TestParseStringToken_WithMultipleLiterals_ReturnsAllLiterals(t *testing.T) {
	ctx := context.Background()
	body := "\"foo bar\r\n\" 'baz bat'"
	res, idx, err := ParseStringToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetStringToken())
	assert.Equal(t, 2, len(res.GetStringToken().StringLiterals))
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_DOUBLE, res.GetStringToken().StringLiterals[0].QuotationMarkType)
	assert.Equal(t, "foo bar \r\n", res.GetStringToken().StringLiterals[0].Value)
	assert.Equal(t, pbtoken.QuotationMarkType_QUOTATION_MARK_TYPE_SINGLE, res.GetStringToken().StringLiterals[1].QuotationMarkType)
	assert.Equal(t, "baz bat", res.GetStringToken().StringLiterals[1].Value)
	assert.Equal(t, 21, idx)
}
