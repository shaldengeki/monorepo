# fitbit-challenges

![Test status](https://github.com/shaldengeki/fitbit-challenges/actions/workflows/test.yaml/badge.svg)

## Development

### Set up pre-commit

This will set up some hooks that will fix e.g. trailing whitespace or formatting issues when you `git commit`:
```
pip install -r requirements.txt
pre-commit install
pre-commit run --all-files
```

### Run the app
Install [docker compose](https://docs.docker.com/compose/install/), then:

```
docker compose up
```

That should bring up the full stack of applications.

Navigate in a browser to:
- [The API](http://localhost:5000/graphql)
- [The frontend](http://localhost:5001)

You should be able to make changes to frontend files and see them show up ~immediately!
