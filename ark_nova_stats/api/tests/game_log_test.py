import sys
import urllib.parse

import pytest
from flask.testing import FlaskClient
from python.runfiles import Runfiles

from ark_nova_stats.api.tests.fixtures import app, client


def test_submit_game_log(client: FlaskClient) -> None:
    r = Runfiles.Create()
    sample_game_fixture = r.Rlocation(
        "_main/ark_nova_stats/api/tests/fixtures/sample_game.log.json"
    )
    with open(sample_game_fixture, "r") as sample_game_logfile:
        game_log = sample_game_logfile.read()

    response = client.post(
        "/graphql",
        json={
            "query": """
                mutation {
                    submitGameLog(
                        log: \""""
            + urllib.parse.quote(game_log)
            + """\",
                        source: "BGA"
                    ) {
                        success
                    }
                }
            """
        },
    )
    assert response.json["data"]["success"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
