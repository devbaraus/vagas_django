FROM python:3.10-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev icu-data-full py3-setuptools cmake \
    && apk add tiff-dev jpeg-dev openjpeg-dev zlib-dev freetype-dev lcms2-dev \
    libwebp-dev tcl-dev tk-dev harfbuzz-dev fribidi-dev libimagequant-dev \
    libxcb-dev libpng-dev

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./src .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0"]