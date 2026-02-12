## 09 An Introduction to Kernel Synchronization

In a shared memory application, developers must ensure that sharedresources are pro-tected from concurrent access.The kernel is no exception.Shared resources require pro-tection from concurrent access because ifmultiple threads of execution1 access and manipulate the data at the sametime, the threads may overwrite each other’s changes or access data while itis in an inconsistent state. Concurrent access of shared data is a recipe forinstability that often proves hard to track down and debug—getting it rightat the start is important.

在共享内存应用程序中，开发人员必须确保共享资源受到保护，避免并发访问。内核也不例外。共享资源需要防范并发访问，因为如果多个执行线程同时访问并操作数据，线程可能会相互覆盖修改内容，或是在数据处于不一致状态时对其进行访问。共享数据的并发访问是引发系统不稳定的根源，这类问题往往难以排查和调试 —— 从一开始就做好防护至关重要。

Properly protecting shared resources can be tough.Years ago, before Linuxsupported symmetrical multiprocessing, preventing concurrent access of data wassimple. Because only a single processor was supported, the only way datacould be concurrently accessed was if an interrupt occurred or if kernel codeexplicitly rescheduled and enabled another task to run.With earlier kernels,development was simple.

妥善保护共享资源并非易事。多年前，在 Linux 尚未支持对称多处理时，防止数据并发访问十分简单。由于系统仅支持单处理器，数据出现并发访问的唯一场景，只有发生中断，或是内核代码主动调度并允许其他任务运行时。在早期内核版本中，开发工作相对简单。

Those halcyon days are over. Symmetrical multiprocessing support wasintroduced in the 2.0 kernel and has been continually enhanced ever since. Multiprocessingsupport implies that kernel code can simultaneously run on two or moreprocessors. Conse-quently, without protection, code in the kernel, runningon two different processors, can simultaneously access shared data at exactly the same time.With the introduction of the 2.6 kernel, the Linux kernel is preemptive.This implies that (again, in the absence of pro-tection)the scheduler can preempt kernel code at virtually any point and reschedule another task.Today, a number of scenarios enable for concurrency inside the kernel, and they all require protection.

这样的轻松时期已然过去。Linux 2.0 内核引入了对称多处理支持，此后该特性不断得到完善。多处理支持意味着内核代码可以在两个或多个处理器上同时运行。因此，若缺乏保护机制，运行在不同处理器上的内核代码，可能会在同一时刻同时访问共享数据。而 2.6 内核的推出，让 Linux 内核成为可抢占式内核。这意味着（同样在无保护的情况下）调度器几乎可以在任意时刻抢占内核代码，并调度其他任务运行。如今，内核内部存在多种会引发并发的场景，这些场景都需要进行防护。

This chapter discusses the issues of concurrency and synchronization in theabstract, as they exist in any operating system kernel.The next chapterdetails the specific mecha-nisms and interfaces that the Linux kernelprovides to solve synchronization issues and prevent race conditions.

本章从抽象层面探讨任意操作系统内核中都存在的并发与同步问题。下一章将详细介绍 Linux 内核为解决同步问题、避免竞态条件所提供的具体机制与接口。

### Critical Regions and Race Conditions

**临界区与竞态条件**

Code paths that access andmanipulate shared data are called critical regions (also called criticalsections). It is usually unsafe for multiple threads of execution to access thesame resource simultaneously.To prevent concurrent access during criticalregions, the pro-grammer must ensure that code executes **atomically**—that is, operations complete without interruption as if the entire critical regionwere one indivisible instruction. It is a bug if it is possible for two threads ofexecution to be simultaneously executing within the same criticalregion.When this does occur, we call it a race condition, so-named becausethe threads raced to get there first. Note how rare a race condition in yourcode might mani-fest itself—debugging race conditions is often difficultbecause they are not easily repro-ducible. Ensuring that unsafe concurrencyis prevented and that race conditions do not occur is called **synchronization**.

