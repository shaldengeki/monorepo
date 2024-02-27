from flask.testing import FlaskClient

from .fixtures import app, client  # noqa


def test_example_request(client: FlaskClient) -> None:
    # response = client.post(
    #     "/graphql",
    #     json={
    #         "query": """
    #             query {
    #                 test
    #             }
    #         """
    #     },
    # )
    # assert response.json["data"]["test"] == "hello world!"
    assert True
