## 08 Bottom Halves andDeferring Work

The previous chapter discussed interrupt handlers, the kernel mechanism fordealing with hardware interrupts. Interrupt handlers are an important—indeed, required—part of any operating system. Due to various limitations,however, interrupt handlers can form only the first half of any interruptprocessing solution.These limitations include

- nterrupt handlers run asynchronously and thus interrupt other, potentially important, code, including other interrupt handlers.Therefore, to avoid stalling the    inter-rupted code for too long, interrupt handlers need to run as quickly aspossible.
- Interrupt handlers run with the current interrupt level disabled at best (if IRQF_DISABLED is unset), and at worst (if IRQF_DISABLED is set) with allinterrupts on the current processor disabled.As disabling interrupts preventshardware from communicating with the operating systems, interrupt handlersneed to run as quickly as possible.
-  Interrupt handlers are often timing-critical because they deal withhardware.
- Interrupt handlers do not run in process context; therefore, they cannotblock.This limits what they can do.

上一章讨论了**中断处理程序**—— 内核用于处理硬件中断的机制。中断处理程序是任何操作系统中至关重要（甚至是必不可少）的组成部分。但受多种限制影响，中断处理程序只能作为中断处理方案的**上半部**。这些限制包括：

- 中断处理程序**异步执行**，因此会打断其他可能很重要的代码（包括其他中断处理程序）。为避免被打断的代码被阻塞过久，中断处理程序必须尽可能快速地执行。
- 中断处理程序运行时，最优情况下（未设置 `IRQF_DISABLED`）当前中断级会被禁用，最坏情况下（设置了 `IRQF_DISABLED`）**当前处理器上所有中断都会被禁用**。由于禁用中断会阻断硬件与操作系统的通信，因此中断处理程序必须尽快执行完毕。
- 中断处理程序往往与硬件直接交互，因此**对时序要求严格**。
- 中断处理程序**不运行在进程上下文**中，因此**不能阻塞**。这极大限制了它能执行的操作。

It should now be evident that interrupt handlers are only a piece of thesolution to managing hardware interrupts. Operating systems certainly need a quick,asynchronous, simple mechanism for immediately responding to hardwareand performing any time-critical actions. Interrupt handlers serve thisfunction well; but other, less critical work can and should be deferred to alater point when interrupts are enabled.

现在不难看出，中断处理程序只是硬件中断管理方案的一部分。操作系统确实需要一种快速、异步、简洁的机制，用于立即响应硬件并完成所有**对时间敏感的操作**，中断处理程序很好地承担了这一角色；但其他**非紧急工作**，可以且应当被推迟到中断重新启用后的某个时机再处理。

Consequently, managing interrupts is divided into two parts, or halves.The first part, interrupt handlers (top halves), are executed by the kernel asynchronously in immediate response to a hardware interrupt, as discussed in the previous chapter.This chapter looks at the second part of the interrupt solution, bottom halves.

因此，中断处理被划分为两个部分（或称两个半部）。

第一部分是**中断处理程序（上半部）**，由内核异步执行，用于立即响应硬件中断，这部分内容已在上一章讨论。

本章将介绍中断处理方案的第二部分：**下半部**。

### Bottom Halves

The job of bottom halves is to perform any interrupt-relatedwork not performed by the interrupt handler. In an ideal world, this is nearlyall the work because you want the interrupt handler to perform as little work(and in turn be as fast) as possible. By offload-ing as much work as possibleto the bottom half, the interrupt handler can return control of the system towhatever it interrupted as quickly as possible.

下半部的职责，是完成中断处理程序中未做完的、与中断相关的工作。在理想情况下，下半部会承担**几乎全部工作**，因为我们希望中断处理程序只做尽可能少的事，从而执行得尽可能快。通过把尽可能多的工作卸载到下半部，中断处理程序就能尽快把系统控制权交还给被它中断的代码。

Nonetheless, the interrupt handler must perform some of the work. Forexample, the interrupt handler almost assuredly needs to acknowledge to the hardwarethe receipt of the interrupt. It may need to copy data to or from thehardware.This work is timing-sensitive, so it makes sense to perform it inthe interrupt handler.

尽管如此，仍有一部分工作必须由中断处理程序完成。例如，中断处理程序几乎必然需要**向硬件应答中断已收到**；它也可能需要与硬件之间进行数据拷贝。这类工作对**时序敏感**，因此放在中断处理程序中执行是合理的。

Almost anything else is fair game for performing in the bottom half. Forexample, if you copy data from the hardware into memory in the top half, it certainlymakes sense to process it in the bottom half. Unfortunately, no hard and fastrules exist about what work to perform where—the decision is left entirely upto the device-driver author.Although no arrangement is illegal, anarrangement can certainly be suboptimal. Remember, inter-rupt handlers runasynchronously, with at least the current interrupt line disabled. Mini-mizingtheir duration is important.Although it is not always clear how to divide thework between the top and bottom half, a couple of useful tips help:

