 - title = 浅谈 Web 用户验证的几种方式
 - url = web-authorizations
 - tags = 
 - datetime = 2018-02-21T16:10:34.000000+08:00
 - template = article.html

这片文章试图介绍清楚网站前端与后端之间数据交流时用到的技术，诸如 Session，Cookies，Token，Jwt 等等；同时解释清楚几个初学者容易混淆的地方。


<!--more-->


## HTTP VS HTTPS
HTTP 到底有什么弊端，HTTPS 到底解决了什么问题。

在 HTTP 中，Client 发送内容给 Server 的过程是全部明文发送的，双方都不会验证对方发送过来的东西是不是正确的。同时在 HTTP 传输的过程中，因为数据是明文暴露的，所以网络中间人（任何网络中间人）都可以对这份数据进行修改。

假设 A 发送数据「2333」给 B，而有人在传输的过程中修改成「6666」了，B 对这一切一无所知。

即便存在一个确认机制：B 会发送一个确认信息给 A「你发给我的信息是不是『6666』」。在数据回传给 A 的时候，中间人一样会把「6666」改成「2333」从而让确认环节正常进行。

那 HTTPS 作为 HTTP 的改进者到底做了什么事情了。（著者：这里不会详细地介绍 HTTPS 的工作机制，只会以简单的逻辑和见解让读者明白 HTTPS 做了那些事情）

首先，我们希望数据传入过程中不被修改，最好不被查看。不被查看是次要内容，因为只要能确认不被修改，我们有 N 种方法让数据不被查看。那么 HTTPS 就是冲着这个大目的去了。

简单来说 HTTPS = HTTP + SSL。SSL保证了传输过程中数据不被修改。简单可以理解成在 HTTPS 通讯的时候，会生成 A、B 两个钥匙和一个箱子。A 上锁只能 B 解锁；B 上锁只能 A 解锁。Client 和 Server 通过某种方法（Diffie-Hellman）协商生成钥匙 A 和 B，一人拿一把，那么我们把 HTTP 报文放入这个箱子中就可以了。在这同时把报文放入箱子的过程（RSA 加密）就保证了数据不可被查看。

