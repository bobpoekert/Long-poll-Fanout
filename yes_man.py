import tornado.web as web
from tornado.ioloop import IOLoop

class YesHandler(web.RequestHandler):

    def post(self):
        self.finish('ok')

app = web.Application([
    ('/', YesHandler)
])

if __name__ == '__main__':
    app.listen(8000)
    IOLoop.instance().start()