-  If the work is time sensitive, perform it in the interrupt handler.
-  If the work is related to the hardware, perform it in the interrupt handler.
- If the work needs to ensure that another interrupt (particularly the sameinterrupt) does not interrupt it, perform it in the interrupt handler.
- For everything else, consider performing the work in the bottom half.

几乎除此之外的所有工作，都适合放在下半部完成。例如，如果你在上半部把数据从硬件读到内存，那么对这些数据的后续处理，就非常适合放到下半部。遗憾的是，**哪些工作该放在哪里执行并没有硬性规则**，决定权完全交给设备驱动开发者。虽然没有哪种划分方式是非法的，但不合理的划分显然会导致性能变差。请记住：中断处理程序是异步执行的，且运行时至少会屏蔽当前中断线，**尽可能缩短它的执行时间至关重要**。尽管如何在上半部与下半部之间划分工作并不总是很明确，但下面几条实用原则可以参考：

- 如果工作**对时间敏感**，放在中断处理程序中执行。
- 如果工作**与硬件直接相关**，放在中断处理程序中执行。
- 如果需要确保该工作**不会被其他中断（尤其是同一中断）打断**，放在中断处理程序中执行。
- 除此之外的所有工作，都可以考虑放在下半部执行。

#### Why Bottom Halves?

It is crucial to understand why to defer work, and whenexactly to defer it.You want to limit the amount of work you perform in aninterrupt handler because interrupt handlers run with the current interruptline disabled on all processors.Worse, handlers that register withIRQF_DISABLED run with all interrupt lines disabled on the local processor,plus the current interrupt line disabled on all processors. Minimizing the timespent with inter-rupts disabled is important for system response andperformance.Add to this the fact that interrupt handlers run asynchronouslywith respect to other code—even other interrupt handlers—and it is clearthat you should work to minimize how long interrupt handlers run. Processingincoming network traffic should not prevent the kernel’s receipt of key-strokes.The solution is to defer some of the work until later.

理解**为何要推迟工作**，以及**究竟何时推迟**，这一点至关重要。我们需要限制在中断处理程序中完成的工作量，因为中断处理程序运行时，**所有处理器**上的**当前中断线**都会被屏蔽。更糟糕的是，使用 `IRQF_DISABLED` 注册的处理程序，会在**本地处理器**上屏蔽**全部中断线**，同时还会在所有处理器上屏蔽当前中断线。尽可能缩短中断被屏蔽的时间，对系统响应性和性能至关重要。除此之外，中断处理程序相对于其他代码（甚至其他中断处理程序）都是**异步运行**的，因此显然应当尽量缩短中断处理程序的执行时间。处理 incoming 网络流量，不应该阻塞内核接收键盘输入。解决方案就是把一部分工作推迟到后面再做。

But when is “later?”The important thing to realize is that later is often simply not now. 

但 “后面” 究竟是什么时候？需要明白的关键点是：**“后面” 往往只是 “不是现在” 而已**。

The point of a bottom half is not to do work at some specific point in thefuture, but sim-ply to defer work until any point in the future when thesystem is less busy and interrupts are again enabled. Often, bottom halvesrun immediately after the interrupt returns.The key is that they run with allinterrupts enabled.

下半部的意义，并不是要在未来某个精确时间点执行工作，而只是**把工作推迟到未来任意一个系统没那么繁忙、并且中断已重新启用的时机**。很多时候，下半部会在中断处理程序返回后**立刻执行**。核心区别在于：它们运行时**所有中断都是开启状态**。

Linux is not alone in separating the processing of hardware interrupts intotwo parts; most operating systems do so.The top half is quick and simple and runs with some or all interrupts disabled.The bottom half (however it is implemented)runs later with all interrupts enabled.This design keeps system latency lowby running with interrupts disabled for as little time as necessary.

并非只有 Linux 会把硬件中断处理拆成两部分，大多数操作系统都是这么做的。**上半部**快速、简单，运行时会屏蔽部分或全部中断；**下半部**（无论具体如何实现）会在稍后运行，且运行时**所有中断都已启用**。这种设计通过把中断屏蔽时间压缩到最短必需时长，从而维持较低的系统延迟。

#### A World of Bottom Halves

Unlike the top half, which is implemented entirelyvia the interrupt handler, multiple mechanisms are available for implementinga bottom half.These mechanisms are different interfaces and subsystemsthat enable you to implement bottom halves.Whereas the pre-vious chapterlooked at just a single way of implementing interrupt handlers, this chapterlooks at multiple methods of implementing bottom halves. Over the course ofLinux’s history, there have been many bottom-half mechanisms. Confusingly,some of these mechanisms have similar or even dumb names. It requires aspecial type of programmer to name bottom halves.

