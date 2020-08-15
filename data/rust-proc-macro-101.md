 - title = Rust 过程宏 101
 - url = rust-proc-macro-101
 - tags = 
 - datetime = 2020-06-11T18:43:26.000000+08:00
 - template = article.html

在 Rust 1.45 中，Rust 的{卫生宏}(Hygienic macro)迎来了 stable 版本，这意味着{过程宏}(Procedural macro)和{声明宏}(Declare macro)板块全面稳定。那么是时候该认真学习一边过程宏的内容了。

过程宏相比于声明宏的灵活度更加高，其本质是输入一段 Rust 的 AST 产生一段 AST 的函数，同时 Rust 提供了三种不一样的语法糖来满足不同的使用场景。

- {函数式}(Function-like)的宏 - 这跟声明宏很类似
- Derive 宏 - `#[derive(CustomDerive)] ` - 一个用于结构体和枚举类型的宏
- {参数宏}(Attribute macros) - `#[CustomAttribute]` 


<!--more-->



## 行为影响

这三种宏的的效果也不完全一致。 {函数式宏}(Function-like macro) 和 {参数宏}(Attribute macros) 拥有**修改原AST**的能力，而Derive 宏就只能做追加的工作。

### {函数式宏}(Function-like macro) 

```rust
#[proc_macro]
pub fn my_macro(INPUT_TOKEN_STREAM) -> TokenStream {
    OUTPUT_TOKEN_STREAM
}

my_macro!(INPUT_TOKEN_STREAM)
```

经过编译之后，6L 就会被**替换**成 `OUTPUT_TOKEN_STREAM`

### Derive 宏

```rust
#[proc_macro_derive(MyMacro)]
pub fn derive_my_macro(INPUT_TOKEN_STREAM) -> TokenStream {
	OUTPUT_TOKEN_STREAM
}

#[derive(MyMacro)]
struct MyStruct {...}
```

经过编译之后， 6-7L 就会被编译成以下：

```rust
#[derive(MyMacro)]
struct MyStruct {...}

OUTPUT_TOKEN_STREAM
```

可见，原来的 `MyStruct` 并不会被影响，也无法改变，而能做的只是在其后追加新的AST，通常用来生成 `Builder` 和 `impl Blabla for MyStruct` 从而改变`MyStruct` 的行为。

### {参数宏}(Attribute macros)

```rust
#[proc_macro_attribute]
pub fn my_macro(ATTR_TOKEN_STREAM, INPUT_TOKEN_STREAM) -> TokenStream {
    OUTPUT_TOKEN_STREAM
}

#[my_macro(a=1,b=2)]
fn method() {...}
```

在这个例子中

- `ATTR_TOKEN_STREAM` 为 `a=1, b=2`
- `INPUT_TOKEN_STREAM` 为 `fn method() {...}`

而编译之后， 6-7L 编译成 `OUTPUT_TOKEN_STREAM`

## 入门例子使用

了解了过程宏的相关基本知识之后呢，就可以根据自己的需求选择不同的实现方式来简化代码。下面会以一个例子来介绍怎么设计一个 Derive 宏，不感兴趣的可以跳过这个章节。 

