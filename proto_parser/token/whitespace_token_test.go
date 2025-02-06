package token

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
)

func ParseWhitespaceToken_WithEmptyString_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, err := ParseWhitespaceToken(ctx, 0, "")
	assert.NotNil(t, err)
}

func ParseWhitespaceToken_WithNonWhitespace_ReturnsError(t *testing.T) {
	ctx := context.Background()
	_, err := ParseWhitespaceToken(ctx, 0, "")
	assert.NotNil(t, err)
	errType := TokenNotParseableError("test")
	assert.ErrorAs(t, err, &errType)
}
