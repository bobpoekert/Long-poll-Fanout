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

* bin: A simple binary format that is more efficient and better suited to native clients. Responses in this format are sequences of messages in the form `<request url>\n<big-endian uint32_t length field><length bytes of data>`

Dependencies
------------

Python 2.7

Tornado

TODO
-----

* Honor Cache-Control and Expires headers (changing the polling interval)
* Allow upstream servers to use postbacks instead of polling
* 

License
-------

The MIT License (MIT)

Copyright (c) <year> <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


