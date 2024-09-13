package game_server

import (
	"testing"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/game_state_provider"

	proto "github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto"
	stateProto "github.com/shaldengeki/monorepo/ark_nova_stats/proto"
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
		t.Fatalf("GetStateRequest should result in no GetState err, but got %v", err)
	}

	if actual.GameState.Round != 0 {
		t.Fatalf("GetStateRequest should result in empty GetStateResponse, but got %q", actual)
	}
}

func TestGetState_WhenStaticStateProviderGiven_ReturnsPopulatedState(t *testing.T) {
	state := stateProto.GameState{Round: 1, BreakCount: 2, BreakMax: 3}
	s := New(game_state_provider.NewStaticGameStateProvider(state))
	r := proto.GetStateRequest{GameId: 1}
	actual, err := s.GetState(nil, &r)
	if err != nil {
		t.Fatalf("GetStateRequest should result in no GetState err, but got %v", err)
	}

	if actual.GameState.Round != 1 {
		t.Fatalf("GetStateRequest should return round 1, but got %q", actual.GameState.Round)
	}
	if actual.GameState.BreakCount != 2 {
		t.Fatalf("GetStateRequest should return break count 2, but got %q", actual.GameState.BreakCount)
	}
	if actual.GameState.BreakMax != 3 {
		t.Fatalf("GetStateRequest should return break max 3, but got %q", actual.GameState.BreakMax)
	}
}

func TestValidateState_WhenEmptyStateGiven_ReturnsValid(t *testing.T) {
	s := New(nil)
	r := proto.ValidateStateRequest{}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) > 0 {
		t.Fatalf("Empty ValidateStateRequest should result in zero validation errors, but got %v", res.ValidationErrors)
	}
}

func TestValidateState_WhenRoundIsNegative_ReturnsError(t *testing.T) {
	s := New(nil)
	r := proto.ValidateStateRequest{GameState: &stateProto.GameState{Round: -1}}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}
}
