import shutil
import sys

from flask_migrate import downgrade, revision, upgrade

from mc_manager.api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/mc_manager/api/migrations/binary.runfiles/_main/mc_manager/api/migrations/alembic.ini",
        "/mc_manager/api/migrations/alembic.ini",
    )

    command = sys.argv[1]

    with app.app_context():
        if command == "downgrade":
            downgrade(directory="/mc_manager/api/migrations")
        if command == "upgrade":
            upgrade(directory="/mc_manager/api/migrations")
        elif command == "new":
            revision(directory=sys.argv[2], message=sys.argv[3])
        else:
            raise ValueError(
                f"Unrecognized command passed to migrations binary: {command}"
            )
