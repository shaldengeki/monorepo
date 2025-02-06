package errors

import (
	"fmt"
)

type TokenNotParseableError string
func (e TokenNotParseableError) Error() string {
	return fmt.Sprintf("Cannot parse body as token: %v", string(e))
}
