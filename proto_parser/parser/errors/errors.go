package errors

import (
	"fmt"
)

type NodeNotParseableError struct {
	Message string
}

func (e NodeNotParseableError) Error() string {
	return fmt.Sprintf("Cannot parse token as node: %s", e.Message)
}
