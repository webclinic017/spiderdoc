FROM python:latest
LABEL Name=spiderdoc Version=0.0.1
WORKDIR /
# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
# Run the application:
COPY SMA.py /
ENTRYPOINT ["python","./SMA.py"]
