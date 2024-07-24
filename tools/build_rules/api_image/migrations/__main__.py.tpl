import shutil

from flask_migrate import upgrade

from {app_package} import app

if __name__ == "__main__":
    # Copy the alembic.ini.
    shutil.copyfile(
        "/{api_package_path}/migrations/binary.runfiles/_main/{api_package_path}/migrations/alembic.ini",
        "/{api_package_path}/migrations/alembic.ini",
    )

    with app.app_context():
        upgrade(directory="/{api_package_path}/migrations")
