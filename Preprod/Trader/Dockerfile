FROM python:latest
LABEL Name=trader Version=1.0.0
WORKDIR /
# Install dependencies:
COPY ./requierment.txt /
RUN pip install -r requierment.txt
COPY ./symbols.txt .
# Run the application:
COPY ./trader.py /
ENTRYPOINT ["python","/trader.py"]
