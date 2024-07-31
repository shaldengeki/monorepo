import time

from skeleton.config import app, db

max_delay = 10


def main() -> int:
    with app.app_context():
        while True:
            start = time.time()
            # Do work here.
            delay = (start + max_delay) - time.time()
            if delay > 0:
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
