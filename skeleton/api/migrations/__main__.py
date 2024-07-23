import shutil

from flask_migrate import upgrade

from skeleton.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/skeleton/api/migrations/binary.runfiles/_main/skeleton/api/migrations/alembic.ini",
        "/skeleton/api/migrations/alembic.ini",
    )

    with app.app_context():
        upgrade(directory="/skeleton/api/migrations")
