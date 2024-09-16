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

func (s *gameServer) ValidatePlayerConservationProjectReward(ctx context.Context, conservationReward *associate.ConservationProjectReward, seenRecurringRewards map[associate.ConservationProjectRecurringReward]int, seenOneTimeRewards map[associate.ConservationProjectOneTimeReward]int) []string {
	if conservationReward.GetRecurringReward() != associate.ConservationProjectRecurringReward_CONSERVATIONPROJECTRECURRINGREWARD_UNKNOWN {
		recurringReward := conservationReward.GetRecurringReward()
		if _, found := seenRecurringRewards[recurringReward]; found {
			return []string{"Player has duplicate recurring conservation rewards"}
		}
	} else if conservationReward.GetOneTimeReward() != associate.ConservationProjectOneTimeReward_CONSERVATIONPROJECTONETIMEREWARD_UNKNOWN {
		oneTimeReward := conservationReward.GetOneTimeReward()
		if _, found := seenOneTimeRewards[oneTimeReward]; found {
			return []string{"Player has duplicate one-time conservation rewards"}
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

func (s *gameServer) ValidatePlayerPartnerZoo(ctx context.Context, partnerZoo associate.PartnerZoo, seenPartnerZoo map[associate.PartnerZoo]int) []string {
	if partnerZoo == associate.PartnerZoo_PARTNERZOO_UNKNOWN {
		return []string{"Partner zoo cannot be unknown type"}
	}

	return []string{}
}

func (s *gameServer) ValidatePlayerPartnerZoos(ctx context.Context, partnerZoos []associate.PartnerZoo) []string {
	if len(partnerZoos) > 7 {
		return []string{"Player cannot have more than 7 conservation project rewards"}
	}

	seenPartnerZoos := map[associate.PartnerZoo]int{}

	for _, partnerZoo := range partnerZoos {
		if errors := s.ValidatePlayerPartnerZoo(ctx, partnerZoo, seenPartnerZoos); len(errors) > 0 {
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

	if len(playerGameState.ActionCards) != 5 {
		return []string{"Player must have exactly 5 action cards"}
	}

	seenCardTypes := map[player_game_state.PlayerActionCardType]int{}
	seenStrengths := map[int32]int{}

	for _, actionCard := range playerGameState.ActionCards {
		if errors := s.ValidatePlayerActionCard(ctx, actionCard, seenCardTypes, seenStrengths); len(errors) > 0 {
			return errors
		}
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

	// repeated University universities = 9;

	// repeated AnimalCard animals = 10;
	// repeated SponsorCard sponsors = 11;

	// PlayerMap map = 12;

	// PlayerHand hand = 13;

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
