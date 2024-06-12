FROM ghcr.io/prefix-dev/pixi:latest

WORKDIR /app
COPY . /app

RUN pixi install



CMD ["pixi", "run", "server"]
