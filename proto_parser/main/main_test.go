package main

import (
	"context"
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEmpty(t *testing.T) {
	ctx := context.Background()
	res, err := ParseProtoText(ctx, "")
	require.Nil(t, err)
	assert.Equal(t, 0, len(res.Nodes))
}
