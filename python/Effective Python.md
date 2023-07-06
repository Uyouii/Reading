## 培养Pythonic思维

### 第1条 查询自己使用的Python版本

```shell
$ python3 --version
Python 3.8.10

$ python3
Python 3.8.10 (default, Nov 26 2021, 20:14:08)
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> print(sys.version_info)
sys.version_info(major=3, minor=8, micro=10, releaselevel='final', serial=0)
>>> print(sys.version)
3.8.10 (default, Nov 26 2021, 20:14:08)
[GCC 9.3.0]
```

深度依赖Python 2代码库的开发者可以考虑用2to3（Python预装的工具）与six这样的工具过渡到Python 3。

### 第2条 遵循PEP 8风格指南

Python Enhancement Proposal #8叫作PEP 8，它是一份针对Python代码格式而编订的风格指南。

https://peps.python.org/pep-0008/

#### 与空白有关的建议

- 用空格（space）表示缩进，而不要用制表符（tab）。
- 和语法相关的每一层缩进都用4个空格表示。
- 每行不超过79个字符。
- 对于占据多行的长表达式来说，除了首行之外的其余各行都应该在通常的缩进级别之上再加4个空格。
- 在同一份文件中，函数与类之间用两个空行隔开。
- 在同一个类中，方法与方法之间用一个空行隔开。
- 使用字典时，键与冒号之间不加空格，写在同一行的冒号和值之间应该加一个空格。
- 给变量赋值时，赋值符号的左边和右边各加一个空格，并且只加一个空格就好。
- 给变量的类型做注解（annotation）时，不要把变量名和冒号隔开，但在类型信息前应该有一个空格。

#### 与命名有关的建议

- 函数、变量及属性用小写字母来拼写，各单词之间用下划线相连，例如：lowercase_underscore。
- 受保护的实例属性，用一个下划线开头，例如：_leading_underscore。
- 私有的实例属性，用两个下划线开头，例如：__double_leading_underscore。
- 类（包括异常）命名时，每个单词的首字母均大写，例如：CapitalizedWord。
- 模块级别的常量，所有字母都大写，各单词之间用下划线相连，例如：ALL_CAPS。
- 类中的实例方法，应该把第一个参数命名为self，用来表示该对象本身。
- 类方法的第一个参数，应该命名为cls，用来表示这个类本身。

#### 与表达式和语句有关的建议

- 采用行内否定，即把否定词直接写在要否定的内容前面，而不要放在整个表达式的前面，例如应该写if a is not b，而不是if not a is b。
- 不要通过长度判断容器或序列是不是空的，例如不要通过if len(somelist)== 0判断somelist是否为[]或''等空值，而是应该采用if not somelist这样的写法来判断，因为Python会把空值自动评估为False。
- 如果要判断容器或序列里面有没有内容（比如要判断somelist是否为[1]或'hi'这样非空的值），也不应该通过长度来判断，而是应该采用if somelist语句，因为Python会把非空的值自动判定为True。
- 如果表达式一行写不下，可以用括号将其括起来，而且要适当地添加换行与缩进以便于阅读。
- 多行的表达式，应该用括号括起来，而不要用\符号续行。

#### 与引入有关的建议

- import语句（含from x import y）总是应该放在文件开头。
- 引入模块时，总是应该使用绝对名称，而不应该根据当前模块路径来使用相对名称。例如，要引入bar包中的foo模块，应该完整地写出from bar import foo，即便当前路径为bar包里，也不应该简写为import foo。
- 文件中的import语句应该按顺序划分成三个部分：首先引入标准库里的模块，然后引入第三方模块，最后引入自己的模块。属于同一个部分的import语句按字母顺序排列。

#### 提示

Pylint（https://www.pylint.org/）是一款流行的Python源码静态分析工具。它可以自动检查受测代码是否符合PEP 8风格指南，而且还能找出Python程序里的许多种常见错误。

### 第3条 了解bytes与str的区别

