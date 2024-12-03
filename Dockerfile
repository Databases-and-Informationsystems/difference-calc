# Basisimage
FROM python:3.12-alpine

RUN apk add git
WORKDIR /app

ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD . /app

EXPOSE 8443

CMD ["flask", "run", "--host=0.0.0.0", "--port=8443"]

