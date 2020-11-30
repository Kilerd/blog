 - title = Rust Web初试
 - url = first-taste-rust-web
 - tags = 
 - datetime = 2017-01-06T23:15:27.000000+08:00
 - template = article.html

Rust 是最近中意的一门语言。相比于 C 和 C++，我更加喜欢 Rust 的语法。

奈何 Rust 的学习曲线太陡了，一直都只能在入门阶段徘徊，没能深入了解 Rust。 个人感觉最大的问题在于没能搞懂 Rust 的所有权、引用借用和生命周期三个方面。

因此，我尝试着用 Rust 来进行 Web 开发，从而加深对 Rust 语法的了解。


<!--more-->


我选用的是 Iron 这个 Web 框架。本质上讲 Iron \(或者说 Rust 的Web框架\)都不能做到像 RoR、Django、Lavaral 那样一站式开发。 Iron 给我的感觉就像 Python 中的 Flask， 甚至更像 Node.js 中的 Koa。

这篇文章尝试介绍下 Iron 这个框架的编写流程，和给予想学习 Rust 的小伙伴们一些帮助和著者的些许理解。

环境选择 Rust + Iron + Tera

项目模型是 TODOLIST

## Iron 基本介绍


Iron 组件的基本介绍：
- `Iron` Iron 主类，用以启动HTTP服务器
- `Router` 路由类，属于 Handler
- `Chain` 中间件链类，用于处理 Handler、AfterMiddleware、BeforeMiddleware、AroundMiddleware

Iron 的组织方式是 MVC：
- MODEL 层用来定义 Web 中用到的模型。通常使用 ORM
- VIEW 层是模版渲染
- CONTROLLER 层用来控制业务逻辑

所以我们根据 MVC 的模式来建立项目结构，在你的 Rust 项目(用 Cargo 创建)`src`文件夹中的结构是这样的：
```
src/
|----controllers
|----|----todo.rs
|----|----mod.rs
|----routers.rs
|----models.rs
|----lib.rs
|----main.rs
```

- `controllers` 文件夹中放的是 CONTROLLER 层的内容， 文件夹内的文件就是 CONTROLLER 分类，分模块编写。
- `routers.rs` 用来单独处理路由
- `models.rs` MODEL 定义文件
- `lib.rs` RUST LIB 格式文件，告知 Rust 这是一个库项目
- `main.rs` RUST APP 格式文件，项目入口文件。

## `Cargo.toml`

我们把项目名称称为 `todolist` ， `cargo.toml` 的依赖信息如下：
```toml
[dependencies]
iron = "*"
router = "*"
tera = "*"
diesel = "*"
lazy_static = "*"
```
- `iron` Iron Web 框架
- `router` Iron Router 库
- `tera` 模版解析库
- `diesel` PostgreSQL 的 ORM 库
- `lazy_static` 延迟加载库

## `lib.rs` 分析
```rust
extern crate iron;
extern crate router;

pub mod controllers;
pub mod models;
pub mod routers;
```

- 引用了了两个外部库 `iron`, `router`
- 定义了三个子模块 `controllers`, `models`, `routers`

## `model.rs`
```rust

struct ToDoItem {
    item_id: i32,
    value: String,
    done: bool,
}
pub struct ToDoList {
    list : Vec<ToDoItem>,
}

impl ToDoList {
    pub fn add(&self, value: &str) {
        // some code
    }

    pub fn delete(&self, item_id: i32) {
        // some code
    }
}
```

这里不多解释，因为使用 ORM 和不使用的MODEL是不一样的。所以不过多分析，这里只是定义了两个结构而已。

## `controllers`
该文件夹中有两个文件 `mod.rs`， `todo.rs`

### `mod.rs`
```rust
pub mod todo;
```
这个文件只是告知该文件夹中有几个子模块，这里定义了一个模块 `todo`。 这是 Rust 的模块定义的固定格式。详情查看 Rust 官方文档。

### `todo.rs`
这里是我们自己定义的关于 TODOLIST 业务的 CONTROLLER
```rust
use iron::status;
use iron::prelude::*;

pub fn todo_show(_: &mut Request) -> IronResult<Response> {
    Ok(Response::with((status::Ok, "todo list")))
}

pub fn todo_add(_: &mut Request) -> IronResult<Response> {
    Ok(Response::with((status::Ok, "add page")))
}
pub fn todo_delete(_: &mut Request) -> IronResult<Response> {
    Ok(Response::with((status::Ok, "delete page")))
}
```