注：
- HTTPS 无法加密 访问网站域名和IP 内容。新版提案在促进这个过程（感谢[hxsf](https://www.v2ex.com/member/hxsf)的纠正）
- 目前 HTTPS 和 HTTP 2.0 是相辅相成的，所有请理性区分哪个功能属于HTTPS，哪个属于 HTTP 2.0

## 当前后端分离
当前 Web 开发逐渐趋向各司其职，前端忙前端的，后端忙后端的，同时随着前端框架的流行，前后端分离的开发流程和注意事项可以算是每位 Web 开发的必须掌握的技巧。

那么前后端分离开发相比于传统开发需要注意的是什么。

HTTP 是一个无状态的连接过程，每一次访问对于 Server 来说都是新用户，那么需要一些技术来让 Server 知道这次连接过来的是谁。从而产生了 Session 和 Cookies 技术。其中 Cookies 是 HTTP 协议中规定的，而 Session 是基于 Cookies 衍生出来的技术，在接下来两节中会详细讲解这两种技术。

可是在前后端分离的开发环境中，前端是使用 socket (通常是`axios`)来创建一次 HTTP 连接的，不是浏览器创建的，所以 Cookies 没法有效储存，导致了 Cookies 和 Session 无法使用。所以我们会采用手动的形式来模拟浏览器处理 Cookies 的流程来创造一套属于自己的 HTTP 用户认证方式，比较成气候的有：JWT、TOKEN。

接下来将一一讲述这几种技术的实现过程和认证过程。

为了更加生动，我会把 Server 比喻成商店（包括商店工作人员）；Client 比喻成购物者。不同的网站（不同的域名）对应成不同的商店；不同的访问者对应不同的购物者。

## COOKIES
Cookies 是 HTTP 协议中自带的内容，所以浏览器对其的支持都是很好的。同时 Cookies 是对用户透明的，用户不用做任何操作，浏览器会根据 HTTP 报文来做处理。

Cookies 说白了就是一个简单的KV（key-value）的数组，具体流程是这样的：
- Client 访问 Server 时会自动带上 Cookies，具体实现是在 HTTP 头部的 `Cookies` 中传递过去。
- Server 可以在 Client 中写入 Cookies，具体是在 HTTP 响应报文头部中`Set-Cookie` 来告诉浏览器需要在 Client 中记录这些信息，以后访问的时候顺便带过来。

Cookies 实际上就是这么简单。如果生动点讲：
- 购物者来到了 A 商店，买了一瓶水。商店收银员在他身上做了一个标记，记下了他买了一瓶水（`Set-Cookie: bought=1-water`）
- 当购物者再来商店的时候，因为他身上是有标记的，所以商店收银员一眼就看到了（`Cookies: bought=1-water`），就告诉购物者「你上次买了一瓶水，这次也一样吗」

这便是 Cookies 无需用户参与就能做到的信息传递，全部由浏览器实现。
### 当前后端分离
正是因为 Cookies 是在 Client 访问 Server 时，由浏览器自动添加的，并且前端采用`axios`来构建一个 HTTP 连接时，不会自动加上 Cookies，所以 Cookies 在前后端分离中并不能使用。

当然也有比较坎坷的解决方案，前端在调用完登陆 API 后，把 Cookies 记录下来，在接下来每次 API 调用过程中加上这些 Cookies。**但是不推荐这么做，除非你是做爬虫**

## SESSION
Session 是在 Cookies 发展中为了解决 Cookies 某些弊端而产生的技术，但是本质上还是 Cookies 的使用。

设想下，正如上述例子中，我们使用 Cookies 来记录购物者购买过的商品，如果商品类别很多很多，Cookies 便会很大很大，导致 HTTP 协议或者浏览器无法正常处理 Cookies（**每个域名建议不超过50条 Cookie 记录，总体积不超过 4093 bytes**）

那么如果我真的有「让用户携带很多信息」的需求呢？Session 因此诞生，其解决方法是：
- Server 为每个用户打上一个标签（Session-id），然后**把本来需要存在 Cookies 中的消息存在 Server 中，不记录在 Cookies 中**，现在就只把这个标签记录在 Cookies 中。
- 当 Client 再次访问时，因为 Cookies 自动携带的原因，Server 知道了这个用户的标签（Session-id），然后查询本地记录，找出该用户对应的信息。

用回购物者的例子来讲：
- 购物者来 A 商店买了一瓶水，收银员在自己的本子上记下了「商店第 666 号用户（Session-id）购买了一瓶水」，然后在购买者上打下了「这位是 666 号用户」（`Set-Cookie: user-id=666`）
- 当用户再来商店时，收银员查看了他的标签（Cookies）「这位是 666 号用户」（`Cookies:user-id=666`）。这时候收银员知道了这是 666 号用户，然后查看自己的本子看看 666 号用户到底买过了什么，然后发现了这条信息「商店第 666 号用户购买了一瓶水」，然后告诉购物者「你上次买了一瓶水，这次也一样吗」

这样无论购物者买了多少东西，我们都只需在购物者身上打下用户标签（Session-id）这个信息。

如果你了解过 Session，都知道 Session 会在浏览器关闭后失效，这是因为 Cookies 的 `Max-Age` 来实现的。HTTP 协议允许 Server 设置 Cookies 的有效时间：
- `Max-Age` 大于 0 ：有效时间就是这个数值，单位`秒`
- `Max-Age` 等于 0 ：Cookies 马上失效
- `Max-Age` 小于 0 ：Cookies 保存在浏览器的内存中。自然浏览器关闭时就失效了，从而实现了 Session 的时效性的问题。

Session 在 Server 中是怎么保存用户信息的，可以有多种方法，常见的有：
- `In-Memory` 即直接存在程序中，方便，但是不适合于多实例的 Web 程序或者分布式 Web 程序
- `Redis-based` 即保存信息在 Redis 中，解决了 IM 储存方式不适用于分布式的缺点。
### 当前后端分离
Session 是依赖 Cookies 存在的，所以在前后端分离中自然不能使用。

## TOKEN
上述在 Cookies 部分讲到在前后端分离是如何让 Cookies 生效，其实 Token 就是复现这一个过程。

Token 是一个很泛的讲法，业内称票据（我也不是很清楚中文怎么称呼它），它可以是 Session-id，也可以是一串随机的字符。但是它的作用跟Session-id 一样都是为了识别不同的访问者，同时验证它的有效性。

Token 是一个很广泛的说法，是因为它只提供了一个验证的准则，而不是一个具体的做法，所以 JWT、OAUTH 都可以算是 Token 的一种实现。

在我看来，Token的过程就是这么一回事：
Client —> Server: 嘿，我是那个谁啊
Server —> Client: 知道了，你记着你的票号 123456，半个小时内有有效

// 几分钟后
Client —> Server: 嘿，我的票号是 123456，帮我买瓶水，钱从账户扣
Server —> Client: （嗯，123456 在有效期内）好嘞

Client —> Server: （我试下用别人的账号买东西）嘿，我的票号是 666666，帮我买瓶水，钱从账户扣
Server —> Client: （嗯？我们根本就没有 666666 这个票号的记录啊）兄弟，你是来搞事的吧

// 半个小时后
Client —> Server: 嘿，我的票号是 123456，帮我买瓶水，钱从账户扣
Server —> Client: （em，好像过时了）诶诶诶，你的票号过期了，不办理了

OK，我们再回看一下整个 Token 的使用过程。

「Server —> Client: 知道了，你记着你的票号 123456，半个小时内有有效」 想比于 Cookies 和 Session 的自动处理，Token 这里明确告诉了用户他的票号和有效期（当然，有效期不是必须的），这是一个需要用户参与的过程。也就是说 Server 必须通过某种方式通知 Client，而不是像 Cookies 和 Session 那样使用 `Set-Cookie`就可以完成的。比较常用的方法有：
- 通过 HTTP RESPONSE 报文中 Headers 返回 `Token:123456`
- 通过 HTTP RESPONSE 报文中Content 返回`{'status':'OK', 'data':{'token':'123456'}}`

使用 Header 携带消息的方法使用较少，普遍都是使用 Content 来携带消息，因为通常情况下，需要返回的信息不只是 Token 本身，还有相关的附加信息：`Expire-time` 等等

「Client —> Server: 嘿，我的票号是 123456，帮我买瓶水，钱从账户扣」在 Client 进行后续访问时，需要手动带上 Token 以确认自己的身份（因为现在没有 Cookies 和 Session 可使用了），那么如何携带这些信息呢？
- 通过 HTTP REQUEST 报文中 Header 携带 `Token:123456`
- 通过 HTTP URL 携带：`http://foo.com/buy?good=water&number=1&token=123456`
- 通过 HTTP FORM 携带：这个方法只能出现在非 GET 请求下。

上述讲的三种方法，最常见的是前两种，第三种少使用的原因是需要为 GET 设计另外一种 Token 携带方案，而前两种适合于所有 HTTP 访问

实际上，Token 可以理解为人工干预生成的 Session-id，它不会把数据发送给 Client，只发送一个「一群数据对应的 ID」。这个想法跟 Session 是一样的，区别于 Session 的是 Token 使用得更加广泛。如果把Token 用 Cookies 来传递，就是另类的 Session，适用于传统的非前后端分离开发；如果把Token 利用 Header 或 Content 传递，便适合前后端分离开发。

Token 的具体实现有很多，完全可以自己设计一套出来，只要符合团队需求即可。
## JWT
既然有了 Token，为啥还要单独拿出 JWT 来讲呢？简单来说，JWT 是 Token 的具体且应用广泛的实现。

上文讲到 Token 可以理解成为用户自己实现的 Session，那么 JWT 在某种程度上可以理解为自己实现的 Cookies，原因如下：
- JWT 需要 Server 手动传递给用户，用户需要手动携带，所以还是归属于 Token 范畴
- JWT 选择把所有信息放在用户端，所以这属于 Cookies 的处理手法。

在之前的内容里面，我们都没有涉及到数据安全这个问题。因为 JWT 包含了部分内容，所以集中在这里讲。当我们把数据放在 Cookies 时，我们要考虑一个问题：这些数据放在用户端，被人看到，被人拿去会不会产生什么问题。

首先，被人看到，即数据机密性问题。如果这些数据包含了用户隐私或者商业机密的时候，被人看到必然不可，Session 类的处理手法就解决了这个问题，保存在用户端的内容只是一个随机的字符串，其与真实数据的映射关系只有 Server 知道，所以解决了机密性的问题。

其次，被人拿去，即用户伪造的问题。在上述 Token 例子中，Server 识别 Client 的唯一方式就是 Client 携带过来的票号。如果 Server 生成票号的方法被识破（举例来讲只是使用用户 ID 作为票号），那么入侵者就可以轻松的模拟任何用户进行网站访问。再假设 A 用户的票号被入侵者获取了，那么入侵者就可以使用这个票号来模拟 A 用户访问。目前没有比较好的方法解决「Token 被盗取从而模拟其访问」的方案。

但是我们可以尽量地提升被攻击的成本：
- 使用随机字符串来作为 Token
- 如果使用 Cookies 类在 Client 存储数据的方式，请建立 Token-Data 的映射方式，只在 Client 处存储 Token
- 建立 Token 的有效性机制。如「Session 的仅当前浏览器上下文有效」和「两次访问在30分钟内有效」等等。这样即便入侵者拿到某用户的 Token，也只能在一定时间内进行入侵行为。
- 建立如 JWT 类似的 Token 有效性机制。

JWT 的有效性包含了两点：时效性，有效性。

 - 时效性指 JWT 提供了 Token 的过期时间。
 - 有效性指 JWT 可以验证当前的 Token 是否被修改。JWT 的组成是这样的：`Header||Payload||Signature`
   - `Header` 标明了这是一个 JWT，而且使用了什么 Hash 算法
   - `Payload` 储存了你保存在用户数据和 JWT 自身的一些必要信息
   - `Signature` 是 Server 对 Header 和 Payload 的 HMAC 结果

为什么 JWT 可以验证 Token 是否有效呢？如果Payload 被伪造了，那么对应的 Signature 必然会变。然而 Signature 的生成需要一个只有 Server 知道的 Secret。因此 JWT 不可被伪造。

当然了，JWT 也不是没有弊端，因为 JWT 是把数据完全储存在 Client 端，而且当一个 JWT Token 生成时便无法修改。JWT 自身有一个过期时间，那么我们如何让一个 JWT Token 提前过期呢？为此我们要维护一个 JWT Token 的黑名单来限制这些 JWT 的访问。或者 JWT Payload 部分也是采用 Token-Data 的映射关系，只在 JWT 中储存一个 Token。

## 其他
Token 的范围很广，而且通过 Token 的流程，用户可以设计出很多相似或者更加安全、更加适合于多方使用的方案。上述讲解的都是 Server-Client 双方方案。如果是三方或以上的话，就需要自行协商方案，例子有 Oauth 2.0 和 SSO。当然了这些都不在这篇文章的介绍范围内，因为可以根据自身项目情况对已有方案进行改造从而满足自身需求。

## 总结
Session 和 Cookies 更加适合传统的非前后端分离式开发。

JWT 对于所有开发都比较适合。

Token 需要自行协商数据格式，通过选择对应的数据载体也适合于所有开发情况。若选择 Cookies 来装载 Token 适合传统开发。
**在选择任何一种认证方式，请注意数据的安全性**