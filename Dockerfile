FROM python:latest
LABEL Name=spiderdoc Version=0.0.1
WORKDIR /
RUN mkdir /outfile
# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /outfile/position
RUN mkdir /outfile/total
# Run the application:
COPY SMA.py .
COPY /outfile .
ENTRYPOINT ["python","./SMA.py"]
