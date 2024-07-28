import os
import shutil
import sys

from flask_migrate import downgrade, revision, upgrade

from ark_nova_stats.config import app

if __name__ == "__main__":
    working_dir = sys.argv[1]
    os.chdir(working_dir)
    alembic_ini = sys.argv[2]
    try:
        shutil.copyfile(
            alembic_ini,
            "./alembic.ini",
        )
    except shutil.SameFileError:
        pass

    command = sys.argv[3]

    with app.app_context():
        if command == "downgrade":
            downgrade(directory=".")
        if command == "upgrade":
            upgrade(directory=".")
        elif command == "new":
            revision(directory=".", message=sys.argv[4])
        else:
            raise ValueError(
                f"Unrecognized command passed to migrations binary: {command}"
            )
