package boolean_token

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseBooleanToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseBooleanToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseBooleanToken_NonValue_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseBooleanToken(ctx, 0, " fal8bu")
	require.Error(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseBooleanToken_WithBooleanValueOnly_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "false"
	res, idx, err := ParseBooleanToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetBooleanToken())
	assert.Equal(t, false, res.GetBooleanToken().Value)
	assert.Equal(t, len(body), idx)
}

func TestParseBooleanToken_WithPartialBooleanValue_ReturnsBooleanValue(t *testing.T) {
	ctx := context.Background()
	body := "true; sdg8u0ga98"
	res, idx, err := ParseBooleanToken(ctx, 0, body)
	require.NoError(t, err)
	require.NotNil(t, res.GetBooleanToken())
	assert.Equal(t, true, res.GetBooleanToken().Value)
	assert.Equal(t, 4, idx)
}
