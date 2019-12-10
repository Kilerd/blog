 - title = 简单几步打造个人集群和自动化流水线
 - url = personal_docker_cluster_and_ci_package_pipeline
 - tags = 
 - datetime = 2019-06-13 13:16:33 +0800

在认识的小伙伴发了他做的项目部署文档出来之后，我便决定开始写这篇文章，原因是他使用的部署方式太麻烦，而且太不自动化，同时有时候也会因为开发任务繁忙导致没能部署好等等。

这篇文章是介绍了一个极度适合用于个人或者几个人的小团队使用的集群搭建方式，在保证了安全性的同时，提供了几乎全自动的部署方式，在手动配置一次之后，每次服务更新都是自动触发的，极大地减少了部署的时间。

本篇文章适用于 GIT-FLOW 类似的「master 即 生产代码」的一切工作模式（或者某一个分支为生产代码）。如果您的开发模式不符合这个特征，那么可以关闭网页了。

<!--more-->

## 服务器架构

服务器方面，为了方便使用，我们选择了 docker swarm 而不是 k8s，我们先看一个全览图：

![server-structure.jpg](https://i.loli.net/2019/06/13/5d0220558718054830.jpg)

整个架构的思路就是用 NGINX 来代理所有的 web 应用，内部每个应用都以 stack 的方式部署，同时配合 Portainer 进行自动化更新。一个超级简单的部署模式，却基本满足了我个人的所有开发场景。



## 环境部署

首先你要有一台独立的服务器，什么发行版都不所谓了，我们不会在宿主机里面干任何事情，一切都是在Docker 内实现。

服务器只需要对外暴露 80 和 443 端口即可，ssh 使用密钥的方式登陆保证安全。

### 安装Docker 并启动 Docker Swarm 模式

因为这里采用了单机的方式，所以一步就启动了 swarm 模式：

```shell
docker swarm init
```

### 安装 Nginx

在这里 Nginx 作为 Load Balancer 和自动 HTTPS 的工具，需要实现服务发现的功能，你可以用 `docker-gen` 自己撸一个，也可以采用现成的软件来完成。这里我才用了这个 [buchdag/letsencrypt-nginx-proxy-companion-compose](https://github.com/buchdag/letsencrypt-nginx-proxy-companion-compose/blob/master/2-containers/compose-v3/environment/docker-compose.yaml) 。

先创建一个 nginx network：

```shell
docker network create nginx-net --attachable
```



因为我喜欢吧 volume 不与任何服务直接挂钩，所以我的 volume 都是独立创建的：

```shell
docker volume create nginx-conf
docker volume create nginx-vhost
docker volume create nginx-html
docker volume create nginx-dhparam
docker volume create nginx-certs
```

最后以 stack 的模式启动 nginx: 

```yaml
version: '3'

services:

  nginx-proxy:
    image: jwilder/nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - nginx-conf:/etc/nginx/conf.d
      - nginx-vhost:/etc/nginx/vhost.d
      - nginx-html:/usr/share/nginx/html
      - nginx-dhparam:/etc/nginx/dhparam
      - nginx-certs:/etc/nginx/certs:ro
      - /var/run/docker.sock:/tmp/docker.sock:ro
    labels:
      - "com.github.jrcs.letsencrypt_nginx_proxy_companion.nginx_proxy"
    networks:
      - nginx-net

  letsencrypt:
    image: jrcs/letsencrypt-nginx-proxy-companion
    depends_on:
      - nginx-proxy
    volumes:
      - nginx-vhost:/etc/nginx/vhost.d
      - nginx-html:/usr/share/nginx/html
      - nginx-dhparam:/etc/nginx/dhparam:ro
      - nginx-certs:/etc/nginx/certs
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - nginx-net

volumes:
  nginx-conf:
    external:
      name: nginx-conf
  nginx-vhost:
    external:
      name: nginx-vhost
  nginx-html:
    external:
      name: nginx-html
  nginx-dhparam:
    external:
      name: nginx-dhparam
  nginx-certs:
    external:
      name: nginx-certs

networks:
  nginx-net:
    external: true
```



```shell
docker stack deploy --compose-file nginx.yml nginx
```

OK，这个时候 nginx 就已经创建好了。

### 安装 Portainer 

Portainer 是一个为数不多的简洁，消耗资源又少的 docker 管理面板，有他可以更加直观地管理集群的内容，同时新版的 Portainer 还提供了一个比较方便的更新服务的方法，所以他对于我来说是必须的

```yaml
version: "3"
services:
  agent:
    image: portainer/agent
    environment:
      # REQUIRED: Should be equal to the service name prefixed by "tasks." when
      # deployed inside an overlay network
      AGENT_CLUSTER_ADDR: tasks.agent
      # AGENT_PORT: 9001
      # LOG_LEVEL: debug
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /var/lib/docker/volumes:/var/lib/docker/volumes
    networks:
      - agent_network
    deploy:
      mode: global
      placement:
        constraints: [node.platform.os == linux]

  portainer:
    image: portainer/portainer
    command: -H tcp://tasks.agent:9001 --tlsskipverify
    environment:
      VIRTUAL_HOST: portainer.kilerd.me
      VIRTUAL_PORT: 9000
      LETSENCRYPT_HOST: portainer.kilerd.me
      LETSENCRYPT_EMAIL: blove694@gmail.com
    volumes:
      - portainer_data:/data
    networks:
      - agent_network
      - nginx-net
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]

networks:
  agent_network:
    driver: overlay
  nginx-net:
    external: true

volumes:
  portainer_data:
```



**注意：这里不能直接照抄配置文件了**：在 `portainer` 这个服务里面，对外暴露出了一个GUI管理页面，他是需要通过 nginx 进行代理才能访问的，所以需要修改 `VIRTUAL_HOST` `LETSENCRYPT_HOST` 为你的域名， `LETSENCRYPT_EMAIL` 为你的邮箱。

```shell
docker stack deploy --compose-file portainer.yml portainer
```

好，不出意外的话，你就可以通过 `https://你的域名` 来访问到 Portainer 的页面了，进去改密码，就完事了。



### 部署自己的 Docker Registry

首先先创建 volumes：

```shell
docker volume create registry_data
docker volume create registry_auth
```

然后在 `registry_auth` 生成一个用于提供密码保护的配置文件 `.passwd` ，因为 registry 没有密码很不安全

```shell
cd /var/lib/docker/volumes/registry_auth/_data
docker run --entrypoint htpasswd registry:2 -Bbn 用户名 密码 > .passwd
```

**上述不要直接复制，请修改用户名密码**

然后，部署 stack：

```
version: "3"
services:
  registry:
    image: registry:2
    environment:
      VIRTUAL_HOST: registry.kilerd.me
      VIRTUAL_PORT: 5000
      LETSENCRYPT_HOST: registry.kilerd.me
      LETSENCRYPT_EMAIL: blove694@gmail.com
      REGISTRY_AUTH: htpasswd
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/.passwd
      REGISTRY_AUTH_HTPASSWD_REALM: Registry Realm
    volumes:
      - registry_data:/var/lib/registry
      - registry_auth:/auth
    networks:
      - nginx-net
volumes:
  registry_auth:
    external:
      name: registry_auth
  registry_data:
    external:
      name: registry_data

networks:
  nginx-net:
    external: true

```

**上述不要直接复制，请修改访问地址，邮箱**

因为 nginx 有默认最大传输大小，所以可能会导致`docker push image` 失败，在 image 太大时，所以需要一下命令取消限制：

```shell
cd /var/lib/docker/volumes/nginx-vhost/_data
echo "client_max_body_size 0;" > registry.kilerd.me
```

**上述不要直接复制，请修改域名**

这样必要的东西就完成了，环境就完全搭建完毕。

## 自动化流水线

接下来就是怎么通过流水线自动发布新版本的应用了，这里会以我的一个小项目为例子，一一说明你需要怎么做。

假设我们的项目就是一个简单的文本：

```shell
echo "hello world" > index.html
```

然后我们编写一个超级简单的 Dockerfile：

```dockerfile
FROM python:3.7

COPY index.html index.html

EXPOSE 8000
CMD ["python -m http.server 8000"]
```

这个docker 会暴露出 8000 端口作为 http 访问。



### Travis CI or Circle CI

相比自己搭建一套CI，我现在了 Circle CI 来做持续集成和持续部署。我们的策略是这样的：

- 如果不是 master 分支，不执行
- 打包docker 镜像
- 推送到我们刚刚部署的 Registry
- 更新我们的服务



先看看 circle ci 的配置文件：

```yaml
version: 2
jobs:
  build:
    working_directory: /app
    docker:
      - image: docker:17.05.0-ce-git
    steps:
      - checkout
      - setup_remote_docker
      - restore_cache:
          keys:
            - v1-{{ .Branch }}
          paths:
            - /caches/app.tar
      - run:
          name: Load Docker image layer cache
          command: |
            set +o pipefail
            docker load -i /caches/app.tar | true
      - run:
          name: Build application Docker image
          command: |
            docker build --cache-from=app -t app .
      - run:
          name: Save Docker image layer cache
          command: |
            mkdir -p /caches
            docker save -o /caches/app.tar app
      - save_cache:
          key: v1-{{ .Branch }}-{{ epoch }}
          paths:
            - /caches/app.tar
      - run:
          name: Push to registry
          command: |
            docker login registry.kilerd.me -u 用户名 -p 密码
            docker tag app registry.kilerd.me/app
            docker push registry.kilerd.me/app
  deploy:
    machine:
      enabled: true
    steps:
      - run:
          name: update service
          command: |
            curl -X POST PORTAINER_WEBHOOK_URL
workflows:
  version: 2
  build-and-deploy:
    jobs:
      - build:
          filters:
            branches:
              ignore:
                - develop
                - /feature-.*/
      - deploy:
          requires:
            - build
          filters:
            branches:
              only: master
```



上面这个配置信息很多都是与缓存有关的，用来加快`docker build ` 的过程，主要的只有几行：

- `docker login registry.kilerd.me -u 用户名 -p 密码` 登陆部署的 Registry
- `docker tag app registry.kilerd.me/app` 打 TAG
- `docker push registry.kilerd.me/app` 推送
- `curl -X POST PORTAINER_WEBHOOK_URL` 更新服务，这里因为还没有在集群里面创建 stack，所以还没有这个 `PORTAINER_WEBHOOK_URL` ，下文会补上。

**注意：上述用户名、密码、PORTAINER_WEBHOOK_URL 请用 circle 的 environment variable 来储存，不要直接写在配置文件内** （作者就吃了这样的亏，导致项目无法开源）



OK，推到项目仓库，circle ci 就开始执行了，配置没问题的话， registry 里面就已经有这个application 的 docker 镜像了，但是更新会失败，因为我们还没有创建application的stack。



### Application Stack

对于一个应用我们都要创建一个独立的stack，并接入 `nginx-net` 让 nginx 为应用代理http，同时申请 https 证书。

那么这个应用的 stack 文件要这么写：

```yaml
version: "3"
services:
  backend:
    image: registry.kilerd.me/app:latest
    environment:
      VIRTUAL_HOST: test.kilerd.me
      VIRTUAL_PORT: 8000
      LETSENCRYPT_HOST: test.kilerd.me
      LETSENCRYPT_EMAIL: blove694@gmail.com
    networks:
      - nginx-net

networks:
  nginx-net:
    external: true
  backend:
```

**上述配置文件不要直接复制，请修改 镜像地址，域名，邮箱**

创建 stack，之后我们就去要去找到刚刚缺失的那个 `PORTAINER_WEBHOOK_URL` 


![Screen Shot 2019-06-13 at 9.01.43 PM.png](https://i.loli.net/2019/06/13/5d024996dc34d88705.png)

进入你想更新的那个 Service Detail 页面，开启 `Service webhook` 功能，链接就出来了，把它复制到circle的配置中。

一切就完成了。

### 开发流程

如果你的开发流程是基于 GIT-FLOW 的话，那么可以 follow 一下步骤进行开发 ：

- 在 `feature/xxx` 分支开发对于 Feature
- 开发完成进入 `develop` 分支进行验证
- release version 阶段把 `develop` 合并进 `master` 分支
- Circle CI 收到 `master` 分支的推送 webhook， 触发docker image 构建
- 构建完成，推送 image 到 registry
- 推送完成，通过 `PORTAINER_WEBHOOK_URL` 触发 Portainer 更新指定的 Service



> docker service update xxx 一直都有个问题，不会主动拉取latest的镜像，portainer 自带的这个可以满足，所以说在我的开发环境里面他是必须的。比如就只能 ssh 到服务器，手动执行命令更新。

所以在开发阶段，只要开发然后推送，其他都由 CI 帮你完成所有的部署功能。



## 缺点和优化的地方

- 这个部署方式只适用于单机 docker swarm 集群，多机需要用 NAS 来创建 volume
- 如果打包出来的docker image 无法执行，没有一个有效的回退旧版本机制
- 目前没有找到比较好的日志收集方式