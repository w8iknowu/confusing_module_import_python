# Python中令人困惑的模块导入
> 一句话总结: 绝对路径保平安

## 问题描述
我在过去很长一段使用Python的时间里, 都仅限于一些简单模块, 文件结构也都很简单, 文件嵌套不会超过2层, 所以即便在模块导入上碰到些<code>Module Not Found</code>的问题, 也都是出问题那会儿去网上搜下方法赶紧应付过去----直到现在.

比如说我当前有个项目, 里面我有两个功能需要实现, 功能1和功能2可以独立运行, 但最终会搭配使用. 我将其分别放在该项目的两个文件夹下, 各自作为一个独立模块, 在这每个文件夹内, 包含了一些为了该模块服务的子模块(或者说子文件夹), 类似于:
```
─ my_project
    ├── main.py
    ├── module_1
    │   ├── __init__.py
    │   ├── data
    │   ├── enum_type
    │   └── module_1.py
    └── module_2
        ├── __init__.py
        ├── data
        ├── enum_type
        └── module_2.py
```
子模块之间可能会互相调用, 于是我在开发过程中频繁地出现找不到模块的问题, 比如好不容易调试好了modue_1/enum_type下的某个枚举文件, 然后在module_1.py中导入时发现找不到模组, 而在好不容易完成module_1的功能, 并在module_2/module_2.py中尝试调用时, 又告诉我找不到module_1模块的位置...

鉴于解决模块路径花费过多时间, 所以决定至少从这次起, 要找到一个稳妥且绝大多数时刻都适用的导入方式, 以免以后又在这种踩了不知多少次的坑上继续耗费时间. 

本文测试环境以Python3.10为主, 但适用于Python3的任意版本.
> [!WARNING]
> ***本文流水账记事, 且水得会比较厉害, 可直接跳转至总结部分.***

## 什么是脚本(Script)
现在当你尝试学习Python时, 在配置环境后, 按照当前大部分的教程, 基本都是手动或在IDE内新建一个hello.py文件, 键入经典的问候代码, 点击IDE(VSCode, PyCharm等)的运行按钮或在命令台里通过<code>python3 hello.py</code>即可完成程序的运行. 但我们(或者说只是我自己)也许忘了, 最开始的hello代码是在Shell(终端)内, 通过Python解释器运行的. 就是那个在命令行界面内输入<code>python3</code>后弹出的界面:
```bash
# Python解释器:
neowell@Vault:~/project/confusing_import$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> print('hello world!')
hello world!
>>>
```
但用这种方式运行的代码, 在你退出解释器后就会丢失<sup>1</sup>, 下次进入解释器时就得重新输入代码. 方便起见, 会考虑先将代码保存在一个文件里, 这样当你需要执行时直接使用这个文件中的内容就好了. 这内容就是所谓的***脚本(Script)***. 
> [!NOTE]
> 此处的"脚本"指的是你实际编写的代码内容, 而不是用于保存代码的xxx.py文件本身.

## 什么是模块(Module)
通过编写脚本, 除了可防止代码运行后丢失外, 还有一个好处, 就是可以复用, 当多个程序都需要调用同一个函数时, 你不必将这段函数代码复制到每个程序中, 只用通过语句声明来调用同一个文件就好.

那么像这样的一个保存了特定脚本内容、可被其它程序调用, 或者说导入的文件， 就被称作***模块(Module)***.
一个模块文件通过后缀 ***.py*** 被Python识别. 我们平时写的各种```.py```文件其实可以看作是一个个模块.

### 演示-1
现在我们来看一个简单例子, 为了使我们的hello world代码在退出解释器后仍能被使用, 我们创建一个<code>hello_module.py</code>文件用于保存以下代码:
```python
# hello_module.py
def say_hello() -> None:
    print('Hello world!')
```
现在我们通过终端重新进入Python解释器, 通过<code>import</code>关键字来调用该模块并使用模块的<code>say_hello</code>函数, 请留意执行时的路径:
```bash
# 1. 列出当前文件
neowell@Vault:~/project/confusing_import/simple_case$ ls
hello_module.py

# 2. 查看hello_module.py的内容
neowell@Vault:~/project/confusing_import/simple_case$ cat hello_module.py
# hello_module.py
def say_hello() -> None:
    print('Hello world!')

# 3. 在解释其中导入模块并调用其中的方法
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
>>> hello_module.say_hello() # 通过module.xx的方式访问模块中的特定函数
Hello world!
>>>
```
甚至可以在一段程序里重复调用:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
>>> hello_module.say_hello()
Hello world!
>>> hello_module.say_hello()
Hello world!
>>> hello_module.say_hello()
Hello world!
>>>
```
看, 这样一来我们不用在解释器内重新编写代码, 只用导入提前写好的模块就可以了, 也不用担心退出解释器后代码的丢失问题了.

除了<code>import module</code>的写法, 你也可用通过<code>from module import function</code>的方式只导入特定的函数:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from hello_module import say_hello
>>> say_hello()
Hello world!
>>>
```

### 演示-2
这样做的另一个好处则在于, 通过模块导入来使用其中函数的方式, 可以避免两个模块中出现同名函数时, 发生调用冲突的问题. <code>module_1.hello()</code>与<code>module_2.hello()</code>得以通过模块名区分.

