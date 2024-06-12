FROM ghcr.io/prefix-dev/pixi:latest

WORKDIR /app
COPY . /app

RUN pixi install



EXPOSE 5000
CMD ["pixi", "run", "server"]
