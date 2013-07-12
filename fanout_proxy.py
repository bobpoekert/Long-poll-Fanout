import tornado.web as web
import tornado.httpclient as http
from tornado.options import define, options
import weakref, re, struct
from functools import partial
import cStringIO as StringIO

define('auth_url',
    help='An endpoint that takes post requests with comma-separated lists of urls and returns either 200 indicating the client is allowed to access those urls or 403 otherwise')
define('port', default='5000')

def make_sse_response_blob(url, repsonse):
    res = StringIO()
    res.write('event: %s\n' % url)
    lines = re.split(r'[\r\n]+', response.body)
    for line in lines:
        res.write('data: %s\n' % line)
    res.write('\r\n')
    return res.getvalue()

def make_binary_response_blob(url, response):
    res = StringIO()
    res.write(url)
    res.write('\n')
    res.write(struct.pack('>I', len(response.body)))
    res.write(response.body)
    return res.getvalue()

serializers = {
    'sse':make_sse_response_blob,
    'bin':make_binary_response_blob}

class ReferenceCounter(object):

    def __init__(self):
        self.mapping = {}

    def add(self, item):
        try:
            self.mapping[item] += 1
        except KeyError:
            self.mapping[item] = 1

    def remove(self, item):
        try:
            self.mapping[item] -= 1
            if self.mapping[item] < 1:
                del self.mapping[item]
        except KeyError:
            pass

    def get(self, item):
        return self.mapping.get(item, 0)

    def __contains__(self, item):
        return item in self.mapping

    def values(self):
        return self.mapping.keys()

class KeyMapping(object):

    def __init__(self):
        self.keys_to_clients = {}
        self.serializer_references = ReferenceCounter()

    def add(self, key, serializer, client):
        self.serializer_references.add(serializer)
        try:
            s = self.keys_to_clients[key]
        except KeyError:
            s = set([])
            self.keys_to_clients[key] = s
            self.fetch_url(key)

        s.add(weakref.ref(client, partial(self.remove_value, key, serializer)))

    def remove_value(self, key, serializer, ref):
        self.serializer_references.remove(serializer)
        v = self.keys_to_clients[key]
        v.remove(ref)
        if not v:
            del self.keys_to_clients[v]

    def fetch_url(self, url):
        http.AsyncHTTPClient().fetch(url, partial(self.got_url, url))

    def got_url(self, url, response):
        refs = self.keys_to_clients.get(url)

        if not refs:
            return

        serial = dict((s, s(url, response)) for s in self.serializer_references.values())

        for client_ref in refs:
            client = client_ref()
            client.send_blob(url, serial[client.serializer])

        self.fetch_url(url)

key_mapping = KeyMapping()

class PersistentClientHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, serializer, urls):
        self.urls = urls
        try:
            self.serializer = serializers[serializer]
        except KeyError:
            self.send_error(400, 'Invalid serializer')
            self.finish()
            return

        headers = self.request.headers()
        headers.add('X-Real-IP', self.request.remote_ip)
        request = httpclient.HTTPRequest(
            config.auth_url,
            headers=headers)
        AsyncHTTPClient().fetch(request, self.got_auth_response)

    def got_auth_response(self, response):
        if response.code == 200:
            self.setup_connections()
        else:
            self.set_status(response.code)
            self.finish(response.body)

    def setup_connections(self):
        urls = self.urls.split(',')
        for url in urls:
            key_mapping.add(url, self.serializer, self)
        self.set_status(200)

    def send_blob(self, blob):
        self.write(blob)
        self.flush()

app = web.Application([
    ('/(.*?)/(.*)', PersistentClientHandler)
])

if __name__ == '__main__':
    import tornado.ioloop as ioloop
    options.parse_command_line()
    assert options.auth_url, 'You must specify an auth_url'
    app.listen(options.port)
    ioloop.IOLoop.instance().start()
