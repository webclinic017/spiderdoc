FROM python:latest
LABEL Name=spiderdoc Version=0.0.1
WORKDIR /
RUN mkdir /outfile
# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /position
RUN mkdir /total
# Run the application:
COPY SMA.py .
ENTRYPOINT ["python","./SMA.py"]
