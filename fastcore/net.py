# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03b_net.ipynb (unless otherwise specified).

__all__ = ['url_default_headers', 'urlquote', 'urlwrap', 'ExceptionsHTTP', 'HTTP4xxClientError', 'HTTP5xxServerError',
           'HTTP400BadRequestError', 'HTTP401UnauthorizedError', 'HTTP402PaymentRequiredError', 'HTTP403ForbiddenError',
           'HTTP404NotFoundError', 'HTTP405MethodNotAllowedError', 'HTTP406NotAcceptableError',
           'HTTP407ProxyAuthRequiredError', 'HTTP408RequestTimeoutError', 'HTTP409ConflictError', 'HTTP410GoneError',
           'HTTP411LengthRequiredError', 'HTTP412PreconditionFailedError', 'HTTP413PayloadTooLargeError',
           'HTTP414URITooLongError', 'HTTP415UnsupportedMediaTypeError', 'HTTP416RangeNotSatisfiableError',
           'HTTP417ExpectationFailedError', 'HTTP418AmAteapotError', 'HTTP421MisdirectedRequestError',
           'HTTP422UnprocessableEntityError', 'HTTP423LockedError', 'HTTP424FailedDependencyError',
           'HTTP425TooEarlyError', 'HTTP426UpgradeRequiredError', 'HTTP428PreconditionRequiredError',
           'HTTP429TooManyRequestsError', 'HTTP431HeaderFieldsTooLargeError', 'HTTP451LegalReasonsError', 'urlopen',
           'urlread', 'urljson', 'urlcheck', 'urlclean', 'urlretrieve', 'urldest', 'urlsave', 'urlvalid', 'urlrequest',
           'urlsend', 'do_request', 'start_server', 'start_client']

# Cell
from .imports import *
from .foundation import *
from .basics import *
from .xtras import *
from .parallel import *
from functools import wraps

import json,urllib,contextlib
import socket,urllib.request,http,urllib
from contextlib import contextmanager,ExitStack
from urllib.request import Request,urlretrieve,install_opener
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode,urlparse,urlunparse
from http.client import InvalidURL

