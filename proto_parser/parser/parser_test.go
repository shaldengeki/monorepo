package parser

import (
	"context"
	"testing"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEmpty(t *testing.T) {
	ctx := context.Background()
	res, err := Parse(ctx, []pbtoken.Token{})
	require.Nil(t, err)
	assert.Equal(t, 0, len(res.Nodes))
}
