import shutil
import sys

from flask_migrate import downgrade, revision, upgrade

from ark_nova_stats.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/ark_nova_stats/api/migrations/binary.runfiles/_main/ark_nova_stats/api/migrations/alembic.ini",
        "/ark_nova_stats/api/migrations/alembic.ini",
    )

    command = sys.argv[1]

    with app.app_context():
        if command == "downgrade":
            downgrade(directory="/ark_nova_stats/api/migrations")
        if command == "upgrade":
            upgrade(directory="/ark_nova_stats/api/migrations")
        elif command == "new":
            revision(directory=sys.argv[2], message=sys.argv[3])
        else:
            raise ValueError(
                f"Unrecognized command passed to migrations binary: {command}"
            )
