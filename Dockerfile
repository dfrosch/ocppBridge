FROM ubuntu:24.04
COPY dist/Central.x /app/Central.x
WORKDIR /app
ENTRYPOINT ["./Central.x"]
