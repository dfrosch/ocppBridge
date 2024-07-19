#openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -days 365 -out server.crt

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt -config openssl.cnf

