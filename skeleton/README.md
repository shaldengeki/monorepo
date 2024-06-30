# skeleton

Base project for webapps.

## Development

### Set up pre-commit

This will set up some hooks that will fix e.g. trailing whitespace or formatting issues when you `git commit`:
```
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Run the app
Install [docker compose](https://docs.docker.com/compose/install/), then:

```
docker compose -f docker-compose.yaml -f docker-compose.override.yaml up
```

That should bring up the full stack of applications.

Navigate in a browser to:
- [The API](http://localhost:5000/graphql)
- [The frontend](http://localhost:5001)

You should be able to make changes to frontend files and see them show up ~immediately!

### Run tests

To run tests once, run `bazel test //skeleton/...`, which will run Python and JS tests. The command will error out if any tests failed.
