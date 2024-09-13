package game_server

import (
	"testing"

	proto "github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto"
)

func TestGetState_WhenEmptyRequest_ReturnsError(t *testing.T) {
	s := New(nil)
	r := proto.GetStateRequest{}
	res, err := s.GetState(nil, &r)
	if res != nil {
		t.Fatalf("Empty GetStateRequest should result in nil GetStateResponse, but got %q", res)
	}

	if err == nil {
		t.Fatalf("Empty GetStateRequest should result in GetState err, but didn't see one")
	}
}
