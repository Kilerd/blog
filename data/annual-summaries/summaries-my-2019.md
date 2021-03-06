 - title = 2019 个人总结
 - url = summaries-my-2019
 - tags = 
 - datetime = 2019-12-31T21:34:22.000000+08:00
 - template = article.html



无意中翻博客草稿的时候，发现了 2018 的总结还在停留在草稿阶段，现在就已经要写 2019 年度总结了，不禁感叹时间流逝之快。

<!--more-->

## R.I.P Python 2

Python 2 停止维护，这绝对是一件所有 Pythonista 值得写入 2020 第一篇文章内的描述。我大概从2014年开始接触Python，但是就已经开始用 Python 3来写项目了。从 14 年到现在，除了写项目逻辑之外更多的时间是花费在 2 与 3 的兼容上面。虽然说 `six` 这种专门用来做兼容性库的存在极大的简化了兼容的实现，我还是十分希望能免去这些工作量。

一开始确实没有太大的理由和动力去做迁移工作，但是 Python 3 的一点点进步足以让迁移有足够的优势：Hash 算法的优化提升了部分性能；async 语法和 asyncio 生态的建立；type hint 的出现。这些让 Python 使用起来更加像一门现代化的语言。

时至今日，Python 2 的死去，是一件好事，摆脱了这么一个巨大的历史包袱，希望 Python 3 可以有更好的发展，搞搞 JIT，研究一下GIL。希望Python 3 越走越好。

另外 Guido 的退位也为 Python 带来了新的治理模式，不再是独裁者的所有物。[hpy](https://github.com/pyhandle/hpy) 的出现也让 Python 有望存在一个标准的 spec，这样下来越来越多的更好的解析器有望可以涌现。

## OverWatch 赛事

工作后对游戏的热爱就只能投放在赛事上。LOL 上 FPX 夺冠，Dota 里 大巴黎老干爹没能杀入决赛复仇 OG，这些都不是很关心。守望先锋在 2019 年的表现才是让人，让我无比兴奋的。

先是在世界杯上拿下亚军，再是在国内组出了 4 支俱乐部角逐 OWL 第二赛季的战场。同时 成都 Hunter 队的全华姿态也让国内对其抱有了极大的盼头。一是世界杯上中国队的超常发挥，二是对全华班的执着。听闻 Hunter 背后的老板跟 RNG 的老板还是同一个。从 OWL 第一赛季的「我们根本u知道怎么才能赢」到这个赛季的龙队获得第三赛段冠军，4支还是3支战队杀入季后赛这一切都在宣告着守望先锋在国内的蓬勃发展。正如林迟青说的那样「 We are ready to let the world know CHINA again」。

2020 年的第三赛季的主客场机制让不少 OWL 比赛在国内举行，相信氛围一定很好。可惜的事情是 Hunter 那位被誉为「神医」的主教练 RUI 因伤离队了，不知道成都队能不能在第三赛季保持水平的同时越战越勇。 

## 坚定了 Rust 的路线

在工作上写了一年 Java，虽说还是一如既往的讨厌它，但是毕竟是用来吃饭的本领，还是专研了一下，起码保证了自己的饭碗不会丢失。但是在业务的时间里面，更加坚定了3年前做的一个决定「学习 Rust」。

怎么说呢，前段时间看到一段文字可以很好的描述我对 Rust 的态度：

> 大概五六月的时候我领着团队系统地学习了一下 Rust 语言，后来就有一搭没一搭的写点随手就扔的一次性代码。看到 Signal 的这篇文章后，我按捺不住心头的激情一一终于可以 用 Rust 做一个似乎有点什么用的工具了！写下来总体感觉，Rust 有可以媲美 ruby 的表现力，又有可以媲美 C++ 的性能（如果使用正确了），加上略逊于 haskell，但可以秒杀大部分主流语言的类型系统，使得用 rust 写代码是一种享受（除了编译速度慢）。这样一个 小工具200来行代码（包括单元测试，生成式测试以及一个简单的benchmark）就可以完 成，估计用 python, elixir 和 nodejs 都不那么容易达到。 

大概就是这样，得益于过程宏等的一些生态，可以让代码写起来如同脚本语言那样的表现力和编写体验，既有极优秀的性能，还有完备的类型系统。这样 Rust 在各个领域都可以表现得很棒。

Rust 也让我真正的走上了 PL 的道路，之前的我可能是站在巨人肩膀上的，完全不知道脚下的巨人是谁，能干什么。但是 Rust 让我成功的走出了这一步。慢慢地了解到了类型系统及其图灵完备性，数理系统，逆变协变等等这些可能你日常都在使用，但是不知道其缘由和机理的事情。

我很庆幸在业务我不再是一个简单的CRUD boy，虽然我还有很长的一条路要走，但是起码我在2019迈出了那一步。很感谢 Rust 为我带来的这一个改变。

## Side Projects

如同我在「技术断舍离」里面描述的那样，我开始不喜欢写同类型的项目，逐渐接触不同领域的东西。我开始认真地想做一个社区，希望能把 Resource.rs 给做好。我认真反思自己做过的东西，那些没能让我学习到的项目都是一次拖慢你节奏的过程。我注册了3min.work，寓意是「三分热度工作室」，我希望我的一些零时性的，阶段性的，实验性的作品或者尝试可以放在这里，让我有一个更加直观的感受，同时也不会阻止我的前进。

## 最后

一年来，虽说工作不如意，学习上没啥进步，也开始慢慢接受自己的平庸。但是我始终坚信着「勤能补拙」这个朴实的道理。