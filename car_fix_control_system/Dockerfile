FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.prod.txt /app/

RUN apt-get update && apt-get install -y \
    libpq-dev gcc --no-install-recommends \
 && pip install --upgrade pip \
 && pip install -r requirements.prod.txt

COPY . /app/


EXPOSE 8000

CMD ["gunicorn", "car_fix_control_system.wsgi:application", "--bind", "0.0.0.0:8000"]
