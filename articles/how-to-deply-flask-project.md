 - title = 如何正确的部署 Flask 项目
 - url = how-to-deply-flask-project
 - tags = 
 - datetime = 2016-11-25 12:07:27 +0800

# 系统 Python 设置

由于每个 Linux 发行版的内置 Python 都不太一样，而且为了避免你的项目在不同的 Python 版本下出现各种奇怪问题。

比如，`requests` 库在 python 2.7.5 的环境下访问 HTTPS 网站会出现 SNI 的问题，导致访问失败。

所以我们需要使用 `pyenv` 和 `virtualenv` 。

**注：强烈不建议直接更新系统里面的 Python ，否则你会出现各种各样的奇怪问题**


<!--more-->


## pyenv

pyenv 允许你在一台机器上配置多个版本的 python 环境

### 安装

```bash
sudo apt-get install curl git-core // 依赖库
curl -L https://raw.github.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
```

如果执行成功，那么 `pyenv` 就会安装到 `~/.pyenv` 目录里面。

为了方便我们用 `pyenv subcommand` 的方法来调用 `pyenv` ，我们要在 `~/.bashrc` 文件中添加以下内容

``` bash
export PYENV_ROOT="${HOME}/.pyenv"

if [ -d "${PYENV_ROOT}" ]; then
  export PATH="${PYENV_ROOT}/bin:${PATH}"
  eval "$(pyenv init -)"
fi
```

`~/.bashrc` 的作用大概就是用户配置文件

执行 `source ~/.bashrc`  以重新加载用户配置文件。

至此，`pyenv` 就安装好了。

### 使用

- `pyenv install --list`

  列出目前 `pyenv` 安装过的所有 Python 版本

- `pyenv install $version`

  `$version` 就是你想要安装的 Python 版本

- `pyenv versions` 

  显示当前系统用的是哪个 Python 版本

- `pyenv global $version`

  把当前系统的 Python 版本切换到 `$version` 这个版本。该命令在本教材中并不用到，故不多介绍，如果你想了解更多，可以查看`pyenv` 的 API 文档

## virtualenv

用于分离 Python 库

### 安装

如果你是使用以上的方法安装`pyenv`的话，那么 `virtualenv` 就已经安装完了。
**强烈不建议用其他方法安装 virtualenv， 那将会是一种很麻烦很折腾的方法**

### 使用

- `pyenv virtualenv $version $name`

  用于创建一个指定 Python 版本的虚拟环境

  - `$version` 你需要的 Python 版本
  - `$name` 该虚拟环境的名称

- `rm -rf ~/.pyenv/versions/$name/`

  删除名称为`$name`的虚拟环境。 

 **注意： 这里用到了`rm -rf` 谨慎使用，使用前先检查代码**


# 基本需求

首先我们需要一下这几个库来来帮助我们部署，建议在 virtualenv 中安装，以免感染系统

- `gunicorn`

  用 WSGI 的方式来启动 flask 项目

- `gevent`

  python 中比较好的网络库，提供更加高效的 I/O 读写

- `supervisor`

  守护进程，避免进程意外退出

安装方法：

```shell
pip install gunicorn gevent supervisor
```


# 部署你的 Flask 项目

## Flask 项目结构

为了做演示，我们暂定需要部署的 Flask 项目结构是这个样子的

```
flaskproject
|----app
|----|----templates
|----|----static
|----|----models.py
|----|----views
|----|----|----__init__.py
|----|----|----user.py
|----|----functions.py
|----config.py
|----run.py
```

**项目结构并不是固定的，可以自己根据自己项目的情况自行分配**

`run.py` 中就是 Flask 项目的入口，内容大致如下

```python
from flask import Flask

app = Flask()

# ... some configs
```

或者使用`create_app()` 模式

```python
from flask import Flask

def create_app():
    app = Flask()
    
    # ... some configs
    
    return app
```

## Supervisor + Gunicorn + Gevent

### 前提设置

首先启动之前已经创建好的 virtualenv 虚拟环境

```shell
pyenv activate $name
```

如果正常启动的话，在 bash 命令行上面应该会出现环境的名字

```shell
($name) # 
```

没正常启动的样子是这样的

```shell
# 
```

进去之后呢，用`pip` 安装你的项目依赖

```shell
pip install -r requirements.txt
```

### 配置 Supervisor

进入项目文件夹

然后输出 supervisor 默认配置文件 `supervisor.conf` : (`$name` 是 virtualenv 环境的名称)

```shell
~/.pyenv/versions/$name/bin/echo_supervisord_conf > supervisor.conf
```

然后打开 `supervisor.conf` ，然后在文件的最后添加一下内容

```
[program:myapp]
command=~/.pyenv/versions/$name/bin/gunicorn -k gevent -w2 -b0.0.0.0:9000 run:app   ; supervisor启动命令
directory=/home/myproject                                                 ; 项目的文件夹路径
startsecs=0                                                               ; 启动时间
stopwaitsecs=0                                                            ; 终止等待时间
autostart=true                                                            ; 是否自动启动
autorestart=true                                                          ; 是否自动重启
stdout_logfile=/home/myproject/log/gunicorn.log                           ; log 日志
stderr_logfile=/home/myproject/log/gunicorn.err                           ; 错误日志
```

