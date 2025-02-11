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

func TestSyntax_WithProto3_WithSingleQuotes_ReturnsNode(t *testing.T) {
	ctx := context.Background()
	res, err := ParseProtoText(ctx, "syntax = 'proto3';")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res.Nodes))
	assert.Equal(t, "proto3", res.Nodes[0].GetSyntaxNode().Syntax)
}

func TestSyntax_WithProto3_WithDoubleQuotes_ReturnsNode(t *testing.T) {
	ctx := context.Background()
	res, err := ParseProtoText(ctx, "syntax = \"proto3\";")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res.Nodes))
	assert.Equal(t, "proto3", res.Nodes[0].GetSyntaxNode().Syntax)
}

func TestSyntax_WithProto2_WithSingleQuotes_ReturnsNode(t *testing.T) {
	ctx := context.Background()
	res, err := ParseProtoText(ctx, "syntax = 'proto2';")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res.Nodes))
	assert.Equal(t, "proto2", res.Nodes[0].GetSyntaxNode().Syntax)
}

func TestSyntax_WithProto2_WithDoubleQuotes_ReturnsNode(t *testing.T) {
	ctx := context.Background()
	res, err := ParseProtoText(ctx, "syntax = \"proto2\";")
	require.Nil(t, err)
	assert.Equal(t, 1, len(res.Nodes))
	assert.Equal(t, "proto2", res.Nodes[0].GetSyntaxNode().Syntax)
}