关于每个模块的名字, 我们可以通过全局变量```__name__```来取得:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
>>> hello_module.__name__
'hello_module'
>>>
```


你可以放心地在另一个模块中同样编写一个<code>say_hello</code>函数, 并在同一个程序中调用:
```python
# howdy_module.py
def say_hello() -> None:
    """greeting with another form"""
    print(f'Howdy world!')
```
```bash
# 两个不同的问候模块
neowell@Vault:~/project/confusing_import/simple_case$ ls
hello_module.py  howdy_module.py

# 调用不同模块的同名方法
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
>>> import howdy_module
>>> hello_module.say_hello()
Hello world!
>>> howdy_module.say_hello()
Howdy world!
>>>
```
你也可以通过<code>as</code>为模块或函数赋予一个别名来进一步简化调用方式:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module as hm
>>> from howdy_module import say_hello as say_hello
>>> hm.say_hello()
Hello world!
>>> say_hello()
Howdy world!
>>>
```
### 演示-3
当通过<code>import</code>导入模块时, 会执行模块内的代码, 这也是上述的演示代码中, 要将目标代码以函数的形式封装的原因. 如果不这么做, 而是直接将指定代码写入文件的话:
```python
# naive_module.py
print('Hello world from naive module!')
```
那么在导入模块的那一步, 就会直接执行模块中的代码, 这种擅自执行的情况显然不是我们想看见的:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import naive_module
Hello world from naive module!
>>>
```
> [!NOTE]
> 我们可以利用这个特性来简化自己程序的一些初始化操作, 这一特点将在后文阐述. 但除此以外, 我们在编写模块时, 应当避免这样的状况, 将所需的功能代码封装起来.
## 什么是包(Package)
我们需要通过编写脚本的形式管理我们的代码, 并加以复用, 这个成品文件就是模块. 同样地, 我们在完成一个个模块文件后, 也需要管理这些文件.

以我们先前的代码举例, 我们用英文输出了一句问候语"Hello world", 现在我们拓展一下, 要求用不同语言来输出这句问候语, 进一步, 不仅仅是问候语, 我们要求按语种, 分别输出各自语言里表示道歉、感谢等通用词语, 为此你需要有诸如```apology.py```, ```thank.py```等, 现在我们又增加了语种要求, 所以你的实际文件名可能诸如```chinese_hello.py```, ```english_hello.py```, ```chinese_apology.py```, ```english_apology.py```...

你当然可以像这样一把梭, 全部放在一起. 不过为了更好地管理与今后方便拓展, 这时我们就需要包(Package)了. 简单来说, 包可以看作我们日常在电脑里为了分类创建的各种文件夹, 比如在上述这个例子里, 我们如果以包的思路去组织文件, 它的形式大概如下:
```bash
world_module/
├── __init__.py # 将world_module初始化为一个包
├── chinese
│   ├── __init__.py # 将chinese初始化为一个子包
│   ├── apology.py
│   ├── hello.py
│   └── thank.py
└── english
    ├── __init__.py # 将english初始化为一个子包
    ├── apology.py
    ├── hello.py
    └── thank.py
```
整体结构与使用文件夹分类无异. 通过在每个文件夹下创建一个```__init__.py```文件, 这样才可以让Python将这些文件夹视作可调用的包. 我们通过两个```hello.py```文件来看下效果:
```bash
# 1. 此处只关注world_module文件夹
neowell@Vault:~/project/confusing_import$ ls
day_of_life  my_project  simple_case  world_module

# 2. 查看两个语言模块下的问候子模块
neowell@Vault:~/project/confusing_import$ cat world_module/chinese/hello.py
def say_hello() -> None:
    print(f'你好, 世界!')
neowell@Vault:~/project/confusing_import$ cat world_module/english/hello.py
def say_hello() -> None:
    print('Hello World!')

# 3. 分别调用它们
neowell@Vault:~/project/confusing_import$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import world_module.chinese.hello as c_hello
>>> import world_module.english.hello as e_hello
>>> c_hello.say_hello()
你好, 世界!
>>> e_hello.say_hello()
Hello World!
>>>
```
通过包的形式, 方便模块的统一与拓展, 而且在语义上也更容易理解模块的作用.
> [!NOTE]
> 关于```__init__.py```, 将在后面一章来解释其主要作用, 当前只用记得一点: 当你使用文件夹管理模块文件时, 请在这个文件夹下创建一个空的```__init__.py```文件(包括文件夹内的嵌套文件夹), 使Python将这个文件夹标记为一个包.

## Python文件的运行方式
### 脚本式运行
在上一章中, 通过编写脚本, 将其保存为一个.py文件, 便可将其作为一个模块供其它程序调用. 除此以外, 我们也可以直接运行编写的脚本文件本身, 格式为<code>python3 xx.py</code>.这也是我们大部分人所熟知的方式.
#### 演示-1
同样以上一章的例子<code>hello_module.py</code>, 为了使代码运行, 在定义函数后对其调用:
```python
# hello_module.py
# 定义函数
def say_hello() -> None:
    print('Hello world!')

# 调用函数
say_hello()
```
运行结果:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3 hello_module.py
Hello world!
```
#### 演示-2
在上一章末尾的<code>naive_module</code>例子提到过, 我们应当避免在文件内直接放入可执行代码, 为此, 我们可以使用上一章提到的全局变量 ***\_\_name\_\_***. 当我们调用模块时, 通过<code>module.\_\_name\_\_</code>可以获取模块的模块名, 而当我们通过脚本式直接运行模块文件时, 会把 ***\_\_name\_\_*** 的值赋值为 ***"\_\_main\_\_"***, 我们可以先改写上述的文件来测试下:

```python
# hello_module.py
# 定义函数
def say_hello() -> None:
    print('Hello world!')

# 调用函数
say_hello()

# 查看当前的__name__
print(f'__name__ = {__name__}')
```

运行结果:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3 hello_module.py
Hello world!
__name__ = __main__
```
基于此原理, 我们可以在模块文件中, 通过判断 ***\_\_name\_\_*** 的值来决定:
```python
# hello_module.py
# 定义函数
def say_hello() -> None:
    print('Hello world!')

if __name__ == '__main__':
    say_hello()
```
这样无论以模块被调用, 还是以脚本式运行, 都可以根据这个if条件来分情况执行:
* 以脚本运行:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3 hello_module.py
Hello world!
```
* 以模块调用:
```bash
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
>>> hello_module.say_hello()
Hello world!
>>>
```
> [!TIP]
> 这是Python中运行代码的推荐方式, 如果你有其它语言基础, 会发现这像其它语言中的main函数概念, 这样也能让你的代码层次更清晰, 在查看别人的代码时, 你也容易知道该从哪里入手.

### 模块的搜索方式
> [!NOTE]
> 本章可能需要你对Python的虚拟环境有基本的了解或使用经验, virtualenv, conda, poetry等皆可. 至少需要了解虚拟环境的创建和切换, 以及在不同环境下安装过第三方模块.

当你在脚本中导入外部模块(或包)时, 解释器会从以下这几个地方进行搜索<sup>2</sup>:
1. 安装Python时的默认值
2. <code>PYTHONPATH</code>环境变量
3. 运行脚本时脚本的所在目录

> [!NOTE]
> Python的搜索路径可以通过<code>sys.path</code>进行查看, 通过<code>sys.executable</code>可以查看python解释器的路径. 通过这两个方法, 我们可以自行验证当前python环境的模块搜索路径, 以及当处于虚拟环境时, 此时的解释器位置. 这是两个非常有用的命令, 接下来以此我们查看下以上三种方法的运作形式. 请留意每个例子中执行的路径位置.

#### 1. 安装python时的默认值
这是当我们在系统下(无论是主机还是容器中)安装python(无论通过包管理工具、自行编译还是其它方式)时的情况, 我们还是先通过解释器来查看相关内容:
```bash
# 查看默认Python环境的包搜索路径, 以及Python的执行路径
neowell@Vault:~/project/confusing_import/simple_case$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> sys.path
['', '/usr/lib/python310.zip', '/usr/lib/python3.10', '/usr/lib/python3.10/lib-dynload', '/home/neowell/.local/lib/python3.10/site-packages', '/usr/local/lib/python3.10/dist-packages', '/usr/lib/python3/dist-packages']
>>> sys.executable
'/usr/bin/python3'
>>>
```
当然, 这个部分我们当前可以不用关心, 这些部分一般是我们使用```pip```安装第三方包时使用的路径. 主要作用在创建虚拟环境时的查看, 请留意创建路径:
```bash
# 1. 创建虚拟环境的文件夹, 名为env_sc, 位于simple_case下
neowell@Vault:~/project/confusing_import/simple_case$ python3 -m venv env_sc

# 2. 激活虚拟环境
neowell@Vault:~/project/confusing_import/simple_case$ source env_sc/bin/activate

# 3. 查看虚拟环境下Python执行路径的变化
(env_sc) neowell@Vault:~/project/confusing_import/simple_case$ python
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> sys.path
['', '/usr/lib/python310.zip', '/usr/lib/python3.10', '/usr/lib/python3.10/lib-dynload', '/home/neowell/project/confusing_import/simple_case/env_sc/lib/python3.10/site-packages']
>>> sys.executable
'/home/neowell/project/confusing_import/simple_case/env_sc/bin/python'
>>>
```
我在<code>simple_case</code>文件夹里面创建并激活了一个虚拟环境, 通过这种方法创建的python解释器路径就是我创建虚拟环境时对应的路径了.
> [!TIP]
> 题外话: 只要你的项目涉及第三方模块的安装时, 你就应该通过虚拟环境工具或docker等容器管理工具创建相互独立的Python开发环境. 或者极端点说, 任何情况下你都不应该在系统默认的Python环境内运行项目, 关于这一点, 在2023年甚至已有老哥想通过PEP704将该想法化为了提案<sup>3</sup>.

