package integer_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseIntegerToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseIntegerToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseIntegerToken_WithNonNumeric_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseIntegerToken(ctx, 0, "foo")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseIntegerToken_WithDecimal_ReturnsDecimalToken(t *testing.T) {
	ctx := context.Background()
	body := "-2768323"
	res, idx, err := ParseIntegerToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetIntegerToken())
	assert.True(t, res.GetIntegerToken().GetDecimalToken().Negative)
	assert.Equal(t, "2768323", res.GetIntegerToken().GetDecimalToken().Literal)
	assert.Equal(t, len(body), idx)
}
