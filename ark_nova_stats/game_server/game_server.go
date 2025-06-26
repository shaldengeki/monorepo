package game_server

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/game_state_provider"

	"github.com/shaldengeki/monorepo/ark_nova_stats/game_server/proto/server"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/associate"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/cards"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/game_state"
	"github.com/shaldengeki/monorepo/ark_nova_stats/proto/player_game_state"

	"google.golang.org/grpc"
)

type gameServer struct {
	server.UnimplementedGameServerServer

	gameStateProvider game_state_provider.GameStateProvider
}

func (s *gameServer) GetState(ctx context.Context, request *server.GetStateRequest) (*server.GetStateResponse, error) {
	if request.GameId == 0 {
		return nil, errors.New("Game ID not provided")
	}

	state, err := s.gameStateProvider.GetState(ctx, request.GameId)
	if err != nil {
		return nil, errors.New(fmt.Sprintf("Could not fetch game state: %v", err))
	}

	r := server.GetStateResponse{GameState: state}
	return &r, nil
}

func (s *gameServer) CalculateBreakMax(players int) int {
	return 1 + 4*players
}

func (s *gameServer) ValidateBreak(ctx context.Context, gameState *game_state.GameState) []string {
	if gameState.BreakCount < 0 {
		return []string{"Break count should be >= 0"}
	}

	if gameState.BreakMax < 1 {
		return []string{"Break max should be >= 1"}
	}

	if gameState.BreakMax < gameState.BreakCount {
		return []string{"Break count should be <= break max"}
	}

	if int(gameState.BreakMax) != s.CalculateBreakMax(len(gameState.PlayerGameStates)) {
		return []string{"Break max is incorrect for this number of players"}
	}

	return []string{}
}

