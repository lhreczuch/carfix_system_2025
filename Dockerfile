FROM python:3

ENV PYTHONUNBUFFERED=1
WORKDIR /car_fix_control_system

COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt
COPY . .