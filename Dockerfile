FROM daocloud.io/library/python:3.5-alpine
LABEL maintainer="Jarvis-Wong"

COPY server/ /www/

WORKDIR /www

RUN pip3 install -r requirements.txt

CMD ["python3", "run.py"]