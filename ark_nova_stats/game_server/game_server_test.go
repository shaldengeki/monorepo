package game_server

import (
	"testing"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/game_state_provider"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto/server"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/associate"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/display_state"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/game_state"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/player_game_state"
)

func TestGetState_WhenEmptyRequest_ReturnsError(t *testing.T) {
	s := New(nil)
	r := server.GetStateRequest{}
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
	r := server.GetStateRequest{GameId: 1}
	actual, err := s.GetState(nil, &r)
	if err != nil {
		t.Fatalf("GetStateRequest should result in no GetState err, but got %v", err)
	}

	if actual.GameState.Round != 0 {
		t.Fatalf("GetStateRequest should result in empty GetStateResponse, but got %q", actual)
	}
}

func TestGetState_WhenStaticStateProviderGiven_ReturnsPopulatedState(t *testing.T) {
	state := game_state.GameState{Round: 1, BreakCount: 2, BreakMax: 3}
	s := New(game_state_provider.NewStaticGameStateProvider(state))
	r := server.GetStateRequest{GameId: 1}
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
	r := server.ValidateStateRequest{}
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
	r := server.ValidateStateRequest{GameState: &game_state.GameState{Round: -1}}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}
}

func TestValidateState_WhenBreakCountIsNegative_ReturnsError(t *testing.T) {
	s := New(nil)
	r := server.ValidateStateRequest{GameState: &game_state.GameState{Round: 1, BreakCount: -1}}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}
}

func TestValidateState_WhenBreakMaxIsLessThanOne_ReturnsError(t *testing.T) {
	s := New(nil)
	r := server.ValidateStateRequest{GameState: &game_state.GameState{Round: 1, BreakMax: 0}}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}
}

func TestValidateState_WhenBreakCountExceedsMax_ReturnsError(t *testing.T) {
	s := New(nil)
	r := server.ValidateStateRequest{GameState: &game_state.GameState{Round: 1, BreakMax: 1, BreakCount: 2}}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}
}

func TestValidateState_WhenBreakMaxMismatchPlayerCount_ReturnsError(t *testing.T) {
	s := New(nil)

	// One-player should have a break of 5.
	playerGameStates := []*player_game_state.PlayerGameState{
		&player_game_state.PlayerGameState{},
	}
	r := server.ValidateStateRequest{GameState: &game_state.GameState{Round: 1, BreakMax: 6, PlayerGameStates: playerGameStates}}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}

	// Two-player should have a break of 9.
	playerGameStates = []*player_game_state.PlayerGameState{
		&player_game_state.PlayerGameState{},
		&player_game_state.PlayerGameState{},
	}
	r = server.ValidateStateRequest{GameState: &game_state.GameState{Round: 1, BreakMax: 8, PlayerGameStates: playerGameStates}}
	res, err = s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}

	// Three-player should have a break of 13.
	playerGameStates = []*player_game_state.PlayerGameState{
		&player_game_state.PlayerGameState{},
		&player_game_state.PlayerGameState{},
		&player_game_state.PlayerGameState{},
	}
	r = server.ValidateStateRequest{GameState: &game_state.GameState{Round: 1, BreakMax: 14, PlayerGameStates: playerGameStates}}
	res, err = s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}

	// Four-player should have a break of 17.
	playerGameStates = []*player_game_state.PlayerGameState{
		&player_game_state.PlayerGameState{},
		&player_game_state.PlayerGameState{},
		&player_game_state.PlayerGameState{},
		&player_game_state.PlayerGameState{},
	}
	r = server.ValidateStateRequest{GameState: &game_state.GameState{Round: 1, BreakMax: 16, PlayerGameStates: playerGameStates}}
	res, err = s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}
}

func TestValidateDisplay_WhenDisplayEmpty_IsOK(t *testing.T) {
	s := New(nil)

	displayCards := []*display_state.DisplayCard{}

	displayState := display_state.DisplayState{
		Cards: displayCards,
	}

	res := s.ValidateDisplay(nil, &game_state.GameState{Round: 1, BreakMax: 1, DisplayState: &displayState})
	if len(res) > 0 {
		t.Fatalf("Should have no validation errors, but got %v", res)
	}
}