func (s *gameServer) ValidateDisplay(ctx context.Context, gameState *game_state.GameState) []string {
	if gameState.DisplayState != nil && gameState.DisplayState.Cards != nil {
		if len(gameState.DisplayState.Cards) > 6 {
			return []string{"Display must contain at most six cards"}
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerActionCardToken(ctx context.Context, token *player_game_state.PlayerActionCardToken) []string {
	if token.TokenType == player_game_state.PlayerActionCardTokenType_PLAYERACTIONCARDTOKENTYPE_UNKNOWN {
		return []string{"Player action card token type must be set to a known value"}
	}

	if token.NumTokens < 1 {
		return []string{"Player action card token count must be set to > 0, if passed at all"}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerActionCard(ctx context.Context, actionCard *player_game_state.PlayerActionCard, seenCardTypes map[player_game_state.PlayerActionCardType]int, seenStrengths map[int32]int) []string {
	if actionCard.CardType == player_game_state.PlayerActionCardType_PLAYERACTIONCARDTYPE_UNKNOWN {
		return []string{"Player action card type must be set to a known value"}
	}
	if _, ok := seenCardTypes[actionCard.CardType]; ok {
		return []string{"Player has multiple instances of an action card type"}
	} else {
		seenCardTypes[actionCard.CardType] = 1
	}

	if actionCard.Strength < 1 || actionCard.Strength > 5 {
		return []string{"Player action card strength must be within [1, 5]"}
	}

	if _, ok := seenStrengths[actionCard.Strength]; ok {
		return []string{"Player has multiple instances of an action card strength"}
	} else {
		seenStrengths[actionCard.Strength] = 1
	}

	for _, token := range actionCard.Tokens {
		if errors := s.ValidatePlayerActionCardToken(ctx, token); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerActionCards(ctx context.Context, actionCards []*player_game_state.PlayerActionCard) []string {
	if len(actionCards) != 5 {
		return []string{"Player must have exactly 5 action cards"}
	}

	seenCardTypes := map[player_game_state.PlayerActionCardType]int{}
	seenStrengths := map[int32]int{}

	for _, actionCard := range actionCards {
		if errors := s.ValidatePlayerActionCard(ctx, actionCard, seenCardTypes, seenStrengths); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerConservationProjectReward(ctx context.Context, conservationReward *associate.ConservationProjectReward, seenRecurringRewards map[associate.ConservationProjectRecurringReward]int, seenOneTimeRewards map[associate.ConservationProjectOneTimeReward]int) []string {
	if conservationReward.GetRecurringReward() != associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_UNKNOWN {
		recurringReward := conservationReward.GetRecurringReward()
		if _, found := seenRecurringRewards[recurringReward]; found {
			return []string{"Player has duplicate recurring conservation rewards"}
		} else {
			seenRecurringRewards[recurringReward] = 1
		}
	} else if conservationReward.GetOneTimeReward() != associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_UNKNOWN {
		oneTimeReward := conservationReward.GetOneTimeReward()
		if _, found := seenOneTimeRewards[oneTimeReward]; found {
			return []string{"Player has duplicate one-time conservation rewards"}
		} else {
			seenOneTimeRewards[oneTimeReward] = 1
		}
	} else {
		return []string{"Conservation project reward cannot be unknown type"}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerConservationProjectRewards(ctx context.Context, conservationRewards []*associate.ConservationProjectReward) []string {
	if len(conservationRewards) > 7 {
		return []string{"Player cannot have more than 7 conservation project rewards"}
	}

	seenConservationRecurringRewards := map[associate.ConservationProjectRecurringReward]int{}
	seenConservationOneTimeRewards := map[associate.ConservationProjectOneTimeReward]int{}

	for _, conservationReward := range conservationRewards {
		if errors := s.ValidatePlayerConservationProjectReward(ctx, conservationReward, seenConservationRecurringRewards, seenConservationOneTimeRewards); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerPartnerZoo(ctx context.Context, partnerZoo associate.PartnerZoo, seenPartnerZoos map[associate.PartnerZoo]int) []string {
	if partnerZoo == associate.PartnerZoo_PARTNERZOO_UNKNOWN {
		return []string{"Partner zoo cannot be unknown type"}
	}

	if _, found := seenPartnerZoos[partnerZoo]; found {
		return []string{"Player has duplicate partner zoos"}
	} else {
		seenPartnerZoos[partnerZoo] = 1
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerPartnerZoos(ctx context.Context, partnerZoos []associate.PartnerZoo) []string {
	if len(partnerZoos) > 4 {
		return []string{"Player cannot have more than 4 partner zoos"}
	}

	seenPartnerZoos := map[associate.PartnerZoo]int{}

	for _, partnerZoo := range partnerZoos {
		if errors := s.ValidatePlayerPartnerZoo(ctx, partnerZoo, seenPartnerZoos); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerUniversity(ctx context.Context, university associate.University, seenUniversities map[associate.University]int) []string {
	if university == associate.University_UNIVERSITY_UNKNOWN {
		return []string{"University cannot be unknown type"}
	}

	if _, found := seenUniversities[university]; found {
		return []string{"Player has duplicate universities"}
	} else {
		seenUniversities[university] = 1
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerUniversities(ctx context.Context, universities []associate.University) []string {
	if len(universities) > 3 {
		return []string{"Player cannot have more than 3 universities"}
	}

	seenUniversities := map[associate.University]int{}

	for _, university := range universities {
		if errors := s.ValidatePlayerUniversity(ctx, university, seenUniversities); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidateAnimalCard(ctx context.Context, animalCard *cards.AnimalCard, seenAnimals map[int64]int) []string {
	if animalCard.Card == nil {
		return []string{"Animal card must have a Card object set"}
	}

	if animalCard.Card.CardId < 1 {
		return []string{"Card ID must be >= 1"}
	}

	if _, found := seenAnimals[animalCard.Card.CardId]; found {
		return []string{"Player has duplicate animals"}
	} else {
		seenAnimals[animalCard.Card.CardId] = 1
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerAnimals(ctx context.Context, animalCards []*cards.AnimalCard) []string {
	seenAnimals := map[int64]int{}

	for _, animalCard := range animalCards {
		if errors := s.ValidateAnimalCard(ctx, animalCard, seenAnimals); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidateSponsorCard(ctx context.Context, sponsorCard *cards.SponsorCard, seenSponsors map[int64]int) []string {
	if sponsorCard.Card == nil {
		return []string{"Sponsor card must have a Card object set"}
	}

	if sponsorCard.Card.CardId < 1 {
		return []string{"Card ID must be >= 1"}
	}

	if _, found := seenSponsors[sponsorCard.Card.CardId]; found {
		return []string{"Player has duplicate sponsors"}
	} else {
		seenSponsors[sponsorCard.Card.CardId] = 1
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerSponsors(ctx context.Context, sponsorCards []*cards.SponsorCard) []string {
	seenSponsors := map[int64]int{}

	for _, sponsorCard := range sponsorCards {
		if errors := s.ValidateSponsorCard(ctx, sponsorCard, seenSponsors); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerMap(ctx context.Context, playerMap *player_game_state.PlayerMap) []string {
	// TODO: implement this.
	return []string{}
}

func (s *gameServer) ValidatePlayerHandCard(ctx context.Context, playerHandCard *player_game_state.PlayerHandCard, seenCards map[int64]int) []string {
	if playerHandCard.GetAnimalCard() != nil {
		card := playerHandCard.GetAnimalCard()

		if card.Card.CardId < 1 {
			return []string{"Animal card ID must be >= 1"}
		}
	} else if playerHandCard.GetSponsorCard() != nil {
		card := playerHandCard.GetSponsorCard()

		if card.Card.CardId < 1 {
			return []string{"Sponsor card ID must be >= 1"}
		}
	} else if playerHandCard.GetConservationProjectCard() != nil {
		card := playerHandCard.GetConservationProjectCard()

		if card.Card.CardId < 1 {
			return []string{"Conservation project card ID must be >= 1"}
		}
	} else if playerHandCard.GetEndgameScoringCard() != nil {
		card := playerHandCard.GetEndgameScoringCard()

		if card.Card.CardId < 1 {
			return []string{"Endgame scoring card ID must be >= 1"}
		}
	} else {
		return []string{"Hand card must have a Card object set"}
	}

	if _, found := seenCards[card.Card.CardId]; found {
		return []string{"Player has duplicate hand cards"}
	} else {
		seenCards[card.Card.CardId] = 1
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerHand(ctx context.Context, hand *player_game_state.PlayerHand) []string {
	seenCards := map[int64]int{}

	for _, card := range hand.Cards {
		if errors := s.ValidatePlayerHandCard(ctx, card, seenCards); len(errors) > 0 {
			return errors
		}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerGameState(ctx context.Context, playerGameState *player_game_state.PlayerGameState) []string {
	if playerGameState.PlayerId <= 0 {
		return []string{"Player ID not set"}
	}

	if playerGameState.Reputation < 0 {
		return []string{"Player reputation must be >= 0"}
	}

	if playerGameState.Conservation < 0 {
		return []string{"Player conservation must be >= 0"}
	}

	if playerGameState.Appeal < 0 {
		return []string{"Player appeal must be >= 0"}
	}

	if playerGameState.Money < 0 {
		return []string{"Player money must be >= 0"}
	}

	if errors := s.ValidatePlayerActionCards(ctx, playerGameState.ActionCards); len(errors) > 0 {
		return errors
	}

	// TODO validations for:
	// conservation project rewards don't line up with map
	// Probably put this in proto or golang, not the database?
	if errors := s.ValidatePlayerConservationProjectRewards(ctx, playerGameState.ConservationProjectRewards); len(errors) > 0 {
		return errors
	}

	if errors := s.ValidatePlayerPartnerZoos(ctx, playerGameState.PartnerZoos); len(errors) > 0 {
		return errors
	}

	if errors := s.ValidatePlayerUniversities(ctx, playerGameState.Universities); len(errors) > 0 {
		return errors
	}

	if errors := s.ValidatePlayerAnimals(ctx, playerGameState.Animals); len(errors) > 0 {
		return errors
	}

	if errors := s.ValidatePlayerSponsors(ctx, playerGameState.Sponsors); len(errors) > 0 {
		return errors
	}

	if errors := s.ValidatePlayerMap(ctx, playerGameState.Map); len(errors) > 0 {
		return errors
	}

	if errors := s.ValidatePlayerHand(ctx, playerGameState.Hand); len(errors) > 0 {
		return errors
	}

	return []string{}
}

func (s *gameServer) ValidateState(ctx context.Context, request *server.ValidateStateRequest) (*server.ValidateStateResponse, error) {
	if request.GameState == nil {
		return &server.ValidateStateResponse{}, nil
	}

	if request.GameState.Round < 1 {
		return &server.ValidateStateResponse{ValidationErrors: []string{"Round count should be >= 1"}}, nil
	}

	errs := s.ValidateBreak(ctx, request.GameState)
	if len(errs) > 0 {
		return &server.ValidateStateResponse{ValidationErrors: errs}, nil
	}

	errs = s.ValidateDisplay(ctx, request.GameState)
	if len(errs) > 0 {
		return &server.ValidateStateResponse{ValidationErrors: errs}, nil
	}

	if request.GameState.PlayerGameStates == nil || len(request.GameState.PlayerGameStates) < 1 {
		return &server.ValidateStateResponse{ValidationErrors: []string{"At least one player game state must be passed"}}, nil
	}

	// TODO validations for:
	// duplicates across player game states, i.e. animals, sponsors, hand cards, or unique buildings
	// will probably require sharing global state and passing it in.

	for _, playerGameState := range request.GameState.PlayerGameStates {
		errs = s.ValidatePlayerGameState(ctx, playerGameState)
		if len(errs) > 0 {
			return &server.ValidateStateResponse{ValidationErrors: errs}, nil
		}
	}

	return &server.ValidateStateResponse{}, nil
}

func New(gameStateProvider game_state_provider.GameStateProvider) *gameServer {
	return &gameServer{gameStateProvider: gameStateProvider}
}

func main() {
	lis, err := net.Listen("tcp", "localhost:5003")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	server.RegisterGameServerServer(grpcServer, New(nil))
	grpcServer.Serve(lis)
}

/*
	TODO:
		- write tests for invalid states within each board component, like:
			- invalid buildings (off grid, two of one, enclosure over-occupied, etc)
			- invalid partner zoos (two of one)
			- invalid animals (too many for the enclosures we have)
		- implement ValidateState, passing each test

		future directions:
		- spin up game server
			- spin up game server, backed by postgres
			- create database tables
			- backfill with BGA game logs
				- Add a CreateTable rpc
				- In Python, add worker logic to call CreateTable with game logs
			- in stats db, call GetState and render endgame state
		- support play
			- add protos for taking actions
			- add TakeAction rpc and implement it, returning GameState
*/
