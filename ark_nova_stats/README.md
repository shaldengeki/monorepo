# ark_nova_stats

A collection of tools and services for analyzing Ark Nova games.

See the README.md in individual directories.

## API

This is a webapp designed to store Ark Nova replays, in BGA format.

To run, do:
```bash
docker compose -f docker-compose.yaml -f docker-compose.override.yaml up
```

To deploy to production:

```bash
cd api
fly deploy
```

## bga_log_parser

A Python library used to parse Ark Nova gameplay logs in BGA format.

## emu_cup

A set of scripts I'm using to analyze replays from the Emu Cup, an Ark Nova tournament between high-ranked players on BGA.
