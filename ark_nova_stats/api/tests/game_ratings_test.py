import sys

import pytest
from flask.testing import FlaskClient
from python.runfiles import Runfiles

from ark_nova_stats.api.tests.fixtures import app, client


def read_fixture(name: str) -> str:
    r = Runfiles.Create()
    fixture_path = r.Rlocation(f"_main/ark_nova_stats/bga_log_parser/fixtures/{name}")
    with open(fixture_path, "r") as fixture_file:
        return fixture_file.read().strip()


def test_submit_game_ratings(client: FlaskClient) -> None:
    ratings_fixture_content = read_fixture("sample_game_ratings.json")
    response = client.post(
        "/graphql",
        json={
            "query": """
                mutation($ratings: String!, $tableId: Int!) {
                    submitGameRatings(
                        ratings: $ratings,
                        tableId: $tableId,
                    ) {
                        id
                        newElo
                        priorElo
                        newArenaElo
                        priorArenaElo
                    }
                }
            """,
            "variables": {
                "ratings": ratings_fixture_content,
                "tableId": 1,
            },
        },
    )
    assert response.json.get(
        "data", {}
    ), f"data field not set on response json: {response.json}"
    assert response.json["data"].get(
        "submitGameRatings", {}
    ), f"submitGameRatings field not set on response json: {response.json['data']}"

    data = response.json["data"]["submitGameRatings"]
    assert 2 == len(
        data
    ), f"Two ratings should have been created: {response.json['data']}"

    # sorryimlikethis
    assert 2093 == data[0]["priorElo"]
    assert 2099 == data[0]["newElo"]
    assert 2019 == data[0]["priorArenaElo"]
    assert 2034 == data[0]["newArenaElo"]

    # GushenTale
    assert 1943 == data[1]["priorElo"]
    assert 1937 == data[1]["newElo"]
    assert 1922 == data[1]["priorArenaElo"]
    assert 1907 == data[1]["newArenaElo"]


def test_submit_non_arena_game_ratings(client: FlaskClient) -> None:
    ratings_fixture_content = read_fixture("ratings_non_arena.json")
    response = client.post(
        "/graphql",
        json={
            "query": """
                mutation($ratings: String!, $tableId: Int!) {
                    submitGameRatings(
                        ratings: $ratings,
                        tableId: $tableId,
                    ) {
                        id
                        newElo
                        priorElo
                        newArenaElo
                        priorArenaElo
                    }
                }
            """,
            "variables": {
                "ratings": ratings_fixture_content,
                "tableId": 1,
            },
        },
    )
    assert response.json.get(
        "data", {}
    ), f"data field not set on response json: {response.json}"
    assert response.json["data"].get(
        "submitGameRatings", {}
    ), f"submitGameRatings field not set on response json: {response.json['data']}"

    data = response.json["data"]["submitGameRatings"]
    assert 2 == len(
        data
    ), f"Two ratings should have been created: {response.json['data']}"

    # sorryimlikethis
    assert 2112 == data[0]["priorElo"]
    assert 2116 == data[0]["newElo"]
    assert data[0]["priorArenaElo"] is None
    assert data[0]["newArenaElo"] is None

    # rudaZz
    assert 1890 == data[1]["priorElo"]
    assert 1885 == data[1]["newElo"]
    assert data[1]["priorArenaElo"] is None
    assert data[1]["newArenaElo"] is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
