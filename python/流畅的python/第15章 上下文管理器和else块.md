## 上下文管理器和else块

### 先做这个，再做那个：if语句之外的else块

else子句不仅能在if语句中使用，还能在for、while和try语句中使用。

for/else、while/else和try/else的语义关系紧密，不过与if/else差别很大。

else子句的行为如下:

- for: 仅当for循环运行完毕时（即for循环没有被break语句中止）才运行else块。
- while: 仅当while循环因为条件为假值而退出时（即while循环没有被break语句中止）才运行else块。
- try: 仅当try块中没有异常抛出时才运行else块。官方文档还指出：“else子句抛出的异常不会由前面的except子句处理。”

在所有情况下，如果异常或者return、break或continue语句导致控制权跳到了复合语句的主块之外，else子句也会被跳过。

在这些语句中使用else子句通常能让代码更易于阅读，而且能省去一些麻烦，不用设置控制标志或者添加额外的if语句。

在循环中使用else子句的方式如下述代码片段所示：

 ```python
 for item in my_list:
   if item.flavor == 'banana':
     break
   else:
     raise ValueError('No banana flavor found!')
 ```

after_call（　）不应该放在try块中。为了清晰和准确，try块中应该只抛出预期异常的语句。因此，像下面这样写更好：

```python
try:
  dangerous_call()
except OSError:
  log('OSError...')
else:
  after_call()
```

在Python中，try/except不仅用于处理错误，还常用于控制流程。为此，Python官方词汇表还定义了一个缩略词（口号）:

- EAFP： 取得原谅比获得许可容易（easier to ask for forgivenessthan permission）。这是一种常见的Python编程风格，先假定存在有效的键或属性，如果假定不成立，那么捕获异常。这种风格简单明快，特点是代码中有很多try和except语句。与其他很多语言一样（如C语言），这种风格的对立面是LBYL风格。
- LBYL：三思而后行（look before you leap）。这种编程风格在调用函数或查找属性或键之前显式测试前提条件。与EAFP风格相反，这种风格的特点是代码中有很多if语句。在多线程环境中，LBYL风格可能会在“检查”和“行事”的空当引入条件竞争。例如，对if key in mapping: return mapping[key]这段代码来说，如果在测试之后，但在查找之前，另一个线程从映射中删除了那个键，那么这段代码就会失败。这个问题可以使用锁或者EAFP风格解决。

### 上下文管理器和with块

上下文管理器对象存在的目的是管理with语句，就像迭代器的存在是为了管理for语句一样。

with语句的目的是简化try/finally模式。这种模式用于保证一段代码运行完毕后执行某项操作，即便那段代码由于异常、return语句或sys.exit（　）调用而中止，也会执行指定的操作。finally子句中的代码通常用于释放重要的资源，或者还原临时变更的状态。

上下文管理器协议包含`__enter__`和`__exit__`两个方法。with语句开始运行时，会在上下文管理器对象上调用`__enter__`方法。with语句运行结束后，会在上下文管理器对象上调用`__exit__`方法，以此扮演finally子句的角色。

最常见的例子是确保关闭文件对象。演示把文件对象当成上下文管理器使用：

```python
>>> with open('mirror.py') as fp:  # ➊
...     src = fp.read(60)  # ➋
...
>>> len(src)
60
>>> fp  # ➌
<_io.TextIOWrapper name='mirror.py' mode='r' encoding='UTF-8'>
>>> fp.closed, fp.encoding  # ➍
(True, 'UTF-8')
>>> fp.read(60)  # ➎
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: I/O operation on closed file.
```

- ❶ fp绑定到打开的文件上，因为文件的`__enter__`方法返回self。
- ❸ fp变量仍然可用
- ❺ 但是不能在fp上执行I/O操作，因为在with块的末尾，调用`TextIOWrapper.__exit__`方法把文件关闭了。

执行with后面的表达式得到的结果是上下文管理器对象，不过，把值绑定到目标变量上（as子句）是在上下文管理器对象上调用`__enter__`方法的结果。

`__enter__`方法除了返回上下文管理器之外，还可能返回其他对象。

不管控制流程以哪种方式退出with块，都会在上下文管理器对象上调用`__exit__`方法，而不是在`__enter__`方法返回的对象上调用。

with语句的as子句是可选的。对open函数来说，必须加上as子句，以便获取文件的引用。不过，有些上下文管理器会返回None，因为没什么有用的对象能提供给用户。