Python有两种类型可以表示字符序列：一种是bytes，另一种是str。bytes实例包含的是原始数据，即8位的无符号值（通常按照ASCII编码标准来显示）。

str实例包含的是Unicode码点（code point，也叫作代码点），这些码点与人类语言之中的文本字符相对应。

```shell
$ python3
Python 3.8.10 (default, Nov 26 2021, 20:14:08)
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> a = 'a\u0300 propos'
>>> print(list(a))
['a', '̀', ' ', 'p', 'r', 'o', 'p', 'o', 's']
>>> print(a)
à propos
```

要把Unicode数据转换成二进制数据，必须调用str的encode方法。要把二进制数据转换成Unicode数据，必须调用bytes的decode方法。调用这些方法的时候，可以明确指出自己要使用的编码方案，也可以采用系统默认的方案，通常是指UTF-8。

两种不同的字符类型与Python中两种常见的使用情况相对应：

- 开发者需要操作原始的8位值序列，序列里面的这些8位值合起来表示一个应该按UTF-8或其他标准编码的字符串。
- 开发者需要操作通用的Unicode字符串，而不是操作某种特定编码的字符串。

通常需要编写两个辅助函数（helper function），以便在这两种情况之间转换，确保输入值类型符合开发者的预期形式。

第一个辅助函数接受bytes或str实例，并返回str：

```python
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode('utf-8')
    return bytes_or_str
```

第二个辅助函数也接受bytes或str实例，但它返回的是bytes：

```python
def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        return bytes_or_str.encode('utf-8')
    return bytes_or_str
```

bytes与str这两种类型似乎是以相同的方式工作的，但其实例并不相互兼容，所以在传递字符序列的时候必须考虑好其类型:

- 可以用+操作符将bytes添加到bytes，str也可以这样，但是不能将str实例添加到bytes实例，也不能将bytes实例添加到str实例。

- bytes与bytes之间可以用二元操作符（binary operator）来比较大小，str与str之间也可以，但是str实例不能与bytes实例比较。

- 判断bytes与str实例是否相等，总是会评估为假（False），即便这两个实例表示的字符完全相同，它们也不相等。

- 两种类型的实例都可以出现在%操作符的右侧，用来替换左侧那个格式字符串（format string）里面的%s。

  - 如果格式字符串是bytes类型，那么不能用str实例来替换其中的%s，因为Python不知道这个str应该按照什么方案来编码。

  - 如果格式字符串是str类型，则可以用bytes实例来替换其中的%s，问题是，这可能跟你想要的结果不一样。

    ```python
    print('red %s' % b'blue')
    red b'blue'
    ```

  - 这样做，会让系统在bytes实例上面调用__repr__方法（参见第75条），然后用这次调用所得到的结果替换格式字符串里的%s，

- 在操作文件句柄的时候，这里的句柄指由内置的open函数返回的句柄。这样的句柄默认需要使用Unicode字符串操作，而不能采用原始的bytes。

  - 在调用open函数时，指定的是'w'模式，所以系统要求必须以文本模式写入。如果想用二进制模式，那应该指定'wb'才对。在文本模式下，write方法接受的是包含Unicode数据的str实例，不是包含二进制数据的bytes实例。
  - 在调用open函数时指定的是'r'模式，所以系统要求必须以文本模式来读取。若要用二进制格式读取，应该指定'rb'。以文本模式操纵句柄时，系统会采用默认的文本编码方案处理二进制数据。
  - 或者是在调用open函数的时候，通过encoding参数明确指定编码标准，以确保平台特有的一些行为不会干扰代码的运行效果。

### 第4条 用支持插值的f-string取代C风格的格式字符串与str.format方法

Python 3.6添加了一种新的特性，叫作**插值格式字符串（interpolated formatstring，简称f-string）**。新语法特性要求在格式字符串的前面加字母f作为前缀。

```python
key = 'my_var'
value = 1.234
formatted = f'{key} = {value}'
print(formatted)

my_var = 1.234
```

