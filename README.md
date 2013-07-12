Long-poll-Fanout
================

A proxy server that broadcasts the responses of long-polling requests to multiple clients. Given a sequence of request urls this server will poll those urls (at most one request per url at a time) and send the responses to the client down a persistent connection. When a response is recieved from a given url, that response is copied and sent to all clients requesting that url.

Usage
-----

python fanout\_proxy.py --auth\_server=http://example.com/auth

curl 'http://localhost:5000/bin/http://www.example.com/a,http://www.example.com/b'

Authorizaiton
-------------

Before a client is sent any data, a POST request is made to the auth\_server url you specified. It's sent the comma-separated list of urls that the user provided as postdata. If this endpoint returns a 200 response, the request is allowed to continue. Otherwise, the response from the auth server is passed on to the client and the request is terminated.

Response Formats
---------------

You can specify the response format you want in the first element of the url path.

There are two response formats:

* sse: Server-Sent Events. This response format is compatible with the EventSource api available in most browsers. The event types are the urls you requested, and the data is the request body.

* bin: A simple binary format that is more efficient and better suited to native clients. Responses in this format are sequences of messages in the form
    <request url>\n<big-endian uint32_t length field><length bytes of data>

Dependencies
------------

Python 2.7

Tornado
