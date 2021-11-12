FROM python:general
LABEL Name=spiderdoc Version=0.0.1
WORKDIR /home/spiderdoc/spiderdoc
COPY printAmnt.py ./
COPY venv ./
CMD ["python","printAmnt"]
