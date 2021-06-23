FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY currency/ /currency/
COPY main.py /
CMD gunicorn -b 0.0.0.0:8000 main:app --access-logfile -

