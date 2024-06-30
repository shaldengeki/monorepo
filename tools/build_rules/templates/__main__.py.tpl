from python.runfiles import Runfiles
import os
import subprocess

from {app_package} import app

if __name__ == "__main__":
    # First, run wait-for-postgres.
    r = Runfiles.Create()
    env = os.environ
    env.update(r.EnvVars())
    p = subprocess.run(
        [r.Rlocation("scripts/wait_for_postgres")],
        env = env,
    )

    # Then run the app.
    app.run(host="0.0.0.0")
