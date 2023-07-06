## 条款8：优先选用nullptr，而非0或者NULL

字面常量0的型别是int，而非指针。当C++在使用指针的语句中发现了一个0，也会勉强把它解释为空指针，但这是一个不得已而为之的行为。C++的基本观点还是0的型别是int，而非指针。

从实际效果上说，以上结论对于NULL也成立。0和NULL都不具备指针型别。



C++98中的基本观点可能在指针型别和整型之间进行重载时发生意外。如果向这样的重载函数传递0和NULL，时从来不会调用到要求指针型别的重载版本的。

```cpp
void f(int);        // three overloads of f
void f(bool);
void f(void*);

f(0);               // calls f(int), not f(void*)

f(NULL);            // might not compile, but typically calls
                    // f(int). Never calls f(void*)
```

f(NULL)的不确定性是NULL的型别在实现中的余地的一种反映。例如，如果NULL的定义为0L，那么这个调用就有多义性了。因为从long到int，从long到bool，从0L到void*的型别转换被视为同样好的。

一个指导原则是，不要在指针型别和整型型别之间做重载。

nullptr的优点是，它不具备整型型别。实话实说，它也不具备指针型别。nullptr的实际型别是std::nullptr_t，并且，在一个漂亮的循环定义下，std::nullptr_t的定义被指定为nullptr的型别。

型别std::nullptr_t可以隐式转换到所有裸指针型别，这就是nullptr可以扮演所有型别指针的原因。

调用重载函数f时传入nullptr会调用void*那个重载版本，因为nullptr无法被视作任何一种整型。

```cpp
f(nullptr);         // calls f(void*) overload
```



nullptr在有模板的前提下表现最亮眼。在模板型别推导中，0和NULL都会被推导成为int，但是nullptr会被推导为指针型别。

所以，当想表示空指针时，使用nullptr，而非0或NULL。

## 总结

-   相对于0或NULL，优先选用nullptr。
-   避免在整型和指针型别之间重载。

