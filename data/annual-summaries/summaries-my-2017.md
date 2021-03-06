 - title = 2017 个人总结
 - url = summaries-my-2017
 - tags = 
 - datetime = 2017-12-29T14:39:44.000000+08:00
 - template = article.html

> 鲁迅说过："Sometimes you need to leave things behind to move forward"
>
> 这一年下来，整个过程就是这样的情况。放弃了一些东西，努力了一些东西。


<!--more-->


## 我选择了怎样的编程语言

在17年以前，我是一个完完全全的 NO-JS 开发者，在写网站的时候，都是使用后端渲染和纯CSS写界面。可是 NodeJS 这些年的快速发展和用户 UI 优化的迫切需求，让我不得不开始系统地学习 JavaScript。

在同学的介绍下，我正式系统的学习ES6、ES7语法，这让我感受到了 JS 新语法与 Python 的相似性。在抛弃了 jQuery 和原生语法之后，进度一帆风顺。而且在 VueJS 和 React 中，我选择了 React，因为这符合了我喜欢 Micro Framework 的习惯，并且 React + Redux 的逻辑个人觉得会比 Vuejs 来得更加直接和清晰。

都 8102 年了，应该使用 Python3 了，所以我写的库基本上都是不支持 Python2 的。Py3 的最大成就可以算得上异步了，async/await 的语法糖支持和 asyncio 成为标准库让我最为兴奋。同时配合 mypy 做静态类型检查，Python 就有了基本的编写大型软件的能力，配合 uvloop 做异步性能优化，起码在 web 领域可以不输于 Nodejs。

Python 的 mypy 支持和 JavaScript 的 TypeScript 方言都让这两门语言有了类型检查的能力，但是我还是破解地渴望学习一门编译型语言。Rust 和 Golang 都是在我的选择范围之内。Rust 是我最最喜欢的一门语言，奈何其学习坡度太陡，所以几度学习都不能成功坚持下去。Golang 虽说很简单，可是个人感觉有些地方用起来还是不太舒服，例如 tab 缩进，无泛型，没有好用的包管理等等。今后估计还是会选择继续学习 Rust。

所以一年写来技术栈就成了这样的布局：Rust 高性能任务 + Python 做 API 服务 + React Redux 做 UI。

## 我做了哪些项目

Python3 中没有一个异步框架使用得比较舒服，所以就自己做了一个了 [Nougat](https://github.com/NougatWeb/nougat)。这个框架也是命途多舛，几度设计，几度重构，到现在只留下了一个纯粹的基于中间件的框架和一个路由器。但是使用起来却异常舒服。现在框架基本定型了，差的就是文档更新和自动重载的开发模式。

在学习爬虫的过程中，自己折腾了一个很小的爬虫框架 [Gear](https://github.com/Kilerd/gear)，现在才刚刚起步，代码也还不完善，可是架构却异常地清晰。

一个很简单的网页文本翻译器 [Coconut](https://github.com/Kilerd/coconut)。这是一个简单的 Chrome 插件。它在纯文本的表现力上还算不错。

一个简单的 Github Star 检索器 [Star Collector](https://github.com/Kilerd/star_collector)。这同样是一个 Chrome 插件，可以很快速地搜索到已经 star 的项目。当 star 数量很多的时候，这样检索会比 Github 自带的舒服很多。

自从注册了 bearnote.com 之后，就一直有一个魔咒“编写一个多人笔记 / 博客网站”。Nougat 的出现也是为它服务的，可惜最后还是没能写出来。最后打算用 Nougat 来写一个单人博客，这个任务不会很难，同时可以测试一下 Nougat 的表现力。

