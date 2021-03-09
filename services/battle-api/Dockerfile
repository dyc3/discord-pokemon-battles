FROM golang:1.16-alpine
WORKDIR /app
ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64
RUN apk add --no-cache git
RUN git clone https://github.com/StevensSEC/pokemonbattlelib .
EXPOSE 4000
RUN go build
CMD ["go", "run", "./http"]
