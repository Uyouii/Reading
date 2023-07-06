## 条款3：理解decltype

先看看一般的案例

```cpp
const int i = 0;           // decltype(i) is const int

bool f(const Widget& w);   // decltype(w) is const Widget&
                           // decltype(f) is bool(const Widget&)

struct Point {
  int x, y;                // decltype(Point::x) is int
};                         // decltype(Point::y) is int

Widget w;                  // decltype(w) is Widget

if (f(w)) …                // decltype(f(w)) is bool

template<typename T>       // simplified version of std::vector
class vector {
public:
  …
  T& operator[](std::size_t index);
  …
};

vector<int> v;             // decltype(v) is vector<int>
…
if (v[0] == 0) …           // decltype(v[0]) is int&
```

C++11中，decltype的主要用途大概就是在于声明那些返回值类型依赖于形参型别的函数模板。

一般来说，含有型别T的对象的容器，其operator[]会返回T&。std::queue就属于这种情况，而std::vector也几乎总是属于这种情况。只有std::vector<bool>对应的operator[]并不返回bool&，而时返回一个全新的对象。容器的operator[]的返回类型取决于改容器本身。

### 示例1：

```cpp
template<typename Container, typename Index>    // works, but
auto authAndAccess(Container& c, Index i)       // requires
  -> decltype(c[i])                             // refinement
{
  authenticateUser();
  return c[i];
}
```

函数名字之前的auto和型别推导没有任何关系，它只是说明了这里使用了C++11中的**返回值型别尾序语法**（trailing return type syntax），即改函数的返回值型别将在形参列表之后（在->之后）。

尾序返回值的好处在于，在指定返回值型别时可以使用函数形参。

采用这种声明形式之后，operator[]返回值是什么型别，authAndAccess的返回值就是什么型别。

### 示例2：

C++11允许对单表达式的lambda返回值型别实施推导，而C++14则将这个允许返回扩张到了一切lambda表达式和一切函数。

在C++14中可以去掉返回值型别尾序语法，而只保留前导auto。在这样的声明形式中，auto确实会发生型别推导。具体的说，它说明编译器会依据函数实现来实施函数返回值推导。

```cpp
template<typename Container, typename Index>    // C++14;
auto authAndAccess(Container& c, Index i)       // not quite
{                                               // correct
  authenticateUser();
  return c[i];                  // return type deduced from c[i]
}
```

编译器会对auto之行为返回型别的函数实现模板型别推导，在上例中，这样就留下了隐患。

大多数含有型别T的对象的容器operator[]会返回T&，但是条款1说明，模板型别推导过程中，初始化表达式的引用性会被忽略。

### 示例3：

如果希望authAndAccess按照期望运作，就要对其返回值执行decltype型别推导。

在C++14中通过decltype(auto)饰词解决了这个问题：auto制定了欲实施推导的型别，而推导过程采用的是decltype的规则。

```cpp
template<typename Container, typename Index>   // C++14; works,
decltype(auto)                                 // but still
authAndAccess(Container& c, Index i)           // requires
{                                              // refinement
  authenticateUser();
  return c[i];
}
```

现在，authAndAccess的返回值型别和c[i]的返回值型别一致了。

### 示例4：

decltype(auto)并不限于在函数返回值型别处使用。也可以在初始化表达式处应用decltype型别推导规则：

```cpp
Widget w;

const Widget& cw = w;

auto myWidget1 = cw;             // auto type deduction:
                                 // myWidget1's type is Widget

decltype(auto) myWidget2 = cw;   // decltype type deduction:
                                 // myWidget2's type is
                                 //   const Widget&
```

### 示例5：

容器的传递方式是对非常量的左值引用（lvalue-reference-to-non-const)，因为返回该容器的某个元素的引用，就意味着允许用户对容器进行修改。不过这也意味着无法向该函数传递右值容器。右值是不能绑定到左值引用的（除非是对常量的左值引用）。

要解决这种情况，重载是一个办法，但是需要维护两个函数。

另一种方式是采用一种既能绑定到左值也能绑定到右值的引用形参：万能引用。

```cpp
template<typename Container, typename Index>    // c is now a
decltype(auto) authAndAccess(Container&& c,     // universal
                             Index i);          // reference
```

条款25：对万能引用要应用std::forward

```cpp
template<typename Container, typename Index>       // final
decltype(auto)                                     // C++14
authAndAccess(Container&& c, Index i)              // version
{
  authenticateUser();
  return std::forward<Container>(c)[i];
}
```

这个版本徐娅c++14编译器，如果只能使用C++11的版本，需要自己指定返回值型别。

```cpp
template<typename Container, typename Index>       // final
auto                                               // C++11
authAndAccess(Container&& c, Index i)              // version
-> decltype(std::forward<Container>(c)[i])
{
  authenticateUser();
  return std::forward<Container>(c)[i];
}
```



### 深入理解decltype及其使用

想要彻底理解decltype的行为，需要熟悉若干特殊情况，这里只看一例就可以更深入的理解decltype及其使用。

将decltype应用于一个名字之上，就会得到该名字的声明类型。

名字其实是左值表达式，如果仅有一个名字，decltype的行为保持不变。

不过，如果是比仅有名字更复杂的左值表达式的话，decltype就保证得出的型别总是左值引用。

这种行为一般而言没什么影响，因为绝大多数左值表达式都自带一个左值引用饰词。例如：返回左值的函数总是返回左值引用。

```cpp
int x = 0;
```

例如：decltype(x)的结果是int，但是decltype((x))的结果变成了int&，因为(x)是比名字更复杂的表达式。

但是一个无关紧要的小改动，可能会影响到函数型别的推导结果：

```cpp
decltype(auto) f1()
{
  int x = 0;
  …
  return x;        // decltype(x) is int, so f1 returns int
}

decltype(auto) f2()
{
  int x = 0;
  …
  return (x);      // decltype((x)) is int&, so f2 returns int&
}
```

## 总结

-   绝大多数情况下，decltype会得出变量或者表达式的型别而不做任何修改。
-   对于型别为T的左值表达式，除非该表达式仅有一个名字，decltype总是得出型别T&
-   C++14支持decltype(auto)，和auto一样，它会从其初始化表达式出发来推导型别，但是它的型别推导使用的是decltype的规则。






