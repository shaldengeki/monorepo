import shutil

from flask_migrate import upgrade
from python.runfiles import Runfiles

from mc_manager.api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    r = Runfiles.Create()
    alembic_ini_src = r.Rlocation("_main/mc_manager/api/migrations/alembic.ini")
    shutil.copyfile(alembic_ini_src, "/mc_manager/api/migrations/alembic.ini")

    with app.app_context():
        upgrade(directory="/mc_manager/api/migrations")
