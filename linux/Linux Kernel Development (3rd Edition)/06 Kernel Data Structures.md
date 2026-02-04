[toc]

## Kernel Data Structures

### Linked List

#### The Linux Kernel’s Implementation

The Linux kernel approach is different. Instead of turning the structure into alinked list, the Linux approach is to embed a linked list node in the structure!

Linux 内核采用的方法则截然不同。它**并非将整个结构体转化为链表**，而是选择**将一个链表节点嵌入到结构体内部**！

The linked-list code is declared in the header file <linux/list.h> and the datastruc-ture is simple:

这套链表操作代码声明在头文件 `<linux/list.h>` 中，对应的数据结构十分简洁：

```c
struct list_head {
    struct list_head *next;
   	struct list_head *prev;
};
```

The next pointer points to the next list node, and the prev pointer points tothe pre-vious list node.Yet, seemingly, this is not particularly useful.Whatvalue is a giant linked list...of linked list nodes? The utility is in how thelist_head structure is used:

`next` 指针指向链表中的下一个节点，`prev` 指针指向链表中的前一个节点。不过，从表面上看，这个设计似乎没什么实际用处 —— 一个由链表节点组成的庞大链表，能有什么价值呢？它的实用性，体现在 `list_head` 结构体的**使用方式**上：

```c
struct fox {
    unsigned long tail_length; 
    unsigned long weight;       
    bool is_fantastic;         
    struct list_head list;
};
```

With this, list.next in fox points to the next element, and list.prev in foxpoints to the previous. Now this is becoming useful, but it gets better.Thekernel provides a family of routines to manipulate linked lists. For example,the list_add() method adds a new node to an existing linked list.Thesemethods, however, are generic:They accept only list_head structures. Using the macro container_of(), we can easily find the parent structure containingany given member variable.This is because in C, the offset of a givenvariable into a structure is fixed by the ABI at compile time.

通过将 `list_head` 嵌入到 `fox` 结构体中，`fox` 中的 `list.next` 会指向链表的下一个元素，`fox` 中的 `list.prev` 会指向链表的前一个元素。到这里，这个设计已经开始体现价值了，但它的强大之处还不止于此。内核提供了一整套用于操作链表的函数接口，例如 `list_add()` 方法可用于向一个已存在的链表中添加新节点。不过，这些方法都是**通用的**：它们仅接受 `list_head` 结构体作为参数。

借助 `container_of()` 宏，我们可以轻松通过任意给定的成员变量，找到其所属的**宿主结构体**（父结构体）。这是因为在 C 语言中，结构体中某个成员变量相对于结构体起始地址的偏移量，会在编译阶段由应用程序二进制接口（ABI）固定下来，不会发生变化。

```c
#define container_of(ptr, type, member) ({ \
    const typeof( ((type *)0)->member ) *__mptr = (ptr); \
    (type *)( (char *)__mptr - offsetof(type, member) ); \
})
```

Using container_of(), we can define a simple function to return the parentstructure containing any list_head:

```c
#define list_entry(ptr, type, member) \
    container_of(ptr, type, member)
```

Armed with list_entry(), the kernel provides routines to create, manipulate,and otherwise manage linked lists—all without knowing anything about thestructures that the list_head resides within.

借助 `list_entry()` 宏，内核提供了一系列用于创建、操作和管理链表的函数 ——**这些函数完全无需知晓 `list_head` 节点所在的宿主结构体的任何信息**，实现了链表操作与具体业务结构体的解耦。

**List Heads**

The previous section shows how easy it is to take an existingstructure—such as ourstruct fox example—and turn it into a linked list.Withsimple code changes, our struc-ture is now manageable by the kernel’slinked list routines. But before we can use those routines, we need acanonical pointer to refer to the list as a whole—a head pointer.

上一节内容展示了，将一个已有的结构体（比如我们的`struct fox`示例）改造为链表是一件多么简单的事。只需进行少量代码修改，我们的结构体就能被内核的链表操作函数所管理。但在使用这些函数之前，我们需要一个**用于指代整个链表的标准指针 —— 头指针**。

One nice aspect of the kernel’s linked list implementation is that our foxnodes are indistinguishable. Each contains a list_head, and we can iterate from any onenode to the next, until we have seen every node.This approach is elegant,but you will generally want a special pointer that refers to your linked list,without being a list node itself. Inter-estingly, this special node is in fact anormal list_head:

Linux 内核链表实现的一个精妙之处在于：我们所有的`fox`节点之间是**无差别的**。每个`fox`节点都包含一个`list_head`结构体，我们可以从任意一个节点出发，遍历到下一个节点，直至遍历完所有节点。这种设计简洁优雅，但在实际使用中，你通常会需要一个特殊的指针来指代整个链表，而这个指针本身**并非一个普通的链表节点**。有趣的是，这个特殊节点实际上就是一个普通的`list_head`结构体：

```c
static LIST_HEAD(fox_list);
```

This defines and initializes a list_head named fox_list.The majority of thelinked list routines accept one or two parameters: the head node or the head nodeplus an actual list node. Let’s look at those routines.

