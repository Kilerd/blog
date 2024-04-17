- title = iPhone 下的 99% 自动化记账
- url = iphone-sms-financial-worker
- tags = 
- datetime = 2024-04-17T18:00:00.000000+08:00
- template = article.html


因为一些众所周知的原因，国内的大部分银行都无法通过API的方式访问到个人账户下的账单，同时因为支付宝与微信的普及，银行系统里面通常记录的交易信息也是不完整的，以至于在中国环境下实现自动化记账是一件很麻烦的事情。经过多次更改后，我的记账模式已经做到了相当高的自动化，于是便有了这篇文章，记录并分享一下我是如何进行自动化记账的。

<!--more-->

前提条件、准备：

- iPhone 一台
- 银行 APP （例如：招商银行）
- 个人域名
- cloudflare 账号
- 个人服务器

我们会把整个流程分成三个部分来讨论：数据采集端、数据处理端、数据修正端

## 数据采集端

本阶段的核心是我们需要把银行消费的短信通知采集到，然后推送给有编程能力的处理器。

### 银行交易短信开通

![](/statics/images/iphone-sms-financial-worker-1.jpg)

这是一切的开始，我们需要在银行APP中开启「账务变动通知」，并且把「通知起点金额」设置为0，这样我们就可以通过短信来接受到所有银行卡的变动

### Shortcut 自动化

![](/statics/images/iphone-sms-financial-worker-2.jpg)

iOS因为安全的考虑，应用程序除了「短信过滤」分类之外并没有能力感知和处理短信，可是自动化中却存在一种神奇的自动化「短信：当收到妈妈的短信时」，他是一种可以根据「短信发件人」和「短信关键字」来触发自动化的触发点。

光有这个前提还不可以完成数据的采集流程，以下两点才是关键：

- 所有交易短信都包含了****招商银行****四个字，所以我们可以采用它为触发点
- 自动化中，可以通过「输入快捷指令的短信」这个参数获取到具体的短信内容

那么我们可以把它发送到一个**数据处理端**中真正的处理我们的短信，所以我们的自动化其实是做了以下几件事情：

- 当短信内容包含「**招商银行**」四个字时，触发自动化
- 把短信内容作为 payload 以 HTTPS 的方式（自动化中的执行步骤叫「获取URL内容」）发送至**数据处理端**

## 数据处理端

这里我们采用了 cloudflare worker 来作为我们的数据处理端，从上文可知，我们的短信会以https post的方式发送到worker 中来。 那么我们就可以通过以下代码在worker中取出短信内容

```tsx
const request_payload: { sms: string } = await request.json();
```

那么我们就需要做数据提取了，招商银行的短信可以简单的分为好几类：

- 支出消费
- Apple pay 支付
- 退款

那么我们就以支出消费来举例子，一个简单的支出短信是这样的

```tsx
【招商银行】您账户0000于04月09日06:43在【支付宝-payee】快捷支付114.15元，余额9999.99 
```

那么我们就可以通过正则的模式来取出交易账户、时间、payee、金额 等信息，这里我的正则大概长这个样子

```tsx
const CONSUME = /您账户(?<account>\d+)于(?<month>\d+)月(?<day>\d+)日(?<hour>\d+):(?<min>\d+)在【(?<payee>[^】]+)】快捷支付(?<amount>\d+(\.\d+))元/;
```

因为我们用的是正则中 named group 的写法，在真正的处理流程中，我们可以通过以下的代码获取到短信的细节

```tsx
const match_consume = request_payload.sms.match(CONSUME);
if (match_consume) {
    // @ts-ignore
    const { groups: { account, month, day, hour, min, payee, amount } } = CONSUME.exec(request_payload.sms);
    // add your logic here...
}
```

自此我们获取到了短信的交易时间、交易对手、金额，接下来就可以把它转换成复式记账的账户了

```tsx
const ACCOUNTS = {
'0000': 'Assets:CMB-DebitCard'
};

const target_account = ACCOUNTS[account] ?? DEFAULT_ACCOUNT;

const PAYEE = {
'肯德基': 'Expenses:Eat'
};

const target_payee = PAYEE[payee] ?? "Expenses:FixMe";
```

然后可以构建 API 请求，把数据发送到 zhang 或者 fava 等具有API请求能力的服务端。

```tsx
const payload = { 
    // construct the json payload based on your financial tool
}
```

自此我们就可以完成了把数据处理并推送至服务端储存的流程，如果你在使用 zhang，那么就可以在web UI中查看到一条记录 

![](/statics/images/iphone-sms-financial-worker-3.png)

### Expenses:FixMe

关于那些payee 无法分类的，我目前的做法会分配到 `Expenses:FixMe` 中，并把交易标注成 `Waring`  ，以便在后续的流程中重点修正。

## 数据修正端

虽然我们完成了数据的采集，但是就如同上图的交易以下，我们只获取到了

- payee 为 **上海拉扎斯信息科技有限公司**
- narration 为空

实际上，这是一笔饿了么消费，金额流转路经为 `饿了么` → `支付宝` → `招商银行`  。我们在饿了么上购买了什么商品早已经在一层一层数据流转中消失了，这时候我们就需要人工介入做数据修正工作了。

目前来说对于 zhang，有两种方式做数据修正： web ui 和 手机APP。 这里我们就用手机APP来举例，我们可以选择晚上睡觉前把一天的数据再次回顾和修正

![](/statics/images/iphone-sms-financial-worker-4.jpg)

通过 APP 的交易编辑功能可以完成交易的修正

![](/statics/images/iphone-sms-financial-worker-5.jpg)

## 一些注意的点

- 建议最后的消费卡集中到同一张卡中，因为整个流程的前提是基于银行短信通知来实现的，而银行的短信通知是需要收费的，3元一张卡，所以集中到同一张卡可以降低服务费的支出
- 前提准备中提及到了个人域名，这里主要是两个用途
        - cloudflare 的 worker 绑定个人域名的访问成功率高很多
        - 个人账本需要可以被 worker 直接访问，所以也需要绑定个人域名，当然也可以使用 clouldflare tunnel 来做内网服务穿透
- 如果你家里有多的iPhone和 NAS，可以通过iPhone自带的短信同步功能同步到家里内网备用机，备用机执行Shortcut自动化，worker 和账本都放在nas内网中，避免账本因配置不当暴露在公网