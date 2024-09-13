package game_server

import (
	"testing"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/game_state_provider"

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


func TestGetState_WhenEmptyStateProviderGiven_ReturnsEmptyState(t *testing.T) {
	s := New(game_state_provider.NewEmptyGameStateProvider())
	r := proto.GetStateRequest{GameId: 1}
	actual, err := s.GetState(nil, &r)
	if err != nil {
		t.Fatalf("Empty GetStateRequest should result in no GetState err, but got %q", err)
	}

	if actual.GameState.Round != 0 {
		t.Fatalf("Empty GetStateRequest should result in empty GetStateResponse, but got %q", actual)
	}

}
