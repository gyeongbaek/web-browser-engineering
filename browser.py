import socket


class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"  # 조건이 True이면 코드 진행

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        # host에 연결 -> 소켓을 통해 다른 컴퓨터와 통신
        s = socket.socket(
            family=socket.AF_INET,  # IPv4
            type=socket.SOCK_STREAM,  # TCP 연결 방식(연속 데이터 스트림)
            proto=socket.IPPROTO_TCP,  # TCP 프로토콜
        )
        s.connect((self.host, 80))  # 튜플로 인자 전달

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(' ', 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            body = response.read()
            s.close()
            return body


def show(body):
    in_tag = False
    for c in body:
        if c == '<':
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")


def load(url):
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
