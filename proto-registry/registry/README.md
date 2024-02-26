# registry service

This is a minimal web service that registers & exposes schemas, [adhering to the Confluent Schema Registry API](https://docs.confluent.io/platform/current/schema-registry/develop/api.html#subjects). It is intended to serve as a reference implementation and is _not_ production-ready.

## Development

We support building & running via OCI-compatible container images (via Bazel) or via Docker.

### Bazel

Do `bazel build //api:image`. Run on the container runtime of your choice.

### Docker

Install docker compose on your platform, then do `docker compose --env-file env.development up`.
