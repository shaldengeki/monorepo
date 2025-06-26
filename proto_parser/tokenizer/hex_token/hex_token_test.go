package hex_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseHexToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseHexToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseHexToken_WithNonDigits_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseHexToken(ctx, 0, "foo")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseHexToken_WithDash_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseHexToken(ctx, 0, "-")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseHexToken_WithLeadingNonZero_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseHexToken(ctx, 0, "12345")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseHexToken_WithoutLeadingX_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseHexToken(ctx, 0, "012345")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseHexToken_WithInvalidCharacter_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseHexToken(ctx, 0, "0xR123456789Af")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseHexToken_WithPartial_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseHexToken(ctx, 0, "0x")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseHexToken_WhenWholeBody_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "0x345289374abC"
	res, idx, err := ParseHexToken(ctx, 0, body)
	require.NoError(t, err)
	assert.False(t, res.Negative)
	assert.Equal(t, body, res.Literal)
	assert.Equal(t, len(body), idx)
}

func TestParseHexToken_WithPartialCharacters_ReturnsLeadingDigits(t *testing.T) {
	ctx := context.Background()
	body := "0x293810aCd*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseHexToken(ctx, 0, body)
	require.NoError(t, err)
	assert.False(t, res.Negative)
	assert.Equal(t, "0x293810aCd", res.Literal)
	assert.Equal(t, 11, idx)
}

func TestParseHexToken_WithNegativeValue_ReturnsNegative(t *testing.T) {
	ctx := context.Background()
	body := "-0x293810aCd*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseHexToken(ctx, 0, body)
	require.NoError(t, err)
	assert.True(t, res.Negative)
	assert.Equal(t, "0x293810aCd", res.Literal)
	assert.Equal(t, 12, idx)
}