这行代码定义并初始化了一个名为`fox_list`的`list_head`变量（作为链表头）。内核的大多数链表操作函数，都接受一个或两个参数：要么是链表头节点，要么是链表头节点加上一个实际的普通链表节点。接下来，我们就来看看这些链表操作函数。

#### Manipulating Linked Lists

ListsThe kernel provides a family of functions tomanipulate linked lists.They all take point-ers to one or more list_headstructures.The functions are implemented as inline func-tions in generic Cand can be found in <linux/list.h>.

内核提供了**一整套用于操作链表的函数**，这些函数均接收一个或多个`list_head`结构体指针作为参数。它们以**内联函数**的形式，用通用 C 语言实现，定义在头文件`<linux/list.h>`中。

Interestingly, all these functions are O(1).1 This means they execute inconstant time, regardless of the size of the list or any other inputs. Forexample, it takes the same amount of time to add or remove an entry to orfrom a list whether that list has 3 or 3,000 entries.This is perhaps notsurprising, but still good to know.

有趣的是，所有这些链表操作函数的时间复杂度都是**O(1)**（常数时间复杂度）。这意味着，无论链表的长度如何（也无论其他输入参数是什么），这些函数的执行时间都是固定不变的。例如，向一个链表中添加或删除一个节点，无论该链表包含 3 个节点还是 3000 个节点，所消耗的时间都是相同的。这一点或许不足为奇，但依旧值得明确。

Adding a Node to a Linked List To add a node to a linked list:

向链表中添加节点可使用以下函数：

```c
list_add(struct list_head *new, struct list_head *head)
```

This function adds the new node to the given list immediately after the headnode.

该函数会将`new`指向的新节点，添加到给定链表中`head`节点的**紧后方**。

Because the list is circular and generally has no concept of first or lastnodes, you can pass any element for head. If you do pass the “last” element,however, this function can be used to implement a stack.

由于内核链表是**循环链表**，且通常没有明确的 “首节点” 和 “尾节点” 概念，因此你可以将链表中的任意一个节点作为`head`参数传入。不过，如果你传入的是链表的 “尾节点”，那么这个函数就可以用来实现 **栈（先进后出，LIFO** 的数据结构。

Returning to our fox example, assume we had a new struct fox that we wanted to add to the fox_list list.We’d do this:

回到我们的`fox`结构体示例：假设我们有一个新的`struct fox`实例，想要将它添加到`fox_list`链表中，我们可以这样操作：

```c
list_add(&f->list, &fox_list);
```

To add a node to the end of a linked list:

若要将节点添加到链表的末尾，可使用以下函数：

```c
list_add_tail(struct list_head *new, struct list_head *head)
```

This function adds the new node to the given list immediately before the head node.Aswith list_add(), because the lists are circular, you can generally pass any element forhead.This function can be used to implement a queue, however, if you pass the “first”element.

该函数会将`new`指向的新节点，添加到给定链表中`head`节点的**紧前方**。与`list_add()`函数类似，由于内核链表是循环结构，你通常可以将链表中的任意一个节点作为`head`参数传入。不过，如果你传入的是链表的 “首节点”，那么这个函数就可以用来实现 **队列（先进先出，FIFO）** 的数据结构。

Deleting a Node from a Linked ListAfter adding a node to a linked list, deleting a nodefrom a list is the next most important operation.To delete a node from a linked list, uselist_del():

向链表中添加节点之后，从链表中删除节点是第二重要的链表操作。要从链表中删除一个节点，可使用`list_del()`函数：

```c
list_del(struct list_head *entry)
```

This function removes the element entry from the list. Note that it does not free anymemory belonging to entry or the data structure in which it is embedded; this functionmerely removes the element from the list.After calling this, you would typically destroyyour data structure and the list_head inside it.

该函数会将`entry`指向的节点从链表中移除。**注意：该函数并不会释放`entry`节点本身，也不会释放它所嵌入的业务结构体占用的任何内存**—— 它仅完成 “将节点从链表中脱离” 的操作，不涉及任何内存释放逻辑。调用该函数后，你通常需要自行销毁对应的业务结构体，以及其中嵌入的`list_head`节点（释放相关内存）。

For example, to delete the fox node we previous added to fox_list: 

举个例子，要删除我们之前添加到`fox_list`链表中的那个`fox`节点，可按如下方式操作：

```c
list_del(&f->list);
```

Note the function does not receive as input fox_list. It simply receives a specific node and modifies the pointers of the previous and subsequent nodes such that thegiven node is no longer part of the list.The implementation is instructive:

```c
static inline void __list_del(struct list_head *prev, struct list_head *next) {next->prev = prev; prev->next = next;    }static inline void list_del(struct list_head *entry) {__list_del(entry->prev, entry->next);}
```

…

**Saving a Couple Dereferences**