该章节的代码实现已经放在了 [Github kilerd/rust-derive-macro-demo](https://github.com/Kilerd/rust-derive-macro-demo)

### 非过程宏实现

在一次业务实现中，需要根据错误类型返回前端不同的错误码和消息。这意味着我们对于不同的错误需要三个不同的字段

- HTTP {返回码}(status code)
- 错误的 Code
- 错误的具体描述内容

返回给前端的结构是这样的

```json
{
    "code": "INVALID_EMAIL",
    "message": "Invalid email"
}
```

对于Java来说，这很容易用一个枚举类型来描述这样的需求：

```java
public enum BusinessError {

    InvalidEmail(400, "INVALID_EMAIL", "Invalid email"),
    InvalidPassword(400, "INVALID_Password", "Invalid password");

    int httpCode;
    String code;
    String message;
    BusinessError(int httpCode, String code, String message) {
        this.httpCode = httpCode;
        this.code = code;
        this.message = message;
    }
}
```

在这种情况下需要增加错误类型的时候，只需要在 4L 处新增即可，影响的范围不大。

而对于Rust来说，{枚举类型}(enum)更加像是一种数据结构，所以无法像 Java 一样在 3-4L 里面储存这样的信息，为了达成同样的效果，我们需要在函数里面自己实现返回的内容：

```rust
pub enum BusinessError {
    InvalidEmail,
    InvalidPassword
}

impl BusinessError {
    pub fn get_http_code(&self) -> u16 {
        match self {
            BusinessError::InvalidEmail => 400,
            BusinessError::InvalidPassword => 400,
        }
    }
    pub fn get_code(&self) -> String {
        match self {
            BusinessError::InvalidEmail => String::from("INVALID_EMAIL"),
            BusinessError::InvalidPassword => String::from("INVALID_PASSWORD"),
        }
    }
    pub fn get_message(&self) -> String {
        match self {
            BusinessError::InvalidEmail => String::from("Invalid email"),
            BusinessError::InvalidPassword => String::from("Invalid password"),
        }
    }
}
```

实际看起来问题也不是很大，可以很好的完成业务需求，但是考虑一下增加错误类型这个业务场景，那么就需要在 3L，10L，16L，22L处做修改，影响的范围就很大了。

同时我们可以很轻松的看得出来对于 `get_code` 和 `get_message` 都是对枚举值进行简单的字面格式转换，那么人工做这么一件事件是很耗时的。这个时候就可以让过程宏代替我们实现 `impl BusinessError {...}` 里面的所有内容。

### Derive 宏的建立

为了简化代码，我们决定把 `BusinessError` 改造成以下的格式：

```rust
#[derive(DetailError)]
pub enum BusinessError {
    InvalidEmail,
    #[detail(code=400, message="this is an invalid password")]
    InvalidPassword
}
```

对于错误类型 `InvalidEmail` ，我们默认返回 httpCode `400`， code `INVALID_EMAIL` ， message `Invalid email`。但是我们可以通过 `#[detail(code, message)]` 来定制化 `httpCode` 和 `message`。

我们先拟定需要创建的宏的名称为 `DetailError` 。那么第一步先把项目改成 workspace 的目录结构。然后在其下面新增一个 `detail_error `的lib。

```toml
[workspace]
members = [".", "detail_error"]

[dependencies]
detail_error = {path="./detail_error"}
```

通过 `cargo new detail_error --lib` 创建好 lib 后，需要对 `detail_error/Cargo.toml` 增加「这个库是过程宏库」才可以访问到 `proc_macro` 这么一个特殊的库。

```toml
[lib]
proc-macro = true
```

其后，在 `detail_error/lib.rs` 中声明过程宏处理函数：

```rust
use proc_macro::TokenStream;

#[proc_macro_derive(DetailError, attributes(detail))]
pub fn detail_error_fn(input: TokenStream) -> TokenStream {
    "".parse().unwrap()
}
```

自此，我们的代码就不会报错了，但是我们还没有在`detail_error_fn` 里面返回我们期望的 `impl BusinessError{...}` 的 AST。实际上这个宏没有做任何事情。



### 实现 `get_http_code` 方法

第一步，我们需要先把`TokenStream` 格式化成我们期望的枚举结构。那么就用到了 `syn` 库，这个库提供了`parse_macro_input!` 这个宏来更加方便得访问 AST，在我们把 `TokenStream` 格式化成 `ItemEnum` 后就可以用`dbg!` 来查看其内部的数据了。

```rust
let enum_struct = parse_macro_input!(input as syn::ItemEnum);
dbg!(enum_struct);
```

```rust
enum_struct = ItemEnum {
    attrs: [],
    vis: Public(...),
    enum_token: Enum,
    ident: Ident { ident: "BusinessError", span: #0 bytes(64..77),},
    generics: Generics {...},
    brace_token: Brace,
    variants: [
        Variant {
            attrs: [],
            ident: Ident {ident: "InvalidEmail", span: #0 bytes(84..96),},
        },
        Comma,
        Variant {
            attrs: [...],
            ident: Ident { ident: "InvalidPassword", span: #0 bytes(165..180),},
        },
    ],
}

```

在这里我们先 hardcode 所有的返回值是 `400`，先不理会在 `#[detail]` 中的配置，那么我们最关心的是

- `.ident` - 枚举的名字
- `.variants[].ident` - 枚举里面有多少成员，以及成员的名字

那么我们可以很轻松的拿到这些值：

```rust
let ident = &enum_struct.ident;
let variants_ident:Vec<&Ident> = enum_struct.variants.iter().map(|variant| &variant.ident).collect();
```

但是拿到这些值之后，我们的期望还不够，我们期望的是构建出以下的代码： 

```rust
impl BusinessError {
    pub fn get_http_code(&self) -> u16 {
        match self {
            BusinessError::InvalidEmail => 400,
            BusinessError::InvalidPassword => 400,
        }
    }
}
```

想比如手动拼 `TokenStream` ，`quote` 这个库提供了更加人性化的方式来生成`TokenStream`。我们可以通过以下的代码来生产我们期望的那个函数：

```rust
let output = quote! {
    impl #ident {
        pub fn get_http_code(&self) -> u16 {
            match self {
                #(#ident::#variants_ident => 400,)*
            }
        }
    }
};
```

这里面一些 `quote` 特定的文法

- `#VARIABLE` 可以访问到当前作用域下的同名变量
- `#(   )*` 用于展开循环

自此，我们完成了`get_http_code`的方法实现。

### 实现 `get_code` 方法

在`get_http_code` 中我们了解了怎么输出一整个函数，对于 `get_code` 来说，每一个枚举分支类型返回的值都是不同的，这意味着我们在 `let variants_ident:Vec<&Ident> = enum_struct.variants.iter().map(|variant| &variant.ident).collect();` 这里就不能简单的拿到枚举成员的 `Ident` 了，我们需要在循环内构件出类似 `BusinessError::InvalidEmail => String::from("INVALID_EMAIL")` 这样的完整分支语句。这里其实也是很简单的。

```rust
let code_fn_codegen:Vec<proc_macro2::TokenStream> = enum_struct.variants.iter().map(|variant| {
        let variant_ident = &variant.ident;
        let content = inflector::cases::screamingsnakecase::to_screaming_snake_case(&variant_ident.to_string());
        quote! {
            #ident::#variant_ident => String::from(content)
        }
    }).collect();
```

> 1. 这里为了简单的演示效果，才用了 `inflector` 这个字符串格式转换库
> 2. 这里用到了 `proc_macro2` 这个库，下文会讲为什么需要和其与`proc_macro`的区别

然后再拼凑 `get_code` 方法签名：

```rust
pub fn get_code(&self) -> String {
    match self {
        #(#code_fn_codegen,)*
    }
}
```

`get_message`的方法也是同样的道理这里就不重复描述了。



### 从 `#[detail]` 中读取数据实现配置化

对于每一个 Variant 的 attr 数据都会储存在 `attrs` 这个字段中。 `#[detail(code=400, message="this is an invalid password")]` 就会被格式化成以下的AST： (省略了很多没必要的字段)

```rust
attrs: [
    Attribute {
        path: Path { segments: [ PathSegment { ident: Ident { ident: "detail",}},],},
        tokens: TokenStream [
            Group {
                stream: TokenStream [
                    Ident { ident: "code", },
                    Punct { ch: '=', },
                    Literal { lit: Lit { kind: Integer, symbol: "400" }},
                    Ident { ident: "message", },
                    Punct { ch: '=', },
                    Literal { lit: Lit { kind: Str, symbol: "this is an invalid password" }},
                ],
            },
        ],
    },
],
```

可以看到 `code=400, message="this is an invalid password"` 一样被格式化成了 `TokenStream` 。然而取数据出来也不是一件很简单的事情。所以为了解决这个问题，`darling` 应运而生，其借鉴了 `serde` 的思想，把`TokenStream` 反序列化成自定义的结构。

根据 `darling` 的写法，我们需要把我们期望的数据写成结构体：

```rust
// derive FromDeriveInput, 表示这个结构体可以用 `syn::DeriveInput` 转换过来
#[derive(Debug, FromDeriveInput)]
// darling 自身的配置，接受 `detail` attr的数据，只允许 enum 的结构体，struct 报错。
#[darling(attributes(detail), supports(enum_any))]
struct DetailErrorEnum {
    // enum 的名称
    ident: syn::Ident,
    // enum 的枚举成员格式化成 DetailErrorVariant 
    data: darling::ast::Data<DetailErrorVariant, darling::util::Ignored>,
}

#[derive(Debug, FromVariant)]
#[darling(attributes(detail))]
struct DetailErrorVariant {
    ident: syn::Ident,
    // fields 的数据， 指的是 `InvalidEmail(String)` 里面的 `String`
    fields: darling::ast::Fields<syn::Field>,
    // 这里表示从 `FromMeta` 中取数据，这里特指 `#[detail(code=400)]`
    #[darling(default)]
    code: Option<u16>,
    // 这里表示从 `FromMeta` 中取数据，这里特指 `#[detail(message="detail message")]`
    #[darling(default)]
    message: Option<String>,
}
```

接着我们需要把 `proc_macro::TokenStream` 转换成 `proc_macro2::TokenStream` 再转换成 `syn::DeriveInput` 再转换成 `DetailErrorEnum`

```rust
let proc_macro2_token = proc_macro2::TokenStream::from(input);
let derive_input = syn::parse2::<DeriveInput>(input).unwrap();
let detail_error: DetailErrorEnum = DetailErrorEnum::from_derive_input(&derive_input).unwrap();
```

通过`dbg!()` 可以看到反序列化之后的结果：

```rust
[detail_error/src/lib.rs:39] &detail_error = DetailErrorEnum {
    ident: Ident { ident: "BusinessError", },
    data: Enum(
        [
            DetailErrorVariant {
                ident: Ident { ident: "InvalidEmail", },
                fields: Fields { style: Unit, fields: [], },
                code: None,
                message: None,
            },
            DetailErrorVariant {
                ident: Ident { ident: "InvalidPassword", },
                fields: Fields { style: Unit, fields: [], },
                code: Some( 500, ),
                message: Some(  "this is an invalid password", ),
            },
        ],
    ),
}

