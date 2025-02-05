package main

import (
	"context"
	"fmt"
	"github.com/shaldengeki/monorepo/proto_parser/token"
)

func main() {
	ctx := context.Background()
	fmt.Println("hello!")
	token.ParseTokens(ctx, "")
	return
}
