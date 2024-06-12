FROM ghcr.io/prefix-dev/pixi:latest

RUN pixi install

WORKDIR /app
COPY . /app

EXPOSE 5000
CMD ["pixi", "run", "serve"]