str.format方法所支持的那套迷你语言，也就是在{}内的冒号右侧所采用的那套规则，现在也可以用到f-string里面，而且还可以像早前使用str.format时那样，通过!符号把值转化成Unicode及repr形式的字符串。

```python
if __name__ == "__main__":
    key = 'my_var'
    value = 1.234
    formatted = f'{key!r:<10} = {value:.2f}'
    print(formatted)
   
'my_var'   = 1.23
```

在f-string方法中，各种Python表达式都可以出现在{}里。

f-string也可以写成多行的形式，类似于C语言的相邻字符串拼接（adjacent-string concatenation）。

```python
for i, (item, count) in enumerate(pantry):
    print(f'#{i+1}: '
          f'{item.title():<10s} = '
          f'{round(count)}')
```

### 第5条 用辅助函数取代复杂的表达式

如果你发现表达式越写越复杂，那就应该考虑把它拆分成多个部分，并且把这套逻辑写到辅助函数里面。这样虽然要多编几行代码，但可以让程序更加清晰，所以总体来说还是值得的。

语法简洁的Python虽然可以写出很多浓缩的句式，但应该避免让这样的写法把表达式弄得太复杂。我们要遵循DRY原则，也就是不要重复自己写过的代码（Don't Repeat Yourself）。

### 第6条 把数据结构直接拆分到多个变量里，不要专门通过下标访问

Python还有一种写法，叫作拆分（unpacking）。这种写法让我们只用一条语句，就可以把元组里面的元素分别赋给多个变量。元组的元素本身不能修改，但是可以通过unpacking把这些元素分别赋给相应的变量，那些变量是可以修改的。

```python
item = ('Peanut butter', 'Jelly')
first, second = item
print(first, 'and', second)

Peanut butter and Jelly
```

通过unpacking来赋值要比通过下标去访问元组内的元素更清晰，而且这种写法所需的代码量通常比较少。

有了unpacking机制之后，只需要写一行代码就可以交换这两个元素

```python
a, b = b, a
```

因为Python处理赋值操作的时候，要先对=号右侧求值，于是，它会新建一个临时的元组，把a[i]与a[i-1]这两个元素放到这个元组里面。

unpacking机制还有一个特别重要的用法，就是可以在for循环或者类似的结构（例如推导与生成表达式，这些内容参见第27条）里面，把复杂的数据拆分到相关的变量之中。

### 第7条 尽量用enumerate取代range

Python内置的range函数适合用来迭代一系列整数。

如果要迭代的是某种数据结构，例如字符串列表，那么可以直接在这个序列上面迭代。

Python有个内置的函数，叫作enumerate。enumerate能够把任何一种迭代器（iterator）封装成惰性生成器（lazy generator，参见第30条）。这样的话，每次循环的时候，它只需要从iterator里面获取下一个值就行了，同时还会给出本轮循环的序号，即生成器每次产生的一对输出值。

```python
color_lost = ['red', 'blue', 'green']
it = enumerate(color_lost)
print(next(it))
print(next(it))

(0, 'red')
(1, 'blue')
```

enumerate输出的每一对数据，都可以拆分（unpacking）到for语句的那两个变量里面（unpacking机制参见第6条），这样会让代码更加清晰。

```python
color_lost = ['red', 'blue', 'green']
for i, color in enumerate(color_lost):
    print(f'{i + 1} : {color}'

1 : red
2 : blue
3 : green
```

还可以通过enumerate的第二个参数指定起始序号，例如，可以从1开始计算。

```python
color_lost = ['red', 'blue', 'green']
for i, color in enumerate(color_lost, 1):
    print(f'{i} : {color}')
```

### 第8条 用zip函数同时遍历两个迭代器

python内置的zip函数能把两个或更多的iterator封装成惰性生成器（lazy generator）。每次循环时，它会分别从这些迭代器里获取各自的下一个元素，并把这些值放在一个元组里面。而这个元组可以拆分到for语句里的那些变量之中。

```python
for name, count in zip(names, counts):
    if count > max_count:
        longest_name = name
        max_count = count
```

