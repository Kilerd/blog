 - title = 自制 Web 框架的那些事儿
 - url = things-of-creating-web-framework
 - tags = 
 - datetime = 2018-07-12T03:15:28.000000+08:00
 - template = article.html

> 不想造轮子的程序员不是一个好码农。  —— 鲁迅


<!--more-->


## Nougat 的发展流程

> 我不知道点进来看这篇文章的人，有多少是知道我在写一个Python的异步框架的。
>
> 不过无所谓，这篇文章适合于任何人看，适当的时候跳过代码部分即可。实际上更多的是对 Python 的一些见解。

那时候写项目，特别是在跟前端对接的时候，我就在想「写 API 文档好麻烦啊」，「难道就不能自动生成这些文档吗？」。

是啊，为啥不能自动生成呢？Parameters 的读入和处理都在代码里面写好了。返回的内容也是在代码里面的。难道我就不能改一下代码就可以轻松生成 API 文档了吗？

那一段时间，我整天都在想这个事情。当时我用 Flask 写一个 API 的流程基本是这样的：下文用用户注册来做演示：

- **定义 URL** 根据 RESTFUL 来说，用户注册实际上就是添加一个用户资源，所以 URL 为`POST /user`
- **定义这个 API 需要那些参数** 简单来讲，邮箱、密码就足够了
- **考虑参数的类型**
- **编写 API 逻辑** 这里就是把信息储存
- **返回的内容** 这里考虑生成一个 token 给用户

Flask 代码大概长这样：

```python
@app.route('/user', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    
    valid_email(email)
    valid_password(email)
    
    # register logic here
    UserService.register(email, password)
    
    return {
        'token': token_generator()
    }
```

上述的五个步骤对于一份API文档来说，除了第四部逻辑部分是不需要的，其他部分都应该展示在文档中。

那么如果传统的开发流程包括了两个步骤：写代码 和 写文档。可是这是一项十分重复的工作，而且存在实效性的问题：代码更新之后文档还没来得及更新导致对接时出现问题。

细看每一步，我们又可以采用自动化的方式来生成这些重复的信息：

- `@app.route('/user', methods=['POST'])` 完全可以解析到 `POST /user`
- `email = request.form.get('email')` 和 `valid_email(email)` 则可以合并成一步，通过一个函数来实现这项自动化的工作 `email = Parameter('email', from='form', type=email)`
- `return` 部分在大型的系统中都需要在返回之前检查输出的内容是否符合我们预期的值

这样细想之后，代码就可以写出以下的形式：

```python
@app.route('/user', methods=['POST'])
@param('email', email, location='form')
@param('password', password, location='form')
@marshal({
    'token': str
})
def register():
    UserService.register(params.email, params.password)
    
    return {
        'token': token_generator()
    }
```

两份代码，就个人而言，我更喜欢第二种，因为后者的层次感更加分明：

- API 的URL 是什么
- 这个 API 规定了哪些参数，从哪里获取，期望的类型？等等
- 返回值什么，包含了哪些字段
- 业务逻辑是什么

根据这些特点，我实现了这样的Router：https://github.com/Riparo/nougat-router

由于在 flask 上面的造诣不深，对「如何编写一个 Flask 的插件」不熟悉，所以我决定自己去写一个 Web 框架。是的，一切从头来，从零开始。到目前为止已经断断续续维护了1年多了，提交了差不多300个commit。

决定写这个框架的时候，心里想着要把这样的一个 Router 实现，同时要深入了解一下 Python 的异步。所以就变成了写一个异步的 Web 框架。

在最开始的那段时间，我在抄袭 Sanic，对，抄袭，对着 Sanic 的第一次提交记录抄了一个可运行的框架。此后我就对这个抄来的东西改了无数次，每一次修改都是一次不同库的选择和思考：

