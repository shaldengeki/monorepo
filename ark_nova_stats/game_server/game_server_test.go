package game_server

import (
	"testing"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/game_state_provider"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto/server"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/associate"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/cards"
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
	actionCards := []*player_game_state.PlayerActionCard{
		&player_game_state.PlayerActionCard{
			CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_UNKNOWN,
			Strength: 1,
		},
	}

	res := s.ValidatePlayerActionCards(nil, actionCards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenDuplicateActionCard_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCards := []*player_game_state.PlayerActionCard{
		&player_game_state.PlayerActionCard{
			CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
			Strength: 1,
		},
		&player_game_state.PlayerActionCard{
			CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
			Strength: 2,
		},
	}

	res := s.ValidatePlayerActionCards(nil, actionCards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenActionCardStrengthZero_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCards := []*player_game_state.PlayerActionCard{
		&player_game_state.PlayerActionCard{
			CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
			Strength: 0,
		},
	}

	res := s.ValidatePlayerActionCards(nil, actionCards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenActionCardStrengthTooHigh_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCards := []*player_game_state.PlayerActionCard{
		&player_game_state.PlayerActionCard{
			CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
			Strength: 6,
		},
	}

	res := s.ValidatePlayerActionCards(nil, actionCards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerActionCard_WhenActionCardStrengthDuplicated_ReturnsError(t *testing.T) {
	s := New(nil)
	actionCards := []*player_game_state.PlayerActionCard{
		&player_game_state.PlayerActionCard{
			CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_ANIMALS,
			Strength: 6,
		},
		&player_game_state.PlayerActionCard{
			CardType: player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_SPONSORS,
			Strength: 6,
		},
	}

	res := s.ValidatePlayerActionCards(nil, actionCards)
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
	rewards := []*associate.ConservationProjectReward{
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_RecurringReward{
				RecurringReward: associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_UNKNOWN,
			},
		},
	}

	res := s.ValidatePlayerConservationProjectRewards(nil, rewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenOneTimeTypeUnknown_ReturnsError(t *testing.T) {
	s := New(nil)
	rewards := []*associate.ConservationProjectReward{
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_UNKNOWN,
			},
		},
	}

	res := s.ValidatePlayerConservationProjectRewards(nil, rewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenDuplicateRecurring_ReturnsError(t *testing.T) {
	s := New(nil)
	rewards := []*associate.ConservationProjectReward{
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_RecurringReward{
				RecurringReward: associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_SNAPPING,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_RecurringReward{
				RecurringReward: associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_SNAPPING,
			},
		},
	}

	res := s.ValidatePlayerConservationProjectRewards(nil, rewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenDuplicateOneTime_ReturnsError(t *testing.T) {
	s := New(nil)
	rewards := []*associate.ConservationProjectReward{
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_AVIARY_REPTILE_HOUSE,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_AVIARY_REPTILE_HOUSE,
			},
		},
	}

	res := s.ValidatePlayerConservationProjectRewards(nil, rewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerConservationProjectReward_WhenTooManyRewards_ReturnsError(t *testing.T) {
	s := New(nil)
	rewards := []*associate.ConservationProjectReward{
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_AVIARY_REPTILE_HOUSE,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_ASSOCIATION_WORKER,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_TWELVE_MONEY,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_THREE_X,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_UNIVERSITY,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_AVIARY_REPTILE_HOUSE,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_DETERMINATION,
			},
		},
		&associate.ConservationProjectReward{
			Reward: &associate.ConservationProjectReward_OneTimeReward{
				OneTimeReward: associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_TWO_REPUTATION,
			},
		},
	}
	res := s.ValidatePlayerConservationProjectRewards(nil, rewards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerPartnerZoos_WhenPartnerZooUnknownType_ReturnsError(t *testing.T) {
	s := New(nil)
	res := s.ValidatePlayerPartnerZoos(nil, []associate.PartnerZoo{associate.PartnerZoo_PARTNERZOO_UNKNOWN})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerPartnerZoos_WhenDuplicatePartnerZoos_ReturnsError(t *testing.T) {
	s := New(nil)
	res := s.ValidatePlayerPartnerZoos(nil, []associate.PartnerZoo{associate.PartnerZoo_PARTNERZOO_ASIA, associate.PartnerZoo_PARTNERZOO_EUROPE, associate.PartnerZoo_PARTNERZOO_ASIA})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerPartnerZoos_WhenTooManyPartnerZoos_ReturnsError(t *testing.T) {
	s := New(nil)
	res := s.ValidatePlayerPartnerZoos(nil, []associate.PartnerZoo{associate.PartnerZoo_PARTNERZOO_ASIA, associate.PartnerZoo_PARTNERZOO_EUROPE, associate.PartnerZoo_PARTNERZOO_AFRICA, associate.PartnerZoo_PARTNERZOO_AMERICAS, associate.PartnerZoo_PARTNERZOO_AUSTRALIA})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerPartnerZoos_WhenUniversityUnknownType_ReturnsError(t *testing.T) {
	s := New(nil)
	res := s.ValidatePlayerUniversities(nil, []associate.University{associate.University_UNIVERSITY_UNKNOWN})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerUniversities_WhenDuplicateUniversities_ReturnsError(t *testing.T) {
	s := New(nil)
	res := s.ValidatePlayerUniversities(nil, []associate.University{associate.University_UNIVERSITY_TWO_SCIENCE, associate.University_UNIVERSITY_SCIENCE_TWO_REPUTATION, associate.University_UNIVERSITY_TWO_SCIENCE})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerUniversities_WhenTooManyUniversities_ReturnsError(t *testing.T) {
	s := New(nil)
	res := s.ValidatePlayerUniversities(nil, []associate.University{associate.University_UNIVERSITY_TWO_SCIENCE, associate.University_UNIVERSITY_SCIENCE_TWO_REPUTATION, associate.University_UNIVERSITY_REPUTATION_HAND_SIZE, associate.University_UNIVERSITY_TWO_SCIENCE})
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerAnimals_WithNoAnimals_IsOK(t *testing.T) {
	s := New(nil)

	cards := []*cards.AnimalCard{}

	res := s.ValidatePlayerAnimals(nil, cards)
	if len(res) > 0 {
		t.Fatalf("Should result in no validation errors, but got %v", res)
	}
}

func TestValidatePlayerAnimals_WhenCardIdNotSet_ReturnsError(t *testing.T) {
	s := New(nil)

	cards := []*cards.AnimalCard{
		&cards.AnimalCard{
			Card: &cards.Card{},
		},
	}

	res := s.ValidatePlayerAnimals(nil, cards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}

func TestValidatePlayerAnimals_WithDuplicateAnimals_ReturnsError(t *testing.T) {
	s := New(nil)

	cards := []*cards.AnimalCard{
		&cards.AnimalCard{
			Card: &cards.Card{
				CardId: 1,
			},
		},
		&cards.AnimalCard{
			Card: &cards.Card{
				CardId: 2,
			},
		},
		&cards.AnimalCard{
			Card: &cards.Card{
				CardId: 1,
			},
		},
	}

	res := s.ValidatePlayerAnimals(nil, cards)
	if len(res) < 1 {
		t.Fatalf("Should result in a validation error, but got %v", res)
	}
}