zip每次只从它封装的那些迭代器里面各自取出一个元素，所以即便源列表很长，程序也不会因为占用内存过多而崩溃。

zip函数本来就是这样设计的：只要其中任何一个迭代器处理完毕，它就不再往下走了。于是，循环的次数实际上等于最短的那份列表所具备的长度。

如果无法确定这些列表的长度相同，那就不要把它们传给zip，而是应该传给另一个叫作zip_longest的函数，这个函数位于内置的itertools模块里。

```python
import itertools
if __name__ == "__main__":
    names = ["name1", "name2", "name3"]
    counts = [len(name) for name in names]
    for name, count in itertools.zip_longest(names, counts):
        print(f'{name} : {count}')
```

如果其中有些列表已经遍历完了，那么zip_longest会用当初传给fillvalue参数的那个值来填补空缺（本例中空缺的为字符串'Rosalind'的长度值），默认的参数值是None。

### 第9条 不要在for与while循环后面写else块

Python的循环有一项大多数编程语言都不支持的特性，即可以把else块紧跟在整个循环结构的后面。

```python
for i in range(3):
    print('Loop', i)
else:
    print('Else block!')
```

奇怪的是，程序做完整个for循环之后，竟然会执行else块里的内容。

如果循环没有从头到尾执行完（也就是循环提前终止了），那么else块里的代码是不会执行的。在循环中使用break语句实际上会跳过else块。

还有一个奇怪的地方是，如果对空白序列做for循环，那么程序立刻就会执行else块。

while循环也是这样，如果首次循环就遇到False，那么程序也会立刻运行else块。

for/else或while/else结构本身虽然可以实现某些逻辑表达，但它给读者（也包括你自己）带来的困惑，已经盖过了它的好处。因为for与while循环这种简单的结构，在Python里面读起来应该相当明了才对，如果把else块紧跟在它的后面，那就会让代码产生歧义。所以，请不要这么写。

### 第10条 用赋值表达式减少重复代码

赋值表达式（assignment expression）是Python 3.8新引入的语法，它会用到海象操作符（walrus operator）。a = b是一条普通的赋值语句，读作a equals b，而a := b则是赋值表达式，读作a walrus b。（_这个符号为什么叫walrus呢？因为把:=顺时针旋转90º之后，冒号就是海象的一双眼睛，等号就是它的一对獠牙。_）

这种表达式很有用，可以在普通的赋值语句无法应用的场合实现赋值，例如可以用在条件表达式的if语句里面。

我们在Python里面经常要先获取某个值，然后判断它是否非零，如果是就执行某段代码。Python引入赋值表达式正是为了解决这样的问题。下面改用海象操作符来写：

```python
if count := fresh_fruit.get('lemon', 0):
    make_lemonade(count)
else:
    out_of_stock()
   
if (count := fresh_fruit.get('apple', 0)) >= 4:
    make_cider(count)
else:
    out_of_stock()
```

有了海象操作符，可以在每轮循环的开头给fresh_fruit变量赋值，并根据变量的值来决定要不要继续循环。

```python
bottles = []
while fresh_fruit := pick_fruit():
    for fruit, count in fresh_fruit.items():
        batch = make_juice(fruit, count)
        bottles.extend(batch)
```

## 列表与字典

### 第11条 学会对序列做切片

Python有这样一种写法，可以从序列里面切割（slice）出一部分内容，让我们能够轻松地获取原序列的某个子集合。凡是实现了`__getitem__`与`__setitem__`这两个特殊方法的类都可以切割。

最基本的写法是用somelist[start:end]这一形式来切割，也就是从start开始一直取到end这个位置，但不包含end本身的元素。

```python
a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

a[:]
a[:5]
a[4:]
a[:-1]
a[2:5]
a[-3:]
a[-3:-1]
```

如果起点与终点所确定的范围超出了列表的边界，那么系统会自动忽略不存在的元素。利用这项特性，很容易就能构造出一个最多只有若干元素的输入序列

```python
first_twenty_items = a[:20]
last_twenty_items = a[-20:]
```

