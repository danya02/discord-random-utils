FROM python:3.9

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY fetch_loop.py /
ENTRYPOINT python3 fetch_loop.py
