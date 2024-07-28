import shutil
import sys

from flask_migrate import downgrade, revision, upgrade

from fitbit_challenges.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/fitbit_challenges/api/migrations/binary.runfiles/_main/fitbit_challenges/api/migrations/alembic.ini",
        "/fitbit_challenges/api/migrations/alembic.ini",
    )

    command = sys.argv[1]

    with app.app_context():
        if command == "downgrade":
            downgrade(directory="/fitbit_challenges/api/migrations")
        if command == "upgrade":
            upgrade(directory="/fitbit_challenges/api/migrations")
        elif command == "new":
            revision(directory=sys.argv[2], message=sys.argv[3])
        else:
            raise ValueError(
                f"Unrecognized command passed to migrations binary: {command}"
            )
