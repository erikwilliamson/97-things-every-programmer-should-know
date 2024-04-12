FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONPATH=/app/src

COPY requirements requirements
COPY ./pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade -r requirements/development.txt

COPY src /app
COPY data /app/data
WORKDIR /app

# start the server
CMD ["uvicorn", "ninety_seven_things.main:app", "--host", "0.0.0.0", "--port", "5555"]
