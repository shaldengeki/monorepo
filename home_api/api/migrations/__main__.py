import shutil

from flask_migrate import upgrade
from python.runfiles import Runfiles

from home_api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    r = Runfiles.Create()
    alembic_ini_src = r.Rlocation("_main/home_api/api/migrations/alembic.ini")
    shutil.copyfile(alembic_ini_src, "/home_api/api/migrations/alembic.ini")

    with app.app_context():
        upgrade(directory="/home_api/api/migrations")