这个文件按照 Iron 框架处理函数的格式写了三个函数(都是简单的返回纯文本)。

## `routers.rs`
```rust
use router::Router;
use controllers::todo::*;

pub fn router_generator() -> Router {
    let mut router = Router::new();
    router.get("/", todo_show, "todo_show");
    router.post("/add", todo_add, "todo_add");
    router.post("/delete", todo_delete, "todo_delete");
    router
}
```
router 的构建函数， 在内部把刚刚写的几个 CONTROLLER 添加至路由中。

## `main.rs`
```rust
extern crate iron;
#[macro_use]
extern crate tera;
#[macro_use]
extern crate lazy_static;

extern crate todolist;

use iron::prelude::Iron;
use tera::{Tera, Context};
use yolk::routers::router_generator;


// 延迟渲染模版
lazy_static! {
    pub static ref TEMPLATES: Tera = {
        let tera = compile_templates!("templates/**/*");
        tera
    };
}


fn main() {
    // 启动 Iron 服务器
    let _server = Iron::new(router_generator()).http("localhost:3000").unwrap();
    println!("On 3000");
}
```
- 引入几个外部模块 `iron`, `lazy_static`
- 引入自己这个模块 `todolist`
- 使用刚刚写的`router_generator` 函数来作为 `Handler` 启动 Iron

## TEMPLATE 库的一些看法
Rust 在 Web 这个方向发展并没有太快。所以在模版上并没有太多优质 的库。在我看来，有两个库是值得参考一下的。
- [Tera](https://github.com/Keats/tera)
- [Handlebars-iron](https://github.com/sunng87/handlebars-iron)

`handlebars-iron` 基本符合 Iron 的设计思想，采用 `AfterMiddleWare` 的思想，对 Controller 的入侵是最小的，而且还可以做到 watch 特性，即无需重启进程都可以重新渲染模版（Rust 是编译性语言，进程执行后就已经把模版渲染好了，所以修改模版文件并不会自动生效。）。有兴趣的可以读者自己阅读相关文献。

著者是中意 Tera 更多的，一下是 Tera 的简单使用：
```rust
// 延迟加载模版渲染
lazy_static! {
    pub static ref TEMPLATES: Tera = {
        let tera = compile_templates!("templates/**/*");
        tera
    };
}

fn main() {
    let context = Context::new(); // 参数类
    context.add("KEY", "VALUE"); // 添加一个参数
    let content = TEMPLATES.render("test.html", context); // 渲染 test.html 这个模版，返回的是 Optional
}
```
如果要使用在 Iron 中，大致是这样的：
```rust
pub fn todo_show(_: &mut Request) -> IronResult<Response> {
    let context = Context::new(); // 参数类
    context.add("KEY", "VALUE"); // 添加一个参数
    let content = TEMPLATES.render("test.html", context);
    Ok(Response::with((status::Ok, content.unwrap()))
}
```
说 Iron 完成度低的原因就在于，返回的类型是 IronResult. 并没有做到直接返回 RUST 基本类型即可。

不过有能力者可以自己写一个宏来处理。


## 对于 ORM 的一些看法

ORM 的使用不方便大概是我放弃用 Rust 写 Web 的主要原因之一。实在是太不优雅了。

[Diesel](https://github.com/diesel-rs/diesel) 是我在那么多 ORM 中比较中意的一个，只支持 PostgreSQL。
感兴趣的读者可以关注一下。


## 关于 Iron
Iron 目前对于使用者来说，就是写很多很多的 MiddleWare， 然后用 `Chain` 类串联起来。 并不能最太多的东西。如果偏要写很多的东西的话，你会发现直接用底层的`hyper`库直接重新实现一个 Web 框架更为实际。

`Router` 类的使用也是挺不方便的，并不能很轻易地让一个 CONTROLLER 绑定在同一链接的两个方法上。这个设计的初衷也是很好的，避免无畏的可访问页面。


## 结言
文章就写完了，主要讲的是怎么构建一个可以扩展的网站框架，而不是网站实现的细节。
希望你有所收获，同时也希望有更多的人喜欢 Rust 这门优雅的语言。