package main

import (
	"context"
	"fmt"
	"github.com/shaldengeki/monorepo/proto_parser"
)

func main() {
	ctx := context.Background()
	fmt.Printf("hello!")
	proto_parser.Parse(ctx, "")
	return
}
