FROM python:3.12

WORKDIR /app

RUN apt-get update \
 && apt-get install -y \
    git \
    sqlite3 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --with dev

COPY . .