访问并操作共享数据的代码路径被称为**临界区**（也称作临界段）。多个执行线程同时访问同一资源，通常是不安全的。为了防止临界区内的并发访问，程序员必须保证代码**原子执行**—— 即操作能不间断地完成，仿佛整个临界区是一条不可分割的指令。如果两个执行线程有可能同时进入同一个临界区执行，这就是一个程序错误。这种情况发生时，我们称之为**竞态条件**，这个名字源于多个线程在 “争抢” 优先进入临界区的执行权。需要注意的是，代码中的竞态条件可能极少显现 —— 调试竞态条件往往十分困难，因为它们很难复现。确保规避不安全的并发、避免竞态条件发生的过程，被称为**同步**。

### Locking

A lock provides such a mechanism; it works much like a lock on a door. Imagine the room beyond the door as the critical region. Inside the room, only one thread of execu    tion can be present at a given time.When a thread enters the room, it locks the doorbehind it.When the thread is finished manipulating the shared data, it leaves the roomand unlocks the door. If another thread reaches the door while it is locked, it must waitfor the thread inside to exit the room and unlock the door before it can enter.Threadshold locks; locks protect data.

锁正是实现这一目标的机制，它的工作原理和门上的锁十分相似。可以把门后的空间想象成临界区，同一时间内，只能有一个执行线程处于该空间中。当一个线程进入该空间时，会在身后锁上门；当线程完成对共享数据的操作后，便离开空间并解锁。如果另一个线程到达时门已上锁，就必须等待内部线程退出并解锁后，才能进入。**线程持有锁，锁保护数据**。

Locks come in various shapes and sizes—Linux alone implements a handful of differ-ent locking mechanisms.The most significant difference between the variousmechanisms is the behavior when the lock is unavailable because another thread alreadyholds it— some lock variants busy wait,2 whereas other locks put the current task tosleep until the lock becomes available.The next chapter discusses the behavior of thedifferent locks in Linux and their interfaces.

锁的形式和种类繁多 —— 仅 Linux 内核就实现了多种不同的锁机制。各类锁机制最核心的区别，在于锁已被其他线程持有而不可用时的处理行为：部分锁会采用**忙等待**，而另一些锁则会将当前任务挂起，直到锁可用为止。下一章会详细介绍 Linux 中各类锁的行为特性及其调用接口。

Astute readers are now screaming.The lock does not solve the problem; it simply shrinks the critical region down to just the lock and unlock code: probably much smaller,sure, but still a potential race! Fortunately, locks are implemented using atomicoperations that ensure no race exists.A single instruction can verify whether the key istaken and, if not, seize it. How this is done is architecture-specific, but almost allprocessors implement an atomic test and set instruction that tests the value of aninteger and sets it to a new value only if it is zero.A value of zero means unlocked. Onthe popular x86 architecture, locks are implemented using such a similar instructioncalled compare and exchange.

敏锐的读者此刻可能会提出疑问：锁本身并没有解决根本问题，它只是将临界区缩小到了加锁和解锁的代码段 —— 尽管范围小了很多，但依旧存在潜在的竞态！所幸的是，锁是通过**原子操作**实现的，这从根本上杜绝了竞态的产生。单条指令即可完成锁状态的检查：若未被占用，则立即获取锁。锁的具体实现与硬件架构相关，但几乎所有处理器都提供了**测试并设置**的原子指令，该指令会检查一个整型变量的值，仅当其为 0（代表未上锁）时，才将其设置为新值。在主流的 x86 架构中，锁则是通过一条名为**比较并交换**的同类指令实现的。

#### Causes of Concurrency

In user-space, the need for synchronization stems from the factthat programs are sched-uled preemptively at the will of the scheduler. Because aprocess can be preempted at any time and another process can be scheduled onto theprocessor, a process can be involun-tarily preempted in the middle of accessing acritical region. If the newly scheduled process then enters the same critical region (say,if the two processes manipulate the same shared memory or write to the same filedescriptor), a race can occur.The same problem can occur with multiple single-threadedprocesses sharing files, or within a single program with signals, because signals canoccur asynchronously.This type of concurrency—in which two things do not actuallyhappen at the same time but interleave with each other such that they might as well—iscalled pseudo-concurrency.

在用户空间中，对同步的需求源于程序会按照调度器的意愿被**抢占式调度**。因为进程随时可能被抢占，另一个进程会被调度到处理器上运行，进程就可能在访问临界区的过程中被强制抢占。如果新调度的进程随后进入同一个临界区（比如两个进程操作同一段共享内存，或向同一个文件描述符写入），就会产生竞态。多个单线程进程共享文件，或是单个程序中处理信号时，也会出现同样的问题 —— 因为信号是异步触发的。这种并发形式下，两个操作并非真正同时发生，而是执行流程相互交错，效果等同于同时执行，被称为**伪并发**。

