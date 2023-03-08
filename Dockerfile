FROM python:3.10-bullseye

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get install -y postgresql-server-dev-all gcc python3-dev musl-dev icu-devtools \
    && apt-get install -y libtiff-dev libjpeg-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev \
    liblcms2-dev libwebp-dev tcl-dev tk-dev libharfbuzz-dev libfribidi-dev libimagequant-dev \
    libxcb1-dev libpng-dev

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./src .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0"]