- **同步还是异步** 这点思考的时间最少，同步的太多了，而且基于 wsgi 的框架也很多，异步才是未来！
- **TCP的处理方式 Stream 还是 Protocol** Asyncio 官宣 Protocol 的效率会比 Stream 高很多。但是 Protocol 的处理函数是同步的，需要在一个同步函数里面 spawn 一个异步处理函数，就是 创建一个 `Future` 来执行框架的代码。在HTTP make respone 的时候需要在 `Future` 中添加 `call_back` 来实现。相比之下 Stream 模式下的代码表现形式会更加直接，可以直接在函数中 `await logic()`，因此，我选择了 Stream 的模式。
- **异步框架的选择** asyncio 是官方推出的异步实现，`curio` 是民间的一个良好实现。
  - 从代码的实现上 `curio` 更加好，更加优雅
  - `asyncio` 由于是官方实现，所以生态做得最好。`curio` 甚至还在修修补补阶段，生态近乎很惨，不过后来推出了`curio-to-asyncio bridge` 使得 `curio` 可以分享 `asyncio` 的部分生态
  - `asyncio` 可以使用 `uvloop` 调度库来加速 Python 的异步处理，让速度上升一个量级。而 `curio` 是纯粹的 Python 实现，所以相比之下 `curio` 的速度会慢一些。
- **HTTP 解析器的选择** `http_tools` 是一个用 C 写的 HTTP 解析器，只能解析报文层面的内容。 `h11` 库同时提供了一个服务器和客户端为主体的DFA，用状态来表示当前HTTP进行到了哪一个环境
- **框架长什么样子** 我个人比较喜欢的都是微框架，框架中不含太多定制的功能，只提供客观的扩展性供客制化。KOA 的用 Middleware 串起来的形式还是 Flask 那种以 Signal 和 Extension 为主的处理呢？

上述的每一点，每一个选择的碰撞都可以在我的框架代码中找到，每一次的修改都让我对 Web 框架的理解深入几分。

## 关于框架生态

一个框架即便再优秀，没有一个完善的生态圈都难以让它成为一个优秀的框架。每一位程序员都是高傲和懒惰的，他们期望框架可以完成他们所需要的一切内容。

我写的这个 Nougat 框架完成后是一个长得非常像 Koa 这样基于 Middleware 的框架，同时我也注入了一些 Flask 的思想进去。即便 Nougat 的设计再好，没有配套使用的库都注定让它成为一个不优秀的框架。

我很长一段时间就是在做这么一件事：为 Nougat 编写各色必备的中间件。但是实际上我并不清楚我需要写哪些，于是乎我便尝试用 Nougat 来写一个 API 服务器，尝试去做一个真正的项目。我在想，在尝试把 Nougat 放进项目中，我需要做什么：

- **完善的路由 Router** 这点很重要，是我这一切一切的起点。文章的上一部分讲述了我是怎么设计路由的。
- **跨域 CORS** 我一直把 Nougat 作为一个构建 API 服务器的快速框架，所以跨域的问题必须要得到解决。于是乎，我把 Koa-CORS 翻译成了 Python 版本。对，代码一行一行的翻译，同时它工作得很棒。
- **异步服务的连接** 项目在启动服务器时，需要初始化数据库连接池，这是一项异步任务，所以它需要在服务器启动之后执行，所以我在 Nougat 中添加了 Signal 的概念，以提供服务器启动前后的任务动作。
- **API 文档** 我是一个十分懒惰的人，既然我的路由已经足够优秀，那么我就不应该手动写一份文档，他应该自动生成。
- **便于开发时的组件** 基本上每个框架都会提供 Auto Reload 的功能，我也为 Nougat 添加了这项功能，采用了 watchdog 和 tornado-reload 两种不同的方案。同时编写了在 Console 上面显示 HTTP 访问记录的 Logger，显示了访问时间，URL，响应状态码，耗时等等。
- **异步 ORM 的集成** Python 生态中两大ORM：SQLalchemy 和 Peewee。可惜的是两者都没有提供完善的异步处理方案，原因会在下一部分详细讲清楚。SQLalchemy 派系的 GINO 迟迟不能解决多对多关系；Peewee-async 至今还未支持 Peewee 3.0。
- **CLI 集成** 到了现在，框架已经有很多命令可以使用了：生产模式启动、开发模式启动、生成 API 文档、SHELL 调试模式等等，所以写了 CLI Manager 来管理 CLI 命令，同时允许 Extension 在注册时添加命令。