> 只要n大于或等于1，somelist[-n:]总是可以切割出你想要的切片。只有当n为0的时候，才需要特别注意。此时somelist[-0:]其实相当于somelist[0:]，所以跟somelist[:]一样，会制作出原列表的一份副本。

切割出来的列表是一份全新的列表。即便把某个元素换掉，也不会影响原列表中的相应位置。

切片可以出现在赋值符号的左侧，表示用右侧那些元素把原列表中位于这个范围之内的元素换掉。这种赋值不要求等号两边所指定的元素个数必须相同。在原列表中，位于切片范围之前和之后的那些元素会予以保留，但是列表的长度可能有所变化。

```python
a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
print('Before ', a)
a[2:7] = [99, 22, 14]
print('After ', a)

Before  ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
After  ['a', 'b', 99, 22, 14, 'h']
```

下面这段代码会使列表变长，因为赋值符号右侧的元素数量比左侧那个切片所涵盖的元素数量要多。

```python
print('Before ', a)
a[2:3] = [47,  11]
print('After ', a)

Before  ['a', 'b', 99, 22, 14, 'h']
After  ['a', 'b', 47, 11, 22, 14, 'h']
```

起止位置都留空的切片，如果出现在赋值符号右侧，那么表示给这个列表做副本，这样制作出来的新列表内容和原列表相同，但身份不同。

```python
b = a[:]
assert b == a and b is not a
```

把不带起止下标的切片放在赋值符号左边，表示是用右边那个列表的副本把左侧列表的全部内容替换掉（注意，左侧列表依然保持原来的身份，系统不会分配新的列表）。

```python
b = a
print('Before a', a)
print('Before b', b)
a [:] = [101, 102, 103]
assert a is b
print('After a', a)
print('Before b', b)

Before a ['a', 'b', 47, 11, 22, 14, 'h']
Before b ['a', 'b', 47, 11, 22, 14, 'h']
After a [101, 102, 103]
Before b [101, 102, 103]
```

### 第12条 不要在切片里同时指定起止下标与步进

除了基本的切片写法外，Python还有一种特殊的步进切片形式，也就是`somelist[start:end:stride]`。这种形式会在每n个元素里面选取一个，这样很容易就能把奇数位置上的元素与偶数位置上的元素分别通过x[::2]与x[1::2]选取出来[1]。

```python
x = [1,2,3,4,5,6,7,8]
odds = x[::2]
evens = x[1::2]
print(odds)
print(evens)

[1, 3, 5, 7]
[2, 4, 6, 8]
```

Python里面有个常见的技巧，就是把-1当成步进值对bytes类型的字符串做切片，这样就能将字符串反转过来。

```python
x = b'mongoose'
y = x[::-1]
print(y)

b'esoognom'
```

Unicode形式的字符串也可以这样反转

```python
x = '程序'
y = x[::-1]
print(y)
    
序程
```

但如果把这种字符串编码成UTF-8标准的字节数据，就不能用这个技巧来反转了。

```python
x = '程序'
x = x.encode('utf-8')
y = x[::-1]
y = y.decode('utf-8')
print(y)

Traceback (most recent call last):
  File "test.py", line 18, in <module>
    y = y.decode('utf-8')
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8f in position 0: invalid start byte

```

建议大家不要把起止下标和步进值同时写在切片里。如果必须指定步进，那么尽量采用正数，而且要把起止下标都留空。即便必须同时使用步进值与起止下标，也应该考虑分成两次来写。

可以改用内置的itertools模块中的islice方法（参见第36条），这个方法用起来更清晰，因为它的起止位置与步进值都不能是负数。

### 第13条 通过带星号的unpacking操作来捕获多个元素，不要用切片

基本的unpacking操作（参见第6条）有一项限制，就是必须提前确定需要拆解的序列的长度。

带星号的表达式（starred expression）也是一种unpacking操作，它可以把无法由普通变量接收的那些元素全都囊括进去。

