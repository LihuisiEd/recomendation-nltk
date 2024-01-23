FROM python:3.11-slim AS base
WORKDIR /usr/local/app
RUN pip install "dask[dataframe]" --upgrade
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py", "0.0.0.0:80"]