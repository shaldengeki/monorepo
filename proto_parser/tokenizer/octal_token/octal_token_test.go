package octal_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseOctalToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseOctalToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseOctalToken_WithNonDigits_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseOctalToken(ctx, 0, "foo")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseOctalToken_WithDash_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseOctalToken(ctx, 0, "-")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseOctalToken_WithDigitsOnly_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "0446672634"
	res, idx, err := ParseOctalToken(ctx, 0, body)
	require.NoError(t, err)
	assert.False(t, res.Negative)
	assert.Equal(t, body, res.Literal)
	assert.Equal(t, len(body), idx)
}

func TestParseOctalToken_WithPartialCharacters_ReturnsLeadingDigits(t *testing.T) {
	ctx := context.Background()
	body := "0676234*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseOctalToken(ctx, 0, body)
	require.NoError(t, err)
	assert.False(t, res.Negative)
	assert.Equal(t, "0676234", res.Literal)
	assert.Equal(t, 7, idx)
}

func TestParseOctalToken_WithNegativeValue_ReturnsNegative(t *testing.T) {
	ctx := context.Background()
	body := "-04623433*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseOctalToken(ctx, 0, body)
	require.NoError(t, err)
	assert.True(t, res.Negative)
	assert.Equal(t, "04623433", res.Literal)
	assert.Equal(t, 9, idx)
}