func TestValidateDisplay_WhenDisplayHasTooManyCards_ReturnsError(t *testing.T) {
	s := New(nil)

	displayCard := display_state.DisplayCard{}

	displayCards := []*display_state.DisplayCard{
		&displayCard,
		&displayCard,
		&displayCard,
		&displayCard,
		&displayCard,
		&displayCard,
		&displayCard,
	}

	displayState := display_state.DisplayState{
		Cards: displayCards,
	}

	res := s.ValidateDisplay(nil, &game_state.GameState{Round: 1, BreakMax: 1, DisplayState: &displayState})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidateState_WhenPlayerGameStatesEmpty_ReturnsError(t *testing.T) {
	s := New(nil)

	playerGameStates := []*player_game_state.PlayerGameState{}

	r := server.ValidateStateRequest{
		GameState: &game_state.GameState{
			Round:            1,
			BreakMax:         1,
			PlayerGameStates: playerGameStates,
		},
	}
	res, err := s.ValidateState(nil, &r)
	if err != nil {
		t.Fatalf("Empty ValidateStateRequest shouldn't cause an error, but got %v", err)
	}

	if len(res.ValidationErrors) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res.ValidationErrors)
	}
}

func TestValidatePlayerGameState_WhenPlayerIdNotSet_ReturnsError(t *testing.T) {
	s := New(nil)

	res := s.ValidatePlayerGameState(nil, &player_game_state.PlayerGameState{})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerGameState_WhenReputationNegative_ReturnsError(t *testing.T) {
	s := New(nil)

	res := s.ValidatePlayerGameState(nil, &player_game_state.PlayerGameState{PlayerId: 1, Reputation: -1})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerGameState_WhenConservationNegative_ReturnsError(t *testing.T) {
	s := New(nil)

	res := s.ValidatePlayerGameState(nil, &player_game_state.PlayerGameState{PlayerId: 1, Conservation: -1})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerGameState_WhenAppealNegative_ReturnsError(t *testing.T) {
	s := New(nil)

	res := s.ValidatePlayerGameState(nil, &player_game_state.PlayerGameState{PlayerId: 1, Appeal: -1})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerGameState_WhenMoneyNegative_ReturnsError(t *testing.T) {
	s := New(nil)

	res := s.ValidatePlayerGameState(nil, &player_game_state.PlayerGameState{PlayerId: 1, Money: -1})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerGameState_WhenActionCardsEmpty_ReturnsError(t *testing.T) {
	s := New(nil)
	state := player_game_state.PlayerGameState{
		PlayerId:    1,
		ActionCards: []*player_game_state.PlayerActionCard{},
	}

	res := s.ValidatePlayerGameState(nil, &state)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerGameState_WhenTooManyActionCards_ReturnsError(t *testing.T) {
	s := New(nil)
	state := player_game_state.PlayerGameState{
		PlayerId: 1,
		ActionCards: []*player_game_state.PlayerActionCard{
			&player_game_state.PlayerActionCard{},
			&player_game_state.PlayerActionCard{},
			&player_game_state.PlayerActionCard{},
			&player_game_state.PlayerActionCard{},
			&player_game_state.PlayerActionCard{},
			&player_game_state.PlayerActionCard{},
		},
	}

	res := s.ValidatePlayerGameState(nil, &state)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenUnknownActionCard_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCard := player_game_state.PlayerActionCard{
		CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_UNKNOWN,
		Strength: 1,
	}
	seenCardTypes := map[player_game_state.PlayerActionCardType]int{}
	seenStrengths := map[int32]int{}
	res := s.ValidatePlayerActionCard(nil, &actionCard, seenCardTypes, seenStrengths)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenDuplicateActionCard_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCard := player_game_state.PlayerActionCard{
		CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
		Strength: 1,
	}
	seenCardTypes := map[player_game_state.PlayerActionCardType]int{
		player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS: 1,
	}
	seenStrengths := map[int32]int{}
	res := s.ValidatePlayerActionCard(nil, &actionCard, seenCardTypes, seenStrengths)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenActionCardStrengthZero_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCard := player_game_state.PlayerActionCard{
		CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
		Strength: 0,
	}
	seenCardTypes := map[player_game_state.PlayerActionCardType]int{}
	seenStrengths := map[int32]int{}
	res := s.ValidatePlayerActionCard(nil, &actionCard, seenCardTypes, seenStrengths)

	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenActionCardStrengthTooHigh_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCard := player_game_state.PlayerActionCard{
		CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
		Strength: 6,
	}
	seenCardTypes := map[player_game_state.PlayerActionCardType]int{}
	seenStrengths := map[int32]int{}
	res := s.ValidatePlayerActionCard(nil, &actionCard, seenCardTypes, seenStrengths)

	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenActionCardStrengthDuplicated_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCard := player_game_state.PlayerActionCard{
		CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
		Strength: 1,
	}
	seenCardTypes := map[player_game_state.PlayerActionCardType]int{}
	seenStrengths := map[int32]int{
		1: 1,
	}
	res := s.ValidatePlayerActionCard(nil, &actionCard, seenCardTypes, seenStrengths)

	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCardToken_WhenActionCardTokensUnknownType_ReturnsError(t *testing.T) {
	s := New(nil)
	token := player_game_state.PlayerActionCardToken{
		TokenType: player_game_state.PlayerActionCardTokenType_PLAYERACTIONCARDTOKENTYPE_UNKNOWN,
		NumTokens: 1,
	}
	res := s.ValidatePlayerActionCardToken(nil, &token)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCardToken_WhenActionCardTokensLessThanOne_ReturnsError(t *testing.T) {
	s := New(nil)
	token := player_game_state.PlayerActionCardToken{
		TokenType: player_game_state.PlayerActionCardTokenType_PLAYERACTIONCARDTOKENTYPE_MULTIPLIER,
		NumTokens: 0,
	}

	res := s.ValidatePlayerActionCardToken(nil, &token)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenRecurringTypeUnknown_ReturnsError(t *testing.T) {
	s := New(nil)
	reward := associate.ConservationProjectReward{
		Reward: &associate.ConservationProjectReward_RecurringReward{
			RecurringReward: associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_UNKNOWN,
		},
	}
	seenConservationRecurringRewards := map[associate.ConservationProjectRecurringReward]int{}
	seenConservationOneTimeRewards := map[associate.ConservationProjectOneTimeReward]int{}

	res := s.ValidatePlayerConservationProjectReward(nil, &reward, seenConservationRecurringRewards, seenConservationOneTimeRewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenOneTimeTypeUnknown_ReturnsError(t *testing.T) {
	s := New(nil)
	reward := associate.ConservationProjectReward{
		Reward: &associate.ConservationProjectReward_OneTimeReward{
			OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_UNKNOWN,
		},
	}
	seenConservationRecurringRewards := map[associate.ConservationProjectRecurringReward]int{}
	seenConservationOneTimeRewards := map[associate.ConservationProjectOneTimeReward]int{}

	res := s.ValidatePlayerConservationProjectReward(nil, &reward, seenConservationRecurringRewards, seenConservationOneTimeRewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenDuplicateRecurring_ReturnsError(t *testing.T) {
	s := New(nil)
	reward := associate.ConservationProjectReward{
		Reward: &associate.ConservationProjectReward_RecurringReward{
			RecurringReward: associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_SNAPPING,
		},
	}
	seenConservationRecurringRewards := map[associate.ConservationProjectRecurringReward]int{
		associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_SNAPPING: 1,
	}
	seenConservationOneTimeRewards := map[associate.ConservationProjectOneTimeReward]int{}

	res := s.ValidatePlayerConservationProjectReward(nil, &reward, seenConservationRecurringRewards, seenConservationOneTimeRewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenDuplicateOneTime_ReturnsError(t *testing.T) {
	s := New(nil)
	reward := associate.ConservationProjectReward{
		Reward: &associate.ConservationProjectReward_OneTimeReward{
			OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_AVIARY_REPTILE_HOUSE,
		},
	}
	seenConservationRecurringRewards := map[associate.ConservationProjectRecurringReward]int{}
	seenConservationOneTimeRewards := map[associate.ConservationProjectOneTimeReward]int{
		associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_AVIARY_REPTILE_HOUSE: 1,
	}

	res := s.ValidatePlayerConservationProjectReward(nil, &reward, seenConservationRecurringRewards, seenConservationOneTimeRewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenTooManyRewards_ReturnsError(t *testing.T) {
	s := New(nil)
	rewards := []*associate.ConservationProjectReward{
		&associate.ConservationProjectReward{},
		&associate.ConservationProjectReward{},
		&associate.ConservationProjectReward{},
		&associate.ConservationProjectReward{},
		&associate.ConservationProjectReward{},
		&associate.ConservationProjectReward{},
		&associate.ConservationProjectReward{},
		&associate.ConservationProjectReward{},
	}
	res := s.ValidatePlayerConservationProjectRewards(nil, rewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}
