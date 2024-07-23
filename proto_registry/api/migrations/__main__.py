import shutil

from flask_migrate import upgrade

from proto_registry.api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/proto_registry/api/migrations/binary.runfiles/_main/proto_registry/api/migrations/alembic.ini",
        "/proto_registry/api/migrations/alembic.ini",
    )

    with app.app_context():
        upgrade(directory="/proto_registry/api/migrations")
