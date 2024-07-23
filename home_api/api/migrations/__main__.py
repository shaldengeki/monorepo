import shutil

from flask_migrate import upgrade

from home_api.api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/home_api/api/migrations/binary.runfiles/_main/home_api/api/migrations/alembic.ini",
        "/home_api/api/migrations/alembic.ini",
    )

    with app.app_context():
        upgrade(directory="/home_api/api/migrations")
