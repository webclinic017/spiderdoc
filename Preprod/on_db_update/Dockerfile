FROM python:latest
LABEL Name=odu Version=1.0.0
WORKDIR /
# Install dependencies:
COPY ./requierment.txt /
RUN pip install -r requierment.txt
COPY ./symbols.txt .
# Run the application:
COPY ./on_db_updt.py /
ENTRYPOINT ["python","/on_db_updt.py"]
