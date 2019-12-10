 - title = 更好的 IDE 配置.RUST
 - url = rust_better_ide
 - tags = 
 - datetime = 2018-12-11 02:51:19 +0800

这段时间一直忙于折腾 Rust，自从 Rust 2018 Edition 出来之后，一个很明显的感受就是写起来更加符合一个现代化编程语言的样子，当然也有可能是我的水平太低了，还不足以体验到 Rust 那种非人类的写法和特性。

这一系列文章会是我记录 Rust 学习路程的文章，那么自然而然地就是从环境配置开始了。

> PS: 这一系列的文章都是以 MacOS 为基础，不会过多涉及 自编译 Rust、环境折腾等等内容，更加注重在如何高效地进行 Rust 开发和 Rust学习技巧。

<!--more-->

## Rustup

Rust 官方推荐使用 Rustup 来安装，这是一个相对好的软件，他可以帮你管理一系列的 Rust 生态。它在某种程度上像 Python 的 `pipenv` ，Node 的 `nvm` 和 `n` 。Rust 的环境需要装很多东西：

- `cargo` 项目管理和依赖管理
- `rust-std` Rust 的 std 库，用于代码提示和分析
- `rustfmt` 用于格式化代码
- `cargo-watch` 监控文件修改以便重启服务的插件

等等，很多很多的配套软件生态。同时 Rust 自己也有三个大版本`stable` `beta` `nightly` 。三个版本之间的组件也各不相同。因此在版本切换的时候就需要同时更新相对于的生态组件。Rustup 就很好的帮助我们管理。

安装就不过多描述，[详情可以查看这里](https://rustup.rs/)

## IDE 的选择

目前来说，Rust 最好用的有三个编译器支持 `vim` `vs code` `JetBrains IntelliJ`

当然如果你愿意折腾其他的IDE，可以查阅这里 [Are we IDE yet](https://areweideyet.com/)

我个人大部分时间用的是 `JetBrains Clion` ，实际上是跟 `IntelliJ` 是一样的。小部分时间在使用 `vs code` 。

这里我会讲一些我日常用的 IDEA 插件

### Rainbow Brackets

![rainbow-brackets.jpg](https://i.loli.net/2018/12/11/5c0f2171407a1.jpg)

这个东西可以让你更加直观地匹配到括号的范围

### Highlight Bracket Pair

![highlight bracket pair.jpg](https://i.loli.net/2018/12/11/5c0f221588cbb.jpg)

在一些复杂的函数里面，可以可以比较清晰地看到当前 block 的范围

### Git Conflict

这个插件是用来高亮 conflict 的范围，不需要人肉查看冲突的范围在哪个部分

### Active Intellij Tab Highlighter 

![tab-highlighter.jpg](https://i.loli.net/2018/12/11/5c0f221598f1a.jpg)

IntelliJ 的高亮 TAB 一直都是一个很麻烦的问题，所以这个插件可以自定义颜色用来高亮当前的 TAB



## 常用的几个 Cargo 组件

### [cargo-watch](https://github.com/passcod/cargo-watch)

cargo-watch 用来自动监听项目文件以重新执行编译工作。目前来说我最经常的使用场景就是

- `cargo watch -x run` 一般用于 web 的开发
- `cargo watch -x test` 用于写库时自动重新跑 Testcase

### Cargo doc

这个就是自带的命令，用于生成项目的文档