import shutil

from src.python.fitbit_challenges.config import app
from flask_migrate import upgrade

from python.runfiles import Runfiles

if __name__ == '__main__':
    # Copy the alembic.ini.
    r = Runfiles.Create()
    alembic_ini_src = r.Rlocation("_main/src/python/fitbit_challenges/api/migrations/alembic.ini")
    shutil.copyfile(alembic_ini_src, "/src/python/fitbit_challenges/api/migrations/alembic.ini")

    with app.app_context():
        upgrade(directory='/src/python/fitbit_challenges/api/migrations')