If you have a symmetrical multiprocessing machine, two processes can actually be exe-cuted in a critical region at the exact same time.That is called true concurrency.Although the causes and semantics of true versus pseudo concurrency aredifferent, they both result in the same race conditions and require the same sort of protection.

如果是对称多处理机器，两个进程则可能**真正同时**在临界区内执行，这被称为**真并发**。尽管真并发与伪并发的产生原因和语义不同，但二者都会引发相同的竞态条件，也需要采用同类的保护机制。

The kernel has similar causes of concurrency:

-  Interrupts— An interrupt can occur asynchronously at almost any time, inter-ruptingthe currently executing code.
- Softirqs and tasklets— The kernel can raise or schedule a softirq or tasklet at almost any time, interrupting the currently executing code.
- Kernel preemption— Because the kernel is preemptive, one task in the kernel can preempt another.
- Sleeping and synchronization with user-space— A task in the kernel can sleep and thus invoke the scheduler, resulting in the running of a new process.
- Symmetrical multiprocessing— Two or more processors can execute kernel code at exactly the same time.

内核中产生并发的诱因与之类似：

- 中断 —— 中断几乎可以在任意时刻异步触发，中断当前正在执行的代码。
- 软中断与 tasklet—— 内核几乎可以在任意时刻触发或调度软中断、tasklet，中断当前执行的代码。
- 内核抢占 —— 由于内核支持抢占，内核中的一个任务可以抢占另一个任务。
- 睡眠及与用户空间的同步 —— 内核中的任务可以睡眠，进而触发调度器，使得新进程得以运行。
- 对称多处理 —— 两个或多个处理器可以**同时**执行内核代码。

Kernel developers need to understand and prepare for these causes of concurrency. It isa major bug if an interrupt occurs in the middle of code that is manipulating a resourceand the interrupt handler can access the same resource. Similarly, it is a bug if kernelcode is preemptive while it is accessing a shared resource. Likewise, it is a bug if codein the kernel sleeps while in the middle of a critical section. Finally, two processorsshould never simultaneously access the same piece of data.With a clear picture of whatdata needs pro-tection, it is not hard to provide the locking to keep the system stable.Rather, the hard part is identifying these conditions and realizing that to preventconcurrency, you need some form of protection. 

内核开发者需要理解这些并发产生的原因并做好应对准备。如果一段代码在操作某资源的过程中触发了中断，且中断处理程序又能访问同一资源，这就是一个严重的程序错误。同理，内核代码在访问共享资源时若可被抢占，属于程序错误；内核代码在临界区执行过程中进入睡眠，同样是程序错误。最后，两个处理器绝不能同时访问同一块数据。只要清晰明确哪些数据需要保护，添加锁机制来保障系统稳定就并非难事。真正的难点在于识别这些并发场景，并意识到需要借助某种保护机制来规避并发问题。

Let us reiterate this point, because it is important. Implementing the actual locking in your code to protect shared data is not difficult, especially when done early on during the design phase of development.The tricky part is identifying the actual shared data and the corresponding critical sections.This is why designing locking into your code from the get-go, and not as an afterthought, is of paramount importance. It can be difficult to go in, ex post, and identify critical regions and retrofit locking into the existing code.Theresulting code is often not pretty, either.The takeaway from this is to always designproper locking into your code from the beginning.

我们再次强调这一点，因为它至关重要。在代码中实现具体的锁机制来保护共享数据并不困难，尤其是在开发的设计阶段就提前完成。真正棘手的是识别出实际的共享数据以及对应的临界区。这就是为什么从一开始就将锁机制融入代码设计，而非事后补救，是重中之重。事后再去梳理、识别临界区，并将锁机制改造进现有代码，难度极大，最终的代码实现往往也十分混乱。由此得出的核心结论是：永远要从开发初期，就为代码设计好完善的锁机制。

