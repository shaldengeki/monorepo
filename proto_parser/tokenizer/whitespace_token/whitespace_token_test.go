package whitespace_token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	tokenErrors "github.com/shaldengeki/monorepo/proto_parser/tokenizer/errors"
)

func TestLeadingWhitespaceLength_WithEmptyString_ReturnsZero(t *testing.T) {
	ctx := context.Background()
	assert.Equal(t, 0, LeadingWhitespaceLength(ctx, ""))
}

func TestLeadingWhitespaceLength_WithAllSpaces_ReturnsLength(t *testing.T) {
	ctx := context.Background()
	assert.Equal(t, 3, LeadingWhitespaceLength(ctx, "\n\t "))
}

func TestLeadingWhitespaceLength_WithLeadingSpaces_ReturnsRightLength(t *testing.T) {
	ctx := context.Background()
	assert.Equal(t, 3, LeadingWhitespaceLength(ctx, "\n\t foo   "))
}

func TestLeadingWhitespaceLength_WithLeadingNonSpaces_ReturnsZero(t *testing.T) {
	ctx := context.Background()
	assert.Equal(t, 0, LeadingWhitespaceLength(ctx, "yay\n\t foo"))
}

func TestParseWhitespaceToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseWhitespaceToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func TestParseWhitespaceToken_WithNonWhitespace_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, _, err := ParseWhitespaceToken(ctx, 0, "syntax  f")
	require.NotNil(t, err)
	var errType *tokenErrors.TokenNotParseableError
	assert.ErrorAs(t, err, &errType)
}

func TestParseWhitespaceToken_WithWhitespaceOnly_ReturnsWholeBody(t *testing.T) {
	ctx := context.Background()
	body := "   \n\t\n   \t     "
	res, idx, err := ParseWhitespaceToken(ctx, 0, body)
	require.Nil(t, err)
	require.NotNil(t, res.GetWhitespaceToken())
	assert.Equal(t, body, res.GetWhitespaceToken().Spaces)
	assert.Equal(t, len(body), idx)
}

func TestParseWhitespaceToken_WithPartialWhitespace_ReturnsLeadingWhitespace(t *testing.T) {
	ctx := context.Background()
	body := "   \n  \t foo bar"
	res, idx, err := ParseWhitespaceToken(ctx, 0, body)
	require.Nil(t, err)
	require.NotNil(t, res.GetWhitespaceToken())
	assert.Equal(t, "   \n  \t ", res.GetWhitespaceToken().Spaces)
	assert.Equal(t, 8, idx)
}
