package whitespace_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	token "github.com/shaldengeki/monorepo/proto_parser/token"
)

func TestParseWhitespaceToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseWhitespaceToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseWhitespaceToken_WithNonWhitespace_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseWhitespaceToken(ctx, 0, "syntax  f")
	require.NotNil(t, err)
	errType := token.TokenNotParseableError("test")
	assert.ErrorAs(t, err, &errType)
}

func TestParseWhitespaceToken_WithWhitespaceOnly_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "   \n\t\n   \t     "
	res, idx, err := ParseWhitespaceToken(ctx, 0, body)
	require.Nil(t, err)
	assert.Equal(t, body, res.Spaces)
	assert.Equal(t, len(body), idx)
}

func TestParseWhitespaceToken_WithPartialWhitespace_ReturnsLeadingWhitespace(t *testing.T) {
	ctx := context.Background()
	body := "   \n  \t foo bar"
	res, idx, err := ParseWhitespaceToken(ctx, 0, body)
	require.Nil(t, err)
	assert.Equal(t, "   \n  \t ", res.Spaces)
	assert.Equal(t, 8, idx)
}