#### 2.```PYTHONPATH```环境变量
我们前面所有的例子都存放在<code>~/project/confusing_import/simple_case</code>这个文件夹下:
```bash
simple_case/
├── env_sc
├── hello_module.py
├── howdy_module.py
├── naive_module.py
└── naked_module.py
```
当我们在上一级目录, 尝试直接导入模块, 这样当然会失败:
```bash
# 1. 返回上一级目录
neowell@Vault:~/project/confusing_import/simple_case$ cd ..

# 2. 尝试在该路径下导入模块
neowell@Vault:~/project/confusing_import$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'hello_module'
>>>
```
我们可以通过为<code>PYTHONPATH</code>添加该路径的方式, 使Python解释器搜索时会检索我们添加的路径位置:
```bash
# 1.查看当前的PYTHONPATH值, 当前为空
neowell@Vault:~/project/confusing_import$ echo $PYTHONPATH

# 2. 将simple_case的路径加入
neowell@Vault:~/project/confusing_import$ export PYTHONPATH=/home/neowell/project/confusing_import/simple_case
# 3. 再次确认
neowell@Vault:~/project/confusing_import$ echo $PYTHONPATH
:/home/neowell/project/confusing_import/simple_case

# 4. 再次尝试导入模块
neowell@Vault:~/project/confusing_import$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
>>> hello_module.say_hello()
Hello world!
>>> sys.path
['', '/home/neowell/project/confusing_import/simple_case', '/usr/lib/python310.zip', '/usr/lib/python3.10', '/usr/lib/python3.10/lib-dynload', '/home/neowell/.local/lib/python3.10/site-packages', '/usr/local/lib/python3.10/dist-packages', '/usr/lib/python3/dist-packages']
>>>
```
通过这种形式, 成功找到了我们所需的模块位置. 通过<code>sys.path</code>会发现<code>PYTHONPATH</code>的路径也被添加进搜索路径
> [!TIP]
> 通过export设置环境变量的方法是临时性的, 在关闭当前窗口后便会丢失. 欲永久性地添加环境变量, 请自行搜索, 本处不作展开.

#### 3. 运行脚本时脚本的所在目录
终端里所处路径无论在哪里, Python的搜索路径都以脚本的位置为默认搜索路径:
```bash
# 在simple_case文件夹下执行脚本:
(env_sc) neowell@Vault:~/project/confusing_import/simple_case$ python hello_module.py
/home/neowell/project/confusing_import/simple_case
/usr/lib/python310.zip
/usr/lib/python3.10
/usr/lib/python3.10/lib-dynload
/home/neowell/project/confusing_import/simple_case/env_sc/lib/python3.10/site-packages
Hello world!

# 返回上级目录并执行脚本:
(env_sc) neowell@Vault:~/project/confusing_import/simple_case$ cd ..
(env_sc) neowell@Vault:~/project/confusing_import$ python simple_case/hello_module.py
/home/neowell/project/confusing_import/simple_case
/usr/lib/python310.zip
/usr/lib/python3.10
/usr/lib/python3.10/lib-dynload
/home/neowell/project/confusing_import/simple_case/env_sc/lib/python3.10/site-packages
Hello world!
```
所以当你的脚本中依赖其它自己编写的其它模块时, 需保证那个模块的路径与脚本路径处在同一位置, 不然就会出现找不到模块的问题.
### 模块式运行
在上一节中, 当我们按脚本运行时, Python会将脚本所在的路径加入到搜索路径中, 那么有没有一种方法将其反过来, 以我们执行时的路径作为搜索路径呢? 这就是本章的作用. 

对于一个保存了脚本内容的```xx.py```, 为脚本运行命令添加一个```-m```的标记, 使Python以模块的方式运行该文件: ```python -m xx```. 由于此处是按模块运行, 所以你需要去除```.py```的文件后缀.
如果你的模块以包的形式管理:
```bash
xx/
├── __init__.py
└── yy.py
```
调用时的命令就为: ```python -m xx.yy```.
#### 演示
我们首先为```hello_module.py```增加一个打印```__name__```的方法, 并在以脚本运行时自动打印```__name___```:
```python
# hello_module.py
def say_hello() -> None:
    print('Hello world!')

def get_name() -> None:
    print(f'当前命名为{__name__}')

if __name__ == '__main__':
    import sys
    for i in sys.path:
        print(i)
    say_hello()
    get_name()
```
此时的```simple_case```文件夹如下, 通过创建```__init__.py```将其变为一个包:
```bash
simple_case/
├── __init__.py (标记该文件夹为一个包)
├── env_sc (虚拟环境)
├── hello_module.py (主要文件)
├── howdy_module.py
├── naive_module.py
└── naked_module.py
```
* 首先还是在```simple_case```文件夹下按脚本与模块方式分别运行:
```bash
# 1. 按脚本运行
(env_sc) neowell@Vault:~/project/confusing_import/simple_case$ python hello_module.py
/home/neowell/project/confusing_import/simple_case
/usr/lib/python310.zip
/usr/lib/python3.10
/usr/lib/python3.10/lib-dynload
/home/neowell/project/confusing_import/simple_case/env_sc/lib/python3.10/site-packages
Hello world!
当前命名为__main__

# 2. 按模块运行
(env_sc) neowell@Vault:~/project/confusing_import/simple_case$ python -m hello_module
/home/neowell/project/confusing_import/simple_case
/usr/lib/python310.zip
/usr/lib/python3.10
/usr/lib/python3.10/lib-dynload
/home/neowell/project/confusing_import/simple_case/env_sc/lib/python3.10/site-packages
Hello world!
当前命名为__main__
```
此时两者的搜索路径同为```/simple_case```
* 接下来我们返回上级目录, 再看下结果:
```bash
# 1. 返回上级目录
(env_sc) neowell@Vault:~/project/confusing_import/simple_case$ cd ..

# 2. 按脚本运行
(env_sc) neowell@Vault:~/project/confusing_import$ python simple_case/hello_module.py
/home/neowell/project/confusing_import/simple_case # <======注意此处
/usr/lib/python310.zip
/usr/lib/python3.10
/usr/lib/python3.10/lib-dynload
/home/neowell/project/confusing_import/simple_case/env_sc/lib/python3.10/site-packages
Hello world!
当前命名为__main__

# 3. 按模块运行
(env_sc) neowell@Vault:~/project/confusing_import$ python -m simple_case.hello_module
/home/neowell/project/confusing_import # <======注意此处
/usr/lib/python310.zip
/usr/lib/python3.10
/usr/lib/python3.10/lib-dynload
/home/neowell/project/confusing_import/simple_case/env_sc/lib/python3.10/site-packages
Hello world!
当前命名为__main__
(env_sc) neowell@Vault:~/project/confusing_import$
```
此时我们发现, 当按模块方式执行时, 搜索路径就根据你当前所处的路径为主了.

