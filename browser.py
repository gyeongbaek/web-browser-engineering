import socket
import ssl
import tkinter

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 12, 18
SCROLL_STEP = 100


class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]  # 조건이 True이면 코드 진행

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        # host에 연결 -> 소켓을 통해 다른 컴퓨터와 통신
        s = socket.socket(
            family=socket.AF_INET,  # IPv4
            type=socket.SOCK_STREAM,  # TCP 연결 방식(연속 데이터 스트림)
            proto=socket.IPPROTO_TCP,  # TCP 프로토콜
        )
        s.connect((self.host, self.port))  # 튜플로 인자 전달

        if self.scheme == 'https':
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

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


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.scroll = 0

        # Tk는 키가 눌렸을 때 함수가 호출되는 바인딩 제공
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)

    def scrollup(self, e):
        if self.scroll - SCROLL_STEP < 0:
            return
        self.scroll -= SCROLL_STEP
        self.draw()

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def draw(self):
        self.canvas.delete('all')
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y+VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()


def show(body):
    in_tag = False
    for c in body:
        if c == '<':
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")


def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == '<':
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text


def layout(text):
    display_list = []  # 화면에 그려야 할 요소 집합
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP

        if cursor_x > WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
