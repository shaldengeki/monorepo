package floating_point_token

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseFloatingPointToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseFloatingPointToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseFloatingPointToken_WithInf_ReturnsInf(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "inf")
	require.NoError(t, err)
	require.NotNil(t, res.GetFloatingPointToken())
	assert.False(t, res.GetFloatingPointToken().Negative)
	assert.True(t, res.GetFloatingPointToken().GetInf())
	assert.Equal(t, 3, idx)
}

func TestParseFloatingPointToken_WithNegativeInf_ReturnsNegativeInf(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-inf")
	require.NoError(t, err)
	require.NotNil(t, res.GetFloatingPointToken())
	assert.True(t, res.GetFloatingPointToken().Negative)
	assert.True(t, res.GetFloatingPointToken().GetInf())
	assert.Equal(t, 4, idx)
}

func TestParseFloatingPointToken_WithNan_ReturnsNan(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "nan")
	require.NoError(t, err)
	require.NotNil(t, res.GetFloatingPointToken())
	assert.False(t, res.GetFloatingPointToken().Negative)
	assert.True(t, res.GetFloatingPointToken().GetNan())
	assert.Equal(t, 3, idx)
}

func TestParseFloatingPointToken_WithNegativeNan_ReturnsNegativeNan(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-nan")
	require.NoError(t, err)
	require.NotNil(t, res.GetFloatingPointToken())
	assert.True(t, res.GetFloatingPointToken().Negative)
	assert.True(t, res.GetFloatingPointToken().GetNan())
	assert.Equal(t, 4, idx)
}

func TestParseFloatingPointToken_WithNonNumeric_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseFloatingPointToken(ctx, 0, "foo")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseFloatingPointToken_WithLeadingMinus_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseFloatingPointToken(ctx, 0, "-")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseFloatingPointToken_WithLeadingMinusAndInvalidValue_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseFloatingPointToken(ctx, 0, "-a")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseFloatingPointToken_WithNumericAndNoPeriod_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseFloatingPointToken(ctx, 0, "01234")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseFloatingPointToken_NoDecimalPoint_WithNegativeExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-03623e-9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, "03623e-9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 9)
}

func TestParseFloatingPointToken_NoDecimalPoint_WithPositiveExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-03623e+9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, "03623e+9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 9)
}

func TestParseFloatingPointToken_NoDecimalPoint_WithUnsignedExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-03623e9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, "03623e9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 8)
}

func TestParseFloatingPointToken_WithLeadingDecimalPoint_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, ".236")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, false, res.GetFloatingPointToken().Negative)
	assert.Equal(t, ".236", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 4)
}

func TestParseFloatingPointToken_WithLeadingDecimalPoint_WithNegativeExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-.03623e-9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, ".03623e-9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 10)
}

func TestParseFloatingPointToken_WithLeadingDecimalPoint_WithPositiveExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-.03623e+9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, ".03623e+9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 10)
}

func TestParseFloatingPointToken_WithLeadingDecimalPoint_WithUnsignedExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-.03623e9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, ".03623e9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 9)
}

func TestParseFloatingPointToken_WithNonLeadingDecimalPoint_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "1.236")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, false, res.GetFloatingPointToken().Negative)
	assert.Equal(t, "1.236", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 5)
}

func TestParseFloatingPointToken_WithNonLeadingDecimalPoint_WithNegativeExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-0.03623e-9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, "0.03623e-9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 11)
}

func TestParseFloatingPointToken_WithNonLeadingDecimalPoint_WithPositiveExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-12.03623e+9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, "12.03623e+9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 12)
}

func TestParseFloatingPointToken_WithNonLeadingDecimalPoint_WithUnsignedExponent_ParsesCorrectly(t *testing.T) {
	ctx := context.Background()
	res, idx, err := ParseFloatingPointToken(ctx, 0, "-2001.03623e9")
	require.NoError(t, err)
	assert.NotNil(t, res.GetFloatingPointToken())
	assert.Equal(t, true, res.GetFloatingPointToken().Negative)
	assert.Equal(t, "2001.03623e9", res.GetFloatingPointToken().GetLiteral())
	assert.Equal(t, idx, 13)
}
