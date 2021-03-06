import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

'''
1. python hello.py --port=8001
2. curl http://localhost:8001/
   curl http://localhost:8001/?greeting=Salutations
'''
from tornado.options import define, options
define("port", default=8001, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        greeting = self.get_argument('greeting', 'Hello')
        self.write(greeting + ', friendly user!')

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()