与完全通过中断处理程序实现的上半部不同，**下半部**有多种实现机制可供选择。这些机制是不同的接口与子系统，用于完成下半部的功能。上一章只讨论了实现中断处理程序（上半部）的唯一方式，而本章会介绍实现下半部的多种方法。在 Linux 的发展历程中，曾出现过许多种下半部机制。令人困惑的是，其中一些机制的名称相近甚至很不直观，给下半部命名确实需要特别的思路。

This chapter discusses both the design and implementation of the bottom-half mecha-nisms that exist in 2.6.We also discuss how to use them in thekernel code you write.The old, but long since removed, bottom-halfmechanisms are historically significant, and so they are mentioned whenrelevant.

本章会讨论 **2.6 内核**中现存的各类下半部机制的设计与实现，也会介绍如何在内核代码中使用它们。一些早已被移除的旧式下半部机制仍具有历史参考意义，因此在相关地方会简要提及。

**The Original “Bottom Half”**

最初的 “Bottom Half”（BH 机制）

In the beginning, Linux provided only the“bottom half” for implementing bottom halves.This name was logicalbecause at the time that was the only means available for deferringwork.The infrastructure was also known as BH, which is what we will call itto avoid confusion with the generic term bottom half.The BH interface wassimple, like most things in those good old days. It provided a staticallycreated list of 32 bottom halves for the entire system.The top half couldmark whether the bottom half would run by setting a bit in a 32-bit integer.Each BH was globally synchronized. No two could run at the same time, evenon different processors.This was easy to use, yet inflexible; a simple  approach, yet a bottleneck.

早期 Linux 只提供一种名为 **bottom half** 的机制来实现延后工作。这个名字在当时很合理，因为它是唯一的延后工作手段。这套基础架构也被简称为 **BH**，为了避免与通用概念 “下半部（bottom half）” 混淆，后文统一称其为 **BH 机制**。

和早年大多数设计一样，BH 接口非常简单：系统全局静态定义了包含 **32 个下半部**的列表。上半部可以通过设置一个 32 位整数中的对应比特位，来标记对应的下半部是否需要执行。

所有 BH 都是**全局同步**的：即使在不同处理器上，也不可能同时运行两个 BH。这种方式易用但缺乏弹性，实现简单，却成为了性能瓶颈。

**Task Queues**

Later on, the kernel developers introduced task queues both as a method of deferring work and as a replacement for the BH mechanism.Thekernel defined a family of queues. Each queue contained a linked list offunctions to call.The queued functions were run at certain times, dependingon which queue they were in. Drivers could register their bot-tom halves inthe appropriate queue.This worked fairly well, but it was still too inflexibletoreplace the BH interface entirely. It also was not lightweight enough forperformance-critical subsystems, such as networking.

后来，内核开发者引入了**任务队列（task queues）**，既作为延后工作的一种方式，也作为 BH 机制的替代方案。

内核定义了一组队列，每个队列包含一个待调用函数的链表。队列中的函数会在特定时机执行，具体取决于所属队列的类型。驱动可以将自己的下半部注册到合适的队列中。

这套机制工作得还算不错，但灵活性仍然不足，无法完全替代 BH 接口；同时，它也不够轻量，难以满足网络等对性能敏感的子系统需求。

**Softirqs and Tasklets**

During the 2.3 development series, the kerneldevelopers introduced softirqs and tasklets. With the exception ofcompatibility with existing drivers, softirqs and tasklets could com-pletelyreplace the BH interface.1 Softirqs are a set of statically defined bottomhalves that can run simultaneously on any processor; even two of the sametype can run concur-rently.Tasklets, which have an awful and confusingname,2 are flexible, dynamically cre-ated bottom halves built on top ofsoftirqs.Two different tasklets can run concurrently on different processors,but two of the same type of tasklet cannot run simultaneously.Thus, taskletsare a good trade-off between performance and ease of use. For mostbottom-half processing, the tasklet is sufficient. Softirqs are useful whenperformance is critical, such as with networking. Using softirqs requiresmore care, however, because two of the same softirq can run at the sametime. In addition, softirqs must be registered statically at com-pile time.Conversely, code can dynamically register tasklets.

在 2.3 开发版系列中，内核开发者引入了**软中断（softirqs）**与**小任务（tasklets）**。除了为保持对现有驱动的兼容性外，软中断和小任务完全可以取代原有的 BH 接口。

软中断是一组**静态定义**的下半部机制，可以在任意处理器上**并发执行**；即便是**同一类型**的两个软中断，也能同时运行。