```python
car_ages = [0, 9 , 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_desending = sorted(car_ages, reverse=True)
oldest, second_oldest, *others = car_ages_desending
print(oldest, second_oldest, others)

20 19 [15, 9, 8, 7, 6, 4, 1, 0]
```

这种带星号的表达式可以出现在任意位置，所以它能够捕获序列中的任何一段元素。

```python
oldest, *others, youngest, = car_ages_desending
print(oldest, youngest, others)

20 0 [19, 15, 9, 8, 7, 6, 4, 1]
```

在使用这种写法时，至少要有一个普通的接收变量与它搭配，否则就会出现SyntaxError。

对于单层结构来说，同一级里面最多只能出现一次带星号的unpacking。

带星号的表达式总会形成一份列表实例。如果要拆分的序列里已经没有元素留给它了，那么列表就是空白的。

unpacking操作也可以用在迭代器上。

带星号的这部分总是会形成一份列表，所以要注意，这有可能耗尽计算机的全部内存并导致程序崩溃。

### 第14条 用sort方法的key参数来表示复杂的排序逻辑

内置的列表类型提供了名叫sort的方法，可以根据多项指标给list实例中的元素排序。在默认情况下，sort方法总是按照自然升序排列列表内的元素。

凡是具备自然顺序的内置类型几乎都可以用sort方法排列，例如字符串、浮点数等。

可以把这样的排序逻辑定义成函数，然后将这个函数传给sort方法的key参数。key所表示的函数本身应该带有一个参数，这个参数指代列表中有待排序的对象，函数返回的应该是个可比较的值（也就是具备自然顺序的值），以便sort方法以该值为标准给这些对象排序。

例如用lambda关键字定义这样一个函数，把它传给sort方法的key参数。

```python
datas.sort(key = lambda x: x.name)
```

> sort方法的一项特征，那就是这个方法是个稳定的排序算法。

### 第15条 不要过分依赖给字典添加条目时所用的顺序

在Python 3.5与之前的版本中，迭代字典（dict）时所看到的顺序好像是任意的，不一定与当初把这些键值对添加到字典时的顺序相同。之所以出现这种效果，是因为字典类型以前是用哈希表算法来实现的（这个算法通过内置的hash函数与一个随机的种子数来运行，而该种子数会在每次启动Python解释器时确定）。所以，这样的机制导致这些键值对在字典中的存放顺序不一定会与添加时的顺序相同，而且每次运行程序的时候，存放顺序可能都不一样。

从Python 3.6开始，字典会保留这些键值对在添加时所用的顺序，而且Python 3.7版的语言规范正式确立了这条规则。于是，在新版的Python里，总是能够按照当初创建字典时的那套顺序来遍历这些键值对。

在Python 3.5与之前的版本中，dict所提供的许多方法（包括keys、values、items与popitem等）都不保证固定的顺序，所以让人觉得好像是随机处理的。

在新版的Python中，这些方法已经可以按照当初添加键值对时的顺序来处理了。

### 第16条 用get处理建不在字典中的情况，不要使用in与KeyError

Python内置的字典（dict）类型提供了get方法，可以通过第一个参数指定自己想查的键，并通过第二个参数指定这个键不存在时应返回的默认值。

```python
count = counters.get(key, 0)
counters[key] = count + 1
```

如果字典里的数据属于比较简单的类型，那么代码最简短、表达最清晰的方案就是get方案。

复杂结构写法：

```python
if(names := votes.get(key)) is None:
    votes[key] = names = []
names.append(who)
```

dict类型提供了setdefault方法，这个方法会查询字典里有没有这个键，如果有，就返回对应的值；如果没有，就先把用户提供的默认值跟这个键关联起来并插入字典，然后返回这个值。

还有个关键的地方要注意：在字典里面没有这个键时，setdefault方法会把默认值直接放到字典里，而不是先给它做副本，然后把副本放到字典中。

### 第17条 用defaultdict处理内部状态中确实的元素而不要用setdefault

Python内置的collections模块提供了defaultdict类，它会在键缺失的情况下，自动添加这个键以及键所对应的默认值。只需要在构造这种字典时提供一个函数就行了，每次发现键不存在时，该字典都会调用这个函数返回一份新的默认值。

