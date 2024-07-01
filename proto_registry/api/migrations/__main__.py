import shutil

from flask_migrate import upgrade
from python.runfiles import Runfiles

from proto_registry.api.config import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    r = Runfiles.Create()
    alembic_ini_src = r.Rlocation("_main/proto_registry/api/migrations/alembic.ini")
    shutil.copyfile(alembic_ini_src, "/proto_registry/api/migrations/alembic.ini")

    with app.app_context():
        upgrade(directory="/proto_registry/api/migrations")