小任务（tasklets）这个名字起得糟糕又容易混淆，它是构建在软中断之上、支持**动态创建**的灵活下半部机制。**不同类型**的小任务可以在不同处理器上并发执行，但**同一类型**的两个小任务无法同时运行。

因此，小任务在性能与易用性之间做了很好的权衡。对于绝大多数下半部处理场景，小任务都足够使用。而软中断则适用于**对性能要求极高**的场景（例如网络子系统）。不过，使用软中断需要更加谨慎，因为同一类型的两个软中断可能并行执行。此外，软中断必须在**编译期静态注册**；与之相对，代码可以在运行时动态注册小任务。

To further confound the issue, some people refer to all bottom halves as software interrupts or softirqs. In other words, they call both the softirqmechanism and bottom halves in general softirqs. Ignore those people.Theyrun with the same crowd that named the BH and tasklet mechanisms.

更让人混淆的是，有些人把所有下半部都统称为 “软件中断” 或 “软中断”。换句话说，他们既把软中断机制叫作 softirq，也把通用意义上的下半部都叫作 softirq。别理这些人，他们和当年给 BH、小任务起名的那拨人是一路的。

While developing the 2.5 kernel, the BH interface was finally tossed to thecurb     because all BH users were converted to the other bottom-half interfaces.Additionally, the task queue interface was replaced by the **work queue** interface.Work queues are a simple yet useful method of queuingwork to later be performed in process context.We get to them later.

在开发 2.5 内核时，BH 接口终于被彻底废弃，因为所有原 BH 用户都已迁移到其他下半部接口。与此同时，任务队列（task queue）接口也被**工作队列（work queue）**接口取代。工作队列是一种简单实用的机制，可将工作排队，延后在**进程上下文**中执行。我们稍后会讲到它。

Consequently, today 2.6 has three bottom-half mechanisms in the kernel:softirqs, tasklets, and work queues.The old BH and task queue interfaces arebut mere memories.

因此，如今的 2.6 内核中存在三种下半部机制：**软中断、小任务、工作队列**。旧的 BH 与任务队列接口，都已成为历史。

**Kernel Timers**

Another mechanism for deferring work is kernel timers. Unlike themechanisms discussed in the chapter thus far, timers defer work for aspecified amount of time. That is, although the tools discussed in thischapter are useful to defer work to any time but now, you use timers to defer work until at least a specific time has elapsed.

另一种用于延后工作的机制是**内核定时器**。与本章目前所讨论的机制不同，定时器会将工作延后**指定的时长**再执行。也就是说，本章介绍的这些工具只适合把工作推迟到 “不是现在” 的任意时刻，而定时器则是用来把工作推迟到**至少经过一段确定时间之后**再运行。

Therefore, timers have different uses than the general mechanismsdiscussed in this chap-ter. A full discussion of timers is given in Chapter 11,“Timers and Time Management.”

因此，定时器的使用场景，与本章介绍的通用延后机制并不相同。关于定时器的完整讲解，会在第 11 章《定时器与时间管理》中详细展开。

Bottom half is a generic operating system term referring to the deferredportion of interrupt processing, so named because it represents the second, or bottom,half of the interrupt processing solution. In Linux, the term currently has thismeaning, too.All the kernel’s mechanisms for deferring work are “bottomhalves.” Some people also confus-ingly call all bottom halves “softirqs.”

**下半部（bottom half）** 是操作系统领域的通用术语，特指中断处理流程中被延后执行的部分；之所以如此命名，是因为它代表了中断处理方案的第二个、也就是**下半**部分。在 Linux 中，该术语目前也沿用这一含义：内核中所有用于**延后工作**的机制，都统称为 “下半部”。部分人还会混淆地将所有下半部都称作 “软中断（softirqs）”。

Bottom half also refers to the original deferred work mechanism inLinux.This mech-anism is also known as a BH, so we call it by that namenow and leave the former as a generic description.The BH mechanism was deprecated a while back and fully removed in the 2.5 development kernelseries.

`bottom half` 也曾专指 Linux 早期的原始延后工作机制，该机制也被简称为 **BH**。因此我们现在用 **BH** 代指这一旧实现，而将 “下半部” 保留为通用概念。BH 机制早已被标记为废弃，并在 2.5 开发版内核系列中被彻底移除。

Currently, three methods exist for deferring work: softirqs, tasklets, and workqueues. 

目前，Linux 内核中有三种实现延后工作的机制：**软中断（softirqs）、小任务（tasklets）和工作队列（work queues）**。

Tasklets are built on softirqs and work queues are their ownsubsystem.

其中，小任务基于软中断实现，而工作队列则是独立的子系统。



