## 条款6： 当auto推导的型别不符合要求时，使用带显式型别的初始化物的习惯用法

```cpp
std::vector<bool> features(const Widget& w);

Widget w;
…

bool highPriority = features(w)[5];  // is w high priority?
…

processWidget(w, highPriority);      // process w in accord
                                     // with its priority
```

如果给上述代码做一个看似无害的改变，把highPriority的型别改成auto，

```cpp
auto highPriority = features(w)[5];  // is w high priority?
```

虽然代码仍然可以通过编译，但是行为变得不可预期了:

```cpp
processWidget(w, highPriority);      // undefined behavior!
```

processWidget的调用现在会导致未定义行为。

其实改了auto的代码中，highPriority的型别不再是bool了。

从概念上说，std::vector<bool>应该持有的是bool型别的元素，但是std::vector<bool>的opertor[]的返回值并不是容器中的一个元素的引用（对于其他所有形参型别而言，std::vector::operator[]都返回这样的值，单单bool是个例外）。

它返回的是个std::vector<bool>::reference型别的对象(这是一个嵌套在std::vector<bool>)里面的类。

之所以有std::vector<bool>::reference，是因为std::vector<bool>做过特化，用了一种压缩形式表示其持有的bool元素，每个bool元素用一个比特来表示。

这种做法给std::vector<bool>的operator[]带来一个问题，因为按常理来说std::vector<T>的operator[]应该返回一个T&，然而C++中却禁止比特的引用。既然不能返回一个bool&，std::vector<bool>的operator[]转而返回了一个表现得像bool&的对象。实现这个效果的原理是，std::vector<bool>::reference做了一个向bool的隐式型别转换。  



### 代理类(proxy class)

std::vector<bool>::reference是个代理类的实例。代理类就是指为了增广其他型别的类。

例如：std::vector<bool>::reference就是为了制造std::vector<bool>的operator[]返回的一个比特制造的引用的假象。标准库中的智能指针也是代理类，他们是为了将资源管理嫁接到裸指针之上。

一些代理类的设计有隐藏在背后的意思，std::vector<bool>::reference就是这样的"隐形"代理，std::bitset相对应的std::bitset::reference也一样。

一个普遍的规律是，“隐形”代理类和auto无法和平共处。这种类的对象往往会设计为仅维持到单个语句之内存在，所以，如果要创造这种类的变量，往往就是违反了基本的库的设计的假定前提。

所以，要防止写出这样的代码：

```cpp
auto someVar = expression of "invisible" proxy class type;
```

一种解决方法是强制进行另一次型别转换。这种方法成为带显式型别的初始化物习惯用法。该方法要求使用auto声明变量，但针对初始化表达进行强制类型转换。

e.g.

```cpp
auto highPriority = static_cast<bool>(features(w)[5]);
```

## 总结

-   “隐形”的代理型别可以导致auto根据初始化表达式推导出的“错误的”型别。
-   带显式型别的初始化物习惯用法强制auto推导出想要的型别。













