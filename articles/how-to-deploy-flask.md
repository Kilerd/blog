 - title = [译文]如何使用Flask部署大型应用？
 - url = how-to-deploy-flask
 - tags = 
 - datetime = 2015-07-14 23:30:18 +0800

原文地址： [https://github.com/mitsuhiko/flask/wiki/Large-app-how-to](https://github.com/mitsuhiko/flask/wiki/Large-app-how-to)

> 译者：本译文已经违背了原文的意图，请勿加以转载。此文仅用于个人使用。

**这篇文章并不是官方的！它包含了很多非官方资源的建议并且没有通过一系列的测试（审查）。这里描述的写法可能很有用，但是同时它也可能很危险。请记住，不要在本文档添加任何附加信息。或者，引用在你的网站或者博客。这篇文章之所以保存，是因为很多`StackOverflow`答案指向了这里**


<!--more-->


这篇文章试图去描述一个由Flask和一些基础的模块组成的大型应用的第一步。

 - SQLAlchemy
 - WTForms

请随时可以修改和添加自己的Tips

# 安装

## Flask
[Flask Installation](http://flask.pocoo.org/docs/installation/)
我建议使用`virtualenv`:它是一个简单并且允许你在同一个机器上执行多个环境的玩意，甚至，他不需要机器上的超级权限(root)，近警示作为一个库文件安装在本地。

## Flask-SQLAlchemy
`SQLAlchemy`提供了一个简单而快捷的方式去映射你的对象到不同的关系型数据库。在`virtualenv`里面用`pip`安装`Flask-SQLAlchemy`:
```bash
pip install flask-sqlalchemy
```
[更多关于Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy/)

## Flask-WTF
`WTForms`提供了一个简单的方式去处理用户提交的数据
```bash
pip install Flask-WTF
```
[更多关于Flask-WTF](http://packages.python.org/Flask-WTF/)

# 概述

好了，到了现在，我们就准备好了所需的所有库。下面是应用的文件夹结构。
```bash
/config.py
/run.py
/shell.py 
/app.db
/app/__init__.py
/app/constants.py
/app/static/
```
对于每一个模块(或者子应用)都会有这样的文件结构(这里展示的是`users`模块)
```bash
/app/users/__init__.py
/app/users/views.py
/app/users/forms.py
/app/users/constants.py
/app/users/models.py
/app/users/decorators.py
```

对于每一个模块，都需要用到模版(jinja)，所以我们以`模版文件夹 + 模块目录`的形式进行储存。

```bash
/app/templates/404.html
/app/templates/base.html
/app/templates/users/login.html
/app/templates/users/register.html
```
我们本应该使用一个专门的http服务来提供静态文件，但是随着科技的发展，我们可以让Flask来完成这项工作。Flask会自动地从`static/`文件夹里面读取静态文件。如果你想使用其他文件夹，那么你可以阅读这篇文章：
[http://flask.pocoo.org/docs/api/#application-object](http://flask.pocoo.org/docs/api/#application-object)

```bash
/app/static/js/main.js
/app/static/css/reset.css
/app/static/img/header.png
```
我们将会创建4个模块：用户模块（用于管理用户的注册、登陆、找回密码、信息修改，甚至第三方登陆/注册）、运用列队服务的邮件模块、文章和评论模块。

## 配置
`/run.py`用于启动网站服务器
```python
from app import app
app.run(debug=True)
```
`/shell.py`将会打开一个Flask环境的控制台。在这个环境下，或许用pdb执行调试并不太理想，但是总是有用的（当你初始化你的数据库时）
```python
#!/usr/bin/env python
import os
import readline
from pprint import pprint

from flask import *
from app import *

os.environ['PYTHONINSPECT'] = 'True'
```

`config.py`储存了所有模块的配置信息。这次，我们将使用`SQLite`数据库，因为他是十分简单、易用。很可能`/config.py`不会是仓库的一部分，因为在测试和生产环境是不同的。
```python
import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = "somethingimpossibletoguess"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
RECAPTCHA_OPTIONS = {'theme': 'white'}
```
 - `_basedir`读取脚本运行所在的目录
 - `DEBUG`说明这是一个开发环境。当发生错误时，你会从Flask得到一个非常有用的错误页面
 - `SECRET_KEY`用于加密Cookies。当这个值改变时，你的用户需要重新登录
 - `ADMINS`会被调用，当你需要发邮件给网站管理员时
 - `SQLALCHEMY_DATABASE_URI` 和 `DATABASE_CONNECT_OPTIONS` 是SQLAlchemy连接信息（建议高强度）
 - `THREAD_PAGE` 我的理解是2/核心数，或许这是错误的理解
 - `CSRF_ENABLED` 和 `CSRF_SESSION_KEY`用于防止异常操作的POST
 - `RECAPTCHA_*` 将使用自带`RecaptchaField`的WTForms，用于验证网站和公钥、私钥。

# 第一个模块
我们将开始写用户模块。为此，我们将会定义一些模型、用于模型的常数、表单，最后是第一个视图和模版。

## 第一个模型（和它的常数文件）
`/app/users/models.py`文件：
```python
from app import db
from app.users import constants as USER

class User(db.Model):

    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.SmallInteger, default=USER.USER)
    status = db.Column(db.SmallInteger, default=USER.NEW)

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password

    def getStatus(self):
        return USER.STATUS[self.status]

    def getRole(self):
        return USER.ROLE[self.role]

    def __repr__(self):
        return '<User %r>' % (self.name)
```
在`/app/users/constants.py`文件中的常数:
```python
# User role
ADMIN = 0
STAFF = 1
USER = 2
ROLE = {
    ADMIN: 'admin',
    STAFF: 'staff',
    USER: 'user',
}

# user status
INACTIVE = 0
NEW = 1
ACTIVE = 2
STATUS = {
    INACTIVE: 'inactive',
    NEW: 'new',
    ACTIVE: 'active',
}
```

译文未完成