package identifier_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseIdentifierToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseIdentifierToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseIdentifierToken_WithNonCharacters_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseIdentifierToken(ctx, 0, " foo bar")
	require.NotNil(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseIdentifierToken_WithCharactersOnly_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "asaspd8728_sdfoijbpsdofi"
	res, idx, err := ParseIdentifierToken(ctx, 0, body)
	require.Nil(t, err)
	require.NotNil(t, res.GetIdentifierToken())
	assert.Equal(t, body, res.GetIdentifierToken().Identifier)
	assert.Equal(t, len(body), idx)
}

func TestParseIdentifierToken_WithPartialCharacters_ReturnsLeadingCharacters(t *testing.T) {
	ctx := context.Background()
	body := "asodfdgdZ*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseIdentifierToken(ctx, 0, body)
	require.Nil(t, err)
	require.NotNil(t, res.GetIdentifierToken())
	assert.Equal(t, "asodfdgdZ", res.GetIdentifierToken().Identifier)
	assert.Equal(t, 9, idx)
}
