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
	res, err := ParseTokens(ctx, "")
	require.Nil(t, err)
	assert.Equal(t, []pbtoken.Token{}, res)
}

func TestParseTokens_WithAllWhitespace_ReturnsWhitespaceToken(t *testing.T) {
	ctx := context.Background()
	res, err := ParseTokens(ctx, "\t  \n   \t")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res))
	expected := pbtoken.Token{
		Token: &pbtoken.Token_WhitespaceToken{
			WhitespaceToken: &pbtoken.WhitespaceToken{Spaces: "\t  \n   \t"},
		},
	}
	assert.Equal(t, expected, res[0])
}
