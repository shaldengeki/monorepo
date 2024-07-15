import shutil

from flask_migrate import upgrade
from python.runfiles import Runfiles

from ark_nova_stats.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    r = Runfiles.Create()
    alembic_ini_src = r.Rlocation("_main/ark_nova_stats/api/migrations/alembic.ini")
    shutil.copyfile(alembic_ini_src, "/ark_nova_stats/api/migrations/alembic.ini")

    with app.app_context():
        upgrade(directory="/ark_nova_stats/api/migrations")