If you happen to already have the next and prev pointers available, you can save acouple cycles (specifically, the dereferences to get the pointers) by calling the internal   list functions directly. Every previously discussed function actually does nothing except find the next and prev pointers and then call the internal functions. The internal functions generally have the same name as their wrappers, except they are prefixed by double underscores. For exam-ple, rather than call list_del(list), you can call __list_del(prev, next). This is useful only if the next and previous pointers are already dereferenced. Otherwise, you are just writing ugly code. See the header <linux/list.h>for the exact interfaces.

如果你恰好已经获取了`next`和`prev`指针（无需额外获取），可以直接调用内核链表的**内部函数**，以此节省几个指令周期（具体来说，就是省去了用于获取这两个指针的两次指针解引用操作）。我们之前讨论的所有链表操作函数，其核心逻辑其实都是先找到对应的`next`和`prev`指针，再调用这些内部函数 —— 它们自身并没有额外的复杂逻辑。

这些内部函数的名称通常与对应的**包装函数**一致，唯一区别是内部函数名前会加双下划线`__`作为前缀。例如，你可以不调用`list_del(list)`（包装函数），而是直接调用`__list_del(prev, next)`（内部函数）。但这种用法**只有在你已经解引用得到`next`和`prev`指针时才有实际意义**；否则，这样写出来的代码只会晦涩难懂且不规范。关于这些内部函数的完整接口定义，可参考头文件`<linux/list.h>`。

#### Traversing Linked Lists

Now you know how to declare, initialize, and manipulate a linkedlist in the kernel.This is all very well and good, but it is meaningless if you have no wayto access your data! The linked lists are just containers that hold your important data;you need a way to use lists to move around and access the actual structures thatcontain the data.The kernel (thank goodness) provides a nice set of interfaces fortraversing linked lists and referencing the data structures that include them.

现在你已经掌握了如何在内核中声明、初始化和操作链表，这些知识固然重要，但如果无法访问链表中存储的实际数据，那这些操作也就失去了意义。链表本身只是承载重要数据的容器，你还需要一套方法，通过链表遍历访问到那些嵌入了`list_head`、包含实际业务数据的结构体。幸运的是，内核提供了一套易用的接口，用于遍历链表并引用其中包含的业务数据结构体。

Note that, unlike the list manipulation routines, iterating over a linked list in its entiretyis clearly an O(n) operation, for n entries in the list.

需要注意的是，与之前那些 O (1) 时间复杂度的链表操作函数不同，**完整遍历一个包含`n`个节点的链表，显然是一种 O (n) 时间复杂度的操作**（遍历时间会随链表节点数量线性增长）。

**The Basic Approach**

The most basic way to iterate over a list is with thelist_for_each()macro.The macro takes two parameters, both list_head structures.Thefirst is a pointer used to point to the current entry; it is a temporary variable that youmust provide.The second is thelist_head acting as the head node of the list you want totraverse (see the earlier section, “List Heads”). On each iteration of the loop, the firstparameter points to the next entry in the list, until each entry has been visited. Usage isas follows:

遍历链表最基础的方式是使用`list_for_each()`宏。该宏接受两个参数，且两个参数均为`list_head`结构体类型：

1. 第一个参数是一个临时指针变量（需要由你自行定义），用于指向遍历过程中的当前链表节点；
2. 第二个参数是作为待遍历链表头节点的`list_head`（可参考前文「链表头节点」部分的内容）。

在循环的每一次迭代中，第一个参数会指向链表中的下一个节点，直到链表中的所有节点都被遍历完毕。该宏的使用示例如下：

```c
struct list_head *p;

list_for_each(p, fox_list)
{
    /* p 指向链表中的一个 list_head 节点 */
    /* p points to an entry in the list */
}
```

Well, that is still worthless! A pointer to the list structure is usually no good; what we need is a pointer to the structure that contains the list_head. For example, with the pre-vious fox structure example, we want a pointer to each fox, not a pointer to the listmember in the structure.We can use the macro list_entry(), which we discussed ear-lier,to retrieve the structure that contains a given list_head. For example:

可即便如此，这样做依旧没有实际价值！仅拿到`list_head`结构体的指针通常毫无用处，我们真正需要的，是**指向包含该`list_head`节点的业务结构体的指针**。比如在之前的`fox`结构体示例中，我们需要的是指向每个`fox`实例的指针，而非指向该结构体中`list`成员（`list_head`类型）的指针。

此时，我们可以使用前文讨论过的`list_entry()`宏，通过给定的`list_head`节点，获取其所属的宿主业务结构体。示例如下：

```c
struct list_head *p;
struct fox *f;

list_for_each(p, &fox_list)
{
    /* f 指向嵌入了该 list_head 节点的 fox 结构体 */
    /* f points to the structure in which the list is embedded */
    f = list_entry(p, struct fox, list);
}
```

The previous approach does not make for particularly intuitive orelegant code, although it does illustrate how list_head nodes function. Consequently,most kernel code uses thelist_for_each_entry() macro to iterate over a linked list.Thismacro handles the work performed by list_entry(), making list iteration simple:

这种先通过`list_for_each()`遍历`list_head`节点，再通过`list_entry()`转换为业务结构体指针的方式，虽然能清晰说明`list_head`节点的工作机制，但写出来的代码既不直观，也不够简洁优雅。

