 - title = HOOK机制浅谈与实现
 - url = how-hooks-works
 - tags = 
 - datetime = 2016-06-25T17:05:34.000000+08:00
 - template = article.html

HOOK机制最常见的地方就是在 windows 系统里面。你可以通过 HOOKS 来监控键盘输入、鼠标点击等等。那到底什么是 HOOK 机制呢？用人话讲就是“允许在特定的行为前后添加自定义行为”

```python
# before doing
do something...
# after doing
```


<!--more-->


### HOOK 与 非HOOK 的对比

这里我们用博客评论做例子（感觉这会是最常见的例子了），并且用伪代码来做演示。

博客评论最基本的函数可以写成这个样子

```c++
function comment_process(){
  Insert to database
}
```

如果我们有那么一个需求：在评论之后发送一个通知邮件给评论者，那么我们就需要修改这个 `commet_process` 函数

```c++
function comment_process(){
  Insert to database
  send_email(commenter);
}
```

如果我们还需要发邮件通知博客主人，那么

```c++
function comment_process(){
  Insert to database
  send_email(commenter);
  send_email(host);
}
```

或许，有人会说可以用配置文件来解决这个问题，就像如下：

```c++
function comment_process(){
  Insert to database
  if(config['send_to_commenter']){
    send_email(commenter);
  }
  if(config['send_to_host']){
    send_email(host);
  }
}
```

看起来这个需求是解决了。但是如果我们需要把这个设计的模式交由用户或者开发者来使用。不可能让他们去直接修改程序的代码。甚者他们还不一定看得懂。

所以，我们可以采用 HOOK 机制，采用插件的方式来完美解决这个问题。

----

像上文所说，我们允许在评论前后自定义行为， 所以`comment_process`函数就可以改成一下形式

```c++
function comment_process(){
  hook.call('COMMENT_BEFORE', args);
  Insert to database
  hook.call('COMMENT_AFTER', args);
}
```

我们先定义一个`hook`变量来操作HOOK，从代码中，我们可以很清晰地看出来在`Insert to database` 操作前，先执行 `COMMENT_BEFORE` 相关的内容； 之后执行`COMMENT_AFTER` 相关内容。

简单来讲，我们可以理解成`hook` 存在两个列表`COMMENT_BEFORE` 和`COMMENT_AFTER` ，当执行`hook.call()` 命令时便遍历执行对应列表中的内容。

所以，如果我们用 HOOK 来实现上述 非HOOK的功能的话， 就是需要把 `send_email(commenter);` 和 `send_email(host);` 加入 `COMMENT_AFTER` 列表中。

可以清晰地看到，无论我们的需求改成怎样，对`comment_process` 函数的入侵和修改都是最小的。

那么，如果能解决怎么把 `自定义行为` 加入列表，就可以完美地写出插件机制。

为此，我们可以为`hook` 变量定义注册函数`register_action()` 

```c++
function register_action(type, action_name){
  list[type].append(action_name);
}
```

自此我们有了一个注册函数，用于添加自定义行为

```c++
hook.register_action('COMMENT_AFTER', 'send_to_commenter');
hook.register_action('COMMENT_AFTER', 'send_to_host');
```

这样列表`COMMENT_AFTER` 就更新成 `['send_to_commenter', 'send_to_host']` 

下面再实现 `hook.call()` 方法：

```c++
function call(type, args){
  for each_one in list[type]{
    each_one(args);
  }
}
```

 

至此，HOOK功能也就基本描述完了，一个简单的插件模式也完成了。

添加功能只用以下两步：

1. 编写对应逻辑的方法/函数
2. 调用`hook.register_action` 方法进行注册



### Python中的具体实现方法 

>  谁叫我主要用python呢 。 ╮(╯_╰)╭

如上文所说，我们存入列表中的是方法的名字(类型为字符串/string)，所以我们需要把字符串转换成方法指针。也就是说，我们需要遍历所有的代码，找出一个方法/变量/函数与之同名。

庆幸的是Python提供了`eval` 函数，可以直接使用

```python
def test_function():
    print 'hey, it is me.'

if __name__ == '__main__':
    
    eval('test_function')() # hey, it is me.
```

居然成功执行了， `eval('test_function')` 指向了`test_function` 这个函数

```python
def test_function():
    print 'hey, it is me.'

if __name__ == '__main__':
    
    print id(test_function) # 4292954292
    print id(eval('test_function')) # 4292954292
    print test_function == eval('test_function') # True
```

