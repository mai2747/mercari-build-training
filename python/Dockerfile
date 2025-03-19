# syntax=docker/dockerfile:1

FROM python:3.13.2-alpine

RUN apk update && apk add --no-cache gcc musl-dev

RUN addgroup -S mercari && adduser -S trainee -G mercari

WORKDIR /app

COPY requirements.txt requirements.txt


COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chown -R trainee:mercari /app

# RUN chown -R trainee:mercari db

USER trainee

# command to execute when build this container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]