因此，内核中的大多数代码都会使用`list_for_each_entry()`宏来遍历链表。该宏已经**封装了`list_entry()`的转换逻辑**，无需手动进行结构体指针转换，让链表遍历操作变得十分简洁：

```c
list_for_each_entry(pos, head, member)
```

Here, pos is a pointer to the object containing the list_head nodes.Think of it as thereturn value from list_entry(). head is a pointer to the list_head head node from which you want to start iterating—in our previous example, fox_list. member is the vari-ablename of the list_head structure in pos—list in our example.This sounds confus-ing, butit is easy to use. Here is how we would rewrite the previous list_for_each() to iterateover every fox node:

此处，`pos` 是一个指向**包含`list_head`节点的业务对象**的指针，你可以把它理解为`list_entry()`宏的返回值。`head` 是一个指向链表头节点的`list_head`类型指针，遍历操作将从这个头节点开始 —— 在我们之前的示例中，这个头节点就是`fox_list`。`member` 则是`pos`所指向的结构体中，`list_head`类型成员的变量名 —— 在我们的示例中，这个变量名就是`list`。

这段参数解释听起来可能有些晦涩难懂，但实际使用起来却非常简单。下面我们就来演示如何改写之前使用`list_for_each()`的代码，以此遍历所有的`fox`节点：

```c
struct fox *f;

list_for_each_entry(f, &fox_list, list)
{
    /* 每次循环迭代时，'f' 指向链表中的下一个 fox 结构体 */
}
```

Now let’s look at a real example, from inotify, the kernel’s filesystem notification system:

现在我们来看一个真实的内核示例，来自内核的文件系统通知机制 ——`inotify`：

```c
static struct inotify_watch *inode_find_handle(struct inode *inode, struct inotify_handle *ih)
{
    struct inotify_watch *watch;
    list_for_each_entry(watch, &inode->inotify_watches, i_list)
    {
        if (watch->ih == ih)
            return watch;
    }
    return NULL;
}
```

This function iterates over all the entries in the inode->inotify_watches list. Each entry is of type struct inotify_watch and the list_head in that structure is namedi_list.With each iteration of the loop, watch points at a new node in the list.The purpose of this simple function is to search the inotify_watches list in the provided inode struc-ture to find an inotify_watch entry whose inotify_handle matches the provided handle.

该函数会遍历`inode->inotify_watches`链表中的所有节点。每个节点的类型都是`struct inotify_watch`，该结构体中的`list_head`成员名为`i_list`。在循环的每一次迭代中，`watch`指针都会指向链表中的一个新的`struct inotify_watch`节点。

这个简单函数的核心作用是：在传入的`inode`结构体的`inotify_watches`链表中进行搜索，找到一个`inotify_handle`与传入的`handle`参数相匹配的`inotify_watch`节点。

…

### Maps

A map, also known as an associative array, is a collection of unique keys, where  each key is associated with a specific value.The relationship between a key and its valueis called a mapping. Maps support at least three operations:

- Add (key, value)
- Remove (key)
- value = Lookup (key)

映射（又称**关联数组**）是一种由唯一键（key）组成的集合，其中每个键都与一个特定的值（value）一一对应。键与对应值之间的这种关系被称为「映射关系」。映射至少支持三种核心操作：

- 新增（Add）：插入一组键值对（key, value）
- 删除（Remove）：根据键（key）移除对应的映射条目
- 查找（Lookup）：根据键（key）获取对应的值（value = Lookup (key)）

Although a hash table is a type of map, not all maps are implemented via hashes. 

尽管哈希表是映射的一种实现方式，但**并非所有映射都基于哈希表实现**。

Instead of a hash table, maps can also use a self-balancing binary search tree to storetheir data.Although a hash offers better average-case asymptotic complexity (see thesection “Algorithmic Complexity” later in this chapter), a binary search tree has betterworst-case behavior (logarithmic versus linear).A binary search tree also enables orderpreservation, enabling users to efficiently iterate over the entire collection in a sortedorder. Finally, a binary search tree does not require a hash function; instead, any keytype is suitable so long as it can define the <= operator.

映射除了可以用哈希表实现外，还可以使用「自平衡二叉搜索树」来存储数据。虽然哈希表在**平均情况**下具有更优的渐进时间复杂度（详见本章后续「算法复杂度」小节），但二叉搜索树的**最坏情况**表现更为出色（时间复杂度为对数级，而哈希表最坏情况为线性级）。此外，二叉搜索树还支持「有序性保留」，能够让用户以有序的方式高效遍历整个集合。最后，二叉搜索树无需依赖哈希函数，只要键类型能够定义「<=」（小于等于）比较运算符，任何类型的键都可以用于这种映射实现。

Although the general term for all collections mapping a key to a value, the name maps often refers specifically to an associated array implemented using a binary search tree as opposed to a hash table. For example, the C++ STL container std::map is implemented using a self-balancing binary search tree (or similar data structure),because it provides the ability to in-order traverse the collection.

