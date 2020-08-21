 - title = 自动解引用.RUST
 - url = rust-auto-deref
 - tags = 
 - datetime = 2019-04-18T06:11:25.000000+08:00
 - template = article.html

解引用应该说是 Rust 为了解决不采用 Class 来实现对象化编程的一个解决方案。假想一下如果 Python 或者 Java 之流，需要对一个结构体（准确来说应该是类）进行自定义扩展：增加字段，增加方法，重写方法等等，我们可以直接用继承的方式来实现

```python
class Base:
	a: int = 2

class Extend(Base):
	my_self_field: int = 3
```

当一个函数希望传入实现了 `Base` 类的所有实例时，可以直接以 `Base` 为约束，限定其参数范围。在 Java 中就可以使用基类或者 Interface 来约束。

```python
def base_bound(param: Base):
    pass
```

这一套在 Rust 并不适用，在 Rust 中时采用 Struct + Trait 来抽象对象化。所以若想对结构体进行扩展，那么就只能再用一层结构体去包（wrap）住原来的结构体。

```rust
struct MyOwnDerefStruct(String);
```

<!--more-->

这里我们就对 `String` 进行了自己的封装，这里并没有对字段进行扩展，但是这确实在 Rust 中比较常见的场景：一旦我们希望对某个特定的 Struct 实现某个特定的 Trait，同时 Struct 和 Trait 都来自第三方库（不在当前库中定义），那么为了实现`impl Trait for Struct` ，我们就需要解决孤儿定律（Orphan Rule），此时我们就可以用这种简单的包装方式来满足他。

> ##### 什么是孤儿定律 Orphan Rule？
>
> 在 Rust 中， 若想对 Struct 实现一个 Trait， 那么 Struct 和 Trait 一定要有一方是在当前库中定义的。
>
> 这个约束很好理解，也很适用。
>
> 假设一个场景：C 库中对 A 的 Struct 实现了 B 中的 Trait。此时我们在当前库中使用了 C 库和 A 库，那么我们可能会对 A 中的 Struct 误解，其可能已经被继承了很多奇怪的 Trait，会严重影响我们对 Struct 的使用

同时，Rust 为了移除运行时和 GC 的消耗，实现了诸多智能指针：`Box` `Rc` `Arc` 等等。所以可能会出现诸如以下的包装 `let param: Arc<Mutex<Box<Vec<i32>>>>;` 这种在 Python 中只是简单的 `a: List<int>` 的包装。

为了方便这种因为语言特性导致的额外包装，Rust 提供了自动解引用 `Deref` 来简化编程。

```rust
#[lang = "deref"]
#[doc(alias = "*")]
#[doc(alias = "&*")]
#[stable(feature = "rust1", since = "1.0.0")]
pub trait Deref {
    /// The resulting type after dereferencing.
    #[stable(feature = "rust1", since = "1.0.0")]
    type Target: ?Sized;

    /// Dereferences the value.
    #[must_use]
    #[stable(feature = "rust1", since = "1.0.0")]
    fn deref(&self) -> &Self::Target;
}
```

若要使用 Deref Trait，我们先看看 Deref 里面有什么东西：

- `type Target` 指的是我们希望被解引用到那个数据结构。
- `deref()` 提供了一个手动调用解引用到 `&Target` 的方法。

回到我们写的 `MyOwnDerefStruct` 例子，我们包装了 `String` 类型，如果现在有一个接收 `&String` 参数的函数，在没有 Deref 的场景我们需要怎么调用他呢？

```rust
struct MyOwnDerefStruct(String);

fn print(s: &String) {
    println!("{}", s);
}

fn main() {
    let deref_struct = MyOwnDerefStruct(String::from("hello world"));
    print(&deref_struct.0);
}

```

在 L9 中，我们需要先通过 `deref_struct.0` 获取到 `MyOwnDerefStruct` 中的第一个属性 `String` ，然后再通过 `&` 来转换成 `&String` 。

如果我们直接用会 C 中的逻辑 `print(&deref_struct)` ，我们会得到以下的错误信息：

```
error[E0308]: mismatched types
  --> src/main.rs:23:11
   |
23 |     print(&deref_struct);
   |           ^^^^^^^^^^^^^ expected struct `std::string::String`, found struct `MyOwnDerefStruct`
   |
   = note: expected type `&std::string::String`
              found type `&MyOwnDerefStruct`

```



此时如果我们为我们的结构体 `MyOwnDerefStruct` 实现自动解引用的话，以上代码就可以正常编译：

```rust
impl Deref for MyOwnDerefStruct {
    type Target = String;

    fn deref(&self) -> &Self::Target {
        return &self.0;
    }
}
```

在上述代码中，我们告诉 Rust 编译器：「我们期望 `MyOwnDerefStruct` 被解到 `String`」，那么在编译过程中碰到需要 `&String` 时，编译器会自动帮我们转换。而且我们还能写出以下相当 tricky 的代码 `print(&&&&&&&&&&&&&&&deref_struct);`（这代码能跑的原因，可以自行去看看 Rust 内部对 & 的处理）



自动解引用还有一个好处就是，他可以直接寻址到 `Target` 的方法。在我们的场景里面，`String` 中有判断两个字符串是否相等的方法 `eq` 。因为自动解引用的存在，我们并不需要 `deref_struct.0.eq("hello world")` 的写法。  `MyOwnDerefStruct` 可以直接调用 `eq` 方法。

```rust
assert_eq!(true, deref_struct.eq("hello world"));
```

这样就避免了在使用智能指针的时候在代码中出现大量的 `variable_box.0.method()` 。避免了 `.0` 的出现，大大地简化了代码，同时也增加了代码的可读性。

## `variable.deref()` 和 `*variable` 的区别

使用解引用的时候需要注意的是函数 `deref()` 和 `*` 的行为是不一样的。

- `deref()` 的函数原型是 `fn deref(&self) -> &Self::Target;` 所以我们拿到的是 Target 的引用 `&Target`
- `*` 是直接拿到 `Target`

所以，简单来说 `variable.deref()` 就等价于 `&*variable`

