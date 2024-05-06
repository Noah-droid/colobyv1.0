FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
