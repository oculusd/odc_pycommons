# OculusD Client Libraries - Common Libraries

These libraries are supporting libraries for other OculusD.com Inc projects.

More details and documentation will follow in the near future. 

This is an initial development effort in very early stages (Alpha) and no 
guarantees are made in terms of production readiness at this stage.

## Installation

### Installation from Source

As with most other GitHub projects, the basic steps of clone, build and install 
should be followed. Below is a very simple example:

```bash
$ git clone https://github.com/oculusd/odc_pycommons.git
$ cd odc_pycommons
$ python3 setup.py sdist
$ pip3 install dist/odc_pycommons-0.0.1.tar.gz
```

## Debugging

You can enable debugging be setting the environment variable `DEBUG` to anything 
else than `'0'`. On Linux, you can accomplish this by running the following at 
the command prompt: `$ export DEBUG=1`.

Below is a simple example of the output that will now be printed to `STDOU`:

```python
>>> from odc_pycommons.models import CommsRequest, CommsRestFulRequest, CommsResponse
* debug enabled
>>> from odc_pycommons.comms import get
>>> req = CommsRequest(uri='https://www.york.ac.uk/teaching/cws/wws/webpage1.html')
>>> resp = get(request=req)
* debugging GET request
send: b'GET /teaching/cws/wws/webpage1.html HTTP/1.1\r\nAccept-Encoding: identity\r\nHost: www.york.ac.uk\r\nUser-Agent: Python-urllib/3.7\r\nConnection: close\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Date header: Server header: Accept-Ranges header: Cache-Control header: Expires header: Vary header: X-Frame-Options header: Content-Length header: Connection header: Content-Type 
>>> resp.response_code
200
```

## Third Party Dependencies

The following third party libraries are used in this project:

* [email-validator](https://github.com/JoshData/python-email-validator) 

Please refer to the various third party suppliers home pages for specific 
licensing information.
