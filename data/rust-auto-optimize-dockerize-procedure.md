 - title = 优化 Rust 的项目 Docker 打包流程.Rust
 - url = rust-auto-optimize-dockerize-procedure
 - tags = 
 - datetime = 2019-04-28T15:52:05.000000+08:00
 - template = article.html

在把 Project Rubble 从 Rocket 框架迁移到 Actix-web 的过程中，我顺便把困惑已久的 Docker 打包流程优化了不少。

这篇文章适用于那些在项目中带有 `Denpendencies.lock` 类似的固定依赖版本的 LOCK 文件。

<!--more-->

一般的构建流程可以分为以下几个步骤：**拉取最新代码** -> **构建** -> **打包** 。拉取代码一般都交由 CI 来完成。下文会着重讲我是怎么优化构建流程的，同时我会依照 Project Rubble 来做真实场景说明，技术栈如下： `Rust + Travis CI`

## 什么都自己编译

```dockerfile
FROM rust:1.29
RUN cargo install diesel_cli --no-default-features --features postgres
EXPOSE 8000
COPY . /app
WORKDIR /app
RUN cargo build --release
ENTRYPOINT ["sh", "./entrypoint.sh"] 
```

这个阶段我们只考虑「如何把项目打包出 docker 的镜像」，所以在这个 Dockerfile 中 有两个超级耗时的命令：

- `cargo install diesel_cli --no-default-features --features postgres`
- `cargo build --release`

第一步实际上是安装 `diesel_cli` ，这是为了项目的 数据库 Migration 服务的，因为在 `entrypoint.sh` 需要调用 `diesel migration run` 命令来更新数据库。

第二步则是构建我们自己的项目。



那么在这个场景下，第一步看似是多余的，`diesel_cli` 的作者肯定对自己的项目用 CI 跑过，测试过。那么我们是否能通过构建好的镜像来缩减这一步的耗时呢。

## 使用打包好的基础镜像

结论是可以的，虽然该库的作者并没有提供这么一个 Docker 镜像，但是社区上面有人封装过了 `clux/diesel_cli`， 所以我们可以用以下的方法来缩减我们构建的时间。

```dockerfile
FROM clux/muslrust:nightly as builder
COPY . /app
WORKDIR /app
RUN cargo build --release

FROM clux/diesel-cli
COPY --from=builder /app/target /application/target
COPY --from=builder /app/migrations /application/migrations
COPY --from=builder /app/Rocket.toml /application/Rocket.toml
COPY --from=builder /app/entrypoint.sh /application/entrypoint.sh
COPY --from=builder /app/target/x86_64-unknown-linux-musl/release/rubble /application/rubble

EXPOSE 8000
WORKDIR /application
CMD ["sh", "./entrypoint.sh"]
```

那么在看回这个构建过程，只剩下一步耗时操作 `cargo build --release` ，我们自己项目的构建过程，这里看似不能再做时间的缩减了，实则不然。

我们来分析一下构建步骤内部是如何操作的：

- 分析 `Cargo.toml` 和 `Cargo.lock` 来确定该应用所依赖的库和库的版本
- 从 `Crates` 下载这些制定版本的库
- 编译这些依赖库
- 编译自己的应用

> 在做深入的分析之前，我们先要了解一下 `docker build` 的缓存机制，简单来说，docker 会对 dockerfile 中的每一步操作进行记录，尤其是 `COPY` 和 `ADD` 操作，如果 COPY 之后的 文件HASH值（这里值的是整个 docker 镜像的哈嘻之）不变，那么在COPY 之后的 RUN 都会沿用之前的运行结果，直接命中缓存。
>
> 来一个例子是说，假设我们写一个这样的Dockerfile
>
> ```dockerfile
> copy test.txt
> RUN cp test.txt copy.txt
> ```
>
> - 第一次执行，我们传入了内容为 `hello world` 的 `test.txt` 文件，docker得到执行后的hash `A`，然后只想步骤二，得到 hash `B`。
> - 第二次执行该脚本时，如果执行完第一步得到的hash值还是 `A` 的话，那么 docker 会跳过执行步骤二，直接去缓存下来的结果。