`eval('test_function')` 成了`test_function` 的一个引用

**BUT**，`eval` 有一个致命的弱点：写不好的话可能会引起漏洞供人注入。（这里不是本文讨论的重点，详情请GOOGLE）并且`eval` 挺慢的， 我们做1,000,000 次 `1 + 1` 试试

```python
import time
def test_function():
    return 1+1
if __name__ == '__main__':
    # eval test
    i=1000000
    start = time.time()
    while i>0:
        eval('test_function')()
        i -= 1
    end = time.time()
    print '{}'.format(end-start)  # 6.56956291199

    # normal test
    i=1000000
    start = time.time()
    while i>0:
        test_function()
        i -= 1
    end = time.time()
    print '{}'.format(end-start)  # 0.15709900856
```

6.57s 和 0.15s 的差距还是蛮大的。 不过均摊到1次的时间就好象可以忽略了。

有了`eval` 函数的帮忙，实现hook就会变得简单不少

PS: 最后讲道理，居然没有用上`eval` ，不过当你用不同写法的时候还是可能会用上的。ㄟ( ▔, ▔ )ㄏ

首先，我们先定义工程目录分布：

```
/app
..../plugins
........__init__.py
......../test_plugin
............__init__.py
............function.py
....hook.py
....view.py
```



其中`hook.py` 用于实现HOOK机制

```python
class Hook:
    _list = {}  # 用于储存HOOK行为

    @classmethod
    def register_action(cls, type, plugin_name, action_name):  # 注册行为
        if type not in cls._list:
            cls._list[type] = []
            cls._list[type].append((plugin_name, action_name))
        elif action_name not in cls._list[type]:
                cls._list[type].append((plugin_name, action_name))

    @classmethod
    def call(cls, type, **args):  # 执行行为
        if type not in cls._list:
            return;
        for action in cls._list[type]:
            exec_string = 'from plugins.{}.function import {}'.format(action[0], action[1])
            exec(exec_string)  # 动态加载
            eval(action[1])(**args)  # 执行

```



`/plugins/test_plugin/function.py` 中就是我们自定义的HOOK行为

```python
def send_to_commenter(**args):
    print 'send email to {}'.format(args['commenter'])

def send_to_host(**args):
    print 'send email to {}'.format(args['host'])
```

这里使用 `**args` 作为参数入口，接受所有参数

`view.py` 中包含两部分内容：前部分为初始化代码； 后部分是模拟函数执行

```python
from hook import Hook

def comment(commenter, content):
    args = {
        'commenter': commenter,
        'host': 'myself'
    }
    Hook.call('COMMENT_BEFORE', **args)
    print content
    Hook.call('COMMENT_AFTER', **args)

# 注册两个钩子
Hook.register_action('COMMENT_AFTER','test_plugin', 'send_to_commenter')
Hook.register_action('COMMENT_AFTER','test_plugin', 'send_to_host')

# 模拟运行 comment 行为
comment('someone@domain.com', 'Hello, Guys')
```

运行结果是很明显的：

```bash
Hello, Guys
send email to someone@domain.com  # send_to_commenter
send email to myself  # send_to_host
```

至此，HOOK机制讲完了， 也可以顺利写出 插件机制 了。

----

但是上面这个程序看起来并不是那么完美，因为还需要手动在代码初始化的地方手动注册HOOK行为。

为什么不用自动注册的方式呢？



在一般的项目里面，数据库是必不可少的，所以我们可以把这个行为记录进一个特定的表`plugins_hook`中(代替`HOOK._list` 作用)。在插件安装和删除的时候，对表`plugins_hook` 进行更新。

所以我们就无需在`view.py` 中用`register_action` 来注册 HOOK 行为。

我们只需在 `/plugins/your-plugin/__init__.py` 中类似地写入以下信息：

```python
# some basic information
NAME = 'Plugin Name'
DESCRIPTION = 'Ohhhhhhhhhhh'
AUTHOR = 'Some One'
EMAIL = 'my email'

# hook register
HOOK_REGISTER = [
  ('COMMENT_AFTER', 'send_to_commenter'),
  ('COMMENT_AFTER', 'send_to_host')
]
```

这样你的插件机制会更加完善。



----

好了，整个HOOK机制就讲完了，希望本文能对你有不少帮助。

PS: 如果你需要其他语言的DEMO，可以联系我，我们可以一起商讨以下。