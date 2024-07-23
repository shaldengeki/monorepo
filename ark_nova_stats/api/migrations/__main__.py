import shutil

from flask_migrate import upgrade

from ark_nova_stats.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/ark_nova_stats/api/migrations/binary.runfiles/_main/ark_nova_stats/api/migrations/alembic.ini",
        "/ark_nova_stats/api/migrations/alembic.ini",
    )

    with app.app_context():
        upgrade(directory="/ark_nova_stats/api/migrations")
