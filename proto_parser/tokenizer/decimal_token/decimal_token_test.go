package decimal_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseDecimalToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseDecimalToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseDecimalToken_WithNonDigits_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseDecimalToken(ctx, 0, "foo")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseDecimalToken_WithDash_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseDecimalToken(ctx, 0, "-")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseDecimalToken_WithDigitsOnly_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "482523904856729387456"
	res, idx, err := ParseDecimalToken(ctx, 0, body)
	require.Nil(t, err)
	assert.False(t, res.Negative)
	assert.Equal(t, body, res.Literal)
	assert.Equal(t, len(body), idx)
}

func TestParseDecimalToken_WithPartialCharacters_ReturnsLeadingDigits(t *testing.T) {
	ctx := context.Background()
	body := "452937456293*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseDecimalToken(ctx, 0, body)
	require.Nil(t, err)
	assert.False(t, res.Negative)
	assert.Equal(t, "452937456293", res.Literal)
	assert.Equal(t, 12, idx)
}

func TestParseDecimalToken_WithNegativeValue_ReturnsNegative(t *testing.T) {
	ctx := context.Background()
	body := "-4837*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseDecimalToken(ctx, 0, body)
	require.Nil(t, err)
	assert.True(t, res.Negative)
	assert.Equal(t, "4837", res.Literal)
	assert.Equal(t, 5, idx)
}