## 模块导入方式的对比
现在回到我们最初问题描述部分的例子, 并为了举例方便, 为模块1添加一个枚举模块:
```bash
─ my_project
    ├── main.py
    ├── module_1
    │   ├── __init__.py
    │   ├── data
    │   ├── enum_type
    │   │   └── __init__.py
    │   │   └── m1_enum.py
    │   └── module_1.py
    └── module_2
        ├── __init__.py
        ├── data
        ├── enum_type
        └── module_2.py
```
我会把主要的逻辑放在```main.py```中, 其中会使用到```module_1```和```module_2```的模块```moduel_1.py```与```module_2.py```, 这些模块它们也会依赖各自的子模块, 比如存放数据的```data```模块, 管理枚举类的```enum_type```模块.

当我首先编写模块1```module_1.py```, 而该模块恰好需要一个枚举类, 为了方便, 我会让自己处于```my_project/module_1/```路径下, 这样我可以方便地使用脚本调用的方式来测试其中的模块:```python module_1.py```. 此时该模块其中的代码大概是这样的:
```python
# m1_enum.py
def enum_call() -> None:
    print(f'This is enum class')
```
```python
# module_1.py
from enum_type.m1_enum import enum_call
def module_1():
    enum_call()
if __name__ == '__main__':
    module_1()
```
此时测试没问题, 我的模块1非常完美:
```bash
# 注意此时所处路径
(env_sc) neowell@Vault:~/project/confusing_import/my_project/module_1$ ls
__init__.py  data  enum_type  module_1.py
(env_sc) neowell@Vault:~/project/confusing_import/my_project/module_1$ python module_1.py
This is enum class
```
OK, 既然模块1的功能已经搞定, 而我最终要在主目录下的```main.py```中调用, 于是我先尝试引入模块1来测试下, 此时的主方法:
```python
import module_1.module_1 as mod_1

def main() -> None:
    mod_1.module_1()

if __name__ == '__main__':
    main()
```
测试看看:
```bash
(env_sc) neowell@Vault:~/project/confusing_import/my_project$ python main.py
Traceback (most recent call last):
  File "/home/neowell/project/confusing_import/my_project/main.py", line 1, in <module>
    import module_1.module_1 as mod_1
  File "/home/neowell/project/confusing_import/my_project/module_1/module_1.py", line 1, in <module>
    from  enum_type.m1_enum import enum_call
ModuleNotFoundError: No module named 'enum_type'
```
发生报错, 当代码执行到```module_1.py```中时, 系统告诉我无法找到```enum_type```这个模块. 之前对模块1的测试没有问题, 此处为何报错了呢? 原因就出在了搜索路径上:
1. 当测试模块1时, 由于是按脚本运行, 所以那时搜索路径为```my_project/module_1```, 这时```enum_type```处于该路径下, 就没有问题;
2. 而当测试主函数时, 搜索路径变为了```my_project/```, 在这个路径下找不到模块1的枚举包, 自然发生了报错.

为了解决该问题, 我们要做的就是将```enum_type```添加到Python的搜索路径中, 比如:
1. 将对应路径添加到```PYTOHNPATH```中;
2. 将```enum_type```移动到```my_project/```下;
3. 在代码中通过```sys.path.append```添加相关路径;
4. 更改```module_1.py```中的导入方式, 将其按照```main.py```的位置进行修改;
5. ...

第一种方法需要你自己手动将路径添加, 当模块众多时, 你可能还得编写一个额外的脚本来进行批量添加操作;第二种显然不行, 虽然有效, 但会完全弄乱文件结构, 第三种方法和第一种类似, 仍需要靠自己手动添加, 而且在文件头添加这样的代码也不大利于阅读, 当然, 这不是什么大问题.

就我个人而言, 当前会推荐第四种方法. 即把***项目的根目录当作起点, 使其中所有的模块调用全部遵循绝对路径的导入方式, 并以模块运行的方式来测试其中的每一个模块文件***.

