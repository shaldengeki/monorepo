import shutil

from flask_migrate import upgrade
from python.runfiles import Runfiles

from fitbit_challenges.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    r = Runfiles.Create()
    alembic_ini_src = r.Rlocation("_main/fitbit_challenges/api/migrations/alembic.ini")
    shutil.copyfile(alembic_ini_src, "/fitbit_challenges/api/migrations/alembic.ini")

    with app.app_context():
        upgrade(directory="/fitbit_challenges/api/migrations")
