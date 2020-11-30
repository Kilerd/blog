 - title = Actix通过什么方法来实现路由注册的.RUST
 - url = rust-how-actix-register-route-in-rust
 - tags = 
 - datetime = 2019-05-13T08:40:47.000000+08:00
 - template = article.html

如果你写过 `actix-web` 1.0 的代码，会发现在路由注册的函数中，你可以传入各种不同签名的函数题。

```rust
App::new()
        .service(
            web::scope("/admin/")
                .service(
                    web::resource("/article").route(
                        web::post().to(post_method),
                        web::delete().to(delete_method)
                    ),
                )
```

不难发现，根据业务的不同，传入 `to` 方法中的函数签名必然会不同，那么 Actix 是怎么处理的呢？或者说是怎么实现这个功能的。接下来我们将一步一步实现这一个类似的需求。

<!--more-->

## 最小的执行框架

为了实现这个功能，我们先模拟出一个最小的框架：有一个路由 `Router` 他里面有一个方法 `to` 来注册 handler，为了方便同时关注我们所想的，handler 这里就设计成只能返回 `String`。

```rust
#[derive(Debug)]
enum Method {
    Head,
    Option,
    Get,
    Post,
    Patch,
    Put,
    Delete,
}

struct Router;

impl Router {
    pub fn to<H>(&self, method: Method, handler: H) -> &Self
    where
        H: Fn() -> String,
    {
        println!("handle route {:?}", method);
        self
    }
}

fn public_route() -> String {
    "hello world".into()
}

fn main() {
    let router = Router {};
    router.to(Method::Get, public_route);
}

```

代码：https://gist.github.com/8c8c8ad0dbe21d0ebacc8d9f6f5f5c78

在这个演示代码中 17L，限定了传入的 handler 只能是 `Fn()->String`，意思是没有参数，同时返回值为 `String`

## 允许传入不同参数

Rocket 和 Actix 都不约而同的采用了 Request Guard 的方式来对路由进行限制或者扩展，有一个例子是说，如果我们希望一个路由只有授权之后才能访问，那么这个 Handler 是这样签名的：

```rust
fn private_route(token: Token) -> String {
    "hello private world".into()
}
```

当我们注册到 `Router` 时，必然需要调用 `to` 方法，`router.to(method::Post, private_route)` ，那会出现一下的错误

```
error[E0593]: function is expected to take 0 arguments, but it takes 1 argument
  --> src/main.rs:37:6
   |
29 | fn private_route(token: Token) -> String {
   | ---------------------------------------- takes 1 argument
...
37 |     .to(Method::Post, private_route);
   |      ^^ expected function that takes 0 arguments

error: aborting due to previous error
```

错误原因是说 `to` 里面的 handler 范型约束了不能带参数，而 Rust 又不能写出类似 `where H: Fn() -> String | Fn(Token) -> String` 的或关系的骚操作，所以只能把这些关系再抽象一层，于是就抽象出了 Trait `HandlerFactory`。 这个 Trait 只是把不同的handler 包装成相似的签名。

```rust
trait HandlerFactory<P> {
    fn call(&self, _: P) -> String;
}
```

这下我们就可以通过 `handler.call()` 来执行这些 handler。

同时，我们对刚刚这两个Handler 实现一下这个 Trait `HandlerFactory`

```rust
impl<F> HandlerFactory<()> for F where F: Fn() -> String {
    fn call(&self, _: ()) -> String {
        (self)()
    }
}

impl<F> HandlerFactory<(Token, )> for F
    where F: Fn(Token) -> String,
{
    fn call(&self, params: (Token, )) -> String {
        (self)(params.0)
    }
}
```

顺便再改一下 `to` 的签名，让 `to` 接受 `HandlerFactory` 的类型就可以把刚刚的两个handler 都通过 `to`方法来注册了。

详情代码看这里：https://gist.github.com/3b166bc90bd6ee6dcb20d3b1f751e119

## FromRequest 的抽象

在第二个handler 里面，我们传入了`Token` 类型的参数，同时用了 `impl<F> HandlerFactory<(Token, )> for Fwhere F: Fn(Token) -> String` 来注册签名，那么如果我们有大量不同类型的参数的话，是不是都要一个一个明确的写出声明呢？其实不然，我们可以给这些类型共同实现一个叫 `FromRequest` 的Trait，来统一处理。

```rust
trait FromRequest {
    fn from_request() -> Self where Self: Sized;
}
```

在 `impl FromRequest for Token`, `impl FormRequest for String` ... 的方法实现之后，Router 知道这是一个「实现了 `FromRequest` Trait 」的类型就可以了。意味着在 `to` 的签名里面可以换成 Trait 的名字，而不是某种具体的类型。又因为我们需要告诉 `HandlerFactory` 这些参数的具体类型，所以需要在其加多一个范型参数。

```rust
trait HandlerFactory<P> {
    fn call(&self, _: P) -> String;
}
```

再看看对单个参数的实现

