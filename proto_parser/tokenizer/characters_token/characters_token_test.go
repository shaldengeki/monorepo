package characters_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestParseCharactersToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseCharactersToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseCharactersToken_WithNonCharacters_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseCharactersToken(ctx, 0, " foo bar")
	require.NotNil(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseCharactersToken_WithCharactersOnly_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "as&aspd8728_sdfoijb]psdofi"
	res, idx, err := ParseCharactersToken(ctx, 0, body)
	require.Nil(t, err)
	require.NotNil(t, res.GetCharactersToken())
	assert.Equal(t, body, res.GetCharactersToken().Characters)
	assert.Equal(t, len(body), idx)
}

func TestParseCharactersToken_WithPartialCharacters_ReturnsLeadingCharacters(t *testing.T) {
	ctx := context.Background()
	body := "asodfdgdZ*DVS)09sd8f fapsdfoij\npsodifjpa"
	res, idx, err := ParseCharactersToken(ctx, 0, body)
	require.Nil(t, err)
	require.NotNil(t, res.GetCharactersToken())
	assert.Equal(t, "asodfdgdZ*DVS)09sd8f", res.GetCharactersToken().Characters)
	assert.Equal(t, 20, idx)
}