Code that is safe from concurrent access from an interrupt handler is said to be **interrupt-safe**. Code that is safe from concurrency on symmetrical multiprocessingmachines is **SMP-safe**. Code that is safe from concurrency with kernel preemption is **preempt-safe**.3 The actual mechanisms used to provide synchronization and protectagainst race conditions in all these cases is covered in the next chapter.

能够安全应对中断处理程序并发访问的代码，被称为**中断安全**代码。在对称多处理架构上可安全应对并发的代码，称为**SMP 安全**代码。能够抵御内核抢占引发并发问题的代码，称为**抢占安全**代码。下一章会详细介绍，在所有这些场景中用于实现同步、防范竞态条件的具体机制。

#### Knowing What to Protect

Identifying what data specifically needs protection is vital.Because any data that can be accessed concurrently almost assuredly needs protection,it is often easier to identify what data does not need protection and work from there.Obviously, any data that is local to one particular thread of execution does not needprotection, because only that thread can access the data. For example, local automaticvariables (and dynamically allocated data structures whose address is stored only on the        stack) do not need any sort of locking because they exist solely on the stack of theexecuting thread. Likewise, data that is accessed by only a specific task does notrequire locking (because a process can execute on only one processor at a time).

明确具体需要保护哪些数据至关重要。由于任何可被**并发访问**的数据几乎都必然需要保护，因此通常更简便的做法是：先找出**不需要保护**的数据，再以此为基础展开分析。

显然，仅隶属于某一特定**执行线程**的本地数据无需保护，因为只有该线程能访问这些数据。例如，局部自动变量（以及地址仅存储在栈上的动态分配数据结构）无需任何形式的加锁，因为它们仅存在于当前执行线程的栈中。同理，仅由特定任务访问的数据也不需要加锁（因为一个进程同一时间只能在一个处理器上执行）。

What does need locking? Most global kernel data structures do.A good rule of thumb is that if another thread of execution can access the data, the data needs some sort oflocking; if anyone else can see it, lock it. Remember to lock data, not code.

那什么数据需要加锁？绝大多数**全局内核数据结构**都需要。一个实用的经验法则是：

**只要其他执行线程能够访问该数据，该数据就需要某种形式的加锁；只要数据能被其他实体访问，就必须加锁。**

切记：要保护的是**数据**，而非代码。

Whenever you write kernel code, you should ask yourself these questions:

- Is the data global? Can a thread of execution other than the current one access it?
-  Is the data shared between process context and interrupt context? Is it shared between two different interrupt handlers?
-  If a process is preempted while accessing this data, can the newly scheduled process access the same data?
- Can the current process sleep (block) on anything? If it does, in what state does that leave any shared data?
- What prevents the data from being freed out from under me?
- What happens if this function is called again on another processor?
- Given the proceeding points, how am I going to ensure that my code is safe from concurrency?

编写内核代码时，你应当自问以下问题：

- 该数据是否为全局数据？除当前执行线程外，其他执行线程能否访问它？
- 该数据是否在**进程上下文**与**中断上下文**之间共享？是否在两个不同的中断处理程序之间共享？
- 若进程在访问该数据时被**抢占**，新调度的进程能否访问同一数据？
- 当前进程是否会因任何原因睡眠（阻塞）？若发生睡眠，会使共享数据处于何种状态？
- 有什么机制能防止数据在使用过程中被释放？
- 若该函数在另一个处理器上被再次调用，会发生什么？
- 结合以上几点，我该如何确保代码在并发场景下的安全性？

In short, nearly all global and shared data in the kernel requires some form of the synchronization methods, discussed in the next chapter.

简而言之，内核中几乎所有全局数据和共享数据，都需要采用下一章将要讨论的某种**同步机制**来保护。

### Deadlocks

A deadlock is a condition involving one or more threads of execution and one or more resources, such that each thread waits for one of the resources, but all theresources are already held.The threads all wait for each other, but they never make anyprogress toward releasing the resources that they already hold.Therefore, none of thethreads can con-tinue, which results in a deadlock.

死锁是一种涉及一个或多个执行线程与一个或多个资源的状态：每个线程都在等待某一资源，但所有相关资源均已被占用。这些线程相互等待，却始终不会释放自己已持有的资源，因此没有任何线程能够继续执行，最终导致死锁。

