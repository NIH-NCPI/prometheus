# https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder
#FROM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

#ENTRYPOINT ['python3']
CMD ["python3", "app.py"]

FROM builder as dev-envs

RUN  apk update && \
    apk add bash && \
    apk add git

RUN addgroup -S docker && \
    adduser -S --shell /bin/bash --ingroup docker vscode

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
