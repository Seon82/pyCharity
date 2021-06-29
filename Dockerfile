FROM python:3.8.8

WORKDIR /pycharity

RUN pip install poetry==1.1.6
COPY poetry.lock pyproject.toml /pycharity/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-dev

COPY ./src /pycharity/src

CMD python -u /pycharity/src/main.py