The simplest example of a deadlock is the self-deadlock:4 If a thread of execution attempts to acquire a lock it already holds, it has to wait for the lock to be released. Butit will never release the lock, because it is busy waiting for the lock, and the result isdeadlock:

最简单的死锁案例是**自死锁**：若一个执行线程试图获取它已持有的锁，就必须等待该锁被释放；但该线程永远不会释放这个锁 —— 因为它正忙于等待锁的释放，最终形成死锁：

acquire lock acquire lock, again wait for lock to become available ...

Similarly, consider n threads and n locks. If each thread holds a lock that the other thread wants, all threads block while waiting for their respective locks to become avail-able.The most common example is with two threads and two locks, which is often calledthe deadly embrace or the ABBA deadlock.

类似地，考虑 n 个线程与 n 把锁的场景：如果每个线程都持有另一个线程想要的锁，那么所有线程都会因等待各自需要的锁而阻塞。最常见的情况是两个线程、两把锁的场景，这通常被称为**致命拥抱（deadly embrace）** 或 **ABBA 死锁**。

Each thread is waiting for the other, and neither thread will ever release its original lock; therefore, neither lock will become available.

每个线程都在等待对方释放锁，而两者都不会释放自己最初持有的锁；因此，两把锁永远都不会变为可用状态。

Prevention of deadlock scenarios is important.Although it is difficult to prove that code is free of deadlocks, you *can* write deadlock-free code.A few simple rules go a long way:

- Implement lock ordering. Nested locks must *always* be obtained in the same order. This prevents the deadly embrace deadlock. Document the lock ordering so others will follow it.
-  Prevent starvation.Ask yourself,*does this code always finish? If* foo *does not occur,will* bar *wait forever?*
- Do not double acquire the same lock.
- Design for simplicity. Complexity in your locking scheme invites deadlocks.

预防死锁场景至关重要。尽管很难证明一段代码完全无死锁，但你**确实可以**编写无死锁的代码。遵循以下几条简单规则能起到显著作用：

1. 实现**锁排序**：嵌套获取锁时，**必须始终**按照相同的顺序获取。这能防止 “致命拥抱” 型死锁。务必记录锁的排序规则，以便其他人遵循。
2. 防止**线程饥饿**：自问：这段代码是否总能执行完毕？如果某个条件（foo）未满足，另一个操作（bar）是否会无限等待？
3. 不要重复获取同一把锁。
4. 设计力求简洁：锁机制的复杂度越高，越容易引发死锁。

The first point is most important and worth stressing. If two or more locks are  acquired at the same time, they must always be acquired in the same order. Let’sassume you have the cat, dog, and fox locks that protect data structures of the samename. Now assume you have a function that needs to work on all three of these datastructures simul-taneously—perhaps to copy data between them.Whatever the case, thedata structures require locking to ensure safe access. If one function acquires the locksin the order cat, dog, and then fox, then every other function must obtain these locks (ora subset of them) in this same order. For example, it is a potential deadlock (and hencea bug) to first obtain the fox lock and then obtain the dog lock because the dog lockmust always be acquired prior to the fox lock.

第一点最为重要，值得着重强调。如果需要同时获取两把或更多锁，**必须始终按照固定的顺序来获取**。

假设你有 `cat`、`dog`、`fox` 三把锁，分别用于保护同名的数据结构。现在假设有一个函数需要同时操作这三个数据结构 —— 比如在它们之间拷贝数据。无论何种场景，这些数据结构都需要加锁以保证安全访问。

如果某个函数按照 **cat → dog → fox** 的顺序获取锁，那么**其他所有函数**在获取这些锁（或其中一部分锁）时，都必须严格遵循这个顺序。

例如，先获取 `fox` 锁、再获取 `dog` 锁的写法，就存在**潜在死锁风险**（属于程序缺陷），因为 `dog` 锁必须始终在 `fox` 锁之前获取。

The order of unlock does not matter with respect to deadlock, although it is common practice to release the locks in an order inverse to that in which they were acquired.

就死锁而言，**解锁的顺序并不重要**；不过按照与加锁相反的顺序释放锁，是常见的工程实践。

Preventing deadlocks is important.The Linux kernel has some basic debugging facili-ties for detecting deadlock scenarios in a running kernel.These features are discussedin the next chapter.

