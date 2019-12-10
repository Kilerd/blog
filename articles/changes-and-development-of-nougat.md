 - title = Nougat(Misuzu) 的进展和改变
 - url = changes-and-development-of-nougat
 - tags = 
 - datetime = 2017-05-25 22:31:00 +0800

Misuzu 这个名字被人吐槽了很久，不知道怎么读，也不知道什么意思。所以就改成了 **Nougat** 这个名字，意为牛轧糖。


<!--more-->


## handler 参数

handler 的参数从原来的 `request` 改成了 `ctx` 。相比于前者， `ctx` 增加了 `request` 和 `app` 的支持。

因为 Nougat 这个框架不像 Flask 那样使用子线程的方式来处理。 所以 Flask 中的 `url_for` 和 `abort` 不能裸露使用。因此必须依赖上下文（Flask 可以在线程池中依靠线程ID 寻找上下文）。所以一定要这样使用`something.url_for()` 和 `something.abourt` 。

`url_for` `abort ` `redirect` 这些操作放在 `request` 中感觉不三不四的。因此采用了`ctx`的写法。

所以handler 的写法就变成了一下的样子：

```python
async def handler(ctx):
	pass
```



## Middleware

原来那种以类的形式来写 middleware，过于累赘，而且不支持异步操作。因此改为 koa-like 的方式来写。

```python
async def middleware(ctx, next):
    # doing before handler
    await next()  # doing handler
    #doing after handler
```



还有一些小小的改进

- 使用 `yarl.URL` 来格式化 URL， 比我自己写更加高效，更加可信
- `register_middleware` 和 `register_section`  改用 `use` 。更加简约
- 完善了文档
- 使用了激进的`TOML` 来做项目配置文件，并且同伴完成了`Config` 模块的编写，不过还需要我重构一次



不过还是需要有一些等待修改的地方(都是我现在能想到的)：

- 对于现在 `ctx.params`的读取方式不太满意，应该重构以下
- 返回内容的格式化还没写
- `param_group` 或者叫 `params` 方法，一次性读入多个通用参数
- 文档自动化的集成



并且，从现在开始 Nougat 从原来的`pre-alpha` 进入了`alpha` 状态，意味着可以尝试投入工程中使用了。

我也会写一个工程去尝试以下 Nougat 的可用性。