 - title = 用 Webpack 和 React 搭建一个适用于 Chrome Extension 的脚手架
 - url = starter_of_chrome_extension
 - tags = 
 - datetime = 2017-11-28 23:19:47 +0800

做为一个不称职的前端设计师，对于前端的框架，尤其是各式各样的 JavaScript 框架，我都是习惯使用官方自带的 CLI 工具来搭建脚手架的。因为在混乱的前端世界中，`Babel` 和 `Webpack` 的配置不是一般的麻烦。而且我对于前端的学习就是冲着写 Side Project 去的，所以效率对我来多很重要。

我选择的前端框架是 React + Redux，同时也有一个很好用的 CLI 工具来初始化 React 项目：[create-react-app](https://github.com/facebookincubator/create-react-app)。对于像我这样的懒人来说，这确实很好用，但同时也有不少缺点。

我是一个勤勤恳恳的 Python 工程师，所以使用装饰器是我的日常，同时 JavaScript 在 ES7 的 Proposal 中也有类似的装饰器提议，那么使用装饰器肯定是必不可少的了。Create-Reat-App 的最大问题就在于**不支持装饰器**


<!--more-->


> ## Can I Use Decorators?
>
> Many popular libraries use [decorators](https://medium.com/google-developers/exploring-es7-decorators-76ecb65fb841) in their documentation.
>
> Create React App doesn’t support decorator syntax at the moment because:
>
> - It is an experimental proposal and is subject to change.
> - The current specification version is not officially supported by Babel.
> - If the specification changes, we won’t be able to write a codemod because we don’t use them internally at Facebook.
>
> However in many cases you can rewrite decorator-based code without decorators just as fine.
> Please refer to these two threads for reference:
>
> - [#214](https://github.com/facebookincubator/create-react-app/issues/214)
> - [#411](https://github.com/facebookincubator/create-react-app/issues/411)
>
> Create React App will add decorator support when the specification advances to a stable stage.

并且还有一个问题在于 Chrome Extension 并不是一个简单的 SPA，所以就需要我们自己来手动配置一份 `webpack.config.js` 了，以下就是我的折腾记录

## 项目结构

```
├── dist
├── src
│   ├── Components
│   │   └── Container
│   │       ├── index.jsx
│   │       └── style.css
│   ├── background.js
│   ├── content.js
│   ├── icon-128.png
│   ├── manifest.json
│   ├── popup.html
│   └── popup.jsx
├── webpack.config.js
├── yarn.lock
├── package-lock.json
├── package.json
└── readme.md
```



一般来说，Chrome Extension 的主要文件如下：

- `manifest.json` Extension 的配置文件，包括了 LOGO，版本号，权限等等
- `popup.html` POPUP 页面，也就是说点击 Extension 图标是显示的页面，实际上就是一个普通的HTML页面
- `background.js` 在后台运作的 JS 文件
- `content.js` 注入用户页面的 JS 文件

当然了，在上面是找不到这几个文件的，我们要做的就是怎么通过上面那一串文件来构建出这几个文件。

我们先来讲下项目中的文件、文件夹是干什么的：

- `dist` 项目生成文件夹，也就是说我们构建出来的文件也是在这里面的。**当开发的时候，在 Chrome 中也是把这个文件夹加载成 Extension**
- `src` 项目的源文件
  - `Components` React 项目中通常用到的组件文件夹，里面的每一个文件夹都是一个组件
  - `background.js` 用来构建后台运作的 JS 文件
  - `content.js` 用来构建注入用户页面的 JS 文件
  - `icon-128.png` 项目 LOGO
  - `manifest.json` 项目的 Chrome Extension 配置文件
  - `popup.html` 用来构建 popup 页面。(如果开发过 React，通常都知道这个文件基本不用怎么动，仅作为一个入口文件而已)
  - `popup.jsx` popup 里面用到的 JS 文件，同时也是 React 的入口
- `webpack.config.js` 自己配置的 Webpack
- `package.json` NPM 配置文件
- `readme.md` 项目介绍



当我们执行 `webpack -p` 来打包 Production 版本的时候， `dist` 文件夹就会生出我们期望的那些文件：

```
├── dist
│   ├── content.bundle.js
│   ├── bundle.css
│   ├── background.bundle.js
│   ├── icon-128.png
│   ├── manifest.json
│   ├── popup.bundle.js
│   └── popup.html
```



## Webpack 配置

OK，那么我们来看看我们从源文件构建出目的文件有哪些步骤：

1. `manifest.json` 和 `icon-128.png` 这种与 JavaScript 无关的文件原封不动的复制过去。
2. `popup.jsx` 构建出一个完整的 React 项目，名字叫做 `popup.bundle.js` ，React 项目中用到的 CSS 构建出 `bundle.css`
3. 把构建出来的 `popup.bundle.js` 在 `popup.html` 中引用
4. `content.js` 和 `background.js` 分别构建出 `content.bundle.js` 和 `background.bundle.js`



### webpack.config.js 内容

这里给出文件完整内容，之后的内容就是按上述内容逐点讲解。若不感兴趣可以直接把文件内容复制走即可。

```js
const path = require('path')
const webpack = require('webpack')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')

module.exports = {
  entry: {
    popup: './src/popup.jsx',
    content: './src/content.js',
    background: './src/background.js'
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].bundle.js'
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
  module: {
    loaders: [
      // We use Babel to transpile JSX
      {
        test: /\.js[x]$/,
        include: [path.resolve(__dirname, './src')],
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets: ['react', 'es2015'],
          plugins: [
            'react-hot-loader/babel'
          ]
        }
      }, {
        test: /\.css$/,
        loader: ExtractTextPlugin.extract({ fallback: 'style-loader', use: 'css-loader' })
      }, {
        test: /\.(ico|eot|otf|webp|ttf|woff|woff2)(\?.*)?$/,
        use: 'file-loader?limit=100000'
      }, {
        test: /\.(jpe?g|png|gif|svg)$/i,
        use: [
          'file-loader?limit=100000', {
            loader: 'img-loader',
            options: {
              enabled: true,
              optipng: true
            }
          }
        ]
      }
    ]
  },
  plugins: [
    // create CSS file with all used styles
    new ExtractTextPlugin('bundle.css'),
    // create popup.html from template and inject styles and script bundles
    new HtmlWebpackPlugin({
      inject: true,
      chunks: ['popup'],
      filename: 'popup.html',
      template: './src/popup.html'
    }),
    // copy extension manifest and icons
    new CopyWebpackPlugin([
      {
        from: './src/manifest.json'
      }, {
        context: './src',
        from: 'icon-**'
      }
    ])
  ]
}

```

### 1. 复制非 JS 内容

这里用到的是 `CopyWebpackPlugin` 这个插件

```js
new CopyWebpackPlugin([
      {
        from: './src/manifest.json'
      }, {
        context: './src',
        from: 'icon-**'
      }
    ])
```

这里做了两件事情：

- 复制 `./src/manifest.json` 到文件前面定义的 `output.path` 中去，或者也可以指定 `to` 属性说明目的路径
- 从 `./src` 中找到符合 `icon-**` 的文件复制过去，这里的目的主要是复制 LOGO

### 2.构建 React 应用

首先我们先把 `popup.jsx` 编译成 `popup.js` ：

```js
{
  test: /\.js[x]$/,
  include: [path.resolve(__dirname, './src')],
  exclude: /node_modules/,
  loader: 'babel-loader',
  query: {
    presets: ['react', 'es2015'],
    plugins: [
      'react-hot-loader/babel'
    ]
  }
}
```

这里是 `module.loaders` 里面关于 JS 和 JSX 的配置信息，有几点需要注意的：

- `loader` 用的是 `babel` ，目的是把我们用 ES6 或者 ES7 写的 React 相关代码进行转码
- `presets` 指的是目的代码，首先指明了需要转义 `react` ，其次要把所有代码翻译到 ES2015

#### reserve jsx file

在这里我碰到了一个坑，就是**Webpack 不会 reverse JSX 文件**

例如，你在一个 JS 文件中引用 `xx.jsx` 文件 ： `import xxx from './xxx'` 。 这样的写法 Webpack 是不认的，一定要写成 `import xxx from './xxx.jsx'` 。这样十分不优雅。

默认的情况下，它只会去找 `xxx` 文件夹、`xxx.js` 、`xxx.json` 。

所以我们要在 Webpack 中指明需要 reverse `.jsx` 这种文件类型：

```js
resolve: {
  extensions: ['.js', '.jsx']
}
```

### 3.把 CSS 和 popup.bundle.js 在 popup.html 中引用

```Js
// create CSS file with all used styles
new ExtractTextPlugin('bundle.css'),
// create popup.html from template and inject styles and script bundles
new HtmlWebpackPlugin({
  inject: true,
  chunks: ['popup'],
  filename: 'popup.html',
  template: './src/popup.html'
}),
```

- 第一个插件指的是把React 中用到的 CSS 抽出来，构建 `bundle.css` 文件
- 第二个插件就是把`bundle.css` 和 `popup.js` 写到 `popup.html` 中

### 4.构建 content.bundle.js 和 background.bundle.js

```js
entry: {
  popup: './src/popup.jsx',
  content: './src/content.js',
  background: './src/background.js'
},
output: {
  path: path.resolve(__dirname, 'dist'),
  filename: '[name].bundle.js'
}
```

实际上这个部分就是告诉了 Webpack 几件事情：

- 有三个文件要构建
- 构建完了之后就根据 `output` 的配置输出

这里有一点需要注意的是：在 `output.filename` 中的 `[name]` 指的是 `entry` 中的 KEY

也就是说：

```js
entry: {
  foo: './src/bar.jsx'
},
output: {
  path: path.resolve(__dirname, 'dist'),
  filename: '[name].bundle.js'
}
```

这代码值的就是用 `./src/bar.jsx` 构建出 `./dist/foo.bundle.js`



## 如何工作

开启 Watch 模式自动监控文件改变，并且 Reload 项目

```bash
webpack --watch
```

**这个 Reload 只适用于 popup.html 相关文件的改变，content.bundle.js 和 background.bundle.js 需要在 Chrome 中 Reload 项目**

## 写在最后

这样的一个脚手架可以给 Chrome Extension 的开发者一个比较好的开发环境。在此之前我一直都是写原生的 JavaScript 代码，导致开发体验十分差。

我也是一个 JavaScript 新手，如有差错，请见谅。