虽然「映射」是所有「键值映射集合」的通用术语，但在很多场景下，「map」这个名称特指**基于二叉搜索树实现的关联数组**（而非基于哈希表实现）。例如，C++ 标准模板库（STL）中的容器 `std::map` 就是基于自平衡二叉搜索树（或类似数据结构）实现的，这是因为自平衡二叉搜索树能够提供「中序遍历」整个集合的能力。

The Linux kernel provides a simple and efficient map data structure, but it is not a general-purpose map. Instead, it is designed for one specific use case: mapping a unique identification number (UID) to a pointer. In addition to providing the three main mapoperations, Linux’s implementation also piggybacks an allocate operation on top of theadd operation.This allocate operation not only adds a UID/value pair to the map but alsogenerates the UID.

Linux 内核提供了一种简单高效的映射数据结构，但它**并非通用目的的映射**。该结构是为一种特定场景专门设计的：将**唯一标识号（UID）映射到指针**。除了支持映射的三种核心操作外，Linux 内核的映射实现还在「新增（Add）」操作之上，额外封装了「分配（allocate）」操作。这种分配操作不仅会向映射中插入一组 UID / 值 对，还会自动生成对应的唯一标识号（UID）。

The idr data structure is used for mapping user-space UIDs, such as inotify watch descriptors or POSIX timer IDs, to their associated kernel data structure, such as theinotify_watch or k_itimer structures, respectively. Following the Linux kernel’s scheme ofobfuscated, confusing names, this map is called idr.

**IDR（idr）数据结构**用于将用户空间的各类唯一标识（UID）—— 例如 inotify 监控描述符、POSIX 定时器 ID 等 —— 分别映射到其对应的内核数据结构，比如 `inotify_watch` 结构体或 `k_itimer` 结构体。秉承 Linux 内核一贯晦涩、难懂的命名风格，这个映射结构被命名为 **idr**。

#### Initializing an idr

Setting up an idr is easy. First you statically define or dynamicallyallocate an idr struc-ture.Then you call idr_init():

```c
void idr_init(struct idr *idp);
```

 For example:

```c
struct idr id_huh; /* statically define idr structure */ 
idr_init(&id_huh); /* initializeprovided idr structure */
```

#### Allocating a New UID

Once you have an idr set up, you can allocate a new UID, which isa two-step process. First you tell the idr that you want to allocate a new UID, allowing itto resize the back-ing tree as necessary.Then, with a second call, you actually requestthe new UID.This complication exists to allow you to perform the initial resizing, whichmay require a memory allocation, without a lock.We discuss memory allocations inChapter 12 and locking in Chapters 9 and 10. For now, let’s concentrate on using idrwithout concern to how we handle locking.

当你完成 idr 数据结构的初始化后，就可以分配新的唯一标识号（UID）了，这个过程分为**两个步骤**。第一步，你需要告知 idr 你要分配新 UID，让它能够按需调整**底层支撑树**的大小（以便容纳新的 UID 映射）。第二步，通过第二次函数调用，你才能实际获取到这个新 UID。

之所以要拆分出这样看似繁琐的两步流程，是为了让你能够在**不持有锁**的情况下执行初始的树大小调整操作 —— 而该操作可能需要进行内存分配。关于内存分配的内容我们将在第 12 章讲解，锁相关内容则在第 9 章和第 10 章讨论。目前，我们先专注于 idr 的使用，暂不考虑如何处理锁相关逻辑。

The first function, to resize the backing tree, is idr_pre_get():

第一步：调整底层支撑树大小 ——`idr_pre_get()` 函数：

```c
int idr_pre_get(struct idr *idp, gfp_t gfp_mask);
```

This function will, if needed to fulfill a new UID allocation, resize the idr pointed at by idp. If a resize is needed, the memory allocation will use the gfp flags gfp_mask (gfpflags are discussed in Chapter 12).You do not need to synchronize concurrent access tothis call. Inverted from nearly every other function in the kernel, idr_pre_get() returns oneon success and zero on error—be careful!

为了满足新 UID 的分配需求，该函数会按需调整 `idp` 所指向的 idr 结构体的底层支撑树大小。如果确实需要调整树大小，对应的内存分配操作会使用 `gfp_mask` 所指定的 GFP 标志位（GFP 标志位的详细说明见第 12 章）。

调用该函数时，**无需对并发访问进行同步处理**（即无需持有锁）。需要特别注意的是：该函数的返回值规则**与内核中几乎所有其他函数相反**—— 返回 1 表示执行成功，返回 0 表示执行失败，使用时务必留意这一点！

The second function, to actually obtain a new UID and add it to the idr, is idr_get_new():

第二步：实际分配 UID 并添加到 idr——`idr_get_new()` 函数

```c
int idr_get_new(struct idr *idp, void *ptr, int *id);
```

This function uses the idr pointed at by idp to allocate a new UID and associate it with the pointer ptr. On success, the function returns zero and stores the new UID inid.On error, it returns a nonzero error code: -EAGAIN if you need to (again) callidr_pre_get() and -ENOSPC if the idr is full.

