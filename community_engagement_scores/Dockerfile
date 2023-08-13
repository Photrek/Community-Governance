FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./app /project/app
COPY ./pkg /project/pkg
COPY ./server/entrypoint.sh /project/app
COPY ./server/nginx.conf /project

RUN apt update \
&& apt upgrade -y \
&& apt install -y gcc nginx \
&& pip install --upgrade pip \
&& pip install -r /project/app/requirements.txt \
&& pip install /project/pkg \
&& pip cache purge \
&& apt purge -y gcc \
&& apt -y autoremove \
&& apt -y clean \
&& ln -sf /dev/stdout /var/log/nginx/access.log \
&& ln -sf /dev/stderr /var/log/nginx/error.log \
&& chmod +x /project/app/entrypoint.sh \
&& mv /project/nginx.conf /etc/nginx/nginx.conf

WORKDIR /project/app
CMD ["./entrypoint.sh"]
