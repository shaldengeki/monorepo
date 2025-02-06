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
