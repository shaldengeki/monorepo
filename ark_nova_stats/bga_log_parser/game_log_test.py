import json
import sys
from pathlib import Path

import pytest
from python.runfiles import Runfiles

from ark_nova_stats.bga_log_parser.exceptions import NonArkNovaReplayError
from ark_nova_stats.bga_log_parser.game_log import GameLog, GameLogEventData


def load_data_from_fixture_file(filename: str) -> dict:
    r = Runfiles.Create()
    fixture_file_path = r.Rlocation(
        str(Path("_main") / "ark_nova_stats" / "bga_log_parser" / "fixtures" / filename)
    )
    with open(fixture_file_path, "r") as fixture_file:
        return json.loads(fixture_file.read().strip())


class TestGameLog:
    def test_parses_sample_game(self):
        game_log = load_data_from_fixture_file("sample_game.log.json")
        x = GameLog(**game_log)

        assert 1 == x.status
        assert 1098 == len(x.data.logs)
        assert "Baboude" == x.data.players[0].name
        assert "sorryimlikethis" == x.data.players[1].name
        assert 537650395 == x.data.logs[0].table_id
        assert 1 == x.data.logs[0].move_id
        assert 1721046021 == x.data.logs[0].time
        assert x.winner is not None and "sorryimlikethis" == x.winner.name
        assert not x.is_tie

    def test_winner_is_none_when_tie(self):
        game_log = load_data_from_fixture_file("tie.log.json")
        x = GameLog(**game_log)
        assert x.winner is None

    def test_detects_tie(self):
        game_log = load_data_from_fixture_file("tie.log.json")
        x = GameLog(**game_log)
        assert x.is_tie

    def test_raises_when_not_ark_nova_replay(self):
        game_log = load_data_from_fixture_file("non_ark_nova_game.log.json")
        with pytest.raises(NonArkNovaReplayError):
            GameLog(**game_log)

    def test_parses_4p_game(self):
        game_log = load_data_from_fixture_file("4p.log.json")
        GameLog(**game_log)

    def test_card_plays_for_4p_game(self):
        game_log = load_data_from_fixture_file("4p.log.json")
        plays = list(GameLog(**game_log).data.card_plays)
        assert 1 == len(plays)
        assert "Dusky-leaf Monkey" == plays[0].card.name
        card_ids = [play.card.id for play in plays]
        assert len(set(card_ids)) == len(card_ids)

    def test_parses_game_stats(self):
        game_log = load_data_from_fixture_file("533468391_darcelmaw_hardyzhao.json")
        x = GameLog(**game_log)

        stats = x.stats
        assert 2 == len(stats.player_stats)

        darcelmaw = stats.player_stats[0]
        assert 93481498 == darcelmaw.player_id
        assert 123 == darcelmaw.score
        assert 1 == darcelmaw.rank
        assert 769 == darcelmaw.thinking_time
        assert 1 == darcelmaw.starting_position
        assert 32 == darcelmaw.turns
        assert 1 == darcelmaw.breaks_triggered
        assert darcelmaw.triggered_end
        assert 5 == darcelmaw.map_id
        assert 72 == darcelmaw.appeal
        assert 25 == darcelmaw.conservation
        assert 9 == darcelmaw.reputation
        assert 6 == darcelmaw.actions_build
        assert 6 == darcelmaw.actions_animals
        assert 4 == darcelmaw.actions_cards
        assert 8 == darcelmaw.actions_association
        assert 8 == darcelmaw.actions_sponsors
        assert 7 == darcelmaw.x_tokens_gained
        assert 1 == darcelmaw.x_actions
        assert 4 == darcelmaw.x_tokens_used
        assert 190 == darcelmaw.money_gained
        assert 147 == darcelmaw.money_gained_through_income
        assert 100 == darcelmaw.money_spent_on_animals
        assert 44 == darcelmaw.money_spent_on_enclosures
        assert 0 == darcelmaw.money_spent_on_donations
        assert 0 == darcelmaw.money_spent_on_playing_cards_from_reputation_range
        assert 3 == darcelmaw.cards_drawn_from_deck
        assert 5 == darcelmaw.cards_drawn_from_reputation_range
        assert 8 == darcelmaw.cards_snapped
        assert 1 == darcelmaw.cards_discarded
        assert 7 == darcelmaw.played_sponsors
        assert 9 == darcelmaw.played_animals
        assert 2 == darcelmaw.release_animals
        assert 4 == darcelmaw.association_workers
        assert 0 == darcelmaw.association_donations
        assert 1 == darcelmaw.association_reputation_actions
        assert 1 == darcelmaw.association_partner_zoo_actions
        assert 2 == darcelmaw.association_university_actions
        assert 4 == darcelmaw.association_conservation_project_actions
        assert 9 == darcelmaw.built_enclosures
        assert 2 == darcelmaw.built_kiosks
        assert 6 == darcelmaw.built_pavilions
        assert 3 == darcelmaw.built_unique_buildings
        assert 43 == darcelmaw.hexes_covered
        assert 0 == darcelmaw.hexes_empty
        assert 3 == darcelmaw.upgraded_action_cards
        assert darcelmaw.upgraded_animals
        assert darcelmaw.upgraded_build
        assert not darcelmaw.upgraded_cards
        assert darcelmaw.upgraded_sponsors
        assert not darcelmaw.upgraded_association
        assert 0 == darcelmaw.icons_africa
        assert 2 == darcelmaw.icons_europe
        assert 5 == darcelmaw.icons_asia
        assert 0 == darcelmaw.icons_australia
        assert 1 == darcelmaw.icons_americas
        assert 1 == darcelmaw.icons_bird
        assert 1 == darcelmaw.icons_predator
        assert 1 == darcelmaw.icons_herbivore
        assert 0 == darcelmaw.icons_bear
        assert 3 == darcelmaw.icons_reptile
        assert 1 == darcelmaw.icons_primate
        assert 1 == darcelmaw.icons_petting_zoo
        assert 0 == darcelmaw.icons_sea_animal
        assert 6 == darcelmaw.icons_water
        assert 4 == darcelmaw.icons_rock
        assert 2 == darcelmaw.icons_science

        hardyzhao = stats.player_stats[1]
        assert 92147740 == hardyzhao.player_id
        assert 118 == hardyzhao.score
        assert 2 == hardyzhao.rank
        assert 1430 == hardyzhao.thinking_time
        assert 2 == hardyzhao.starting_position
        assert 32 == hardyzhao.turns
        assert 4 == hardyzhao.breaks_triggered
        assert not hardyzhao.triggered_end
        assert 5 == hardyzhao.map_id
        assert 76 == hardyzhao.appeal
        assert 22 == hardyzhao.conservation
        assert 15 == hardyzhao.reputation
        assert 7 == hardyzhao.actions_build
        assert 6 == hardyzhao.actions_animals
        assert 5 == hardyzhao.actions_cards
        assert 7 == hardyzhao.actions_association
        assert 7 == hardyzhao.actions_sponsors
        assert 9 == hardyzhao.x_tokens_gained
        assert 1 == hardyzhao.x_actions
        assert 4 == hardyzhao.x_tokens_used
        assert 204 == hardyzhao.money_gained
        assert 130 == hardyzhao.money_gained_through_income
        assert 114 == hardyzhao.money_spent_on_animals
        assert 60 == hardyzhao.money_spent_on_enclosures
        assert 0 == hardyzhao.money_spent_on_donations
        assert 0 == hardyzhao.money_spent_on_playing_cards_from_reputation_range
        assert 19 == hardyzhao.cards_drawn_from_deck
        assert 6 == hardyzhao.cards_drawn_from_reputation_range
        assert 4 == hardyzhao.cards_snapped
        assert 2 == hardyzhao.cards_discarded
        assert 4 == hardyzhao.played_sponsors
        assert 12 == hardyzhao.played_animals
        assert 1 == hardyzhao.release_animals
        assert 3 == hardyzhao.association_workers
        assert 0 == hardyzhao.association_donations
        assert 0 == hardyzhao.association_reputation_actions
        assert 2 == hardyzhao.association_partner_zoo_actions
        assert 0 == hardyzhao.association_university_actions
        assert 5 == hardyzhao.association_conservation_project_actions
        assert 12 == hardyzhao.built_enclosures
        assert 4 == hardyzhao.built_kiosks
        assert 2 == hardyzhao.built_pavilions
        assert 0 == hardyzhao.built_unique_buildings
        assert 34 == hardyzhao.hexes_covered
        assert 9 == hardyzhao.hexes_empty
        assert 3 == hardyzhao.upgraded_action_cards
        assert hardyzhao.upgraded_animals
        assert hardyzhao.upgraded_build
        assert hardyzhao.upgraded_cards
        assert not hardyzhao.upgraded_sponsors
        assert not hardyzhao.upgraded_association
        assert 9 == hardyzhao.icons_africa
        assert 4 == hardyzhao.icons_europe
        assert 0 == hardyzhao.icons_asia
        assert 0 == hardyzhao.icons_australia
        assert 1 == hardyzhao.icons_americas
        assert 1 == hardyzhao.icons_bird
        assert 4 == hardyzhao.icons_predator
        assert 1 == hardyzhao.icons_herbivore
        assert 0 == hardyzhao.icons_bear
        assert 2 == hardyzhao.icons_reptile
        assert 4 == hardyzhao.icons_primate
        assert 0 == hardyzhao.icons_petting_zoo
        assert 0 == hardyzhao.icons_sea_animal
        assert 1 == hardyzhao.icons_water
        assert 2 == hardyzhao.icons_rock
        assert 3 == hardyzhao.icons_science