```

这样的结果和过程都比直接操作 `TokenStream` 更加直观和可靠。

> 但是至今我还不知道对于 `#[detail(code=400, message("password {} is invalid", p1))]` 这种 `message` 是{一组的数据}(group token stream)怎么用 `darling` 来写

这个时候就可以遍历 `detail_error.data[]` 来完成 `get_http_code `的 AST 生成

```rust
let ident = &detail_error.ident;
let variants = detail_error.data.take_enum().unwrap();
let http_code_fn_codegen: Vec<proc_macro2::TokenStream> = variants.iter().map(|variant| {
    let variant_ident = &variant.ident;
    let http_code = variant.code.unwrap_or(400);
    quote! {
        #ident::#variant_ident => #http_code
    }
}).collect();
```

相比于之前的hardcode，现在我们在 5L 取出了在 `#[detail(code=500)]` 中的值。

同理 `get_message` 也可以用同样的方法生成：

```rust
let message = variant.message.clone().unwrap_or_else(|| {
    inflector::cases::sentencecase::to_sentence_case(&variant_ident.to_string())
});
```

自此整个 `BusinessError` 就用过程宏改造完成了。但是真实的业务还没有那么简单，举个例子说，对于认证错误(`AuthenticationError`)，通常需要返回具体的错误内容，这意味着 `message` 需要跟随着变化。也就是说真正的代码是长这个样子的：

