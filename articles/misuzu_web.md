 - title = Misuzu 偏执的 WEB 框架
 - url = misuzu_web
 - tags = 
 - datetime = 2017-04-19 10:31:58 +0800

我是一个不折不扣的偏执狂，所以我认为所谓的产品就应该是为了特定的人群而服务的。这同样适用于 WEB 框架。

现在 Python 中的三大 WEB 框架(Flask, Tornado, Django) 都属于通用型框架，并不存在一个为 API ，尤其是 REST API 设计的框架。这也是 Misuzu 被创建的原因之一。


<!--more-->


Misuzu 是偏执的，它只为 API 服务，因此我为它做了这些限定：
1. RESTFUL API 是用 HTTP METHOD 来区分服务的，因此 Misuzu 在定义路由的时候，就需要指定是哪一种 METHOD，而不是像 Flask 那样可以同时把 GET，POST 写进一个 handler 里面。
2. API 最常见的返回格式就是 `JSON` ，因此应该做到简化对 `JSON` 返回内容的处理，能 `return {"name": "hello"}` 的就不应该`return json.dumps({"name": "hello"})`
3. 框架应该把 HTML 模板引擎设为可选的，而不是必须的，毕竟一个单纯的 API 系统是不需要渲染 HTML 的
4. 我觉得 API 是可以分成几个部分的：参数定义及处理、逻辑处理、返回内容的规范化
5. Python 写出来的作品就应该更 Pythonic，因此我选择了大量使用装饰器这种及其优雅的处理方式

综合了以上几点，Misuzu 的基本模型就出来了：
```python
from misuzu import Misuzu

app = Misuzu(__name__)

@app.get('/<name>')
@app.param('name', str)
async def index(request):
    return {'hello': request.params.name}

app.run()
```

这只是 Misuzu 的第一步，不过也已经确定了它今后的走向。Misuzu 的偏执注定了它不会成为主流，但是只要它能够被一部分人所接受就足以。

如果你喜欢Misuzu，可以前往 [https://github.com/Kilerd/misuzu](https://github.com/Kilerd/misuzu) 了解更多。