```python
from collections import defaultdict

class Visits:
    def __init__(self):
        self.data = defaultdict(set)
    
    def add(self, country, city):
        self.data[country].add(city)
```

### 第18条 学会利用`__missing__`构造依赖键的默认值

Python内置了一种解决方案，可以通过继承dict类型并实现`__missing__`特殊方法。我们可以把字典里不存在这个键时所要执行的逻辑写在这个方法中。

```python
class Pictures(dict):
    def __missing__(self, key):
        value = open_picture(key)
        self[key] = value
        return value
pictures = Pictures()
handle = pictures[path]
handle.seek(0)
image_data = handle.read()
```

## 函数

### 第19条 不要把函数返回的多个数值拆分到三个以上的变量中

在返回多个值的时候，可以用带星号的表达式接收那些没有被普通变量捕获到的值。

我们不应该把函数返回的多个值拆分到三个以上的变量里。一个三元组最多只拆成三个普通变量，或两个普通变量与一个万能变量（带星号的变量）。

假如要拆分的值确实很多，那最好还是定义一个轻便的类或namedtuple（参见第37条），并让函数返回这样的实例。

### 第20条 遇到意外状况时应该抛出异常，不要返回None

Python采用的是动态类型与静态类型相搭配的gradual类型系统，我们不能在函数的接口上指定函数可能抛出哪些异常（有的编程语言支持这样的受检异常（checked exception），调用方必须应对这些异常）。

### 第21条 了解如何在闭包里面使用外围作用域中的变量

Python支持闭包（closure），这让定义在大函数里面的小函数也能引用大函数之中的变量。

函数在Python里是头等对象（first-class object），所以你可以像操作其他对象那样，直接引用它们、把它们赋给变量、将它们当成参数传给其他函数，或是在in表达式与if语句里面对它做比较，等等。闭包函数也是函数，所以，同样可以传给sort方法的key参数。

引用变量：

在表达式中引用某个变量时，Python解释器会按照下面的顺序，在各个作用域（scope）里面查找这个变量，以解析（resolve）这次引用。

1. 当前函数的作用域。

2. 外围作用域（例如包含当前函数的其他函数所对应的作用域）。

3. 包含当前代码的那个模块所对应的作用域（也叫全局作用域，global scope）。

4. 内置作用域（built-in scope，也就是包含len与str等函数的那个作用域）。

如果这些作用域中都没有定义名称相符的变量，那么程序就抛出NameError异常。

给变量赋值：

这要分两种情况处理。

- 如果变量已经定义在当前作用域中，那么直接把新值交给它就行了。
- 如果当前作用域中不存在这个变量，那么即便外围作用域里有同名的变量，Python也还是会把这次的赋值操作当成变量的定义来处理，这会产生一个重要的效果，也就是说，Python会把包含赋值操作的这个函数当成新定义的这个变量的作用域。

Python有一种特殊的写法，可以把闭包里面的数据赋给闭包外面的变量。用nonlocal语句描述变量，就可以让系统在处理针对这个变量的赋值操作时，去外围作用域查找。然而，nonlocal有个限制，就是不能侵入模块级别的作用域（以防污染全局作用域）。

```python
def sort_priority3(numbers, group):
    found = False
    def helper(x):
        nonlocal found
        if x in group:
            found = True
            return (0, x)
        return (1, x)
   	numbers.sort(key=helper)
    return found
```

nonlocal语句清楚地表明，我们要把数据赋给闭包之外的变量。有一种跟它互补的语句，叫作global，用这种语句描述某个变量后，在给这个变量赋值时，系统会直接把它放到模块作用域（或者说全局作用域）中。

### 第22条 用数量可变的位置参数给函数设计清晰的参数列表

在Python里，可以给最后一个位置参数加前缀*，这样调用者就只需要提供不带星号的那些参数，然后可以不再指其他参数，也可以继续指定任意数量的位置参数。