```rust
enum BusinessError {
    AuthenticationError(String)
}
fn get_message(&self) {
    match self {
        BusinessError:AuthenticationError(p1) => format!("with detail {}", p1),
    }
}
```

那么我们之前的过程宏并不支持这样的特性，其实改造也很简单，在 darling 的 `DetailErrorVariant` 的 `fields` 里面就存有着 `String` 这个信息，那么我们只需要在循环体中构建出类似 `#ident::#variant_ident#fields => format!(#message, #fields)` 的语句即可。 感兴趣的读者可以试着让这个demo 支持该功能。

> 在我的真实业务场景用使用 `#[detail(message="with detail {0}")]` 这样的方法来访问具体的字段的

## 关于过程宏的一些实践和认知

### `proc_macro` 和 `proc_macro2` 的区别

前者是 rust 中为 过程宏库（在 `Cargo.toml` 中声明了 `#[lib] proc_macro=true`）中才能访问的特殊库， 而 `proc_macro2` 是与 `proc_macro` 基本一致，但是只是一个普通的库，所以 `syn` , `quote` , `darling` 这些都是建立在 `proc_macro2` 之上的， 所以在我们编写过程宏的时候基本上都是先把 `proc_macro::TokenStream` 转换成 `proc_macro2::TokenStream` 进行各种处理，最后才转换成 `proc_macro::TokenStream` 交回给 rustc。