该函数会利用 `idp` 所指向的 idr 结构体，分配一个新的 UID，并将该 UID 与指针 `ptr`（指向对应的内核数据结构）进行关联。

- 执行成功时：函数返回 0，并将新分配的 UID 存储到 `id` 指针所指向的内存空间中；
- 执行失败时：函数返回一个非 0 的错误码 —— 返回 `-EAGAIN` 表示你需要（再次）调用 `idr_pre_get()` 调整树大小后重试，返回 `-ENOSPC` 表示该 idr 已经满了，无法再分配新的 UID。

Let’s look at a full example:

```c
int id;
int ret;
do {
    if (!idr_pre_get(&idr_huh, GFP_KERNEL)) {
        return -ENOSPC;
    }
    ret = idr_get_new(&idr_huh, ptr, &id);
} while (ret == -EAGAIN);
```

If successful, this snippet obtains a new UID, which is stored in the integer id and maps that UID to ptr (which we don’t define in the snippet).

如果执行成功，这段代码片段会获取一个新的唯一标识号（UID），该 UID 会存储在整型变量`id`中，并且这段代码会将该 UID 与指针`ptr`（我们未在该代码片段中定义此指针）建立映射关系。

The function idr_get_new_above() enables the caller to specify a minimum UID value to return:

函数`idr_get_new_above()`允许调用者指定一个返回 UID 的**最小值**：

```c
int idr_get_new_above(struct idr *idp, void *ptr, int starting_id, int *id);
```

This works the same as idr_get_new(), except that the new UID is guaranteed to beequal to or greater than starting_id. Using this variant of the function allows idr users toensure that a UID is never reused, allowing the value to be unique not only amongcurrently allocated IDs but across the entirety of a system’s uptime.This code snippet isthe same as our previous example, except that we request strictly increasing UID values:

该函数的工作机制与`idr_get_new()`基本一致，唯一区别在于，它保证返回的新 UID**大于或等于`starting_id`（起始 ID）**。使用这个函数变体，idr 的使用者可以确保某个 UID 永远不会被复用，这使得该 UID 不仅在当前已分配的所有 ID 中保持唯一，甚至在**整个系统的运行期间**都具有唯一性。这段代码片段与我们之前的示例逻辑一致，唯一不同的是，我们通过它请求**严格递增**的 UID 值：

```c
int id;
int ret;

do {
    // 预分配内存并调整 idr 底层基数树大小
    if (!idr_pre_get(&idr_huh, GFP_KERNEL)) {
        return -ENOSPC;
    }

    // 尝试分配不小于 next_id 的唯一 UID，关联内核指针 ptr
    ret = idr_get_new_above(&idr_huh, ptr, next_id, &id);
} while (ret == -EAGAIN);  // 若返回 -EAGAIN，循环重试预分配和分配流程

// 若分配成功，更新下一次分配的最小候选 ID 为当前 ID+1
if (!ret) {
    next_id = id + 1;
}
```

#### Looking Up a UID

When we have allocated some number of UIDs in an idr, we can look them up:The caller provides the UID, and the idr returns the associated pointer.This is accomplished, in a much simpler manner than allocating a new UID, with the idr_find()function:

当我们在一个 idr 中分配了若干个 UID 后，还可以对这些 UID 进行**查找操作**：调用者传入需要查找的 UID，idr 会返回与之关联的指针。这项操作的实现方式比分配新 UID 简单得多，只需通过`idr_find()`函数即可完成：

```c
void *idr_find(struct idr *idp, int id);
```

A successful call to this function returns the pointer associated with the UID id in the idr pointed at by idp. On error, the function returns NULL. Note if you mapped NULL to a UID with idr_get_new() or idr_get_new_above(), this function successfully returnsNULL,giving you no way to distinguish success from failure. Consequently, you should not map UIDs to NULL.

调用该函数成功时，会返回`idp`所指向的 idr 中，与 UID`id`相关联的指针；调用失败时，函数返回`NULL`。需要注意的是，如果你通过`idr_get_new()`或`idr_get_new_above()`将某个 UID 映射到了`NULL`，那么该函数也会成功返回`NULL`，这会让你**无法区分操作是成功还是失败**。因此，你不应该将 UID 映射到`NULL`。

#### Removing a UID

To remove a UID from an idr, use idr_remove():

要从 idr 中删除一个 UID，可以使用`idr_remove()`函数：

```c
void idr_remove(struct idr *idp, int id);
```

A successful call to idr_remove() removes the UID id from the idr pointed at by idp.

调用`idr_remove()`成功时，会将 UID`id`从`idp`所指向的 idr 中移除。

Unfortunately, idr_remove() has no way to signify error (for example if id is not in idp).

遗憾的是，`idr_remove()`**没有提供任何错误标识机制**（例如，当待删除的 UID`id`并不存在于`idp`对应的 idr 中时，无法得知操作失败）。

#### Destroying an idr

Destroying an idr is a simple affair, accomplished with the idr_destroy() function: 

