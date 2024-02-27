from src.python.fitbit_challenges.api.app import app
from src.python.fitbit_challenges.scripts.wait_for_postgres import wait_for_postgres

if __name__ == "__main__":
    wait_for_postgres()
    app.run()
