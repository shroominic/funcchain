# AUTO DEV SETUP

echo "SETUP: install poetry (package manager)"
curl -sSL https://install.python-poetry.org | python3 -

echo "SETUP: install dependencies"
poetry install

echo "SETUP: install pre-commit hooks"
poetry run pre-commit install
