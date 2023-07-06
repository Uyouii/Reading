## 条款2： 理解auto 型别推导

在模板型别推导和auto型别推导可以建立起一一映射，它们之间也确实存在着双向的算法变换。

```cpp
template<typename T>
void f(ParamType param);

f(expr);	// 以某表达式调用f
```

在f的调用语句中，编译器会利用expr来推导T和ParamType的型别。

当某变量采用auto来声明的时候，auto就扮演了模板中T这个角色，而变量的饰词则扮演的是ParamType的角色。

- 情况1: *ParamType*是个指针或者引用，但不是个万能引用
- 情况2: *ParamType*是个万能引用
- 情况3: *ParamType*既非指针也非引用

```cpp
// 情况1 或 情况3
auto x = 27;		// 情况3（x既非指针也非引用）

const auto cx = x;	// 情况3（cx既非指针也非引用）

const auto& rx = x;	// 情况1（rx是个引用，但不是个万能引用）

// 情况2
auto&& uref1 = x;	// x的型别是int，且是左值
					// 所以uref1的型别是int&

auto&& uref2 = x;	// cx的型别是const int，且是左值
					// 所以uref2的型别是const int&

auto&& uref3 = 27;	// 27的型别是int，且是右值
					// 所以uref2的型别是int&&
```

数组和函数的情况也适用于auto型别的推导

```cpp
const char name[] = "xxxxxx"	// name的型别是 const char [7]
    
auto arr1 = name;				// arr1的型别是const char *

auto arr2 = name;				// arr1的型别是const char (&)[7]

void someFunc(int, double)		// someFunc是个函数，型别是void(int, double)
    
auto func1 = someFunc;			// fun1的型别是 void(*)(int, double)

auto& func2 = someFunc;			// func2的型别是void(&)(int, double)
```



### auto和模板类型的不同

声明一个int并初始化，C++98中有两种语法

```cpp
int x1 = 27;
int x2(27);
```

C++11为了支持统一初始化(uniform initialization)，增加了下面的语法选项：

```cpp
int x3 = {27};
int x4{27};
```

如果用auto：

```cpp
auto x1 = 27;		// 型别是int，值是27
auto x2(27);		// 同上
auto x3 = {27};		// 型别是 std::initializer_list<int>，值是{27}
auto x4{27};		// 同上
```

后面两个语句，声明了这么一个变量，其型别类型为std::initializer_list<int>，且含有单个值为27的元素。

当用于auto声明变量的初始表达式是大括号起时，推导所得的型别就属于std::initizlizer_list。

对于大括号初始表达式的处理方式，是auto型别推导和模板型别推导的唯一不同之处。当采用auto声明的变量使用大括号初始化表达式进行初始化时，推导所得的型别是std::initializer_list的一个实例型别。

但是如果向对应模板传入一个同样的初始化表达式，型别类型推导将会失败，代码将不同通过编译：

```cpp
auto x = {1,2,3};		// x的型别是 std::initializer_list<int>

template<typename T>
void f(ParamType param);

f({1,2,3})				//错误，无法推导T的型别
```

auto和模板类型推导的唯一区别是，auto会假定用大括号起的初始化表达式是一个std::initialize_list，但是模板型别推导不会。



C++14允许使用auto来说明函数返回值需要推导，而且C++14中的lamba表达式也会在形参中用到auto。然而，这些auto的用法是在使用模板型别推导，而非auto型别推导，所以，带有auto返回值的函数如果需要返回一个大括号起的初始化表达式，是通不过编译的。

```cpp
auto createInitList()
{
    return {1,2,3};			// 错误，无法为{1,2,3}完成型别类型推导
}
```

用auto来指定C++14中lambda式的形参型别时，也不能使用大括号起的初始化表达式

```cpp
std::vector<int> v;
…

auto resetV =
  [&v](const auto& newValue) { v = newValue; };     // C++14

…

resetV({ 1, 2, 3 });          // error! can't deduce type
                              // for { 1, 2, 3 }
```



### 总结

-   在一般情况下，auto型别推导和模板型别推导时一模一样的，但是auto型别推导会假定用大括号括起的初始化表达式代表一个std::intializer_list，但是模板型别推导不会
-   在函数返回值或lambda式的形参中使用auto，意思是使用模板型别推导而非auto型别推导。

