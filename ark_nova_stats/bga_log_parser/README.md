# bga_log_parser

A Python library to parse Ark Nova gameplay logs in BGA format.

First, download the gameplay logs in JSON format somewhere on your computer. Then:

```python
import json
from ark_nova_stats.bga_log_parser.game_log import GameLog

with open('path/to/my/replay.json', 'r') as f:
    log = GameLog(**json.loads(f.read().strip()))

print(log.winner)
```
