import sys

import pytest
from flask.testing import FlaskClient
from python.runfiles import Runfiles

from ark_nova_stats.api.tests.fixtures import app, client


def test_submit_game_logs(client: FlaskClient) -> None:
    r = Runfiles.Create()
    sample_game_fixture = r.Rlocation(
        "_main/ark_nova_stats/bga_log_parser/fixtures/sample_game.log.json"
    )
    with open(sample_game_fixture, "r") as sample_game_logfile:
        game_log = sample_game_logfile.read().strip()

    response = client.post(
        "/graphql",
        json={
            "query": """
                mutation($logs: String!) {
                    submitGameLogs(
                        logs: $logs,
                    ) {
                        id
                        log
                    }
                }
            """,
            "variables": {
                "logs": game_log,
            },
        },
    )
    assert response.json.get(
        "data", {}
    ), f"data field not set on response json: {response.json}"
    assert response.json["data"].get(
        "submitGameLogs", {}
    ), f"submitGameLogs field not set on response json: {response.json['data']}"
    assert (
        response.json["data"]["submitGameLogs"].get("log", "") == game_log
    ), f"game log was not expected value: {response.json}"


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
                mutation($ratings: String!) {
                    submitGameRatings(
                        ratings: $ratings,
                    ) {
                        id
                    }
                }
            """,
            "variables": {
                "ratings": ratings_fixture_content,
            },
        },
    )
    assert response.json.get(
        "data", {}
    ), f"data field not set on response json: {response.json}"
    assert response.json["data"].get(
        "submitGameRatings", {}
    ), f"submitGameRatings field not set on response json: {response.json['data']}"
    assert response.json["data"]["submitGameRatings"].get(
        "id", ""
    ), f"rating ids were not set: {response.json}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
