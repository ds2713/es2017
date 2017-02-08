import socket

# Function to obtain response via HTML.
def http_get(url, port):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes("GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, host), "utf8"))
    fullresponse = []
    while True:
        data = s.recv(100)
        if data:
            fullresponse.append(str(data, "utf8"))
        else:
            break
    s.close()
    return fullresponse

def main():
    response = http_get("http://192.168.1.118/", 8080)
    response_string = str(response).split("START")[-1].split("END")[0]
    time_list = response_string.split(",")
    time_list_int = [int(s) for s in time_list]


if __name__ == '__main__':
    main()
