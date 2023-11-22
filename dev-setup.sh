# AUTO DEV SETUP

# check if rye is installed
if ! command -v rye &> /dev/null
then
    echo "rye could not be found: installing now ..."
    curl -sSf https://rye-up.com/get | bash
    echo "Check the rye docs for more info: https://rye-up.com/"
fi

echo "SYNC: setup .venv"
rye sync

echo "SETUP: install pre-commit hooks"
rye run pre-commit install

echo "TEST: run pytests"
rye run pytest