于是乎，这段时间，项目逻辑并没有写过太多，更多的是在重构 Nougat 的架构和这些组件的组织模式。**框架内每个理所当然的功能都是维护人员辛苦的劳动成果**

## 不争气的 Asyncio

即便是 Python 3.5 便推出的官方支持 Asyncio，到目前来说都属于混乱状态。

目前为止，文件 I/O 没有纳入 asyncio 库是我感到很纳闷的事情，而且 aiofiles 还是通过多线程来实现异步的，不说对不对，感觉起来就是怪怪的。

在网络 I/O 方面，也没有发展出能让人眼前一亮的 ORM。这点让大部分想升级至异步框架的使用者停下了脚步。

我现在甚至有点羡慕 JavaScript 那种全异步的处理了，羡慕的原因恰恰是为什么不能发展出优秀 ORM 的原因。

我们先来看看 Python 里面 ORM 是怎么处理 Relationship 的。

假设我们定义了两个模型： 用户模型，和用户 Token 模型，采用一对一关系：

```python
class User:
    username = Text()
    
class Token:
    access = Text()
    refresh = Text()
    user = ForeignKey(User, back_ref='token')
```

比如我们在用户调用API时验证权限时需要判断 Token 的用户：

```python
token = Token.query.filter(access="...").first()  # whatever

user = token.user
```

如第二行这样读取用户信息是很理所当然的，毕竟这也是 ORM 的一大特色。那么我们再深入一点看看 ORM 是怎么处理第二行的代码的。

实际上 Token 在数据库中储存的 `user` 只是 `user_id` ，是 User 的主键。第一行代码相当于：

```sql
SELECT * FROM token WHERE access="..."
```

注意，我们这个时候并没有查询用户相关的任何信息，当我们执行第二行代码时，相对于在执行：

```sql
SELECT * FROM user WHERE id="{token.user_id}"
```

这个时候才查询用户信息，简单来说就是**按需查询**，同时也是 lazy load。这有时候也是部分用户不喜欢使用 ORM 的原因，因为上述代码可以用一句 SQL 查询完成。直接写 SQL 可以降低数据库的压力。当然了，这不在这篇文章的讨论范围。

换成异步的场景，这些代码会发生什么事情。别忘了，只要是异步调用都需要在方法前面加上 `await` 来表示异步方法。

首先，Python Property 不支持异步调用，所以 `user = token.user` 是不能用的了，即便是你想这样用也不行：`user = await token.user`

如果我们退而求其次，用一个函数来调用 `user = await token.relationship('user')` 。看似表现很棒，但是如果需要调用几层，那么代码看起来将会是灾难性的难受。

```python
# address = token.user.address
address = (await (await token.relationship('user')).relationship('address'))
```

还记得在 Nougat 刚创立起初，有人发 ISSUE 问我有没有写 ORM 的计划，我当时还说 peewee-async 已经很棒了，现在想想都觉得丢人。

不过高兴的是，asyncio 得到了 uvloop 的支援，让 Python 可以在跑起来有可以跟 NodeJS 一拼的机会。

## 我很期待的一些事情

我想，我做的事情已经很多了，也为 Nougat 付出了很多，同时 Nougat 也存在很多问题。但是我想我应该先缓一缓了。

我接下来会继续为 Nougat 把文档继续写好，写一份比较完善的文档。

同时我很期待有人尝试去用 Nougat 写一个网站，给我一些反馈。