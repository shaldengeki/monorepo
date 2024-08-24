import sys

import pytest
from flask.testing import FlaskClient
from python.runfiles import Runfiles

from ark_nova_stats.api.tests.fixtures import app, client


def test_submit_game_ratings(client: FlaskClient) -> None:
    r = Runfiles.Create()
    sample_ratings_fixture = r.Rlocation(
        "_main/ark_nova_stats/bga_log_parser/fixtures/sample_game_ratings.json"
    )
    with open(sample_ratings_fixture, "r") as sample_ratings_logfile:
        ratings_fixture_content = sample_ratings_logfile.read().strip()

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

    # GushenTale
    assert 1943 == data[0]["priorElo"]
    assert 1937 == data[0]["newElo"]
    assert 1922 == data[0]["priorArenaElo"]
    assert 1907 == data[0]["newArenaElo"]

    # sorryimlikethis
    assert 2093 == data[1]["priorElo"]
    assert 2099 == data[1]["newElo"]
    assert 2019 == data[1]["priorArenaElo"]
    assert 2034 == data[1]["newArenaElo"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
