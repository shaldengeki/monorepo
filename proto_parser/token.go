package proto_parser

import (
	"context"
)

type Token struct {
	start FilePosition
	end FilePosition
}

func Parse(ctx context.Context, body string) ([]Token, error) {
	return []Token{}, nil
}
