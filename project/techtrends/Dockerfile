FROM python:3.13
LABEL maintainer="Alexander Placidi"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt && python init_db.py

EXPOSE 6111

CMD [ "python", "app.py" ]