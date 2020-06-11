 - title = 作品集 / 垃圾堆
 - url = portfolios
 - tags = 
 - datetime = 2015-04-18 21:16:11 +0800

这些都是我在做的，已经不在维护的，准备做的项目，如果有兴趣，可以联系我，我会考虑把你加入项目组。当然我的大部分项目都是开源，并且使用 MIT 协议的，欢迎任意使用。

<!--more-->

## Rubble

[GITHUB](<https://github.com/Kilerd/rubble>)

这是一个用 Rust 写的博客程序，也就是我这个博客正在使用中的程序。算是我入门Rust后真正写的一个项目。

- Docker 镜像大小 10 M，运行所需内存 5 M。

- 采用了 actix-web 和 diesel 的技术方案。
- 提供了标准的 Restful API 接口供外部调用。
- 完善的后台管理面板。
- RSS 订阅支持。



## Project Spend

[WEBSITE](https://spend.kilerd.me/)

在不满足市面上的任何记账软件后，我自己胡搞了一个记账的最小化实现。后端采用了 Rust 实现，前端采用了 React + TypeScript 的方案。由于本人不是比较专业的前端，所以界面并不是十分靠谱。

> 这个完全是个人需求驱动的项目，所以基本上都是根据我个人需求进行设计和更新。
>
> 而且目前还没有其他人使用该项目，所以更新的频率和方向都是未知情况

- 后端采用了 Rocket 和 diesel 的技术方案。
- 目前只支持支出和收入两个比较简单的 Feature，预算功能正在火(gui)热(su)开发中。



项目没有开源是因为代码还很乱（从 GraphQL 迁移回 Restful API 的历史代码还没重构），并且因为设计CI/CD的配置还没有开源，不过在不久的将来会开源



## Bearnote

[WEBSITE](https://www.bearnote.com/)  [CLI GITHUB](<https://github.com/Kilerd/bearnote_cli>)

很久之前注册的一个域名，并且打算拿来做一个笔记的网站，但是发现竞争太大就停下来了。

现在拿来做了一个很简单的 Pastebin 网页，但是他不是比较传统的 pastebin。我用 Rust 为他写了一个 CLI 工具，用来上传文件，同时可以打 tag，还支持了删除功能以避免隐私泄露。

同时为了更加好的阅读体验，它是支持指定后缀的方式来高亮文本内容的。当然目前只支持简单的 Markdown 文件的高亮，下一步将准备做 json 和 shell 内容的高亮。

这个网站的目的在于分享长文本的同时，提供比较好的阅读体验。同时还在努力的克服技术难点，希望能做到这样的效果 `bearnote cargo build` 就可以把编译失败的内容记录到 bearnote 网站上面，实时分享出去。



嗯，这个项目也是因为共用一套 CI/CD 配置的原因没有开源，也准备开源了。当然了 CLI 工具现在已经是开源状态了，毕竟这是要跑在客户端的东西，不开源没人敢用。 



## Resource.rs

[GITHUB](<https://github.com/kilerd/resource>) [WEBSITE](<https://resource.rs/>)

一份希望能够提供中文化的Rust学习资源。