首先来修改下本例中的文件:
```python
# module_1.py
from module_1.enum_type.m1_enum import enum_call # <===按根路径导入模块

def module_1():
    enum_call()

if __name__ == '__main__':
    module_1()
```
这样一来, 主函数可以正常运行, 无论哪种方式:
```bash
# 脚本调用
(env_sc) neowell@Vault:~/project/confusing_import/my_project$ python main.py
This is enum class
# 模块调用
(env_sc) neowell@Vault:~/project/confusing_import/my_project$ python -m main
This is enum class
```
当然这时无法按脚本调用```module_1.py```了:
```bash
(env_sc) neowell@Vault:~/project/confusing_import/my_project$ python module_1/module_1.py
Traceback (most recent call last):
  File "/home/neowell/project/confusing_import/my_project/module_1/module_1.py", line 1, in <module>
    from module_1.enum_type.m1_enum import enum_call
  File "/home/neowell/project/confusing_import/my_project/module_1/module_1.py", line 1, in <module>
    from module_1.enum_type.m1_enum import enum_call
ModuleNotFoundError: No module named 'module_1.enum_type'; 'module_1' is not a package
```
没关系, 我们改为模块调用, 使搜寻路径从根目录开始:
```bash
(env_sc) neowell@Vault:~/project/confusing_import/my_project$ python -m module_1.module_1
This is enum class
```
这么做会繁琐了点, 但我认为好处较为明显:
1. 不用考虑导入时的路径问题, 统一导入思路, 减少该部分的思维负担和避免外工作量(编写环境变量导入脚本);
2. 模块的独立化, 比如模块1的功能如果不涉及其它模块的引用, 那么在完成该模块以后, 我完全可以将该模块(文件夹)复制出来丢到另一个项目中, 不用作任何修改就能使用;
3. 方便测试, 如果随后需要进行单元测试, 你可能还需要在根目录下新建一个```test```文件夹, 并存放你的测试代码, 通过这种根目录式的导入方式, 你在测试文件夹下的导入也会更加简洁;
> [!NOTE]
> 通过模块调用也有个比较麻烦的地方, 那就是当你运行命令```python -m xx.yy```时, 是不支持自动补全的... 这其实在你测试模块时会感到麻烦. 此处我的办法是在测试模块时, 用```alias```命令绑定测试命令, 从而简化输入, 比如我把```qq```与模块命令绑定: ```alias qq="python -m xx.yy"```. 这样之后只用在命令行里输入```qq```即可, 而且这个命令也只是临时性的, 关闭当前窗口后就会消失:
> ```bash
> (env_sc) neowell@Vault:~/project/confusing_import/my_project$ alias qq="python -m module_1.module_1"
> (env_sc) neowell@Vault:~/project/confusing_import/my_project$ qq
> This is enum class
> ```

## 模块导入方式总结
不再使用脚本式运行```python module.py```, 而是基于设置根目录为Python搜索路径的思路, 以绝对路径的导入方式, 使导入结构清晰化, 且可统一在根目录下通过```python -m module```的方式测试处于不同路径、不同深度的模块文件而不用担心找不到模块的问题.

...就是还有一点, 我们看上面的那个导入代码```from module_1.enum_type.m1_enum import enum_call```, 这会不会太长了点? 再看那个模块调用的部分```module_1.module_1```, 前面的```module_1```是被```__init__.py```标注为包的文件夹, 后面的```module_1```是模块文件```module_1.py```, 这在命名规则上虽然没什么问题, 但在分辨上却容易造成混淆, 如果子模块嵌套深一些, 这个导入可能会变得很长且不好辨认.

为此, 我们可以通过```__init__.py```这个文件来优化我们在主模块部分的阅读问题.

## 关于__init__.py
之前的章节中, 我们通过创建一个空的```__init__.py```来标记一个文件夹为包(Package), 在本章, 我们通过修改该文件, 来提高我们在主模块中遇到的一些体验问题.

首先, 先处理下在之前包的章节中被刻意忽视的一个部分.
### 无需```__init__.py```即可导入包?
如果你自己之前实操过, 可能会发现自己并没有创建这个```__init__.py```文件, 但仍能正常导入:
```bash
neowell@Vault:~/project/confusing_import$ ls not_package/
hello_module.py
neowell@Vault:~/project/confusing_import$ cat not_package/hello_module.py
# hello_module.py
def say_hello() -> None:
    print('Hello world!')

def get_name() -> None:
    print(f'当前命名为{__name__}')

if __name__ == '__main__':
    import sys
    for i in sys.path:
        print(i)
    say_hello()
    get_name()

neowell@Vault:~/project/confusing_import$ python3
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import not_package.hello_module as hm # <=======未标记的情况下仍能正常导入
>>> hm.say_hello()
Hello world!
>>>
```
当遇到以上情况, 其中一种可能是你的Python版本大于等于```3.3```. 这是因为在```PEP 420```<sup>4</sup>中, 即从```Python3.3```开始, 引入了名为```(隐式)命名空间包(Implicit Namespace Packages)```的机制, 旨在解决处于同一命名空间下不同包的调用问题, 比如:
```bash
company/
├── pkg_1
│   └── mod
│       └── a.py
└── pkg_2
    └── mod
        └── b.py
```
简单点说, 通过该机制, 我们可以通过```mod.a```与```mod.b```的形式调用这两个模块. 但也是由于这个机制, 现在所有在项目下创建的文件夹都会被Python自动看作为一个包.

所以在Python3.2及之前的版本, 你仍需要手动创建```__init__.py```, 而在Python3.3及以后的版本, 你可以不用显式地创建.
在此我也自己通过Docker找了几个对应的镜像验证了下:
#### Python2.7中的导入
Python2.7应该是Python2时代最后的一个大版本, 且是Python2中的主流版本, 所以此处对Python2的实验版本为2.7.
> [!NOTE]
> 由于暂时没找到官方的Python2.7镜像, 所以就选择Centos镜像, 其内部预置Python2.7, 我使用的版本为:
> ```docker pull centos:centos7```

