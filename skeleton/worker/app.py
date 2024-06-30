import datetime
import time
from base64 import b64encode
from datetime import timezone
from typing import Optional
from urllib.parse import urlencode

import requests
from sqlalchemy import desc, update
from sqlalchemy.sql.functions import now

from skeleton.config import app

max_delay = 10


def main() -> int:
    with app.app_context():
        while True:
            start = time.time()
            # Do logic
            delay = (start + max_delay) - time.time()
            if delay > 0:
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
