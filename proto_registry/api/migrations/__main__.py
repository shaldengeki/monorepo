import shutil
import sys

from flask_migrate import downgrade, revision, upgrade

from proto_registry.api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/proto_registry/api/migrations/binary.runfiles/_main/proto_registry/api/migrations/alembic.ini",
        "/proto_registry/api/migrations/alembic.ini",
    )

    command = sys.argv[1]

    with app.app_context():
        if command == "downgrade":
            downgrade(directory="/proto_registry/api/migrations")
        if command == "upgrade":
            upgrade(directory="/proto_registry/api/migrations")
        elif command == "new":
            revision(directory=sys.argv[2], message=sys.argv[3])
        else:
            raise ValueError(
                f"Unrecognized command passed to migrations binary: {command}"
            )