我们首先看下同样的程序在python2.7下的表现:
```bash
[root@0f2acf31a627 simple_case_py2]# ls
hello_module.py

[root@0f2acf31a627 simple_case_py2]# cat hello_module.py
# hello_module.py
def say_hello():
    print('Hello world!')

if __name__ == '__main__':
    say_hello()

[root@0f2acf31a627 simple_case_py2]# python
Python 2.7.5 (default, Oct 14 2020, 14:45:30)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import hello_module
>>> hello_module.say_hello()
Hello world!
>>>
```

现在我们把<code>hello_module.py</code>移动到当前路径下的一个新文件夹, 并尝试调用:
```bash
[root@0f2acf31a627 simple_case_py2]# ls
mod
[root@0f2acf31a627 simple_case_py2]# ls mod/
hello_module.py
[root@0f2acf31a627 simple_case_py2]# python
Python 2.7.5 (default, Oct 14 2020, 14:45:30)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import mod.hello_module as hm
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: No module named mod.hello_module
```
无法找到指定模组, 现在我们在```mod```文件夹内创建一个空的```__init__.py```文件, 再尝试调用:
```bash
[root@0f2acf31a627 simple_case_py2]# touch mod/__init__.py
[root@0f2acf31a627 simple_case_py2]# python
Python 2.7.5 (default, Oct 14 2020, 14:45:30)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import mod.hello_module as hm
>>> hm.say_hello()
Hello world!
```
此时可以成功调用, 通过```__init__.py```文件, 使```mod```文件夹被当作一个模组看待

#### Python3中的导入
* Python3.2
```bash
root@6e1f2113da8a:~# ls
root@6e1f2113da8a:~# mkdir module_1
root@6e1f2113da8a:~# python
Python 3.2.6 (default, Jan 18 2016, 19:21:14)
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import module_1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: No module named module_1 # <======Python3.2下, 没有__init__.py的文件夹无法被Python视作包
>>>

# 创建__init__.py以标记该文件夹为包
root@6e1f2113da8a:~# touch module_1/__init__.py
root@6e1f2113da8a:~# python
Python 3.2.6 (default, Jan 18 2016, 19:21:14)
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import module_1
>>> module_1
<module 'module_1' from 'module_1/__init__.py'>
>>>
```
* Python3.3
```bash
root@be639363057e:~# ls
root@be639363057e:~# mkdir module_1
root@be639363057e:~# python
Python 3.3.7 (default, Sep 19 2017, 23:13:00)
[GCC 4.9.2] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import module_1 # <=======没有__init__.py依然能将module_1视作包导入
>>> module_1
<module 'module_1' (namespace)>  # <=======此时以隐式命名空间的形式将module_1视为包
>>>

# 再显式地创建__init__.py, 重新测试
root@be639363057e:~# touch module_1/__init__.py
root@be639363057e:~# python
Python 3.3.7 (default, Sep 19 2017, 23:13:00)
[GCC 4.9.2] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import module_1
>>> module_1
<module 'module_1' from './module_1/__init__.py'> # <=============显式创建下的情况
>>>
```

#### 显式好于隐式(Explicit is better than implicit)
根据上面的表现, 在没有特别要求, 且使用Python3.3+的情况下, 是否应该省略该文件的创建呢? 这里也装模做样地引用***Python之禅(The Zen of Python)*** 其中的一句话: ```"显式好于隐式(Explicit is better than implicit)"```<sup>5</sup>. 当你不需要使用命名空间包, 仅仅只是用于标记包时, 就不应该使用该功能, 而是显式创建文件来标记文件夹. 通过这样的标记也能帮助你更好地认识、组织项目结构, 哪些文件夹是包, 哪些文件夹仅仅是文件夹.

### 包的初始化
好了, ~~在又水了一章后,~~ 回到```__init__.py```本身.
当从包里导入对应模块时, 会首先执行```__init__.py```中的代码:
```bash
# __init__.py定义一个简单的打印代码
neowell@Vault:~/project/confusing_import$ ls my_package/
__init__.py  __pycache__  hello_module.py
neowell@Vault:~/project/confusing_import$ cat my_package/__init__.py
print(f'__init__率先执行: {__name__}')


# 导入my_package包
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import my_package.hello_module as hm
__init__率先执行: my_package # <======__init__.py内的代码被执行
>>> hm.say_hello()
Hello world!
>>>
```
如同Python类中的```__init__```方法, 用于初始化相关参数. ```__init__.py```就好比包的初始化方法.

现在回到上一章的例子(省略掉无用的module_2):
```bash
.
├── main.py
└──── module_1
       ├── __init__.py
       ├── data
       ├── enum_type
       │   ├── __init__.py
       │   └── m1_enum.py
       └── module_1.py
```
* module_1.py
```python
from module_1.enum_type.m1_enum import enum_call

def module_1():
    enum_call()

if __name__ == '__main__':
    module_1()
```
* main.py
```python
import module_1.module_1 as mod_1

def main() -> None:
    mod_1.module_1()

if __name__ == '__main__':
    main()
```
现在我们来修改对应代码以使用新的导入语句:
1. 枚举包的修改```/module_1/enum_type/__init__.py```:
```python
# 当前m1_enum.py中仅enum_call一个方法
from module_1.enum_type.m1_enum import enum_call
```
2. 此时使用了该包的```/module_1/module_1.py```可简化:
```python
# from module_1.enum_type.m1_enum import enum_call
""" 
当导入module_1.enum_type包时, enum_type/__init__.py首先执行语句:
"from module_1.enum_type.m1_enum import enum_call"
此时enum_call已被导入, 此时在本文件内便可直接调用.

除了缩短代码长度, 语义也更清晰, 即该模块从module_1下的枚举包内导入了一个名为enum_call的方法
"""
from module_1.enum_type import enum_call

def module_1():
    enum_call()

if __name__ == '__main__':
    module_1()
```
3. 我们可以先测试下当前的效果, 注意执行路径仍处于根目录下:
```bash
neowell@Vault:~/project/confusing_import/my_project$ ls
__pycache__  main.py  module_1  module_2
neowell@Vault:~/project/confusing_import/my_project$ python3 -m module_1.module_1
This is enum class
```