### 关于测试

根据第一点的前提下，在转换成 `proc_macro2::TokenStream` 之后其实就跟过程宏没任何关系了，在抽象出一个独立的函数来处理和生成 `proc_macro2::TokenStream` ，我们就可以很轻松的对这个方法进行测试：

```rust
#[proc_macro_derive(DetailError, attributes(detail))]
pub fn detail_error_fn(input: TokenStream) -> TokenStream {
    handler(input.into()).into()
}

fn handler(input: proc_macro2::TokenStream) -> proc_macro2::TokenStream {
    // real handler
}
```

简单来说，我们可以通过 `quote::quote!`来生成 `input` 对 `handler` 测试：

```rust
#[test]
    fn it_works() {
        let input = quote! {...};
        let expected_output = quote! {...};
        let output = handler(input);
        assert_eq!(expected_output.to_string(), output.to_string());
    }
```

> 7L 里面简单的用了 `to_string()` 来判断是否一致，导致输出的代码其实并没有带缩进，如果有需要可以用 `syn::visit`模块进行更加友善的结果输出。

### 用了过程宏之后，为什么就没有代码提示了

这点很正常，因为`impl BusinessError {...}` 里面的内容是编译时生产的，确实是没有办法做到代码提示。试想下有了代码提示又跳转到哪里呢？

其实这个问题也不是无解的。通常的做法是建立一个 `Trait DetailError` 里面定义好我们需要的三个函数，然后再通过过程宏为 `BusinessError` 实现 `impl DetailError for Business {...}`。 这样代码提示和跳转就可以跳到 `DetailError`的定义里面去了。

为此我们需要把原来 `detail_error` 这个lib 改名成 `detail_error_macro` ，再创建一个新的lib 叫 `detail_error` 来定义 Trait `DetailError`。 

这点其实是 Rust 的限制，因为过程宏库无法再{暴露}(expose)出其他的任何 Trait 和结构体。

### 注意 ident 和非ident 的处理

`quote::quote!` 这个宏在处理 `String` 类型的时候会自动加上`"` 形成 `"content"` ，正如数字类型会在后面追加具体的类型一样`400u16`。 所以如果通过`format!` 拼凑出一个 ident 之后需要用 `quote::format_ident!` 转换成 ident 类型，或者直接用 `format_ident! ` 代替 `format!` 。

