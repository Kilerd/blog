 - title = 入门就写一个博客程序吧.RUST
 - url = rust-how-to-learn-it
 - tags = 
 - datetime = 2018-12-28 15:03:59 +0800

> 当你不知道要干什么的时候，那就写个博客程序吧。 —— 鲁迅

是的，鲁迅曾经这么说过。当你的编程能力出现停滞的时候就写一个博客吧，尤其是入门阶段。更具体而言是写一个 CMS 系统，这也是我平时学习的习惯，我会一步一步解释清楚为什么我会选择这样的学习路线。

<!--more-->

## 易上手的角度

相对于 CS 的其他方面来说， WEB 方向一直都是一个门槛相对较低的一个方向，而且在互联网的知识储备也是最丰富的，同时也是最容易做出成品的。WEB 方向可以及时的给学习者带来足够的反馈和满足，这样会更加鼓励初学者。

相比于其他方向，WEB 方向的知识也是最浅的，初学者不需学习过多的前提条件即可开始开发作品。这样可以很容易地让初学者关注在新学语言的语法知识上面，而不会出现本末倒置的情况。毕竟这是一次学习新语言的过程，而不是学习 WEB 知识的过程。

于这样的学习目标下，一个最小型的 WEB 系统可以让我集中注意在语言层面上。一般的语言都会有一个比较成熟的 WEB 生态，那么我们可以比较轻松地学习到如何制作用户权限，如何与数据库打交道，做 CRUD。这可以是我们学习到这个语言大部分的语法，那就足够了，我们并不需要过多关注页面样式和用户交互方面，因为那不是我们的重点。

在这样的学习背景下，我写出了[Project Rubble](https://github.com/Kilerd/rubble)，一个用 Rust 写的博客系统，现在也正式地把博客迁移到了上面去。只有那个程序真正地被使用了，你才会发现程序上会有多少的 BUG。一次一次的BUG 修复足以给你足够多的机会去熟悉该门语言。

Rubble，乱石，这个名字十分贴合我创造这个轮子的原因。我本来就是希望这个项目可以让我真正地了解 Rust 的特点和语法，而且同时他会是我对 Rust 的一些试验的实验场。我需要确保有一个可运行的项目或者 DEMO 来验证我这些想法和技术，那么 Rubble 足以给我提供这样的环境。

在这样的基础下，Rubble 这个项目注定是不稳定的，我可能会拼命地加很多看起来很奇怪的特性进去，因为我需要他去做实验。

## 可行的试验场

正如上文说，一个可运行的试验场是很重要的，因为他是你学习新知识的地方，可以验证可行性的地方。

GraphQL 可以说是一个不算很新的 DSL 了，它在我的学习列表里面也停留了很久，但是就是因为没有一个可以跑的项目，导致我对 GraphQL 的认识和了解只停留在官方文档的阶段，可是这次我真正地把它加到了 Rubble 里面，同时也做了很多思考，关于用户权限的控制，关于缓存，关于递归层数等等，这些问题都是需要在真实项目中测试出来的，而不是靠文档可以提供的。

RSS 的集成却是在意外之中，不过却让我很细地了解了一次 RSS 的内部实现和组成。这虽然并不是学习的主要目的，却是 Rubble 作为一个博客程序必须的部分。

在此之后，一个简单能跑的的程序和网站就出现了，那么对于我而言就存在了一个完整地可以测试的地方了，那么接下来碰到新的知识点就可以在此基础上做修改。

我测试包括一下的内容，分布式的储存和TOKEN实验，主要是在 REDIS 中储存TOKEN，并且还研究了一番 REDIS 集群的搭建和使用，如果没有这个网站，估计我并不知道这些知识我该如何验证。

## 总结

Rubble 并不是一个十分优秀的项目，甚至它的项目结构都是很差的，但是却是我学习 Rust 的一个入门项目，同时也是我的技术试验场。

> 虽然我不能保证这个方法能适合于所有初学者，但是这个方法却是可以优秀的学习方法，毕竟对于大部分初学者而言，是没有能力参与或者制作开源项目的，那么「自娱自乐」是最好的方式。