# Cell
url_default_headers = {
    "Accept":
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

# Cell
def urlquote(url):
    "Update url's path with `urllib.parse.quote`"
    subdelims = "!$&'()*+,;="
    gendelims = ":?#[]@"
    safe = subdelims+gendelims+"%/"
    p = list(urlparse(url))
    p[2] = urllib.parse.quote(p[2], safe=safe)
    for i in range(3,6): p[i] = urllib.parse.quote(p[i], safe=safe)
    return urlunparse(p)

# Cell
def urlwrap(url, data=None, headers=None):
    "Wrap `url` in a urllib `Request` with `urlquote`"
    return url if isinstance(url,Request) else Request(urlquote(url), data=data, headers=headers or {})

# Cell
ExceptionsHTTP = {}

# Cell
class HTTP4xxClientError(HTTPError):
    "Base class for client exceptions (code 4xx) from `url*` functions"
    pass

# Cell
class HTTP5xxServerError(HTTPError):
    "Base class for server exceptions (code 5xx) from `url*` functions"
    pass

# Cell
_opener = urllib.request.build_opener()
_opener.addheaders = list(url_default_headers.items())
install_opener(_opener)

_httperrors = (
    (400,'Bad Request'),(401,'Unauthorized'),(402,'Payment Required'),(403,'Forbidden'),(404,'Not Found'),
    (405,'Method Not Allowed'),(406,'Not Acceptable'),(407,'Proxy Auth Required'),(408,'Request Timeout'),
    (409,'Conflict'),(410,'Gone'),(411,'Length Required'),(412,'Precondition Failed'),(413,'Payload Too Large'),
    (414,'URI Too Long'),(415,'Unsupported Media Type'),(416,'Range Not Satisfiable'),(417,'Expectation Failed'),
    (418,'Am A teapot'),(421,'Misdirected Request'),(422,'Unprocessable Entity'),(423,'Locked'),(424,'Failed Dependency'),
    (425,'Too Early'),(426,'Upgrade Required'),(428,'Precondition Required'),(429,'Too Many Requests'),
    (431,'Header Fields Too Large'),(451,'Legal Reasons')
)

for code,msg in _httperrors:
    nm = f'HTTP{code}{msg.replace(" ","")}Error'
    cls = get_class(nm, 'url', 'hdrs', 'fp', sup=HTTP4xxClientError, msg=msg, code=code)
    globals()[nm] = ExceptionsHTTP[code] = cls

# Cell
#nbdev_comment _all_ = ['HTTP400BadRequestError', 'HTTP401UnauthorizedError', 'HTTP402PaymentRequiredError', 'HTTP403ForbiddenError', 'HTTP404NotFoundError', 'HTTP405MethodNotAllowedError', 'HTTP406NotAcceptableError', 'HTTP407ProxyAuthRequiredError', 'HTTP408RequestTimeoutError', 'HTTP409ConflictError', 'HTTP410GoneError', 'HTTP411LengthRequiredError', 'HTTP412PreconditionFailedError', 'HTTP413PayloadTooLargeError', 'HTTP414URITooLongError', 'HTTP415UnsupportedMediaTypeError', 'HTTP416RangeNotSatisfiableError', 'HTTP417ExpectationFailedError', 'HTTP418AmAteapotError', 'HTTP421MisdirectedRequestError', 'HTTP422UnprocessableEntityError', 'HTTP423LockedError', 'HTTP424FailedDependencyError', 'HTTP425TooEarlyError', 'HTTP426UpgradeRequiredError', 'HTTP428PreconditionRequiredError', 'HTTP429TooManyRequestsError', 'HTTP431HeaderFieldsTooLargeError', 'HTTP451LegalReasonsError']

# Cell
def urlopen(url, data=None, headers=None, **kwargs):
    "Like `urllib.request.urlopen`, but first `urlwrap` the `url`, and encode `data`"
    if kwargs and not data: data=kwargs
    if data is not None:
        if not isinstance(data, (str,bytes)): data = urlencode(data)
        if not isinstance(data, bytes): data = data.encode('ascii')
    return _opener.open(urlwrap(url, data=data, headers=headers))

# Cell
def urlread(url, data=None, headers=None, decode=True, return_json=False, return_headers=False, **kwargs):
    "Retrieve `url`, using `data` dict or `kwargs` to `POST` if present"
    try:
        with urlopen(url, data=data, headers=headers, **kwargs) as u: res,hdrs = u.read(),u.headers
    except HTTPError as e:
        if 400 <= e.code < 500: raise ExceptionsHTTP[e.code](e.url, e.hdrs, e.fp) from None
        else: raise

    if decode: res = res.decode()
    if return_json: res = loads(res)
    return (res,dict(hdrs)) if return_headers else res

# Cell
def urljson(url, data=None):
    "Retrieve `url` and decode json"
    res = urlread(url, data=data)
    return json.loads(res) if res else {}

# Cell
def urlcheck(url, timeout=10):
    if not url: return True
    try:
        with urlopen(url, timeout=timeout) as u: return u.status<400
    except URLError: return False
    except socket.timeout: return False
    except InvalidURL: return False

# Cell
def urlclean(url):
    "Remove fragment, params, and querystring from `url` if present"
    return urlunparse(urlparse(str(url))[:3]+('','',''))

# Cell
def urlretrieve(url, filename=None, reporthook=None, data=None):
    "Same as `urllib.request.urlretrieve` but also works with `Request` objects"
    with contextlib.closing(urlopen(url, data)) as fp:
        headers = fp.info()
        if filename: tfp = open(filename, 'wb')
        else:
            tfp = tempfile.NamedTemporaryFile(delete=False)
            filename = tfp.name

        with tfp:
            bs,size,read,blocknum = 1024*8,-1,0,0
            if "content-length" in headers: size = int(headers["Content-Length"])
            if reporthook: reporthook(blocknum, bs, size)
            while True:
                block = fp.read(bs)
                if not block: break
                read += len(block)
                tfp.write(block)
                blocknum += 1
                if reporthook: reporthook(blocknum, bs, size)

    if size >= 0 and read < size:
        raise ContentTooShortError(f"retrieval incomplete: got only {read} out of {size} bytes", headers)
    return filename,headers

# Cell
def urldest(url, dest=None):
    name = urlclean(Path(url).name)
    if dest is None: dest = name
    dest = Path(dest)
    return dest/name if dest.is_dir() else dest

# Cell
def urlsave(url, dest=None, reporthook=None):
    "Retrieve `url` and save based on its name"
    dest = urldest(url, dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    nm,msg = urlretrieve(url, dest, reporthook)
    return nm

# Cell
def urlvalid(x):
    "Test if `x` is a valid URL"
    return all (getattrs(urlparse(str(x)), 'scheme', 'netloc'))

# Cell
def urlrequest(url, verb, headers=None, route=None, query=None, data=None, json_data=True):
    "`Request` for `url` with optional route params replaced by `route`, plus `query` string, and post `data`"
    if route: url = url.format(**route)
    if query: url += '?' + urlencode(query)
    if isinstance(data,dict): data = (json.dumps if json_data else urlencode)(data).encode('ascii')
    return Request(url, headers=headers or {}, data=data or None, method=verb.upper())

# Cell
@patch
def summary(self:Request, skip=None)->dict:
    "Summary containing full_url, headers, method, and data, removing `skip` from headers"
    res = L('full_url','method','data').map_dict(partial(getattr,self))
    res['headers'] = {k:v for k,v in self.headers.items() if k not in listify(skip)}
    return res

# Cell
def urlsend(url, verb, headers=None, route=None, query=None, data=None, json_data=True,
            return_json=True, return_headers=False, debug=None):
    "Send request with `urlrequest`, converting result to json if `return_json`"
    req = urlrequest(url, verb, headers, route=route, query=query, data=data, json_data=json_data)
    if debug: debug(req)

    if route and route.get('archive_format', None):
        return urlread(req, decode=False, return_json=False, return_headers=return_headers)

    return urlread(req, return_json=return_json, return_headers=return_headers)

# Cell
def do_request(url, post=False, headers=None, **data):
    "Call GET or json-encoded POST on `url`, depending on `post`"
    if data:
        if post: data = json.dumps(data).encode('ascii')
        else:
            url += "?" + urlencode(data)
            data = None
    return urljson(Request(url, headers=headers, data=data or None))

# Cell
def _socket_det(port,host,dgram):
    if isinstance(port,int): family,addr = socket.AF_INET,(host or socket.gethostname(),port)
    else: family,addr = socket.AF_UNIX,port
    return family,addr,(socket.SOCK_STREAM,socket.SOCK_DGRAM)[dgram]

# Cell
def start_server(port, host=None, dgram=False, reuse_addr=True, n_queue=None):
    "Create a `socket` server on `port`, with optional `host`, of type `dgram`"
    listen_args = [n_queue] if n_queue else []
    family,addr,typ = _socket_det(port,host,dgram)
    if family==socket.AF_UNIX:
        if os.path.exists(addr): os.unlink(addr)
        assert not os.path.exists(addr), f"{addr} in use"
    s = socket.socket(family, typ)
    if reuse_addr and family==socket.AF_INET: s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(*listen_args)
    return s

# Cell
def start_client(port, host=None, dgram=False):
    "Create a `socket` client on `port`, with optional `host`, of type `dgram`"
    family,addr,typ = _socket_det(port,host,dgram)
    s = socket.socket(family, typ)
    s.connect(addr)
    return s