解释器调用`__enter__`方法时，除了隐式的self之外，不会传入任何参数。传给`__exit__`方法的三个参数列举如下:

- exc_type: 异常类（例如ZeroDivisionError）。
- exc_value: 异常实例。有时会有参数传给异常构造方法，例如错误消息，这些参数可以使用exc_value.args获取。
- traceback: traceback对象。

我们在with块之外手动调用`__enter__`和`__exit__`方法。

### contextlib模块中的实用工具

自己定义上下文管理器类之前，先看一下Python标准库文档中的“29.6 contextlib—Utilities for with-statementcontexts”。

- closing: 如果对象提供了close（　）方法，但没有实现`__enter__`/`__exit__`协议，那么可以使用这个函数构建上下文管理器。
- suppress: 构建临时忽略指定异常的上下文管理器。
- @contextmanager: 这个装饰器把简单的生成器函数变成上下文管理器，这样就不用创建类去实现管理器协议了。
- ContextDecorator: 这是个基类，用于定义基于类的上下文管理器。这种上下文管理器也能用于装饰函数，在受管理的上下文中运行整个函数。
- ExitStack: 这个上下文管理器能进入多个上下文管理器。with块结束时，ExitStack按照后进先出的顺序调用栈中各个上下文管理器的__exit__方法。如果事先不知道with块要进入多少个上下文管理器，可以使用这个类。例如，同时打开任意一个文件列表中的所有文件。

### 使用@contextmanager

@contextmanager装饰器能减少创建上下文管理器的样板代码量，因为不用编写一个完整的类，定义`__enter__`和`__exit__`方法，而只需实现有一个yield语句的生成器，生成想让`__enter__`方法返回的值。

在使用@contextmanager装饰的生成器中，yield语句的作用是把函数的定义体分成两部分：yield语句前面的所有代码在with块开始时（即解释器调用`__enter__`方法时）执行，yield语句后面的代码在with块结束时（即调用`__exit__`方法时）执行。

示例15-5 mirror_gen.py：使用生成器实现的上下文管理器:

```python
import contextlib
@contextlib.contextmanager
def looking_glass():
  import sys
  original_write = sys.stdout.write
  def reverse_write(text):
    original_write(text[::-1])
  sys.stdout.write = reverse_write
  yield 'JABBERWOCKY'  # ❺
  sys.stdout.write = original_write # ❻
```

- ❺ 产出一个值，这个值会绑定到with语句中as子句的目标变量上。执行with块中的代码时，这个函数会在这一点暂停。
- ❻ 控制权一旦跳出with块，继续执行yield语句之后的代码；这里是恢复成原来的sys. stdout.write方法。

```python
>> from mirror_gen import looking_glass
>>> with looking_glass（ ） as what:  ➊
...      print('Alice, Kitty and Snowdrop')
...      print(what)
...
pordwonS dna yttiK ,ecilA
YKCOWREBBAJ
>>> what
'JABBERWOCKY'
```

其实，contextlib.contextmanager装饰器会把函数包装成实现`__enter__`和`__exit__`方法的类。

这个类的`__enter__`方法有如下作用: 

1. 调用生成器函数，保存生成器对象（这里把它称为gen）。
2. 调用next(gen)，执行到yield关键字所在的位置。
3. 返回next(gen)产出的值，以便把产出的值绑定到with/as语句中的目标变量上。

with块终止时，`__exit__`方法会做以下几件事:

1. 检查有没有把异常传给exc_type；如果有，调用gen.throw(exception)，在生成器函数定义体中包含yield关键字的那一行抛出异常。
2. 否则，调用next(gen)，继续执行生成器函数定义体中yield语句之后的代码。

为了告诉解释器异常已经处理了，`__exit__`方法会返回True，此时解释器会压制异常。如果`__exit__`方法没有显式返回一个值，那么解释器得到的是None，然后向上冒泡异常。使用@contextmanager装饰器时，默认的行为是相反的：装饰器提供的`__exit__`方法假定发给生成器的所有异常都得到处理了，因此应该压制异常。如果不想让@contextmanager压制异常，必须在被装饰的函数中显式重新抛出异常。

> 使用@contextmanager装饰器时，要把yield语句放在try/finally语句中（或者放在with语句中），这是无法避免的，因为我们永远不知道上下文管理器的用户会在with块中做什么。