class TestGameLogEventData:
    def test_is_play_event_returns_true_for_play_action(self):
        play_log = load_data_from_fixture_file("play_event.log.json")
        x = GameLogEventData(**play_log)
        assert x.is_play_action

    def test_is_play_event_returns_true_for_new_conservation_project(self):
        play_log = load_data_from_fixture_file("play_new_conservation_project.log.json")
        x = GameLogEventData(**play_log)
        assert x.is_play_action

    def test_is_play_event_returns_false_for_other_actions(self):
        non_play_log = load_data_from_fixture_file("non_play_event.log.json")
        x = GameLogEventData(**non_play_log)
        assert not x.is_play_action

    def test_played_card_names_for_play_action(self):
        play_log = load_data_from_fixture_file("play_event.log.json")
        x = GameLogEventData(**play_log)
        assert set(["Crested Porcupine"]) == x.played_card_names

    def test_played_card_names_for_new_conservation_project(self):
        play_log = load_data_from_fixture_file("play_new_conservation_project.log.json")
        x = GameLogEventData(**play_log)
        assert set(["Yosemite national park"]) == x.played_card_names

    def test_played_card_for_play_action(self):
        play_log = load_data_from_fixture_file("play_event.log.json")
        x = GameLogEventData(**play_log)
        cards = x.played_cards
        assert cards is not None
        assert 1 == len(cards)
        assert cards[0].id == "A445_CrestedPorcupine"
        assert cards[0].name == "Crested Porcupine"

    def test_played_card_for_new_conservation_project(self):
        play_log = load_data_from_fixture_file("play_new_conservation_project.log.json")
        x = GameLogEventData(**play_log)
        cards = x.played_cards
        assert cards is not None
        assert 1 == len(cards)
        assert cards[0].id == "P114_ReleaseYosemite"
        assert cards[0].name == "Yosemite national park"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
