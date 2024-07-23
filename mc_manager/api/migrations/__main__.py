import shutil

from flask_migrate import upgrade

from mc_manager.api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/mc_manager/api/migrations/binary.runfiles/_main/mc_manager/api/migrations/alembic.ini",
        "/mc_manager/api/migrations/alembic.ini",
    )

    with app.app_context():
        upgrade(directory="/mc_manager/api/migrations")