```
impl<F, P> HandlerFactory<(P, )> for F
    where F: Fn(P) -> String,
          P: FromRequest
{
    fn call(&self, params: (P, )) -> String {
        (self)(params.0)
    }
}
```

在 3L 我们明确地指出 P 需要是实现了 `FromRequest` 的 类型。 好，需求就实现了，具体实现在[这里](https://gist.github.com/4ee6eb1e3dda0f6e7c8858a1c58026ed)

## 多个参数怎么办

handler 里面不可能永远都只有一个参数吧。再看看上面的那个代码，我们在 `HandlerFactory<(P, )> ` 其实是传入了一个 Tuple，里面只有一个值，类型是 P，同时 P 还是 FromRequest 的类型。 

那是不是意味着只要我们有一个 `HandlerFactory<(P, P2)> ` 的实现就可以完成两个参数的传入了呢？没错就是这样，所以我们可以写下以下的代码：

```rust
impl<F, P, P2> HandlerFactory<(P, P2)> for F
    where F: Fn(P, P2) -> String,
          P: FromRequest,
          P2: FromRequest
{
    fn call(&self, params: (P, P2)) -> String {
        (self)(params.0, params.1)
    }
}
```



那三个参数呢？四个参数呢？五个呢？以此往下，是需要重复写大量的 `impl `代码的。但是有一个问题是，对于不同的参数，它的函数签名又不一样，不能用「为某种类型实现某种 Trait」的方式一次性写完。但是又不想写那么多重复的代码怎么办？

在详细看看一个参数的签名和两个参数的签名，其实只有几个地方不一样，而且大致都能复用，那么这时候宏的作用就出来了。这里我从 actix 模仿了一个出来。

```rust
macro_rules! factory_tuple ({ $(($n:tt, $T:ident)),+} => {
    impl<F, $($T,)+> HandlerFactory<($($T,)+)> for F
    where F: Fn($($T,)+) -> String,
    {
        fn call(&self, param: ($($T,)+)) -> String {
            (self)($(param.$n,)+)
        }
    }
});
```

这里 Actix 的源码在[src/handler.rs#L376](<https://github.com/actix/actix-web/blob/df08baf67f166d2d75118b859f1049b01944daf4/src/handler.rs#L376>)

关于 Rust 宏的签名可以通过[这个网站](<https://lukaslueg.github.io/macro_railroad_wasm_demo/>)来查看它的签名。

那么我们在实现不同参数的时候就可以通过以下简单的代码来简单实现：

```rust
factory_tuple!((0, A));
factory_tuple!((0, A), (1, B));
factory_tuple!((0, A), (1, B), (2, C));
```

对于三个参数的宏实现，展开之后是这个样子的：

```rust
impl<F, A, B, C, > HandlerFactory<(A, B, C, )> for F
    where F: Fn(A, B, C ) -> String,
{
    fn call(&self, param: (A, B, C, )) -> String {
        (self)(param.0, param.1, param.2 )
    }
}
```

具体代码可以[看看这里](https://gist.github.com/7610290a37934703a4450888afb54f2f)



## 最后

这个场景确实是很常见的，这里用了以下几个特性来实现了这个功能：

- 为某种类型实现Trait
- 为「实现了某种Trait」的类型实现Trait
- 利用宏消除重复代码

### 彩蛋

看回 [acitx-web handler](<https://github.com/actix/actix-web/blob/df08baf67f166d2d75118b859f1049b01944daf4/src/handler.rs#L411>) 的实现，它只实现到了10个参数，那是不是说只要写出 11 个参数的 handler 就会报错呢？我们感觉来试一下。

```rust

use actix_web::{web, App, HttpServer, Responder};

fn a_lot_parameters(
    a: web::Path<String>,
    b: web::Path<String>,
    c: web::Path<String>,
    d: web::Path<String>,
    e: web::Path<String>,
    f: web::Path<String>,
    g: web::Path<String>,
    h: web::Path<String>,
    i: web::Path<String>,
    j: web::Path<String>,
    //    k: web::Path<String>,
    //    l: web::Path<String>,
    //    m: web::Path<String>,
) -> impl Responder {
    "hello world"
}

fn main() {
    HttpServer::new(move || {
        App::new().route(
            "/{a}/{b}/{c}/{d}/{e}/{f}/{g}/{h}/{i}/{j}/{k}/{l}/{m}",
            web::get().to(a_lot_parameters),
        )
    })
    .bind(("0.0.0.0", 8000))
    .unwrap()
    .run();
}
```

10个的情况正常启动了项目。好我们吧注释去掉一个，再启动看看会不会报错

```
error[E0277]: the trait bound `fn(actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>) -> impl actix_web::responder::Responder {a_lot_parameters}: actix_web::handler::Factory<_, _>` is not satisfied
   --> src/main.rs:121:24
    |
121 |             web::get().to(a_lot_parameters),
    |                        ^^ the trait `actix_web::handler::Factory<_, _>` is not implemented for `fn(actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>, actix_web::types::path::Path<std::string::String>) -> impl actix_web::responder::Responder {a_lot_parameters}`

error: aborting due to previous error
```

YEAH，预期地报错了✌️