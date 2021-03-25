FROM golang:1.16-alpine
ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64
COPY pokemonbattlelib /app
WORKDIR /app
EXPOSE 4000
CMD ["go", "run", "./http"]