- `command`  中的是用 `gunicorn` 和 `gevent` 启用 Flask 项目的命令
  - `-w2` 指的是 `2 worker` 一般设置成 `2 * cpu_nums` 
  - `-b0.0.0.0:9000` 指的是启动在 9000 端口
  - `run:app` 是 Flask 项目入口，如果你用的是`create_app()` 方法的话， 就改成`run:create_app()`
- **所有目录都需要使用绝对路径**



### 操作 Supervisor

- 启动 Supervisor

  `~/.pyenv/versions/$name/bin/supervisord -c supervisor.conf`

- 查看 Supervisor 情况

  `~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf status`

- 重启 Supervisor

  `~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf reload`

- 启动 Supervisor 中某个 / 全部程序

  `~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf start [all][appname]`

- 关闭 Supervisor 中某个 / 全部程序

  `~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf stop [all][appname]`



配置好你的 `supervisor.conf` 文件后，执行启动命令，如果没打错命令基本就已经启动好了，这个时候你应该就可以访问 `http://ip:9000` 来访问到你的 Flask 项目

# Nginx 设置

这里只讨论如何使用 Nginx ，Apache 党请自行转换



## Nginx 安装

详情查看 [Install | Nginx](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/)

## Nginx 配置

进入 Nginx配置文件，或者`/etc/nginx/conf.d/default.conf` ，或者新建 `/etc/nginx/conf.d/myproject.conf`，修改配置文件，以下这是几个建议的配置

- 禁止 IP 访问

  ```
  server {
      listen       80 default_server;
      listen       [::]:80 default_server;
      server_name  _;

      location / {
          return 404;
      }
  }
  ```

- 禁止 HTTP 访问

  ```
  server {
      listen               80;
      server_name          www.myproject.com myproject.com;
      server_tokens        off;
      
      # 跳转至 HTTPS
      location / {
          rewrite ^/(.*)$ https://myproject.com/$1 permanent;
      }
  }
  ```

- HTTPS设置 / 443端口设置

  ```
  server {
      listen               443 ssl http2 fastopen=3 reuseport;

      server_name          www.myproject.com myproject.com;
      server_tokens        off;

  	# SSL 设置
      ssl_certificate      /root/.acme.sh/myproject.com_ecc/fullchain.cer;
      ssl_certificate_key  /root/.acme.sh/myproject.com_ecc/myproject.com.key;
      ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
      ssl_prefer_server_ciphers  on;
      ssl_protocols              TLSv1 TLSv1.1 TLSv1.2;
      ssl_session_cache          shared:SSL:50m;
      ssl_session_timeout        1d;
      ssl_session_tickets        on;
      ssl_stapling               on;
      ssl_stapling_verify        on;
      resolver                   114.114.114.114 valid=300s;
      resolver_timeout           10s;

  	
  	# NGINX 日志
      access_log                 /home/myproject/log/nginx.log;

  	# 禁止非 GET HEAD POST OPTIONS 的访问
      if ($request_method !~ ^(GET|HEAD|POST|OPTIONS)$ ) {
          return           444;
      }
  	
  	# www.myproject.com 跳转至 myproject.com
  	# 可有可无，看个人情况
      if ($host != 'myproject.com' ) {
          rewrite          ^/(.*)$  https://myproject.com/$1 permanent;
      }
  	
  	# 代理 Flask 端口
      location / {
          proxy_http_version       1.1;
  		
  		# HSTS 头设置
          add_header               Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
          add_header               X-Frame-Options deny;
          
          # 添加两个 Request Header
          proxy_set_header         X-Real_IP        $remote_addr;
          proxy_set_header         X-Forwarded-For  $proxy_add_x_forwarded_for;
  		
  		# 代理 9000 端口
          proxy_pass               http://127.0.0.1:9000;
      }
  }
  ```



**这里的SSL申请是用 [acme.sh](https://github.com/Neilpang/acme.sh) 申请的 Let‘s Encrypt ECC证书**

然后重启 Nginx ，项目就配置完成了。就可以使用域名正常访问了（DNS解析正常的情况下）

# 快捷使用方式

因为 Python 的执行方式不像 PHP 那样的脚本式执行，所以当项目代码更新后，需要重启才能使代码生效。

为了方便重启，我们在项目的根目录下创建`reload.sh`

```shell
git pull  // 我是使用 git 拉去项目代码的，这里的作用是更新项目代码
~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf reload  // 重启 Supervisor
echo 'Reload Done'
```

下次我们就可以直接用 `sh reload.sh` 来直接更新项目状态了

# 注意事项

- 服务器的配置不止如此，`iptables` 等等相关软件限制端口访问
- 建议只允许 HTTPS 访问
- 如果不限制端口访问，不建议把 `supervisor` 配置中的监听端口暴露（即使用9000端口）



待完善的内容

- 建议使用 `fabric `来代替`sh reload.sh` 的执行方式
- log 文件如何更高效地分析
- 期待下一篇文章把，下一次将完善这些内容