FROM python:3.7-slim AS compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc wget

# Make sure we use the virtualenv:
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install numpy

# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/opt/venv && \
  make && \
  make install

RUN pip install --global-option=build_ext --global-option="-L/opt/venv/lib" TA-Lib==0.4.16
RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.7-slim AS build-image
ENV TZ="America/New_York"
COPY --from=compile-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
ENV LD_LIBRARY_PATH="/opt/venv/lib"
COPY ./input/* /input/
# Run the application:
COPY ./trader.py /
ENTRYPOINT ["python","/trader.py"]