销毁一个 idr 的操作十分简单，只需调用`idr_destroy()`函数即可：

```c
void idr_destroy(struct idr *idp);
```

A successful call to idr_destroy() deallocates only unused memory associated with  the idr pointed at by idp. It does not free any memory currently in use by allocated UIDs.Generally, kernel code wouldn’t destroy its idr facility until it was shutting down orunloading, and it wouldn’t unload until it had no more users (and thus no more UIDs),but to force the removal of all UIDs, you can call idr_remove_all():

调用`idr_destroy()`成功时，**仅会释放`idp`所指向的 idr 中未被使用的内存**，并不会释放当前已分配 UID 所占用的任何内存。一般来说，内核代码只有在即将关闭或卸载自身功能时，才会销毁对应的 idr 机制；而在卸载之前，内核会确保已经没有任何使用者（因此也不会残留任何已分配的 UID）。但如果需要强制移除 idr 中的所有 UID，可以调用`idr_remove_all()`函数：

```c
void idr_remove_all(struct idr *idp);
```

You would call idr_remove_all() on the idr pointed at by idp before calling idr_destroy(), ensuring that all idr memory was freed.

你应该先对`idp`所指向的 idr 调用`idr_remove_all()`，再调用`idr_destroy()`，这样才能确保 idr 的所有内存都被成功释放。

### Binary Trees

A tree is a data structure that provides a hierarchical tree-like structure ofdata. Mathemati-cally, it is an acyclic, connected, directed graph in which each vertex(called a node) has zero or more outgoing edges and zero or one incoming edges.Abinary tree is a tree in which nodes have at most two outgoing edges—that is, a tree inwhich nodes have zero, one, or two children. 

树是一种提供**分层树形数据结构**的数据结构。从数学角度来说，它是一种**无环、连通、有向图**，图中的每个顶点（称为**节点**）拥有零个或多个出边，以及零个或一个入边。**二叉树**是一种节点最多拥有两个出边的树 —— 也就是说，树中的节点可以拥有零个、一个或两个子节点。

**Red-Black Trees**

A red-black tree is a type of self-balancing binary search tree. Linux’       primary binary tree data structure is the red-black tree. Red-black trees have a specialcolor attribute, which is either red or black. Red-black trees remain semi-balanced byenforcing that the following six properties remain true:

- All nodes are either red or black.
- Leaf nodes are black.
- Leaf nodes do not contain data.
- All non-leaf nodes have two children.
-  If a node is red, both of its children are black.
- The path from a node to one of its leaves contains the same number of black nodes   as the shortest path to any of its other leaves.

红黑树是一种**自平衡二叉搜索树**。Linux 内核中最主要的二叉树数据结构就是红黑树。红黑树的节点拥有一个特殊的**颜色属性**，取值为红色或黑色。红黑树通过强制维持以下六个属性始终成立，来保持自身处于**半平衡**状态：

1. 所有节点非红即黑。
2. 叶子节点为黑色。
3. 叶子节点不存储数据。
4. 所有非叶子节点都拥有两个子节点。
5. 如果一个节点是红色，那么它的两个子节点都必须是黑色。
6. 从一个节点到其任一叶子节点的路径，所包含的黑色节点数量，与该节点到其他任一叶子节点的最短路径所包含的黑色节点数量相同。

Taken together, these properties ensure that the deepest leaf has a depth of no more than double that of the shallowest leaf. Consequently, the tree is always semi-balanced.Why this is true is surprisingly simple. First, by property five, a red node cannot be thechild or parent of another red node. By property six, all paths through the tree to itsleaves have the same number of black nodes.The longest path through the treealternates red and black nodes.Thus the shortest path, which must have the samenumber of black nodes, contains only black nodes.Therefore, the longest path from theroot to a leaf is no more than double the shortest path from the root to any other leaf.

综合来看，这些属性共同保证了：树中**最深叶子节点的深度，不会超过最浅叶子节点深度的两倍**。因此，红黑树始终能保持半平衡状态。这一结论的原理其实非常简单：首先，根据第五条属性，红色节点不能作为另一个红色节点的子节点或父节点；其次，根据第六条属性，树中所有通向叶子节点的路径，都包含相同数量的黑色节点。树中最长的路径，必然是红、黑节点交替出现的路径；而包含相同数量黑色节点的最短路径，则仅由黑色节点组成。由此可知，从根节点到叶子节点的最长路径，其长度不会超过从根节点到其他任一叶子节点最短路径的两倍。

If the insertion and removal operations enforce these six properties, the tree remains semi-balanced. Now, it might seem odd to require insert and remove to maintain theseparticular properties.Why not implement the operations such that they enforce other, simpler rules that result in a balanced tree? It turns out that these properties arerelatively easy to enforce (although complex to implement), allowing insert and removeto guaran-tee a semi-balanced tree without burdensome extra overhead.

