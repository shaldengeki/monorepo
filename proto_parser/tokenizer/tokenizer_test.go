package token

import (
	"context"
	"testing"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEmpty(t *testing.T) {
	ctx := context.Background()
	res, err := Tokenize(ctx, "")
	require.Nil(t, err)
	assert.Equal(t, []pbtoken.Token{}, res)
}

func TestTokenize_WithAllWhitespace_ReturnsWhitespaceToken(t *testing.T) {
	ctx := context.Background()
	res, err := Tokenize(ctx, "\t  \n   \t")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res))
	assert.Equal(t, "\t  \n   \t", res[0].GetWhitespaceToken().Spaces)
}

func TestTokenize_WithAllCharacters_ReturnsCharactersToken(t *testing.T) {
	ctx := context.Background()
	res, err := Tokenize(ctx, "s9d8f7S(D*F&bS(dfs9b7df8s76df))")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res))
	assert.Equal(t, "s9d8f7S", res[0].GetCharactersToken().Characters)
}

func TestTokenize_WithMixedCharactersWhitespace_ReturnsMultipleTokens(t *testing.T) {
	ctx := context.Background()
	res, err := Tokenize(ctx, "aff Ugjnk\n\t  boo")
	require.Nil(t, err)
	assert.Equal(t, 5, len(res))
	assert.Equal(t, "aff", res[0].GetCharactersToken().Characters)
	assert.Equal(t, " ", res[1].GetWhitespaceToken().Spaces)
	assert.Equal(t, "Ugjnk", res[2].GetCharactersToken().Characters)
	assert.Equal(t, "\n\t  ", res[3].GetWhitespaceToken().Spaces)
	assert.Equal(t, "boo", res[4].GetCharactersToken().Characters)
}
