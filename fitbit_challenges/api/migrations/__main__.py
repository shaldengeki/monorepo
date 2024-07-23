import shutil

from flask_migrate import upgrade

from fitbit_challenges.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/fitbit_challenges/api/migrations/binary.runfiles/_main/fitbit_challenges/api/migrations/alembic.ini",
        "/fitbit_challenges/api/migrations/alembic.ini",
    )

    with app.app_context():
        upgrade(directory="/fitbit_challenges/api/migrations")
