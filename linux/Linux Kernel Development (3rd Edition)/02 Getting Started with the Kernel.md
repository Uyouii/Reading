[toc]

## 2 Getting Started with the Kernel

### Building the Kernel

#### Spawning Multiple Build Jobs

**生成多构建任务**

**A Beast of a Different Nature** The Linux kernel has several unique attributes as compared to a normal user-space appli-cation.Although these differences do not necessarily make developing kernel code harder than developing user-space code, they certainly make doing so different.

**与众不同的复杂存在** 与普通的用户空间应用程序相比，Linux 内核具有多项独特的特性。这些差异未必会让内核代码的开发难度高于用户空间代码，但必然会让内核开发的流程与后者截然不同。

These characteristics make the kernel a beast of a different nature. Some of the usual rules are bent; other rules are entirely new.Although some of the differences are obvious (we all know the kernel can do anything it wants), others are not so obvious.The most important of these differences are

- The kernel has access to neither the C library nor the standard C headers.
- The kernel is coded in GNU C.
- The kernel lacks the memory protection afforded to user-space.
- The kernel cannot easily execute floating-point operations.
- The kernel has a small per-process fixed-size stack.
- Because the kernel has asynchronous interrupts, is preemptive, and supports SMP, synchronization and concurrency are major concerns within the kernel.
- Portability is important.

这些特性使得内核成为一个**与众不同的复杂存在**。一些通用的开发规则在这里不再适用，还有一些全新的规则需要遵守。虽然部分差异显而易见（比如我们都知道内核拥有至高无上的操作权限），但另一些差异却并不容易察觉。其中，最为关键的差异如下：

- 内核既无法访问 C 标准库，也无法使用标准 C 头文件。
- 内核采用**GNU C 语言**编写。
- 内核不具备用户空间所拥有的内存保护机制。
- 内核无法轻松执行浮点运算。
- 每个进程都拥有一个**固定大小的小型栈空间**。
- 由于内核存在异步中断、支持内核抢占且兼容对称多处理（SMP）架构，因此同步机制与并发控制是内核开发过程中需要重点关注的问题。
- **可移植性至关重要**。