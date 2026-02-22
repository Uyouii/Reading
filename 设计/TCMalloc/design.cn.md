[tcmalloc](https://google.github.io/tcmalloc/)

# TCMalloc : Thread-Caching Malloc

## Motivation

TCMalloc is a memory allocator designed as an alternative to the system default allocator that has the following characteristics:

- Fast, uncontended allocation and deallocation for most objects. Objects are cached, depending on mode, either per-thread, or per-logical-CPU. Most allocations do not need to take locks, so there is low contention and good scaling for multi-threaded applications.
- Flexible use of memory, so freed memory can be reused for different object sizes, or returned to the OS.
- Low per object memory overhead by allocating “pages” of objects of the same size. Leading to space-efficient representation of small objects.
- Low overhead sampling, enabling detailed insight into applications memory usage.

TCMalloc 是一款专为替代系统默认内存分配器而设计的内存分配器，具备以下特点：

- 对绝大多数对象提供**快速、无竞争**的内存分配与释放。对象会根据运行模式，缓存在**线程本地**或**逻辑 CPU 本地**。大多数分配操作无需加锁，因此竞争小、多线程场景下扩展性好。
- 内存使用灵活：释放后的内存既可重新用于不同大小的对象，也可归还给操作系统。
- 通过为**相同大小的对象批量分配 “页”**，降低单个对象的内存开销，实现小对象的高效空间利用。
- 低开销采样机制，可细致分析应用程序的内存使用情况。

## Usage

You use TCMalloc by specifying it as the `malloc` attribute on your binary rules in Bazel.

## Overview

The following block diagram shows the rough internal structure of TCMalloc:

![Diagram of TCMalloc internal structure](https://google.github.io/tcmalloc/images/tcmalloc_internals.png)

We can break TCMalloc into three components. The front-end, middle-end, and back-end. We will discuss these in more details in the following sections. A rough breakdown of responsibilities is:

- The front-end is a cache that provides fast allocation and deallocation of memory to the application.
- The middle-end is responsible for refilling the front-end cache.
- The back-end handles fetching memory from the OS.

我们可以将 TCMalloc 划分为三大组件：**前端、中端与后端**。后续章节会对它们展开详细讨论，其职责大致划分如下：

- **前端**：作为缓存层，向应用程序提供**快速的内存分配与释放**。
- **中端**：负责**向前端缓存进行填充**。
- **后端**：负责从操作系统中**申请与获取内存**。

Note that the front-end can be run in either per-CPU or legacy per-thread mode, and the back-end can support either the hugepage aware pageheap or the legacy pageheap.

注意：前端可运行在**按 CPU 模式**或传统的**按线程模式**；后端则可支持**感知大页的页堆（pageheap）**，或传统的页堆。

## The TCMalloc Front-end

The front-end handles a request for memory of a particular size. The front-end has a cache of memory that it can use for allocation or to hold free memory. This cache is only accessible by a single thread at a time, so it does not require any locks, hence most allocations and deallocations are fast.

**前端**负责处理指定大小的内存申请。前端维护了一块内存缓存，用于内存分配或存放空闲内存。该缓存**同一时间仅允许单个线程访问**，因此无需任何锁，这使得绝大多数分配与释放操作都能快速完成。

The front-end will satisfy any request if it has cached memory of the appropriate size. If the cache for that particular size is empty, the front-end will request a batch of memory from the middle-end to refill the cache. The middle-end comprises the CentralFreeList and the TransferCache.

如果前端缓存中存有对应大小的空闲内存，就会直接满足请求。如果该尺寸对应的缓存为空，前端会向**中端**申请一批内存来填充缓存。中端由 **中央空闲链表（CentralFreeList）**和**传输缓存（TransferCache）** 组成。

If the middle-end is exhausted, or if the requested size is greater than the maximum size that the front-end caches handle, a request will go to the back-end to either satisfy the large allocation, or to refill the caches in the middle-end. The back-end is also referred to as the PageHeap.

如果中端内存耗尽，或是申请的大小超过了前端缓存所能处理的上限，请求就会转发到**后端**，由后端处理大尺寸分配，或是为中端缓存补充内存。后端也被称作**页堆（PageHeap）**。

There are two implementations of the TCMalloc front-end:

- Originally it supported per-thread caches of objects (hence the name Thread Caching Malloc). However, this resulted in memory footprints that scaled with the number of threads. Modern applications can have large thread counts, which result in either large amounts of aggregate per-thread memory, or many threads having minuscule per-thread caches.
- More recently TCMalloc has supported per-CPU mode. In this mode each logical CPU in the system has its own cache from which to allocate memory. Note: On x86 a logical CPU is equivalent to a hyperthread.

TCMalloc 前端有两种实现：

- 最初支持**线程级缓存**（这也是 “线程缓存 malloc” 名称的由来）。但这种方式会导致内存占用随线程数同步增长。现代应用的线程数量往往很大，要么会产生巨大的线程缓存总开销，要么大量线程只能分到极小的本地缓存。
- 较新的 TCMalloc 支持**按 CPU 模式**。在该模式下，系统中每个**逻辑 CPU** 都拥有自己的分配缓存。注：在 x86 中，逻辑 CPU 等价于超线程。

The differences between per-thread and per-CPU modes are entirely confined to the implementations of malloc/new and free/delete.

线程级模式与按 CPU 模式的区别，**完全只体现在 malloc/new 和 free/delete 的实现内部**。

### Small and Large Object Allocation

Allocations of “small” objects are mapped onto one of [60-80 allocatable size-classes](https://github.com/google/tcmalloc/blob/master/tcmalloc/size_classes.cc). For example, an allocation of 12 bytes will get rounded up to the 16 byte size-class. The size-classes are designed to minimize the amount of memory that is wasted when rounding to the next largest size-class.

小对象的内存分配会被映射到 [60 至 80 个可分配的**大小类（size-class）**](https://github.com/google/tcmalloc/blob/master/tcmalloc/size_classes.cc) 中的某一个。例如，申请 12 字节的内存会被**向上取整**到 16 字节的大小类。这些大小类的设计目标是，将向上取整到下一个更大的大小类时产生的内存浪费降至最低。

When compiled with `__STDCPP_DEFAULT_NEW_ALIGNMENT__ <= 8`, we use a set of sizes aligned to 8 bytes for raw storage allocated with `::operator new`. This smaller alignment minimizes wasted memory for many common allocation sizes (24, 40, etc.) which are otherwise rounded up to a multiple of 16 bytes. On many compilers, this behavior is controlled by the `-fnew-alignment=...` flag. When `__STDCPP_DEFAULT_NEW_ALIGNMENT__` is not specified (or is larger than 8 bytes), we use standard 16 byte alignments for `::operator new`. However, for allocations under 16 bytes, we may return an object with a lower alignment, as no object with a larger alignment requirement can be allocated in the space.

当编译时定义 `__STDCPP_DEFAULT_NEW_ALIGNMENT__ <= 8` 时，通过 `::operator new` 分配的原始内存空间会使用一组按 8 字节**对齐**的尺寸。这种更小的对齐方式能减少许多常见分配尺寸（如 24、40 字节等）的内存浪费 —— 这些尺寸原本会被向上取整到 16 字节的整数倍。在多数编译器中，该行为由 `-fnew-alignment=...` 编译选项控制。若未定义 `__STDCPP_DEFAULT_NEW_ALIGNMENT__`（或其值大于 8 字节），则 `::operator new` 会采用标准的 16 字节对齐方式。但对于小于 16 字节的分配请求，返回的对象可能采用更低的对齐级别，因为该内存空间中无法分配对齐要求更高的对象。

When an object of a given size is requested, that request is mapped to a request of a particular size-class using the [`SizeMap::GetSizeClass()` function](https://github.com/google/tcmalloc/blob/master/tcmalloc/common.h), and the returned memory is from that size-class. This means that the returned memory is at least as large as the requested size. Allocations from size-classes are handled by the front-end.

当申请指定大小的对象时，该请求会通过 [`SizeMap::GetSizeClass()` 函数](https://github.com/google/tcmalloc/blob/master/tcmalloc/common.h) 映射到某个特定的大小类，返回的内存也来自该大小类。这意味着返回的内存空间**至少不小于**申请的尺寸。基于大小类的内存分配由**前端**负责处理。

Objects of size greater than the limit defined by [`kMaxSize`](https://github.com/google/tcmalloc/blob/master/tcmalloc/common.h) are allocated directly from the [backend](https://google.github.io/tcmalloc/design.html#tcmalloc-backend). As such they are not cached in either the front or middle ends. Allocation requests for large object sizes are rounded up to the [TCMalloc page size](https://google.github.io/tcmalloc/design.html#tcmalloc-page-sizes).

尺寸超过 [`kMaxSize`](https://github.com/google/tcmalloc/blob/master/tcmalloc/common.h) 定义上限的对象，会直接从 [后端（backend）](https://google.github.io/tcmalloc/design.html#tcmalloc-backend) 分配内存。因此这类对象不会被缓存到前端或中端中。大对象的分配请求会被向上取整到 [TCMalloc 页大小](https://google.github.io/tcmalloc/design.html#tcmalloc-page-sizes)。

### Deallocation

When an object is deallocated, the compiler will provide the size of the object if it is known at compile time. If the size is not known, it will be looked up in the [pagemap](https://google.github.io/tcmalloc/design.html#pagemap). If the object is small it will be put back into the front-end cache. If the object is larger than kMaxSize it is returned directly to the pageheap.

对象被释放时，如果其大小在**编译期已知**，编译器会直接提供该对象的大小。若大小未知，则会在 **页映射表（pagemap）** 中查询。

- 如果是**小对象**，会被放回**前端缓存**；
- 如果对象大小超过 `kMaxSize`，则会直接归还给**页堆（pageheap）**。

### Per-CPU Mode

In per-CPU mode a single large block of memory is allocated. The following diagram shows how this slab of memory is divided between CPUs and how each CPU uses a part of the slab to hold metadata as well as pointers to available objects.

在按 CPU 模式下，系统会分配一整块连续的大内存。下图展示了这块内存如何在各个 CPU 间划分，以及每个 CPU 如何用其中一部分存放元数据和指向空闲对象的指针。

![Memory layout of per-cpu data structures](https://google.github.io/tcmalloc/images/per-cpu-cache-internals.png)

Each logical CPU is assigned a section of this memory to hold metadata and pointers to available objects of particular size-classes. The metadata comprises one /header/ block per size-class. The header has a pointer to the start of the per-size-class array of pointers to objects, as well as a pointer to the current, dynamic, maximum capacity and the current position within that array segment. The static maximum capacity of each per-size-class array of pointers is [determined at start time](https://github.com/google/tcmalloc/blob/master/tcmalloc/internal/percpu_tcmalloc.h) by the difference between the start of the array for this size-class and the start of the array for the next size-class.

每个逻辑 CPU 都会被分配这段内存中的一个区域，用于存放元数据，以及指向特定**大小类**空闲对象的指针。

元数据为每个大小类维护一个**头部块**。头部中包含：

- 指向该大小类对象指针数组起始位置的指针
- 指向当前动态最大容量的指针
- 指向该数组段内当前位置的指针

每个大小类对象指针数组的**静态最大容量**在启动时确定，由当前大小类数组的起始地址与下一个大小类数组的起始地址之差决定。

At runtime the maximum number of items of a particular size-class that can be stored in the per-cpu block will vary, but it can never exceed the statically determined maximum capacity assigned at start up.

运行时，每个 CPU 区域里可存放的某一大小类对象的最大数量会动态变化，但永远不会超过启动时确定的静态最大容量。

When an object of a particular size-class is requested it is removed from this array, when the object is freed it is added to the array. If the array is [exhausted](https://github.com/google/tcmalloc/blob/master/tcmalloc/cpu_cache.h) the array is refilled using a batch of objects from the middle-end. If the array would [overflow](https://github.com/google/tcmalloc/blob/master/tcmalloc/cpu_cache.h), a batch of objects are removed from the array and returned to the middle-end.

申请某一大小类的对象时，会从该数组中取出对象；对象释放时，则会被放回数组。如果数组**已空**，会从中端批量获取对象来填充数组；如果数组**即将溢出**，则会从数组中批量移出对象并归还给中端。

The amount of memory that can be cached is limited per-cpu by the parameter `MallocExtension::SetMaxPerCpuCacheSize`. This means that the total amount of cached memory depends on the number of active per-cpu caches. Consequently machines with higher CPU counts can cache more memory.

每个 CPU 可缓存的内存总量由参数 `MallocExtension::SetMaxPerCpuCacheSize` 限制。这意味着总缓存内存大小取决于活跃的 CPU 缓存数量，CPU 数量更多的机器可以缓存更多内存。

To avoid holding memory on CPUs where the application no longer runs, `MallocExtension::ReleaseCpuMemory` frees objects held in a specified CPU’s caches.

为避免在应用已不再运行的 CPU 上占用内存，可通过 `MallocExtension::ReleaseCpuMemory` 释放指定 CPU 缓存里的对象。

Within a CPU, the distribution of memory is managed across all the size-classes so as to keep the maximum amount of cached memory below the limit. Notice that it is managing the maximum amount that can be cached, and not the amount that is currently cached. On average the amount actually cached should be about half the limit.

在单个 CPU 内部，内存会在所有大小类之间统筹分配，保证**可缓存的最大容量**不超过限制。注意：系统管控的是**可缓存的最大容量**，而非当前实际缓存的大小。平均来看，实际缓存量大约是限制值的一半。

The maximum capacity is increased when a size-class [runs out of objects](https://github.com/google/tcmalloc/blob/master/tcmalloc/cpu_cache.h), and when fetching more objects, it also considers [increasing the capacity](https://github.com/google/tcmalloc/blob/master/tcmalloc/cpu_cache.h) of the size-class. It can increase the capacity of the size-class up until the total memory (for all size-classes) that the cache could hold reaches the per-cpu limit or until the capacity of that size-class reaches the hard-coded size limit for that size-class. If the size-class has not reached the hard-coded limit, then in order to increase the capacity it can [steal](https://github.com/google/tcmalloc/blob/master/tcmalloc/cpu_cache.h) capacity from another size-class on the same CPU.

当某个大小类的对象耗尽时，会增大其容量；在申请更多对象时，也会考虑为该大小类扩容。扩容会一直进行，直到以下任一条件满足：

- 所有大小类可使用的总缓存内存达到 CPU 级限制
- 该大小类的容量达到其内置硬上限

如果该大小类还没达到硬上限，为了扩容，它可以从**同一 CPU 上的其他大小类 “借用” 容量**。

### Restartable Sequences and Per-CPU TCMalloc

To work correctly, per-CPU mode relies on restartable sequences (man rseq(2)). A restartable sequence is just a block of (assembly language) instructions, largely like a typical function. A restriction of restartable sequences is that they cannot write partial state to memory, the final instruction must be a single write of the updated state. The idea of restartable sequences is that if a thread is removed from a CPU (e.g. context switched) while it is executing a restartable sequence, the sequence will be restarted from the top. Hence the sequence will either complete without interruption, or be repeatedly restarted until it completes without interruption. This is achieved without using any locking or atomic instructions, thereby avoiding any contention in the sequence itself.

按 CPU 模式要实现正常工作，依赖于**可重启序列（restartable sequences）**（可参考 `man rseq(2)` 手册）。

可重启序列本质是一段汇编语言指令块，整体特性与普通函数大致相似，但有一项限制：它不能将 “部分状态” 写入内存，最后一条指令必须是对**更新后完整状态**的单次写入操作。

可重启序列的核心设计思路是：如果线程在执行该序列期间被移出 CPU（比如发生上下文切换），这个序列会**从头重新执行**。

因此，该序列要么无中断地执行完毕，要么被反复重启，直到无中断完成整个执行流程。

这一机制无需使用任何锁或原子指令即可实现，从而彻底避免了序列执行过程中出现的竞争问题。

The practical implication of this for TCMalloc is that the code can use a restartable sequence like [TcmallocSlab_Internal_Push](https://github.com/google/tcmalloc/blob/master/tcmalloc/internal/percpu_tcmalloc.h) to fetch from or return an element to a per-CPU array without needing locking. The restartable sequence ensures that either the array is updated without the thread being interrupted, or the sequence is restarted if the thread was interrupted (for example, by a context switch that enables a different thread to run on that CPU).

对 TCMalloc 来说，这一机制的实际价值在于：

代码可以通过 `TcmallocSlab_Internal_Push`（见[源码](https://github.com/google/tcmalloc/blob/master/tcmalloc/internal/percpu_tcmalloc.h)）这类可重启序列，从按 CPU 数组中取出元素、或向数组归还元素，且**完全无需加锁**。

可重启序列能保证两种结果：要么线程在无中断的情况下完成数组更新；要么若线程被中断（例如因上下文切换，导致其他线程在该 CPU 上运行），则重新执行整个序列。

Additional information about the design choices and implementation are discussed in a specific [design doc](https://google.github.io/tcmalloc/rseq.html) for it.

关于可重启序列的设计考量与实现细节，可参考专门的[设计文档](https://google.github.io/tcmalloc/rseq.html)。

### Legacy Per-Thread mode

In per-thread mode, TCMalloc assigns each thread a thread-local cache. Small allocations are satisfied from this thread-local cache. Objects are moved between the middle-end into and out of the thread-local cache as needed.

在线程本地缓存模式下，TCMalloc 会为每个线程分配一块**线程本地缓存（thread-local cache）**。小对象的内存分配直接从该线程本地缓存中满足，对象会根据需要在中端与线程本地缓存之间迁入或迁出。

A thread cache contains one singly linked list of free objects per size-class (so if there are N size-classes, there will be N corresponding linked lists), as shown in the following diagram.

每个线程缓存针对每种**大小类**，都维护一条空闲对象的单链表（若存在 N 个大小类，就对应 N 条链表），结构如下图所示：

![Structure of per-thread cache](https://google.github.io/tcmalloc/images/per-thread-structure.png)

On allocation an object is removed from the appropriate size-class of the per-thread caches. On deallocation, the object is prepended to the appropriate size-class. Underflow and overflow are handled by accessing the middle-end to either fetch more objects, or to return some objects.

分配内存时，会从线程本地缓存中对应大小类的链表取出对象；释放对象时，则将其插入对应大小类链表的头部。

当缓存不足（下溢）或缓存过多（上溢）时，会通过访问中端来补充更多对象，或归还部分对象。

The maximum capacity of the per-thread caches is set by the parameter `MallocExtension::SetMaxTotalThreadCacheBytes`. However it is possible for the total size to exceed that limit as each per-thread cache has a minimum size [KMinThreadCacheSize](https://github.com/google/tcmalloc/blob/master/tcmalloc/common.h) which is usually 512KiB. In the event that a thread wishes to increase its capacity, it needs to [scavenge](https://github.com/google/tcmalloc/blob/master/tcmalloc/thread_cache.cc) capacity from other threads.

线程本地缓存的总最大容量由参数 `MallocExtension::SetMaxTotalThreadCacheBytes` 设定。但总容量仍可能超出该限制，因为每个线程本地缓存都有一个最小容量 `KMinThreadCacheSize`（通常为 512KiB）。

当某个线程需要扩容时，需要从其他线程**回收**缓存容量。

When threads exit their cached memory is [returned](https://github.com/google/tcmalloc/blob/master/tcmalloc/thread_cache.cc) to the middle-end

线程退出时，其占用的缓存内存会归还给中端。

### Runtime Sizing of Front-end Caches

It is important for the size of the front-end cache free lists to adjust optimally. If the free list is too small, we’ll need to go to the central free list too often. If the free list is too big, we’ll waste memory as objects sit idle in there.

前端缓存空闲链表的大小进行**最优调整**至关重要。如果空闲链表过小，就会频繁需要访问中心空闲链表；如果空闲链表过大，对象会长期闲置其中，造成内存浪费。

Note that the caches are just as important for deallocation as they are for allocation. Without a cache, each deallocation would require moving the memory to the central free list.

需要注意的是，**缓存对内存释放和内存分配同样重要**。如果没有缓存，每次内存释放都需要将内存移回中心空闲链表。

Per-CPU and per-thread modes have different implementations of a dynamic cache sizing algorithm.

- In per-thread mode the maximum number of objects that can be stored is [increased](https://github.com/google/tcmalloc/blob/master/tcmalloc/thread_cache.cc) up to a limit whenever more objects need to be fetched from the middle-end. Similarly the capacity is [decreased](https://github.com/google/tcmalloc/blob/master/tcmalloc/thread_cache.cc) when we find that we have cached too many objects. The size of the cache is also [reduced](https://github.com/google/tcmalloc/blob/master/tcmalloc/thread_cache.cc) should the total size of the cached objects exceed the per-thread limit.
- In per-CPU mode the [capacity](https://github.com/google/tcmalloc/blob/master/tcmalloc/cpu_cache.h) of the free list is increased depending on whether we are alternating between underflows and overflows (indicating that a larger cache might stop this alternation). The capacity is [reduced](https://github.com/google/tcmalloc/blob/master/tcmalloc/cpu_cache.h) when it has not been grown for a time and may therefore be over capacity.

每 CPU 模式与每线程模式下，动态缓存大小调整算法的实现有所不同：

- **每线程模式**

  每当需要从中端获取更多对象时，可存储的对象最大数量会**上调**，直至达到上限。同理，当检测到缓存的对象过多时，容量会**下调**；若缓存对象的总大小超出每线程上限，缓存大小也会**缩减**。

- **每 CPU 模式**

  空闲链表的容量会根据是否在**下溢与上溢之间交替**（这意味着更大的缓存可能终止这种交替）来**上调**。若容量在一段时间内未增长，说明可能已超出合适大小，此时会**下调**容量。

## TCMalloc Middle-end

The middle-end is responsible for providing memory to the front-end and returning memory to the back-end. The middle-end comprises the Transfer cache and the Central free list. Although these are often referred to as singular, there is one transfer cache and one central free list per size-class. These caches are each protected by a mutex lock - so there is a serialization cost to accessing them.

中端负责向前端**供给内存**，并将内存**返还至后端**。中端由传输缓存（Transfer cache）和中心空闲链表（Central free list）组成 —— 尽管这两个组件常被以单数形式提及，但**每个尺寸类别（size-class）** 都对应一个独立的传输缓存和一个独立的中心空闲链表。这些缓存各自由一把互斥锁（mutex lock）保护，因此访问它们会产生**序列化开销**。

### Transfer Cache

When the front-end requests memory, or returns memory, it will reach out to the transfer cache.

当前端请求内存或归还内存时，会与**传输缓存**进行交互。

The transfer cache holds an array of pointers to free memory, and it is quick to move objects into this array, or fetch objects from this array on behalf of the front-end.

传输缓存维护一个指向空闲内存的指针数组，它能够快速地为前端将对象移入该数组，或从该数组中取出对象。

The transfer cache gets its name from situations where one CPU (or thread) is allocating memory that is deallocated by another CPU (or thread). The transfer cache allows memory to rapidly flow between two different CPUs (or threads).

传输缓存的命名源于这样一种场景：一个 CPU（或线程）分配的内存，由另一个 CPU（或线程）进行释放。传输缓存使得内存可以在不同的 CPU（或线程）之间**快速流转**。

If the transfer cache is unable to satisfy the memory request, or has insufficient space to hold the returned objects, it will access the central free list.

如果传输缓存无法满足内存请求，或没有足够空间存放归还的对象，它便会访问**中心空闲链表**。

### Central Free List

The central free list manages memory in “[spans](https://google.github.io/tcmalloc/design.html#spans)”, a span is a collection of one or more “[TCMalloc pages](https://google.github.io/tcmalloc/design.html#tcmalloc-page-sizes)” of memory. These terms will be explained in the next couple of sections.

中心空闲链表以 **跨度（span）**为单位管理内存，一个跨度由一块或多块**TCMalloc 页（TCMalloc page）** 内存组成。这些术语会在后续小节中详细说明。

A request for one or more objects is satisfied by the central free list by [extracting](https://github.com/google/tcmalloc/blob/master/tcmalloc/central_freelist.cc) objects from spans until the request is satisfied. If there are insufficient available objects in the spans, more spans are requested from the back-end.

中心空闲链表通过从跨度中**提取**对象来满足单个或多个对象的内存申请，直至请求被满足。若跨度中的可用对象不足，便会向**后端**申请更多跨度。

When objects are [returned to the central free list](https://github.com/google/tcmalloc/blob/master/tcmalloc/central_freelist.cc), each object is mapped to the span to which it belongs (using the [pagemap](https://google.github.io/tcmalloc/design.html#pagemap-and-spans)) and then released into that span. If all the objects that reside in a particular span are returned to it, the entire span gets returned to the back-end.

当对象被**归还至中心空闲链表**时，系统会借助 **页映射表（pagemap）** 将每个对象映射到其所属的跨度中，再将对象释放到该跨度内。若某个跨度中的所有对象都已全部归还，该跨度整体会被返还给后端。

### Pagemap and Spans

The heap managed by TCMalloc is divided into [pages](https://google.github.io/tcmalloc/design.html#pagesize) of a compile-time determined size. A run of contiguous pages is represented by a `Span` object. A span can be used to manage a large object that has been handed off to the application, or a run of pages that have been split up into a sequence of small objects. If the span manages small objects, the size-class of the objects is recorded in the span.

TCMalloc 管理的堆会被划分为**页（page）**，页的大小在编译时确定。一段连续的页由一个跨度（Span）对象表示。

一个跨度既可以用于管理交付给应用程序的大对象，也可以管理被分割成一系列小对象的连续页。如果跨度用于管理小对象，会在跨度中记录这些对象所属的尺寸类别（size-class）。

The pagemap is used to look up the span to which an object belongs, or to identify the size-class for a given object.

**页映射表（pagemap）** 用于查询对象所属的跨度，或确定指定对象对应的尺寸类别。

TCMalloc uses a 2-level or 3-level [radix tree](https://github.com/google/tcmalloc/blob/master/tcmalloc/pagemap.h) （基数树，一种压缩字典树）in order to map all possible memory locations onto spans.

TCMalloc 采用**二级或三级基数树（radix tree）**，将所有可能的内存地址映射到对应的跨度上。

The following diagram shows how a radix-2 pagemap is used to map the address of objects onto the spans that control the pages where the objects reside. In the diagram **span A** covers two pages, and **span B** covers 3 pages.

下图展示了二级基数树结构的页映射表，如何将对象地址映射到管控其所在内存页的跨度上。图中**跨度 A** 覆盖 2 个页，**跨度 B** 覆盖 3 个页。

![The pagemap maps objects to spans.](https://google.github.io/tcmalloc/images/pagemap.png)

Spans are used in the middle-end to determine where to place returned objects, and in the back-end to manage the handling of page ranges.

跨度在**中端**用于确定归还对象的存放位置，在**后端**用于管理内存页范围的调度。

### Storing Small Objects in Spans

A span contains a pointer to the base of the TCMalloc pages that the span controls. For small objects those pages are divided into at most 216 objects. This value is selected so that within the span we can refer to objects by a two-byte index.

一个跨度（Span）包含一个指针，指向它所管控的 TCMalloc 内存页的起始地址。

对于小对象，这些页会被分割成最多 **2¹⁶（65536）个对象**。选择该数值是为了让跨度内部可以用两字节索引来引用对象。

This means that we can use an [unrolled linked list](https://en.wikipedia.org/wiki/Unrolled_linked_list) to hold the objects. For example, if we have eight byte objects we can store the indexes of three ready-to-use objects, and use the forth slot to store the index of the next object in the chain. This data structure reduces cache misses over a fully linked list.

这意味着我们可以使用展开链表（unrolled linked list）来存放这些对象。

例如，若对象大小为 8 字节，我们可以存储 3 个可直接使用的对象索引，并利用第 4 个位置存储链表中下一个对象的索引。

相比于普通链表，这种数据结构能减少缓存不命中。

The other advantage of using two byte indexes is that we’re able to use spare capacity in the span itself to [cache four objects](https://github.com/google/tcmalloc/blob/master/tcmalloc/span.h).

使用两字节索引的另一个好处是：可以利用跨度自身的富余空间，**缓存 4 个对象**。

When we have [no available objects](https://github.com/google/tcmalloc/blob/master/tcmalloc/central_freelist.cc) for a size-class, we need to fetch a new span from the pageheap and [populate](https://github.com/google/tcmalloc/blob/master/tcmalloc/central_freelist.cc) it.

当某个尺寸类别（size-class）**没有可用对象**时，需要从**页堆（pageheap)**中获取一个新的跨度，并对其进行**初始化填充**。

## TCMalloc Page Sizes

TCMalloc can be built with various [“page sizes”](https://github.com/google/tcmalloc/blob/master/tcmalloc/common.h) . Note that these do not correspond to the page size used in the TLB of the underlying hardware. These TCMalloc page sizes are currently 4KiB, 8KiB, 32KiB, and 256KiB.

TCMalloc 可以使用多种**页大小**进行编译构建。注意，这些页大小与底层硬件 TLB 中使用的页大小**并不对应**。目前 TCMalloc 支持的页大小包括：4KiB、8KiB、32KiB 和 256KiB。

A TCMalloc page either holds multiple objects of a particular size, or is used as part of a group to hold an object of size greater than a single page. If an entire page becomes free it will be returned to the back-end (the pageheap) and can later be repurposed to hold objects of a different size (or returned to the OS).

一块 TCMalloc 页要么存放**多个特定大小的对象**，要么与其他页组成一组，用于存放**大于单页大小**的对象。当一整页变为空闲时，它会被归还给**后端（页堆）**，之后可以重新用于存放其他大小的对象（或归还给操作系统）。

Small pages are better able to handle the memory requirements of the application with less overhead. For example, a half-used 4KiB page will have 2KiB left over versus a 32KiB page which would have 16KiB. Small pages are also more likely to become free. For example, a 4KiB page can hold eight 512-byte objects versus 64 objects on a 32KiB page; and there is much less chance of 64 objects being free at the same time than there is of eight becoming free.

**小页**能以更低的开销更好地满足应用程序的内存需求。例如，使用一半的 4KiB 页只会剩余 2KiB 空间，而 32KiB 页则会剩余 16KiB。

小页也更容易整体变为空闲：比如 4KiB 页可以存放 8 个 512 字节的对象，而 32KiB 页可存放 64 个；64 个对象同时被释放的概率，远低于 8 个对象同时被释放的概率。

Large pages result in less need to fetch and return memory from the back-end. A single 32KiB page can hold eight times the objects of a 4KiB page, and this can result in the costs of managing the larger pages being smaller. It also takes fewer large pages to map the entire virtual address space. TCMalloc has a [pagemap](https://github.com/google/tcmalloc/blob/master/tcmalloc/pagemap.h) which maps a virtual address onto the structures that manage the objects in that address range. Larger pages mean that the pagemap needs fewer entries and is therefore smaller.

**大页**则能减少向后端申请和归还内存的次数。

单个 32KiB 页能存放的对象数量是 4KiB 页的 8 倍，这可以降低大页本身的管理开销。同时，映射整个虚拟地址空间所需的大页数量也更少。

TCMalloc 中有一个**页映射表（pagemap）**，用于将虚拟地址映射到管理该地址范围对象的数据结构。**更大的页意味着页映射表所需的表项更少，体积也更小。**

Consequently, it makes sense for applications with small memory footprints, or that are sensitive to memory footprint size to use smaller TCMalloc page sizes. Applications with large memory footprints are likely to benefit from larger TCMalloc page sizes.

因此，**内存占用小**或对**内存 footprint 敏感**的应用，适合使用较小的 TCMalloc 页大小；**内存占用大**的应用，则更适合使用较大的 TCMalloc 页大小。

## TCMalloc Backend

The back-end of TCMalloc has three jobs:

- It manages large chunks of unused memory.
- It is responsible for fetching memory from the OS when there is no suitably sized memory available to fulfill an allocation request.
- It is responsible for returning unneeded memory back to the OS.

TCMalloc 的后端主要承担**三项工作**：

- 管理**大块未使用内存**。
- 当无合适大小的内存可满足分配请求时，负责从**操作系统**申请内存。
- 负责将不再需要的内存**归还给操作系统**。

There are two backends for TCMalloc:

- The Legacy pageheap which manages memory in TCMalloc page sized chunks.
- The hugepage aware pageheap which manages memory in chunks of hugepage sizes. Managing memory in hugepage chunks enables the allocator to improve application performance by reducing TLB misses.

TCMalloc 提供**两种后端实现**：

- **传统页堆（Legacy pageheap）**：以 TCMalloc 页大小为单位管理内存。
- **支持大页的页堆（hugepage-aware pageheap）**：以大页大小为单位管理内存。以大页块管理内存可减少 **TLB 不命中**，从而提升应用程序性能。

### Legacy Pageheap

The legacy pageheap is an array of free lists for particular lengths of contiguous pages of available memory. For `k < 256`, the `k`th entry is a free list of runs that consist of `k` TCMalloc pages. The `256`th entry is a free list of runs that have length `>= 256` pages:

**传统页堆（legacy pageheap）** 是一个**空闲链表数组**，每个链表对应特定长度的连续可用内存页。

对于 `k < 256`，第 `k` 个表项对应由 **`k` 个 TCMalloc 页**组成的内存段的空闲链表；第 256 个表项则对应长度 **≥ 256 页**的内存段空闲链表：

![Layout of legacy pageheap.](https://google.github.io/tcmalloc/images/legacy_pageheap.png)

An allocation for `k` pages is satisfied by looking in the `k`th free list. If that free list is empty, we look in the next free list, and so forth. Eventually, we look in the last free list if necessary. If that fails, we fetch memory from the system `mmap`.

申请 `k` 个页的分配请求时，会先查找第 `k` 个空闲链表。若该链表为空，则依次查找下一个空闲链表，必要时最终会查找最后一个空闲链表。若仍无法满足，则通过系统的 `mmap` 向操作系统申请内存。

If an allocation for `k` pages is satisfied by a run of pages of length `> k` , the remainder of the run is re-inserted back into the appropriate free list in the pageheap.

如果用**长度大于 k**的内存段满足了 k 个页的分配需求，该段剩余的内存会重新插回页堆中对应的空闲链表。

When a range of pages are returned to the pageheap, the adjacent pages are checked to determine if they now form a contiguous region, if that is the case then the pages are concatenated and placed into the appropriate free list.

当一段内存页归还给页堆时，会检查其**相邻页**是否已形成连续区域；若是，则将这些页**合并**，并放入对应的空闲链表中。

### Hugepage Aware Allocator

The objective of the hugepage aware allocator is to hold memory in hugepage size chunks. On x86 a hugepage is 2MiB in size. To do this the back-end has three different caches:

- The filler cache holds hugepages which have had some memory allocated from them. This can be considered to be similar to the legacy pageheap in that it holds linked lists of memory of a particular number of TCMalloc pages. Allocation requests for sizes of less than a hugepage in size are (typically) returned from the filler cache. If the filler cache does not have sufficient available memory it will request additional hugepages from which to allocate.
- The region cache which handles allocations of greater than a hugepage. This cache allows allocations to straddle multiple hugepages, and packs multiple such allocations into a contiguous region. This is particularly useful for allocations that slightly exceed the size of a hugepage (for example, 2.1 MiB).
- The hugepage cache handles large allocations of at least a hugepage. There is overlap in usage with the region cache, but the region cache is only enabled when it is determined (at runtime) that the allocation pattern would benefit from it.

**支持大页的分配器（hugepage-aware allocator）** 的设计目标，是以**大页大小**的内存块来管理内存。在 x86 架构下，一个大页的大小为 2MiB。

为此，该后端提供了三种不同的缓存：

- **填充缓存（filler cache）** 存放已分配出部分内存的大页。其作用可类比传统页堆，内部同样维护着对应特定数量 TCMalloc 页的内存链表。**小于一个大页**的分配请求（通常）会从该缓存中分配。若填充缓存无足够可用内存，便会申请新的大页来满足分配。
- **区域缓存（region cache）** 负责处理**大于一个大页**的分配请求。该缓存支持分配操作**跨多个大页**，并将多个此类分配紧凑排布在连续区域内，对大小略超大页的分配（如 2.1MiB）尤为适用。
- **大页缓存（hugepage cache）** 负责处理**不小于一个大页**的大型分配。其使用场景与区域缓存存在重叠，但区域缓存仅会在**运行时判定**分配模式能从中获益时才启用。

Additional information about the design choices made in HPAA are discussed in a specific [design doc](https://google.github.io/tcmalloc/temeraire.html) for it.

有关 HPAA（支持大页的分配器）设计选型的更多细节，可查阅其专属**设计文档**。

## Caveats

TCMalloc will reserve some memory for metadata at start up. The amount of metadata will grow as the heap grows. In particular the pagemap will grow with the virtual address range that TCMalloc uses, and the spans will grow as the number of active pages of memory grows. In per-CPU mode, TCMalloc will reserve a slab of memory per-CPU (typically 256 KiB), which, on systems with large numbers of logical CPUs, can lead to a multi-mebibyte footprint.

TCMalloc 会在启动时为 **元数据（metadata）** 预留一部分内存。元数据的占用量会随着堆的增长而增加。

具体来说，**页映射表（pagemap）** 会随 TCMalloc 使用的虚拟地址范围扩大而增长，跨度（Span）的数量则会随活跃内存页的数量增加而增长。在每 CPU 模式下，TCMalloc 会为每个 CPU 预留一块内存（通常为 256 KiB），在拥有大量逻辑 CPU 的系统上，这会带来数 MiB 级的内存占用。

It is worth noting that TCMalloc requests memory from the OS in large chunks (typically 1 GiB regions). The address space is reserved, but not backed by physical memory until it is used. Because of this approach the VSS of the application can be substantially larger than the RSS. A side effect of this is that trying to limit an application’s memory use by restricting VSS will fail long before the application has used that much physical memory.

值得注意的是，TCMalloc 会以**大块**的形式向操作系统申请内存（通常为 1 GiB 的连续区域）。它会先预留地址空间，但在实际使用前不会分配物理内存。

这种机制会使得应用程序的**虚拟内存大小（VSS）**远大于**常驻内存大小（RSS）**。

其副作用是：若试图通过限制 VSS 来管控应用内存，会远早于应用实际消耗对应物理内存时就触发限制。

Don’t try to load TCMalloc into a running binary (e.g., using JNI in Java programs). The binary will have allocated some objects using the system malloc, and may try to pass them to TCMalloc for deallocation. TCMalloc will not be able to handle such objects.

**不要**尝试将 TCMalloc 加载到正在运行的二进制程序中（例如在 Java 程序中通过 JNI 使用）。

程序已通过系统 `malloc` 分配了部分对象，若将这些对象交给 TCMalloc 释放，TCMalloc 无法处理此类对象。

This site is open source. [Improve this page](https://github.com/google/tcmalloc/edit/master/docs/design.md).