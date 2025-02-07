package errors

import (
	"fmt"
)

type TokenNotParseableError struct {
	Message string
}

func (e TokenNotParseableError) Error() string {
	return fmt.Sprintf("Cannot parse body as token: %s", e.Message)
}