死锁的预防至关重要。Linux 内核提供了一些基础调试工具，用于检测运行中内核的死锁场景。这些特性将在下一章详细介绍。

### Contention and Scalability

The term lock contention, or simply contention, describes alock currently in use but that another thread is trying to acquire.A lock that is highlycontended often has threads waiting to acquire it. High contention can occur because alock is frequently obtained, held for a long time after it is obtained, or both. Because alock’s job is to serialize access to a resource, it comes as no surprise that locks canslow down a system’s performance.A highly contended lock can become a bottleneck inthe system, quickly limiting its per-formance. Of course, the locks are also required toprevent the system from tearing itself to shreds, so a solution to high contention mustcontinue to provide the necessary concurrency protection.

**锁竞争（lock contention）**，简称**竞争**，是指一把锁当前已被占用，但其他线程仍在尝试获取该锁的状态。竞争激烈的锁通常会有大量线程排队等待获取。

高竞争的出现，可能是因为锁被频繁申请、持有时间过长，或是两种情况同时存在。

锁的作用是对资源访问进行**串行化**，因此锁会降低系统性能并不奇怪。竞争激烈的锁会成为系统瓶颈，迅速限制整体性能。当然，锁又是保证系统稳定运行不可或缺的机制，因此在解决高竞争问题时，必须继续提供必要的并发保护。

Scalability is a measurement of how well a system can be expanded. In operating sys-tems, we talk of the scalability with a large number of processes, a large number ofprocessors, or large amounts of memory.We can discuss scalability in relation tovirtually any component of a computer to which we can attach a quantity. Ideally,doubling the number of processors should result in a doubling of the system’sprocessor performance. This, of course, is never the case.

**可扩展性（scalability）** 是衡量系统扩展能力的指标。在操作系统中，我们通常关注系统在大量进程、大量处理器或大容量内存场景下的可扩展性。几乎计算机中所有可量化的组件，都可以讨论其可扩展性。

理想情况下，处理器数量翻倍应带来系统性能翻倍，但在现实中这是不可能实现的。

The scalability of Linux on a large number of processors has increased dramatically in the time since multiprocessing support was introduced in the 2.0 kernel. In the earlydays of Linux multiprocessing support, only one task could execute in the kernel at atime. During 2.2, this limitation was removed as the locking mechanisms grew morefine-grained.Through 2.4 and onward, kernel locking became even finer grained.Today,in the 2.6 Linux kernel, kernel locking is very fine-grained and scalability is good.

自 Linux 2.0 内核引入多处理支持以来，Linux 在大量处理器场景下的可扩展性得到了极大提升。

在 Linux 多处理支持的早期，内核中同一时间只能有一个任务执行。到 2.2 内核版本，随着锁机制变得更加**细粒度化**，这一限制被取消。

从 2.4 内核及之后版本开始，内核锁的粒度进一步细化。如今在 2.6 Linux 内核中，内核锁的粒度已经非常精细，可扩展性表现优异。

The granularity of locking is a description of the size or amount of data that a lock protects.A very coarse lock protects a large amount of data—for example, an entire sub-system’s set of data structures. On the other hand, a very fine-grained lock protects asmall amount of data—say, only a single element in a larger structure. In reality, mostlocks fall somewhere in between these two extremes, protecting neither an entiresubsystem nor an individual element, but perhaps a single structure or list of structures.Most locks start off fairly coarse and are made more fine-grained as lock contentionproves to be a problem.

**锁粒度（granularity of locking）** 用于描述一把锁所保护数据的大小或范围。

- **粗粒度锁**：保护大量数据，例如保护整个子系统的所有数据结构。
- **细粒度锁**：只保护少量数据，例如大型结构中的单个元素。

实际中，大多数锁介于两者之间 —— 既不保护整个子系统，也不保护单个元素，而是保护单个结构或结构链表。

大多数锁在设计初期都相对偏粗粒度，当锁竞争成为性能问题时，再逐步优化为更细的粒度。

One example of evolving to finer-grained locking is the scheduler runqueues, dis-cussed in Chapter 4,“Process Scheduling.” In 2.4 and prior kernels, the scheduler had asingle runqueue. (Recall that a runqueue is the list of runnable processes.) Early in the2.6 series, the O(1) scheduler introduced per-processor runqueues, each with a uniquelock. The locking evolved from a single global lock to separate locks for eachprocessor.This was an important optimization, because the runqueue lock was highlycontended on large machines, essentially serializing the entire scheduling process downto a single processor executing in the scheduler at a time. Later in the 2.6 series, theCFS Scheduler improved scalability further.

