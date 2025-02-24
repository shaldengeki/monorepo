package tokenizer

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
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
	res, err := Tokenize(ctx, "s9d8f7S")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res))
	assert.Equal(t, "s9d8f7S", res[0].GetIdentifierToken().Identifier)
}

func TestTokenize_WithMixedCharactersWhitespace_ReturnsMultipleTokens(t *testing.T) {
	ctx := context.Background()
	res, err := Tokenize(ctx, "aff Ugjnk\n-23768\t  04334635 boo")
	require.Nil(t, err)
	assert.Equal(t, 9, len(res))
	assert.Equal(t, "aff", res[0].GetIdentifierToken().Identifier)
	assert.Equal(t, " ", res[1].GetWhitespaceToken().Spaces)
	assert.Equal(t, "Ugjnk", res[2].GetIdentifierToken().Identifier)
	assert.Equal(t, "\n", res[3].GetWhitespaceToken().Spaces)
	assert.Equal(t, "23768", res[4].GetIntegerToken().GetDecimalToken().Literal)
	assert.True(t, res[4].GetIntegerToken().GetDecimalToken().Negative)
	assert.Equal(t, "\t  ", res[5].GetWhitespaceToken().Spaces)
	assert.Equal(t, "04334635", res[6].GetIntegerToken().GetOctalToken().Literal)
	assert.Equal(t, " ", res[7].GetWhitespaceToken().Spaces)
	assert.Equal(t, "boo", res[8].GetIdentifierToken().Identifier)
}
