 - title = Shadcn/ui: 你应该只需一个 web UI 框架
 - url = you-need-shadcn-ui
 - tags =
 - datetime = 2024-10-12T23:37:27.000000+08:00
 - template = article.html

鲁迅说过，我的技术栈里面有两个前端框架，一个是 shadcn/ui，另一个也是shadcn/ui。

这篇文章我们就来讨论一下周树人为什么要暴打鲁迅

<!--more-->

## 我做过的蠢事
人总是善变的，从接触到前端开发开始，我就一直在关注各式各样前端好看的框架。在变化万千的前端世界里面，总能一段时间就会涌出一个好看的框架。
从一开始的[tabler](https://tabler.io/admin-template)，后来到台湾人写的一个很小众的[tocas ui](https://tocas-ui.com/5.0/zh-tw/index.html)，再到后来的 [mantine](https://mantine.dev/)，到现在的 shadcn/ui。

## 为什么一直换

在抛不开颜值的前提下，我一直在找一个比较合适非专业前端使用的框架，目标在于：
 - 颜值至少在中等水平之上
 - 可定制化高
 - 可以用在react生态下
 - 组件足够丰富

前两个框架的选择纯粹是出于颜值的考虑，而当我开始大规模的使用在前端项目中时，就发现了这两个框架的弊端与缺陷，于是就跑步进入了第三个框架的时代。


## 与 Mantine 的蜜月期

Mantine 真的是我超级喜欢的一个框架，它基于了足够优秀的 UI 基础，让你直接套用框架都可以写出颜值中上的网页，这对非前端专业选手来说是一个超级棒的点，我们只需要往里面塞内容就可以了，完全不需要自己额外地增加写前端组件的负担。

同时 Matine 是我见过为数不多组件足够丰富、使用体感最舒服的框架。简单举几个例子：

 - 在表单里面带自动补全的输入框 [AutoComplete](https://mantine.dev/core/autocomplete/)
  - 甚至它自带了 `onMissing` 的逻辑处理
 - 我们常常需要用来做标签输入的 [PillInput](https://mantine.dev/core/pills-input/)
 - 多个值选一个的切换器 [SegmentedControl](https://mantine.dev/core/segmented-control/)
- ColorInput
- PinInput

各式各样你需要的，你以后需要的都能在里面找得到，另外他的人体工学也是很棒的。

有一个场景是你需要在各个地方弹出同一个Modal层展示数据，如果是其他框架，你需要在每个页面写一个Modal，然后单独控制它的展示或隐藏，而 Mantine 采用了类似于Context 注册的模式，
你只需要在Context注册你的Modal类型，然后调用 `modals.openConfirmModal` 就可以完成Modal的展示，这样你的代码就可以统一管理了。

感兴趣的具体可以了解一下：https://mantine.dev/x/modals/

同时 Mantine 还集成了极其强大的 hooks 库，一些很常用的 hook 功能它都能给你直接提供了。
例如：
 - 从 LocalStorage 取数据的 use-local-storage
 - debounce state 的 use-debounced-value
 - 专门为开关/boolean管理的 use-disclosure
 - 检测用户是否离开页面的 use-page-leave

[Mantine Hooks](https://mantine.dev/hooks/use-click-outside/)的强大和完善真的很省事，它帮你解决了前端里面很多很常见的场景，避免了自己去写重复的代码、封装hooks。 真正地做到了开箱即用。

## 我变了

人总是善变的，Mantine 逐渐开始不能满足我的需求了，经常出现了一些让我很难受、但是迫于现状我又得去默默忍受的情况：

Mantine 自带的水平布置控件 `Group` (等驾驭 tailwind 的 `flex item-center`) 是默认自带 `gap` 的，而且最小值只有 `xs`，并不能设置成 `none`。
在这种情况下，当你碰到一些需要根据不同的输入展示不同的内容，而他们又是紧紧贴合的时候（例如金额的 `-` 号），`Group` 就用不上了，你就得手写 css，而 Mantine 又不自带 tailwind，导致了代码里面出现了一些很神经质的割裂。

另外一个例子是Mantine的高度封装让你没办法深度定制。 在 Mantine 退出 Chart 系统时，我第一时间就跟进，把自己手搓的 Chart 系统给改了。
结果是网站的样式得到了统一，毕竟mantine作者的css水平比我高到不知道哪里去。可是它功能出现了一定量的缺失。

[Zhang Accounting](https://github.com/zhang-accounting/zhang) 项目中首页是有一个复合表格的，一个线图来表示账户余额，一个柱状图用来显示每日的收入与支出。
自己手搓的时候可以直接使用 `ComposeChart` 就可以完成功能了，但是 Mantine 迟迟没有引入这个集成。我大概在 5 月份的时候就这个问题[发了一个提问](https://github.com/orgs/mantinedev/discussions/6230)，大概得 7 月底的时候才把[功能给实现](https://github.com/mantinedev/mantine/commit/f5ef82fc33c2a9df7d2b28d710aeef6be90a30b9)

在需要自己尝试去改一些东西的时候，Mantine 这种集成度很高的框架使用起来就很难受了。

## shadcn/ui 神兵天降

没错，就选它！都给她亮灯！ shadcn/ui 似乎在业界里面称之为 headless ui，我也不太懂，但是她却是解决了我上面的各种难点。

一是 css 的统一，基本上你就是在写 tailwind，无论是组件自带的参数还是自己定制的参数都是 tailwind 的原生类，也少了一些类似于 `Group`， `Stack` 和 `Grid` 的重复封装，因为 tailwind 里面就可以很轻松的实现这些功能了。

二是 shadcn/ui 的组件都是单独引入到你的 `src/component` 文件夹里面的，而不是当作一个依赖引入，所以你可以很轻松的去更改他们。

三是 AI 自动补全/代码生成的场景下，对于基于 tailwind 的UI库来说体验太好了，AI可能不能理解 mantine自己写的东西，但是它完全可以理解 tailwind，所以补全出来的代码可用性极其高。
同时 shadcn/ui的流行度也很高，所以补全的可靠性也比其他库高很多。

四是 因为 shadcn/ui 的流行度高，所以社区里面会的人也多，意味着如果你的项目是开源项目的话，贡献者无需通过学习就可以直接贡献你的项目。

一个额外的好消息是：上面讲到的很好用的 hooks 库 `@mantine/hooks` 是一个没有依赖的纯粹库，意味着他可以用在任何UI框架里面，这也是我保留在我项目里面的唯一 mantine 遗产。

## 总结
选 shadcn/ui 无论是何种意义上都是能胜任作为web ui的第一梯队的，虽然它的组件丰富度并不够 mantine 高，但是已经能涵盖 90% 以上的业务场景了。所以选她！