因为每次构建都是对自己项目的全新构建，那么我们可以考虑把下载和编译依赖库的步骤缓存下来。

## 缓存项目的 Rust 依赖

为了缓存项目的依赖部分，我们把 Project Rubble 的 Dockerfile 构建改成了一下的样子：

```dockerfile
FROM clux/muslrust:stable as builder

WORKDIR /app

RUN USER=root cargo new rubble
WORKDIR /app/rubble

COPY Cargo.toml Cargo.lock ./

RUN echo 'fn main() { println!("Dummy") }' > ./src/main.rs

RUN cargo build --release

RUN rm -r target/x86_64-unknown-linux-musl/release/.fingerprint/rubble-*

COPY src src/
COPY migrations migrations/
COPY templates templates/

RUN cargo build --release --frozen --bin rubble


FROM alpine:latest

COPY --from=builder /app/rubble/migrations /application/migrations
COPY --from=builder /app/rubble/templates /application/templates
COPY --from=builder /app/rubble/target/x86_64-unknown-linux-musl/release/rubble /application/rubble

EXPOSE 8000

ENV DATABASE_URL postgres://root@postgres/rubble

WORKDIR /application
CMD ["./rubble"]
```

这个构建过程相比于上一个版本，可以拆成两个小的步骤

### 构建假的项目，下载并编译依赖

```dockerfile
RUN USER=root cargo new rubble
WORKDIR /app/rubble
COPY Cargo.toml Cargo.lock ./
RUN echo 'fn main() { println!("Dummy") }' > ./src/main.rs
RUN cargo build --release
```

相比之前的把所有源文件一起复制到 docker 镜像，这次首先把 `Cargo.toml` `Cargo.lock` 拷贝过去，然后新建一个虚拟的、假的 `main.rs` 来伪造项目入口，为的是保证项目能够正常构建。

那么根据刚刚描述的 Docker 构建缓存策略，如果我们传入的两个 Cargo 文件不变（指的是项目所依赖的内容不变）的情况下，那么我们就不会在每次构建的时候都会下载和编译这些依赖，完全可以复用原来编译好的依赖。

### 删除自己项目的构建信息

```dockerfile
RUN rm -r target/x86_64-unknown-linux-musl/release/.fingerprint/rubble-*
```

这条命令是把自己项目的构建信息删除，因为我这里用的是项目 `rubble` 的信息，所以如果要使用到自己的项目中，请就保证这里删除的目录是正确的。

这里删除的应该是构建二进制文件的指纹 `fingerprint`，其实我也不太清楚为什么在 docker 构建的时候需要删除，在日常编译中却不需要，不太了解 cargo 的运行机制。但是著者试过，如果不删除这个文件，那么在下一步的真正编译项目中便会不成功。

### 真正的构建过程

```dockerfile
COPY src src/
COPY migrations migrations/
COPY templates templates/

RUN cargo build --release --frozen --bin rubble
```

这里就是真正地把项目源文件拷贝进 docker 镜像进行编译

### 最小化运行镜像

```dockerfile
FROM alpine:latest

COPY --from=builder /app/rubble/migrations /application/migrations
COPY --from=builder /app/rubble/templates /application/templates
COPY --from=builder /app/rubble/target/x86_64-unknown-linux-musl/release/rubble /application/rubble

EXPOSE 8000

ENV DATABASE_URL postgres://root@postgres/rubble

WORKDIR /application
CMD ["./rubble"]
```

这一步是可选的，因为 Rust 项目编译之后便不依赖于 Cargo 环境了，编译后的二进制文件可以直接在其对应的平台上运行，所以选择了一个最小的可运行平台来跑，以缩减系统其他套件带来的资源消耗。



至此，我们把整个构建过程能缓存的部分都用缓存实现了，从之前的构建1个小时，到现在在不更新依赖的情况下10分钟完成构建，这个提升还是挺显著的。

此外，项目还重新选择了 `embbed_migration` 来做数据库迁移工作，有意可以参考下 [diesel_migrations](https://docs.rs/diesel_migrations/1.4.0/diesel_migrations/)