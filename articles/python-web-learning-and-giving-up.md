 - title = Python Web 从入门到放弃：Flask or Tornado
 - url = python-web-learning-and-giving-up
 - tags = 
 - datetime = 2017-02-08 23:33:43 +0800

Python Web 这个领域一直都处于不温不火的情况，但是因为 Python 的易上手性，导致了一部分人也在坚持着这一个领域。
Python Web 框架主要有： Django、Flask、Tornado。

这三大党派都有自己坚持的理由：
 - `Django` Full Stack 式的开发模式，开发者查看官方文档即可实现大部分网站的大部分功能。
 - `Flask` Minimal 的框架，框架内部只实现了基础功能。Extensionable 的设计，让你的绝大部分功能都可以通过其他开发者完成的 Extension 来实现。
 - `Tornado` 三者中唯一一个异步框架，Web Framework 和 HTTPClient 的结合，同时也是一个简约的设计。


<!--more-->


对于 Full Stack Framework 和 Micro Framework 的不同看法，把所有 Web 开发者分成了两排人：
 - Full Stack Framework 拥护者认为：无论使用怎样的框架，当网站被设计成大型网站时，框架本身、引用的插件和编写的所有辅助代码都会形成一个异样、另类的 Full Stack Framework（RoR的作者也曾经表示过：任何框架最终都会称为另一个RoR）。那么基于这样的思想，与其在 Micro Framework 上拼凑代码，不如直接使用 Full Stack Framework
 - Micro Framework 拥护者认为：Web 框架就应该实现大部分 Web 通用的功能。对于某些定制性强、业务性强的功能和模块，应该由开发者自己实现。该人群认为，大型网站的差异性远超于小型网站，所以在 Full Stack Framework 中的大部分功能都需要修改后才能在大型网站中使用。翻看和修改框架代码的代价也是远超于自己编写一个完全符合自己设计的模块。基于这样，在大型网站中使用 Micro Framework 是比较合理的决定。

笔者个人是比较偏向轻量级的框架，也就是上述的第二类人。那么就回到这篇文章的核心：Flask 和 Tornado 应该怎么选择。
笔者更偏向 Flask。原因并不是笔者长期使用 Flask，下面来分析下 Flask 和 Tornado 的优劣：
 - Flask 只是一个单独的 Web Framework，Tornado 还包含了 HTTPClient，意思是 Tornado 内置的服务器可以直接用于生产环境，Flask 还需要依靠 Gunicorn 和 Gevent 来用于生产环境和提升性能。 或许在部署方式上，Tornado 获胜
 - 在那么多接触中，Flask 似乎并没有提出一个较好的方法来利用多核，Tornado 在官方文档中就有相关文献和代码。在利用多核上，Tornado 获胜
 - Flask 的 Router 的装饰器更符合人类和 Python 的思想。而 Tornado 的 Route 汇聚方式就那么明显，也有非官方代码实现了装饰器的方式。在 Router 中，各有优劣，各花进各眼，打平。
 - Flask 把一个路由写在一个函数中，而 Tornado 却实现在 class 中，能有效的区分各种 HTTP 方法（GET、POST、PUT、DELETE...），并且提供了`initialize`、`prepare`、`on_finish` 等方法。 这方面，Tornado 获胜
 - Tornado 官方代码自带 Websocket 模块。
 - Flask 支持 Extension 。

上述优劣中，看似 Tornado 获胜点居多，实际上是笔者在常年使用 Flask 中遇到的一些不如意的地方，同时也是希望 Flask 可以改善和采纳的地方。

Flask 支持 Extension 这一点就足矣抵过上述讲的所有点。Tornado 在代码复用上面做的确实是很差。 Flask 通过 Extension 的模式很好的做到了这一点，这也使得 Flask 形成了比较良好的社区 和 产生了大量优秀的 Extension。

Tornado 本质上，每一次处理都交由 `tornado.web.RequestHandler` 来处理。所以在实现大部分功能都是对 `RequestHandler` 进行定制和修改。找不到一个很好的链式继承方式来对 `RequestHandler` 进行重构，就注定 Tornado 的代码重构会很差。

在使用 Tornado 的这段时间，真的挺难受的，估计是习惯了 Flask 的模式，另外在 Flask + Gevent 的配合下，Tornado 的异步优点并不是十分明显。

基本来说，我建议如果入门的话，还是选择 Flask 比较妥当。如某人所说：Tornado 自身的代码实现的很漂亮、很惊人，可是用 Tornado 来组织 Web 代码就显得不那么优雅。

实际上，Tornado 还是有很多设计得很得当的地方。当玩腻了 Flask 后，可以尝试下 Tornado 。或许会有另外一番心得。

PS： 以上是笔者对 Flask 和 Tornado 的一些个人看法，不代表任何官方意见，仅供参考。