```python
def log(messages, *values):
    if not values:
        print(messages)
    else:
        values_str = ', '.join(str(x) for x in values)
        print(f'{message}: {values_str}')
```

如果想把已有序列（例如某列表）里面的元素当成参数传给像log这样的参数个数可变的函数（variadic function），那么可以在传递序列的时采用*操作符。这会让Python把序列中的元素都当成位置参数传给这个函数。

```python
favorites = [7, 33, 90]
log('Favorite colors', *favorites)
```

令函数接受数量可变的位置参数，可能导致两个问题。

- 第一个问题是，程序总是必须先把这些参数转化成一个元组，然后才能把它们当成可选的位置参数传给函数。这意味着，如果调用函数时，把带*操作符的生成器传了过去，那么程序必须先把这个生成器里的所有元素迭代完（以便形成元组），然后才能继续往下执行（相关知识，参见第30条）。这个元组包含生成器所给出的每个值，这可能耗费大量内存，甚至会让程序崩溃。
- 第二个问题是，如果用了*args之后，又要给函数添加新的位置参数，那么原有的调用操作就需要全都更新。例如给参数列表开头添加新的位置参数sequence，那么没有据此更新的那些调用代码就会出错。

### 第23条 用关键字参数来表示可选行为

Python函数里面的所有普通参数，除了按位置传递外，还可以按关键字传递。调用函数时，在调用括号内可以把关键字的名称写在=左边，把参数值写在右边。这种写法不在乎参数的顺序，只要把必须指定的所有位置参数全都传过去即可。另外，关键字形式与位置形式也可以混用。下面这四种写法的效果相同：

```python
def remainder(number, divisor):
    return number % divisor

remainder(20, 7)
remainder(20, divisor=7)
remainder(number=20, divisor=7)
remiander(divisor=7, number=20)
```

如果混用，那么位置参数必须出现在关键字参数之前，否则就会出错。

每个参数只能指定一次，不能既通过位置形式指定，又通过关键字形式指定。

如果有一份字典，而且字典里面的内容能够用来调用remainder这样的函数，那么可以把**运算符加在字典前面，这会让Python把字典里面的键值以关键字参数的形式传给函数。

```python
my_kwargs = {
    'number': 20,
    'divisor': 7
}
assert remiander(**my_kwargs) == 6
```

调用函数时，带**操作符的参数可以和位置参数或关键字参数混用，只要不重复指定就行。

也可以对多个字典分别施加**操作，只要这些字典所提供的参数不重叠就好。

定义函数时，如果想让这个函数接受任意数量的关键字参数，那么可以在参数列表里写上万能形参**kwargs，它会把调用者传进来的参数收集合到一个字典里面稍后处理。

```python
def print_parameters(**kwargs):
    for key, value in kwargs.items():
        print(f'{key} = {value}')
```

关键字参数的灵活用法可以带来三个好处。

- 第一个好处是，用关键字参数调用函数可以让初次阅读代码的人更容易看懂。
- 关键字参数的第二个好处是，它可以带有默认值，该值是在定义函数时指定的。
- 关键字参数的第三个好处是，我们可以很灵活地扩充函数的参数，而不用担心会影响原有的函数调用代码。

### 第24条 用None和docstring来描述默认值会变的参数

参数的默认值只会在系统加载这个模块的时候，计算一遍，而不会在每次执行时都重新计算，这通常意味着这些默认值在程序启动后，就已经定下来了。

要想在Python里惯用的办法是把参数的默认值设为None，同时在docstring文档里面写清楚，这个参数为None时，函数会怎么运作。

```python
import json

def decode(data, default={}):
    try:
        return json.loads(data)
    except ValueError:
        return default
```

系统只会计算一次default参数（在加载这个模块的时候），所以每次调用这个函数时，给调用者返回的都是一开始分配的那个字典，这就相当于凡是以默认值调用这个函数的代码都共用同一份字典。这会使程序出现很奇怪的效果。

### 第25条 用只能以关键字指定和只能按位置传入的参数来设计清晰的参数列表

