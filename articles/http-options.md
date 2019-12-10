 - title = 关于 HTTP OPTIONS
 - url = http_options
 - tags = 
 - datetime = 2017-06-21 23:57:53 +0800

> 本文参考了两篇文章：
>
> -  [OPTIONS - HTTP | MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS)
> - [跨域资源共享 CORS 详解 - 阮一峰的网络日志](http://www.ruanyifeng.com/blog/2016/04/cors.html)

首先 OPTIONS 方法不应该像 GET, POST, PUT 等方法一样返回内容，它返回的应该就只有Header。

OPTIONS 的功能基本上只有两个：

- 在普通访问中，它会返回同 URL 中允许访问的 METHODS
- 在跨域访问 (CORS) 中，返回对应的原站 (Origin) 能访问的METHODS


<!--more-->


## 普通访问

在普通访问时：

```bash
curl -X OPTIONS http://example.org -i
```

返回内容中，就应该包含`allow`  这个响应头来告知访问者，哪些 METHOD 是已经实现了的(可以访问的)

```http
HTTP/1.1 200 OK
Allow: OPTIONS, GET, HEAD, POST
Cache-Control: max-age=604800
Date: Thu, 13 Oct 2016 11:45:00 GMT
Expires: Thu, 20 Oct 2016 11:45:00 GMT
Server: EOS (lax004/2813)
x-ec-custom-error: 1
Content-Length: 0
```

这份响应中的 `Allow` 就包含了`OPTIONS`, `GET`, `HEAD`, `POST` 四种方法。



## CORS 

在非简单请求的情况下，先会把需要请求的方法放在`request header` 中，发送一个`OPTIONS`方法，检测目的方法是否允许访问。

```http
OPTIONS /resources/post-here/ HTTP/1.1 
Host: bar.other 
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8 
Accept-Language: en-us,en;q=0.5 
Accept-Encoding: gzip,deflate 
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7 
Connection: keep-alive 
Origin: http://foo.example 
Access-Control-Request-Method: POST 
Access-Control-Request-Headers: X-PINGOTHER, Content-Type
```

上述例子，在访问`POST http://foo.example/resources/post-here ` 之前， 先回发出一个对应的`OPTIONS` 方法。

```http
HTTP/1.1 200 OK
Date: Mon, 01 Dec 2008 01:15:39 GMT 
Server: Apache/2.0.61 (Unix) 
Access-Control-Allow-Origin: http://foo.example 
Access-Control-Allow-Methods: POST, GET, OPTIONS 
Access-Control-Allow-Headers: X-PINGOTHER, Content-Type 
Access-Control-Max-Age: 86400 
Vary: Accept-Encoding, Origin 
Content-Encoding: gzip 
Content-Length: 0 
Keep-Alive: timeout=2, max=100 
Connection: Keep-Alive 
Content-Type: text/plain
```

其响应报文中有几个参数是值得关注的

- `Access-Control-Allow-Origin` 这个字段描述了哪些网址可以调用这个API的内容。 如果是都允许，就应该返回`*` ，反之，应该直接放回对应的域名
-  `Access-Control-Allow-Methods` 允许访问的METHOD
- `Access-Control-Allow-Headers` 在访问时允许添加的头部信息
- `Access-Control-Max-Age` 用来标识这次`OPTIONS` 的信息有效时间。如果在有效期内，那么不需要再重复发送 `OPTIONS` 请求。



## 看看 Flask 是怎么处理的

```python
import flask
app = flask.Flask(__name__)

@app.route("/")
def index():
    return "hello world"

@app.route("/", methods=["GET", "POST"])
def allow_post_method():
    return "post is allowed here"
```

访问`OPTIONS /` 

```http
HTTP/1.1 200 OK
Allow: OPTIONS, GET, HEAD
Content-Length: 0
Content-Type: text/html; charset=utf-8
Date: Wed, 21 Jun 2017 15:14:58 GMT
Server: Werkzeug/0.12.2 Python/3.6.1
```

访问`OPTIONS /all_post_method`

```http
HTTP/1.1 200 OK
Allow: POST, GET, OPTIONS, HEAD
Content-Length: 0
Content-Type: text/html; charset=utf-8
Date: Wed, 21 Jun 2017 15:38:35 GMT
Server: Werkzeug/0.12.2 Python/3.6.1
```



也就是说，一般的框架都会自动帮你实现 `HEAD` 和 `OPTIONS`  方法。



## Nougat 该怎么办

现在Nougat 是需要自己定义`HEAD` 和 `OPTIONS` 方法的。那么说来，这两个方法需要自动实现。

那么对于 `Access-Control-Allow-Origin` 这个处理方法的话。

我大概会这样设计



对于一个 Section 来说，可以在整个模块的层面上，允许所有 Section 内的 API 都允许这个域来访问，因此这样设计会比较妥当：

```python
api = Section("api")
app.allows(["example.com", "a.com"])
# or
app.allows("*.(example|a).com")
```

现在的想法是，传入一个允许的域列表，或者传入一个正则。



那么对单个 API 来说，也可以在 Section 之外指定其他的域。

```python
@api.get("/")
@api.allow("*.b.com")
async def one_api(ctx):
    pass
```

使用 `allow` 装饰器来传入一个正则，相对于 Section 允许的内容额外添加一部分域。



不过这样设计之后，对于以下例子

```python
api = Secion("api")
app.allows("a.com")

@api.get("/")
async def get(ctx):
    pass

@api.post("/")
@api.allow("b.com")
async def post(ctx):
    pass
```



按照上述例子中 `Access-Control-Allow-Methods` 是返回所有允许访问的方法。

那么如果这时候访问`OPTION /` ， `Access-Control-Allow-Methods` 应该就是 `OPTIONS, HEAD, GET, POST` ， 那么`Access-Control-Allow-Origin` 应该返回什么内容呢： `a.com` 还是`a.com, b.com` 。

如果是前者，那么 `POST / ` 是允许 `b.com `的； 如果是后者， `GET /` 是不允许`a.com`。

还是说存在一种可能性，存在一份 RFC， 讲明了对于一个URL，无论是什么方法， `Access-Control-Allow-Origin` 的值都要是一样的。

**以上关于 Nougat 的一切代码，纯属虚构。并未实现，具体效果请等正式代码出来**