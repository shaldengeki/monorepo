# fitbit-challenges

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
docker compose up
```

That should bring up the full stack of applications.

Navigate in a browser to:
- [The API](http://localhost:5000/graphql)
- [The frontend](http://localhost:5001)

You should be able to make changes to frontend files and see them show up ~immediately!

### Run tests

To run tests once, run `bin/test`, which will run Python and JS tests. The command will error out if any tests failed.

If you're doing JS development, you might find it helpful to set up the test watcher. In a terminal, do `cd frontend && npm test`. This will run an ongoing process to watch for changes to files & re-run tests as needed.
