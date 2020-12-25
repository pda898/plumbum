from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote
from tree import create
from translator import cody
from traceback import print_exc


class Handler(BaseHTTPRequestHandler):
    def go_send(s, status, tp, data):
        s.send_response(status)
        s.send_header('Content-Type', tp)
        s.end_headers()
        s.wfile.write(data)

    def go_js(s, q):
        q = unquote(q)
        try:
            q = create(q)
            q = cody(q, 'py', 'generators/js.py')
        except BaseException:
            print_exc()
            s.go_send(400, 'text/html', '<h1>Error</h1>'.encode('utf8'))
            return
        s.go_send(200, 'text/javascript', q.encode('utf8'))

    def go_page(s):
        with open('jsserver/index.htm', 'rb') as f:
            s.go_send(200, 'text/html', f.read())

    def do_GET(s):
        p = urlparse(s.path)
        if p.path == '/':
            return s.go_page()
        if p.path == '/js':
            return s.go_js(p.query)
        print(p)
        q = unquote(p.query)
        print(q)


def run():
    print('Starting at localhost:8998...')
    try:
        HTTPServer(('0.0.0.0', 8998), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
    print('Stopped!')