如果插入和删除操作能够强制维持上述六个属性，红黑树就能始终保持半平衡。或许你会觉得，要求插入、删除操作维持这些特定属性有些奇怪 —— 为什么不设计一套更简单的规则，让插入、删除操作去遵守，从而实现平衡树呢？事实证明，红黑树的这六个属性**相对容易维持**（尽管具体实现较为复杂），这使得插入、删除操作能够在**不产生繁重额外开销**的前提下，保证树的半平衡状态。

### What Data Structure to Use

WhenThus far we’ve discussed four of Linux’s mostimportant data structures: linked lists, queues, maps, and red-black trees. In thissection, we cover some tips to help you decide which data structure to use in your owncode.

到目前为止，我们已经讨论了 Linux 内核中四种最重要的数据结构：**链表**、**队列**、**映射**和**红黑树**。在本节中，我们将分享一些实用技巧，帮助你在编写自己的内核代码时，选择合适的数据结构。

If your primary access method is iterating over all your data, use a linked list. Intuitively,no data structure can provide better than linear complexity when visiting every element, so you should favor the simplest data structure for that simple job.Also consider linkedlists when performance is not important, when you need to store a relatively smallnumber of items, or when you need to interface with other kernel code that uses linkedlists.

如果你的**主要访问方式是遍历所有数据**，那么请使用链表。直观来说，当需要访问每一个元素时，任何数据结构的时间复杂度都无法优于线性复杂度，因此对于这种简单场景，你应该优先选择最简单的数据结构。此外，在以下场景中也可以考虑使用链表：

1. 对性能要求不高时；
2. 需要存储的数据量相对较小时；
3. 必须与其他使用链表的内核代码进行交互时。

If your code follows the producer/consumer pattern, use a queue, particularly if you want (or can cope with) a fixed-size buffer. Queues make adding and removing itemssimple and efficient, and they provide first-in, first-out (FIFO) semantics, which is whatmost producer/consumer use cases demand. On the other hand, if you need to store anunknown, potentially large number of items, a linked list may make more sense, becauseyou can dynamically add any number of items to the list.

如果你的代码遵循**生产者 / 消费者模式**，那么请使用队列 —— 尤其是当你需要（或能够接受）一个**固定大小缓冲区**时。队列让数据项的添加和删除操作变得简单高效，并且它提供 **先进先出（FIFO）** 的语义，这也是大多数生产者 / 消费者场景的核心需求。

不过，如果你需要存储的数据量未知，且可能非常庞大，那么链表可能是更合适的选择，因为你可以向链表中动态添加任意数量的数据项，无需受缓冲区大小的限制。

If you need to map a UID to an object, use a map. Maps make such mappings easy andefficient, and they also maintain and allocate the UID for you. Linux’s map interface,being specific to UID-to-pointer mappings, isn’t good for much else, however. If you  are dealing with descriptors handed out to user-space, consider this option.

如果你的需求是**将一个唯一标识号（UID）映射到某个对象**，那么请使用映射。映射让这类键值映射操作变得便捷高效，并且它还会自动为你维护和分配 UID。

但需要注意的是，Linux 内核的映射接口是专门针对「UID - 指针」映射设计的，在其他场景下的实用性很低。如果你需要处理分发给用户空间的描述符，那么可以优先考虑这种数据结构。

If you need to store a large amount of data and look it up efficiently, consider a red-black tree. Red-black trees enable the searching in logarithmic time, while still providingan efficient linear time in-order traversal.Although more complicated to implement thanthe other data structures, their in-memory footprint isn’t significantly worse. If you arenot performing many time-critical look-up operations, a red-black tree probably isn’tyour best bet. In that case, favor a linked list.

如果你的需求是**存储大量数据，并且需要高效地查找数据**，那么可以考虑红黑树。红黑树支持**对数时间复杂度的查找操作**，同时还能提供高效的**线性时间复杂度中序遍历**。

尽管红黑树的实现复杂度远高于其他几种数据结构，但它的**内存占用量并不会明显更高**。不过，如果你不需要执行大量对时间敏感的查找操作，那么红黑树很可能不是最佳选择 —— 这种情况下，优先选择链表即可。

None of these data structures fit your needs? The kernel implements other seldom-useddata structures that might meet your needs, such as radix trees (a type of trie) andbitmaps. Only after exhausting all kernel-provided solutions should you consider “rollingyour own” data structure. One common data structure often implemented in individualsource files is the hash table. Because a hash table is little more than some buckets anda hash function, and the hash function is so specific to each use case, there is littlevalue in providing a kernelwide solution in a nongeneric programming language such asC.

如果以上这些数据结构都无法满足你的需求，也无需着急 —— 内核中还实现了一些使用频率较低的数据结构，可能会符合你的要求，例如**基数树（一种字典树 / 前缀树）**和**位图**。

只有在穷尽了所有内核提供的现成解决方案后，你才应该考虑「**自行实现**」数据结构。在各个独立源码文件中，最常被自行实现的一种数据结构是**哈希表**。这是因为哈希表的本质不过是一些「桶」和一个哈希函数，而哈希函数的设计又高度依赖具体的使用场景 —— 在 C 语言这种非通用编程语言中，提供一个适用于整个内核的通用哈希表方案，其实并没有太大的实际价值。





