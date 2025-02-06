package token

import (
	"context"
	"fmt"
	pbtoken "github.com/shaldengeki/monorepo/proto_parser/proto/token"
)

type TokenNotParseableError string
func (e TokenNotParseableError) Error() string {
	return fmt.Sprintf("Cannot parse body as token: %v", string(e))
}


func ParseTokens(ctx context.Context, body string) ([]pbtoken.Token, error) {
	return []pbtoken.Token{}, nil
}