锁粒度不断细化的典型例子是**调度器运行队列**（第 4 章《进程调度》会详细介绍）：

- 在 2.4 及更早内核中，调度器只有**一个全局运行队列**（运行队列是可运行进程的链表）。

- 在 2.6 内核早期，O (1) 调度器引入了**每处理器独立运行队列**，每个队列拥有专属的锁。

锁机制从单一全局锁，演进为每个处理器独立加锁。这是一项重要优化，因为在大型机器上，原有的运行队列锁竞争极其激烈，会导致整个调度流程被串行化，同一时间只能有一个处理器执行调度逻辑。  在 2.6 内核后期，CFS 完全公平调度器进一步提升了可扩展性。

Generally, this scalability improvement is a good thing because it improves Linux’s per-formance on larger and more powerful systems. Rampant scalability “improvements”can lead to a decrease in performance on smaller SMP and UP machines, however,because smaller machines may not need such fine-grained locking but will nonethelessneed to put up with the increased complexity and overhead. Consider a linked list.Aninitial locking scheme would provide a single lock for the entire list. In time, this singlelock might prove to be a scalability bottleneck on large multiprocessor machines thatfre-quently access this linked list. In response, the single lock could be broken up intoone lock per node in the linked list. For each node that you wanted to read or write, youobtained the node’s unique lock. Now there is only lock contention when multipleprocessors are accessing the same exact node.What if there is still lock contention,how-ever? Do you provide a lock for each element in each node? Each bit of eachelement? The answer is no. Even though this fine-grained locking might ensureexcellent scalability on large SMP machines, how does it perform on dual processormachines? The overhead of all those extra locks is wasted if a dual processor machinedoes not see significant lock contention to begin with.

通常来说，这种可扩展性的提升是有益的，因为它能让 Linux 在更大、更强的系统上获得更好的性能。然而，过度追求可扩展性 “优化”，反而会导致在小型 SMP（对称多处理器）和 UP（单处理器）机器上性能下降。这些小型设备并不需要如此细粒度的锁机制，却仍要承担由此带来的复杂度提升与额外开销。

以链表为例，最初的锁方案是为整个链表设置一把全局锁。随着时间推移，在频繁访问该链表的大型多处理器机器上，这把全局锁会成为可扩展性的瓶颈。

针对这个问题，可以将全局锁拆分为链表中每个节点各自独立的锁。当你需要读写某个节点时，只需获取该节点专属的锁即可。这样一来，只有在多个处理器访问**同一个节点**时，才会产生锁竞争。

但如果此时依然存在锁竞争呢？难道要为每个节点里的每个元素都加一把锁？甚至为每个元素的每一位加锁？答案显然是否定的。尽管这种极致细粒度的锁能在大型 SMP 机器上保证极佳的可扩展性，但在双处理器机器上表现又如何？如果双处理器机器本身就不存在显著的锁竞争，那么这些额外锁带来的开销就完全是一种浪费。

Nonetheless, scalability is an important consideration. Designing your locking from thebeginning to scale well is important. Coarse locking of major resources can easilybecome a bottleneck on even small machines.There is a thin line between too-coarselocking and too-fine locking. Locking that is too coarse results in poor scalability ifthere is high lock contention, whereas locking that is too fine results in wastefuloverhead if there is little lock contention. Both scenarios equate to poor performance.Start simple and grow in com-plexity only as needed. Simplicity is key.

尽管如此，可扩展性依然是一个重要的考量因素。在设计锁机制之初，就考虑到良好的可扩展性至关重要。对核心资源采用粗粒度加锁，即便在小型机器上也很容易成为性能瓶颈。

锁的粒度过粗与过细之间只有一线之隔：锁粒度过粗，在锁竞争激烈时会导致可扩展性极差；而锁粒度过细，在锁竞争极少时则会产生不必要的开销。这两种情况最终都会表现为性能低下。

设计时应从简洁入手，仅在实际需要时再增加复杂度，**简洁才是核心**。