4. 接下为了处理```main.py```, 我们首先配置```/module_1/__init__.py```:
```python
from module_1.module_1 import module_1
```
> [!NOTE]
> 通过该步骤, 我们也正式将模块1封装为一个完整的包
5. 而对于```/main.py```:
```python
import module_1.module_1 as mod_1
# from module_1 import module_1 as mod_1 <====也可以这么写

def main() -> None:
    # mod_1.module_1() # <==========需修改此处的调用方式
    mod_1()

if __name__ == '__main__':
    main()
```
之前的module_1.module_1代表的是```module_1.py```这个模块, 所以在调用时需要调用模块中的方法, 名字也是```module_1()```, 而现在修改后, module_1.module_1代表的就是```module_1()```这个方法.

6. 测试, 没问题:
```bash
neowell@Vault:~/project/confusing_import/my_project$ python3 -m main
This is enum class
```
通过```__init__.py```可以方便地预配置部分参数, 但请避免将需要长时间计算的步骤放在这里面, 不然会导致性能问题.

### 区分命名空间
在前面模块部分有提到过, 通过不同的模块作为命名, 我们可以编写相同名称方法置于不同的模块里, 而不用担心重名问题. 此处的```__init__.py```也有这样的作用.

比如对前面的例子, 为了更加正规与管理, 我们在测试时, 其实应当统一放在一个文件夹下, 比如这样:
```bash
neowell@Vault:~/project/confusing_import/my_project$ ls test/
__pycache__  test.py
neowell@Vault:~/project/confusing_import/my_project$ cat test/test.py
"""
此处存放单元测试代码, 现在为了简略暂不使用
"""
import module_1.module_1 as mod_1

def main_test() -> None:
    mod_1()

if __name__ == '__main__':
    main_test()
```
基于前面提到的隐式命名空间, 省略```__init__.py```是可以的, 这样导入没有问题, 我们现在来测试下:
```python
neowell@Vault:~/project/confusing_import/my_project$ python3 -m test.test
/usr/bin/python3: No module named test.test
```
发生报错, 无法找到模块. 这里之所以会这样, 是因为在Python中, 也有一个内置的模块就叫做```test```, 我们可以调用测试下:
```bash
neowell@Vault:~/project/confusing_import/my_project$ python3 -m test
== CPython 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0]
== Linux-5.15.133.1-microsoft-standard-WSL2-x86_64-with-glibc2.35 little-endian
== cwd: /tmp/test_python_194133æ
== CPU count: 22
== encodings: locale=UTF-8, FS=utf-8
0:00:00 load avg: 0.32 Run tests sequentially
...
```
此时我们如果修改test文件夹的名字, 与内置模块区分命名, 就没问题了:
```bash
neowell@Vault:~/project/confusing_import/my_project$ mv test/ testXX
neowell@Vault:~/project/confusing_import/my_project$ python3 -m testXX.test
This is enum class
```
这么做可以解决, 也没有问题. 不过仍需考虑这两点:
1. 以```test```作为测试文件夹命名已属于相对成熟的习惯性约定
2. 依赖了隐式命名空间的(副作用)机制

为此, 我们可以将```test```文件夹标记为一个包, 这样仍可以与内置模块区分:
```bash
neowell@Vault:~/project/confusing_import/my_project$ mv testXX/ test
neowell@Vault:~/project/confusing_import/my_project$ touch test/__init__.py
neowell@Vault:~/project/confusing_import/my_project$ python3 -m test.test
This is enum class
```
## 最后总结
为了避免再在包的导入上耗费不必要的时间, 我选择了一种绝对的方法, 即全部以项目根目录为起点来进行包/模块的导入, 并通过```__init__.py```对包的初始化功能, 简化了在主模块中的导入方式, 并提高了语义信息, 进一步提升了阅读体验.

尽管不够聪明, 但当前够用了, 等以后踩着新坑或有更多经验了再看看怎么去进一步优化吧.
## 参考
[1] [Python官方中文文档: 模块](https://docs.python.org/zh-cn/3.10/tutorial/modules.html#modules)

[2] [Python官方中文文档: 模块搜索路径](https://docs.python.org/zh-cn/3.10/tutorial/modules.html#the-module-search-path)

[3] [Python增强提案 704 - Require virtual environments by default for package installers](https://peps.python.org/pep-0704/)

[4] [Python增强提案 420(已生效) - Implicit Namespace Packages](https://peps.python.org/pep-0420/)

[5] [Python之禅- The Zen of Python(PEP 0020)](https://peps.python.org/pep-0020/)