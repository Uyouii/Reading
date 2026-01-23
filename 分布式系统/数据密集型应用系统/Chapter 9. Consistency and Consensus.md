[toc]

## Chapter 9. Consistency and Consensus

**第九章. 一致性和共识**

The best way of building fault-tolerant systems is to find some **general-purpose abstractions with useful guarantees**, implement them once, and then let applicationsrely on those guarantees. This is the same approach as we used with transactions inChapter 7: by using a transaction, the application can pretend that there are nocrashes (atomicity), that nobody else is concurrently accessing the database (isola‐tion), and that storage devices are perfectly reliable (durability). Even though crashes,race conditions, and disk failures do occur, the transaction abstraction hides thoseproblems so that the application doesn’t need to worry about them.

构建容错系统的最佳方式，是提炼出若干具备**实用保障机制的通用抽象**，对其进行一次性实现，而后让上层应用直接依赖这些保障机制运行。这与我们在第 7 章中讨论事务时采用的思路如出一辙：通过使用事务，应用程序可以**无需考虑**崩溃问题（原子性）、无需考虑其他主体并发访问数据库的情况（隔离性），也无需考虑存储设备的可靠性问题（持久性）。尽管崩溃、竞态条件和磁盘故障实际都会发生，但事务抽象会将这些问题完全屏蔽，让应用程序无需再为其费心。

### Linearizability

**线性一致性**

#### What Makes a System Linearizable?

**什么样的系统具备线性一致性？**

**Linearizability Versus Serializability**

**线性一致性与可串行化的区别**

Linearizability is easily confused with serializability (see “Serializability” on page 251),as both words seem to mean something like “can be arranged in a sequential order.”However, they are two quite different guarantees, and it is important to distinguishbetween them:

线性一致性很容易与可串行化混淆（参见第 251 页 “可串行化”），这两个术语的字面意思都近似于 “可按某种顺序排列”。但实际上，二者是两种截然不同的保障机制，厘清它们的区别至关重要：

**Serializability** Serializability is an isolation property of transactions, where every transaction may read and write multiple objects (rows, documents, records)—see “Single- Object and Multi-Object Operations” on page 228. It guarantees that transac‐ tions behave the same as if they had executed in some serial order (each transaction running to completion before the next transaction starts). It is okay for that serial order to be different from the order in which transactions were actually run [12].

**可串行化** 可串行化是**事务的隔离属性**，适用于包含多对象（行、文档、记录）读写操作的事务场景（参见第 228 页 “单对象与多对象操作”）。它能保证：事务的执行效果，等价于所有事务按照某一种**串行顺序**依次执行 —— 即每个事务都完整执行完毕后，下一个事务才开始执行。这种串行顺序，允许与事务实际的执行顺序不一致 [1

Linearizability Linearizability is a recency guarantee on reads and writes of a register (an indi‐ vidual object). It doesn’t group operations together into transactions, so it does not prevent problems such as write skew (see “Write Skew and Phantoms” on page 246), unless you take additional measures such as materializing conflicts (see “Materializing conflicts” on page 251).

**线性一致性** 线性一致性是**寄存器（单个对象）读写操作的最新性保障**。它不会将多个操作分组为事务，因此无法防范写偏斜这类问题（参见第 246 页 “写偏斜与幻读”），除非额外采取物化冲突等措施（参见第 251 页 “物化冲突”）。

A database may provide both serializability and linearizability, and this combinationis known as strict serializabilityor strong one-copy serializability(strong-1SR) [4, 13].Implementations of serializability based on two-phase locking (see “Two-Phase Lock‐ing (2PL)” on page 257) or actual serial execution (see “Actual Serial Execution” onpage 252) are typically linearizable.

一个数据库可以同时提供可串行化与线性一致性这两种保障，这种组合特性被称为**严格可串行化**或**强单副本可串行化（strong-1SR）**[4,13]。基于两阶段锁（参见第 257 页 “两阶段锁（2PL）”）或严格串行执行（参见第 252 页 “严格串行执行”）实现的可串行化，通常具备线性一致性。

However, serializable snapshot isolation (see “Serializable Snapshot Isolation (SSI)”on page 261) is not linearizable: by design, it makes reads from a consistent snapshot,to avoid lock contention between readers and writers. The whole point of a consistentsnapshot is that it does not include writes that are more recent than the snapshot, andthus reads from the snapshot are not linearizable.

但**可串行化快照隔离（SSI）**（参见第 261 页 “可串行化快照隔离（SSI）”）**不具备线性一致性**：其设计初衷是让事务读取一致性快照，以此避免读写操作之间的锁竞争。而一致性快照的核心特点，就是不包含快照生成之后的新写入操作 —— 因此，基于快照的读取不满足线性一致性要求。

#### Relying on Linearizability

Similar issues arise if you want to ensure that a bank account balance never goes neg‐ative, or that you don’t sell more items than you have in stock in the warehouse, orthat two people don’t concurrently book the same seat on a flight or in a theater.These constraints all require there to be a single up-to-date value (the account balance, the stock level, the seat occupancy) that all nodes agree on.

当你需要确保以下约束条件时，也会遇到类似的问题：银行账户余额绝不能为负、商品出库数量不超过仓库库存量、航班或剧院的同一个座位不会被两人同时预订。这些约束的实现，都需要一个**所有节点均认可的单一最新有效值**—— 即账户余额、库存数量、座位占用状态。

In real applications, it is sometimes acceptable to treat such constraints loosely (forexample, if a flight is overbooked, you can move customers to a different flight andoffer them compensation for the inconvenience). In such cases, linearizability maynot be needed, and we will discuss such loosely interpreted constraints in “Timelinessand Integrity” on page 524.

在实际业务场景中，这类约束有时可以宽松处理。例如，若航班出现超售情况，你可以为乘客改签至其他航班，并为其因此产生的不便提供补偿。在这类场景下，就不需要用到线性一致性；关于这类宽松约束的相关内容，我们将在第 524 页的 **“时效性与完整性”** 一节中展开讨论。

However, a hard uniqueness constraint, such as the one you typically find in rela‐tional databases, requires linearizability. Other kinds of constraints, such as foreignkey or attribute constraints, can be implemented without requiring linearizability[19].

但对于**硬性唯一性约束**（例如关系型数据库中常见的唯一性约束），则必须依赖线性一致性才能实现。而其他类型的约束（如外键约束或属性约束），即便不依赖线性一致性，同样可以实现 [19]。

#### The Cost of Linearizability

**线性一致性的成本**

**The Unhelpful CAP Theorem**

**并无实际指导意义的 CAP 定理**

CAP is sometimes presented as **Consistency**, **Availability**, **Partition tolerance**: pick 2out of 3. Unfortunately, putting it this way is misleading [32] because network parti‐tions are a kind of fault, so they aren’t something about which you have a choice: theywill happen whether you like it or not [38].

CAP 定理有时被阐释为**一致性（Consistency）、可用性（Availability）、分区容错性（Partition tolerance）三者选其二**。但遗憾的是，这种表述具有误导性 [32]—— 因为网络分区属于一种故障类型，它的发生并不以人的意志为转移，无论你是否愿意，它迟早都会出现 [38]。

At times when the network is working correctly, a system can provide both **consistency (linearizability)** and **total availability**. When a network fault occurs, you have tochoose between either **linearizability** or **total availability**. Thus, a better way of phras‐ing CAP would be either Consistent or Available when Partitioned[39]. A more relia‐ble network needs to make this choice less often, but at some point the choice isinevitable.

在网络正常运行时，系统可以同时提供**一致性（线性一致性）\**与\**完全可用性**。而当网络故障导致分区发生时，你就必须在**线性一致性**与**完全可用性**之间做出取舍。因此，对 CAP 定理更准确的表述应当是：**发生网络分区时，一致性与可用性二者择一**[39]。网络可靠性越高，需要做出这种取舍的频率就越低，但从根本上来说，这种选择是无法避免的。

In discussions of CAP there are several contradictory definitions of the term availa‐bility, and the formalization as a theorem [30] does not match its usual meaning [40].Many so-called “highly available” (fault-tolerant) systems actually do not meet CAP’sidiosyncratic definition of availability. All in all, there is a lot of misunderstandingand confusion around CAP, and it does not help us understand systems better, soCAP is best avoided.

在关于 CAP 定理的讨论中，“可用性” 这一术语存在多种相互矛盾的定义，该定理的形式化定义 [30] 与 “可用性” 的常规含义并不相符 [40]。许多所谓的 “高可用”（容错）系统，实际上并不符合 CAP 定理中对可用性的特殊定义。总而言之，围绕 CAP 定理存在大量的误解与混淆，它不仅无法帮助我们更深入地理解系统，反而可能造成困扰，因此最好尽量避免过度依赖这一理论。

The CAP theorem as formally defined [30] is of very narrow scope: it only considersone consistency model (namely linearizability) and one kind of fault (network parti‐tions,vi or nodes that are alive but disconnected from each other). It doesn’t say anything about network delays, dead nodes, or other trade-offs. Thus, although CAP hasbeen historically influential, it has little practical value for designing systems [9, 40].

从形式化定义来看 [30]，CAP 定理的适用范围非常狭窄：它只考量了一种一致性模型（即线性一致性）和一种故障类型（网络分区，也就是节点存活但彼此断开连接的情况）。对于网络延迟、节点宕机，以及其他需要权衡的因素，该定理并未提及。因此，尽管 CAP 定理在历史上具有一定的影响力，但对于实际的系统设计而言，它的实用价值十分有限 [9,40]。

Can’t we maybe find a **more efficient implementation of linearizable storage**? Itseems the answer is no: Attiya and Welch [47] prove that if you want linearizability,the response time of read and write requests is at least proportional to the **uncertainty of delays in the network**. In a network with highly variable delays, like most com‐puter networks (see “Timeouts and Unbounded Delays” on page 281), the responsetime of linearizable reads and writes is inevitably going to be high. A faster algorithmfor linearizability does not exist, but **weaker consistency models** can be much faster,so this trade-off is important for latency-sensitive systems. In Chapter 12 we will dis‐cuss some approaches for avoiding linearizability without sacrificing correctness.

难道我们就不能找到一种**更高效的线性一致性存储实现方案**吗？答案似乎是否定的：阿提亚（Attiya）与韦尔奇（Welch）[47] 证明，若要实现线性一致性，读写请求的响应时间至少与**网络延迟的不确定性成正比**。对于延迟高度可变的网络（如多数计算机网络，参见第 281 页的《超时与无界延迟》一节）而言，线性一致性读写的响应时间必然会处于较高水平。目前并不存在更快速的线性一致性实现算法，但**弱一致性模型**的执行效率可以提升很多，因此这种权衡对延迟敏感型系统而言至关重要。在第 12 章中，我们将探讨一些无需牺牲正确性、同时又能规避线性一致性的实现方案。

### Ordering Guarantees

**顺序保障**

Causality imposes an ordering on events: cause comes before effect; a message is sentbefore that message is received; the question comes before the answer. And, like inreal life, one thing leads to another: one node reads some data and then writes some‐thing as a result, another node reads the thing that was written and writes somethingelse in turn, and so on. These chains of causally dependent operations define thecausal order in the system—i.e., what happened before what.

因果关系会给事件施加一种先后顺序：**因**发生于**果**之前；消息的发送发生于该消息的接收之前；问题的提出发生于该问题的解答之前。与现实场景同理，事件的发生环环相扣：某个节点读取部分数据后，基于这些数据执行写入操作；另一个节点读取此次写入的结果，继而又执行新的写入操作，以此类推。这些**存在因果依赖的操作链**，定义了系统中的**因果顺序**—— 即哪些事件发生在哪些事件之前。

If a system obeys the ordering imposed by causality, we say that it is **causally consistent.** For example, snapshot isolation provides causal consistency: when you readfrom the database, and you see some piece of data, then you must also be able to seeany data that causally precedes it (assuming it has not been deleted in the meantime).

若一个系统遵循因果关系所施加的顺序规则，我们就称该系统具备**因果一致性**。例如，快照隔离就能够提供因果一致性：当你从数据库中读取数据时，若能看到某一份数据，那么你也一定能看到所有在因果关系上先于这份数据产生的数据（前提是这些前置数据在此期间未被删除）。



**The Causal order is not a total order**

**因果顺序并非全序**

The difference between a total order and a partial order is reflected in different data‐base consistency models:

全序与偏序的区别，体现在不同的数据库一致性模型中：

**Linearizability** In a linearizable system, we have a **total order** of operations: if the system behaves as if there is only a single copy of the data, and every operation is atomic, this means that for any two operations we can always say which one happened first. This total ordering is illustrated as a timeline in Figure 9-4.

**线性一致性** 在一个线性一致性系统中，所有操作遵循**全序关系**：如果系统的表现就如同只有一份数据副本，且每个操作都是原子性的，那么这意味着对于任意两个操作，我们始终能够判定二者的先后顺序。这种全序关系可以用图 9-4 中的时间线直观表示。

**Causality** We said that two operations are **concurrent** if neither happened before the other (see “The “happens-before” relationship and concurrency” on page 186). Put another way, two events are ordered if they are causally related (one happened before the other), but they are incomparable if they are concurrent. This means that causality defines a partial order, not a total order: some operations are ordered with respect to each other, but some are incomparable.

**因果关系** 我们曾定义：若两个操作之间不存在 “先发生” 关系，则称这两个操作是**并发**的（参见第 186 页 “‘先发生’关系与并发”）。换而言之，若两个事件存在因果关联（一个事件发生在另一个事件之前），则二者存在明确的先后顺序；若两个事件是并发的，则二者之间**无法比较先后**。这意味着因果关系定义的是一种**偏序关系**，而非全序关系：部分操作之间存在明确的先后顺序，但部分操作之间无法比较。

Therefore, according to this definition, **there are no concurrent operations in a linearizable datastore**: there must be a single timeline along which all operations aretotally ordered. There might be several requests waiting to be handled, but the data‐store ensures that every request is handled atomically at a single point in time, actingon a single copy of the data, along a single timeline, without any concurrency.

因此，根据这个定义，**线性一致性数据存储中不存在并发操作**：所有操作必须沿着一条单一的时间线构成全序关系。系统中可能存在多个等待处理的请求，但数据存储会确保每个请求都在某个时间点被原子性地处理，基于唯一的数据副本、遵循单一的时间线执行，不存在任何并发情况。

Concurrency would mean that the timeline branches and merges again—and in thiscase, operations on different branches are incomparable (i.e., concurrent). We sawthis phenomenon in Chapter 5: for example, Figure 5-14 is not a straight-line totalorder, but rather a jumble of different operations going on concurrently. The arrowsin the diagram indicate causal dependencies—the partial ordering of operations.

并发意味着时间线会产生分支，之后又会合并 —— 在这种情况下，不同分支上的操作之间无法比较先后（即处于并发状态）。我们在第 5 章中已经见过这种现象：例如，图 5-14 所展示的并非一条线性的全序关系，而是多个操作并发执行的混杂状态。图中的箭头代表了因果依赖关系，也就是操作之间的偏序关系。

If you are familiar with distributed version control systems such as Git, their versionhistories are very much like the graph of causal dependencies. Often one commithappens after another, in a straight line, but sometimes you get branches (when sev‐eral people concurrently work on a project), and merges are created when those con‐currently created commits are combined.

如果你熟悉 Git 这类**分布式版本控制系统**，就会发现它们的版本历史与因果依赖关系图非常相似。版本提交通常会沿着一条直线依次进行，但有时也会产生分支（比如多人并发协作同一个项目时）；当这些并发创建的提交被整合到一起时，就会形成合并记录。



**Linearizability is stronger than causal consistency**

**线性一致性强于因果一致性**

So what is the relationship between the causal order and linearizability? The answer is that **linearizability implies causality**: any system that is linearizable will preserve causality correctly [7]. In particular, if there are multiple communication channels in asystem (such as the message queue and the file storage service in Figure 9-5), lineariz‐ability ensures that causality is automatically preserved without the system having todo anything special (such as passing around timestamps between different components).

那么，因果顺序与线性一致性之间存在怎样的关系？答案是**线性一致性蕴含因果一致性**：任何具备线性一致性的系统，都能正确地保持因果关系 [7]。具体来说，若系统中存在多条通信渠道（例如图 9-5 中的消息队列与文件存储服务），线性一致性可以确保因果关系被自动维持，无需系统采取任何特殊手段（比如在不同组件之间传递时间戳）。

The fact that linearizability ensures causality is what makes linearizable systems simple to understand and appealing. However, as discussed in “The Cost of Linearizability” on page 335, making a system linearizable can harm its performance andavailability, especially if the system has significant network delays (for example, if it’s geographically distributed). For this reason, some distributed data systems have abandoned linearizability, which allows them to achieve better performance but can make them difficult to work with.

线性一致性能够保障因果关系这一特性，让线性一致性系统易于理解且颇具吸引力。但正如第 335 页《线性一致性的成本》一节所讨论的，实现系统的线性一致性可能会损害其性能与可用性，在系统存在显著网络延迟的场景下（例如地理分布式系统），这种负面影响尤为突出。正因如此，部分分布式数据系统舍弃了线性一致性 —— 这一做法能换取更优的性能表现，但也会提升系统的使用难度。

The good news is that a middle ground is possible. Linearizability is not the only wayof preserving causality—there are other ways too. A system can be causally consistentwithout incurring the performance hit of making it linearizable (in particular, theCAP theorem does not apply). **In fact, causal consistency is the strongest possibleconsistency model that does not slow down due to network delays, and remains available in the face of network failures** [2, 42].

好消息是，我们可以找到一种**折中方案**。线性一致性并非保持因果关系的唯一方式，还存在其他替代方案。系统可以在不承担线性一致性带来的性能损耗的前提下，实现因果一致性（值得一提的是，这种情况下 CAP 定理不再适用）。实际上，因果一致性是这样一种一致性模型：它是**不会因网络延迟而降低速度、且在网络故障发生时仍能保持可用的最强一致性模型**[2,42]。

In many cases, systems that appear to require linearizability in fact only really require causal consistency, which can be implemented more efficiently. Based on this observation, researchers are exploring new kinds of databases that preserve causality, with performance and availability characteristics that are similar to those of eventually consistent systems [49, 50, 51].

在许多场景下，**看似需要线性一致性的系统**，实际上往往只需要因果一致性即可 —— 而因果一致性的实现效率更高。基于这一发现，研究人员正在探索**具备因果一致性保障能力的新型数据库**，这类数据库的性能与可用性表现，与最终一致性系统相近 [49,50,51]。



#### Sequence Number Ordering

**序列编号排序**

Although causality is an important theoretical concept, actually keeping track of allcausal dependencies can become impractical. In many applications, clients read lotsof data before writing something, and then it is not clear whether the write is causallydependent on all or only some of those prior reads. Explicitly tracking all the datathat has been read would mean a large overhead.

因果关系虽是一个重要的理论概念，但实际追踪所有因果依赖关系，往往不具备可行性。在诸多应用场景中，客户端会先读取大量数据，再执行写入操作，而此时我们很难界定，后续的写入操作是与此前所有的读取操作存在因果依赖，还是仅与其中部分读取操作有关。若要显式追踪所有已读取的数据，会产生极大的性能开销。

However, there is a better way: we can use sequence numbersor timestamps to orderevents. A timestamp need not come from a time-of-day clock (or physical clock,which have many problems, as discussed in “Unreliable Clocks” on page 287). It caninstead come from a logical clock, which is an algorithm to generate a sequence ofnumbers to identify operations, typically using counters that are incremented forevery operation.

不过，我们可以采用一种更优的方案：借助**序列编号**或**时间戳**来为事件排序。时间戳的来源不一定是日历时钟（即物理时钟，其存在诸多弊端，详见第 287 页的《不可靠时钟》），也可以来源于**逻辑时钟**。逻辑时钟是一种生成数字序列以标识操作的算法，通常会为每一次操作递增计数器，以此生成对应的编号。

Such sequence numbers or timestamps are compact (only a few bytes in size), andthey provide a **total order**: that is, every operation has a unique sequence number, andyou can always compare two sequence numbers to determine which is greater (i.e.,which operation happened later).

这类序列编号或时间戳具备**简洁性**（仅占用数个字节的存储空间），并且能够定义一种**全序关系**：也就是说，每一项操作都对应一个唯一的序列编号，通过对比任意两个序列编号的大小，我们就能判断出对应操作的先后顺序（编号更小的操作发生时间更早）。

In particular, we can create sequence numbers in a total order that is consistent withcausality:vii we promise that if operation A causally happened before B, then A occurs before B in the total order (A has a lower sequence number than B). Concurrentoperations may be ordered arbitrarily. Such a total order captures all the causalityinformation, but also imposes more ordering than strictly required by causality.

值得一提的是，我们可以生成一种与因果关系一致的全序序列编号：⁷ 我们保证，若操作 A 在因果关系上发生于操作 B 之前，那么在全序关系中，操作 A 也会排在操作 B 之前（即操作 A 的序列编号小于操作 B）。对于并发操作，则可按照任意顺序排列。这种全序关系既涵盖了所有因果信息，又施加了比因果关系严格得多的排序约束。

In a database with single-leader replication (see “Leaders and Followers” on page152), the replication log defines a total order of write operations that is consistentwith causality. The leader can simply increment a counter for each operation, andthus assign a monotonically increasing sequence number to each operation in thereplication log. If a follower applies the writes in the order they appear in the replica‐tion log, the state of the follower is always causally consistent (even if it is lagging behind the leader).

在采用**单主复制**的数据库中（详见第 152 页的《主节点与从节点》），复制日志定义了一套与因果关系一致的写入操作全序。主节点只需为每一次操作递增计数器，就能为复制日志中的每一项操作分配一个**单调递增**的序列编号。若从节点严格按照复制日志中的顺序执行写入操作，那么无论其同步进度是否落后于主节点，自身的数据状态都能始终保持**因果一致性**。



A Lamport timestamp bears no relationship to a physical time-of-day clock, but it provides **total ordering**: if you have two timestamps, the one with a greater countervalue is the greater timestamp; if the counter values are the same, the one with thegreater node ID is the greater timestamp.

**兰波特时间戳**与物理日历时钟毫无关联，但它能够实现**全序关系排序**：若存在两个时间戳，计数器数值更大的那个时间戳更大；若两个时间戳的计数器数值相同，则节点 ID 更大的那个时间戳更大。

So far this description is essentially the same as the even/odd counters described inthe last section. The key idea about Lamport timestamps, which makes them consis‐tent with causality, is the following: every node and every client keeps track of themaximum counter value it has seen so far, and includes that maximum on everyrequest. When a node receives a request or response with a maximum counter valuegreater than its own counter value, it immediately increases its own counter to thatmaximum.

截至目前，上述描述本质上与上一节提到的**奇偶计数器**机制完全一致。兰波特时间戳之所以能与因果关系保持一致，其核心设计思路如下：**每个节点与每个客户端都会记录自身迄今为止见过的最大计数器值，并在每次请求中附带该最大值**。当某个节点接收到的请求或响应中，携带的最大计数器值大于自身当前的计数器值时，该节点会立即将自身的计数器更新为这个最大值。

This is shown in Figure 9-8, where client A receives a counter value of 5 from node 2,and then sends that maximum of 5 to node 1. At that time, node 1’s counter was only1, but it was immediately moved forward to 5, so the next operation had an incre‐mented counter value of 6.

这一过程如图 9-8 所示：客户端 A 从节点 2 获取到计数器值 5，随后便将这个最大值 5 携带至发往节点 1 的请求中。此时，节点 1 自身的计数器值仅为 1，但它会立即将计数器更新为 5，因此其执行的下一次操作，对应的计数器值就会递增为 6。

![DDIA 9-8](../../images/distribuide_system/DDIA-9-8.jpg)

As long as the maximum counter value is carried along with every operation, thisscheme ensures that the ordering from the Lamport timestamps is consistent withcausality, because every causal dependency results in an increased timestamp.

只要每次操作都携带当前的最大计数器值，这套机制就能确保兰波特时间戳所定义的排序与因果关系一致 —— 因为每一个因果依赖关系，都会对应一个递增的时间戳。

#### Total Order Broadcast

**全序广播**

Total order broadcast is usually described as a protocol for exchanging messagesbetween nodes. Informally, it requires that two safety properties always be satisfied:

- **Reliable delivery** No messages are lost: if a message is delivered to one node, it is delivered to all nodes.
- **Totally ordered delivery** Messages are delivered to every node in the same order.

全序广播通常被定义为一种节点间的消息交换协议。通俗来讲，该协议要求始终满足以下两项**安全属性**：

- **可靠投递**：无消息丢失。若一条消息被投递至某一节点，就必须被投递至所有节点。
- **全序投递**：所有节点接收消息的顺序完全一致。

A correct algorithm for total order broadcast must ensure that the reliability and ordering properties are always satisfied, even if a node or the network is faulty. Of course, messages will not be delivered while the network is interrupted, but an algorithm can keep retrying so that the messages get through when the network is eventually repaired (and then they must still be delivered in the correct order).

一个正确的全序广播算法，必须确保上述可靠性与有序性属性始终成立，即便是在节点或网络发生故障的情况下。当然，网络中断期间消息无法完成投递，但算法可以持续重试，确保网络恢复后消息能够成功送达（且送达时仍需遵循既定的正确顺序）。

**Using total order broadcast**

**全序广播的应用场景**

Consensus services such as ZooKeeper and etcd actually implement total orderbroadcast. This fact is a hint that there is a strong connection between total orderbroadcast and consensus, which we will explore later in this chapter.

ZooKeeper、etcd 这类**共识服务**的底层，实际上都实现了全序广播机制。这一特性也暗示了全序广播与共识之间存在紧密的关联，我们将在本章后续内容中深入探讨这一点。

Total order broadcast is exactly what you need for database replication: if every mes‐sage represents a write to the database, and every replica processes the same writes inthe same order, then the replicas will remain consistent with each other (aside fromany temporary replication lag). This principle is known as **state machine replication**[60], and we will return to it in Chapter 11.

全序广播的特性，恰好满足数据库复制的核心需求：如果每条消息对应一次数据库写入操作，且所有副本都按照相同顺序处理这些写入请求，那么各副本之间的数据状态就能保持一致（暂不考虑暂时性的复制延迟）。这一实现原理被称为**状态机复制**[60]，我们会在第 11 章中进一步展开讨论。

Similarly, total order broadcast can be used to implement **serializable transactions**: asdiscussed in “Actual Serial Execution” on page 252, if every message represents adeterministic transaction to be executed as a stored procedure, and if every node pro‐cesses those messages in the same order, then the partitions and replicas of the data‐base are kept consistent with each other [61].

同理，全序广播也可用于实现**可串行化事务**：正如第 252 页《实际串行执行》一节所述，若每条消息对应一个可作为存储过程执行的确定性事务，且所有节点都按同一顺序处理这些消息，那么数据库的各个分区与副本就能维持数据一致性 [61]。

An important aspect of total order broadcast is that the order is fixed at the time themessages are delivered: a node is not allowed to retroactively insert a message into anearlier position in the order if subsequent messages have already been delivered. Thisfact makes total order broadcast stronger than timestamp ordering.

全序广播的一个关键特性在于，消息的投递顺序在送达时即被固定：如果后续消息已经完成投递，节点就不能再将新消息回溯插入到顺序中的靠前位置。这一特性使得全序广播的排序能力，要强于基于时间戳的排序方式。

Another way of looking at total order broadcast is that it is a way of creating a **log** (asin a replication log, transaction log, or write-ahead log): delivering a message is likeappending to the log. Since all nodes must deliver the same messages in the sameorder, all nodes can read the log and see the same sequence of messages.

从另一个角度理解，全序广播相当于构建了一份**日志**（类似复制日志、事务日志或预写式日志）：投递消息的过程，就等同于向日志中追加内容。由于所有节点接收消息的顺序完全一致，因此它们读取这份日志时，看到的消息序列也完全相同。

Total order broadcast is also useful for implementing a lock service that provides **fencing tokens** (see “Fencing tokens” on page 303). Every request to acquire the lockis appended as a message to the log, and all messages are sequentially numbered inthe order they appear in the log. The sequence number can then serve as a fencingtoken, because it is monotonically increasing. In ZooKeeper, this sequence number is called **zxid** [15].

全序广播还可用于实现支持**围栏令牌**的锁服务（详见第 303 页《围栏令牌》）。所有获取锁的请求都会作为消息追加到日志中，日志中的消息会按照顺序被分配一个连续的序列号。这个序列号即可作为围栏令牌，因为它具备单调递增的特性。在 ZooKeeper 中，该序列号被称为 **zxid**[15]。

**Implementing linearizable storage using total order broadcast**

**基于全序广播实现线性化存储**

Total order broadcast is asynchronous: messages are guaranteed to be delivered relia‐bly in a fixed order, but there is no guarantee about when a message will be delivered(so one recipient may lag behind the others). By contrast, linearizability is a recencyguarantee: a read is guaranteed to see the latest value written.

全序广播是**异步**的：它能确保消息以固定顺序实现可靠投递，但并不保证消息的投递时间（因此部分接收方可能会落后于其他节点）。相比之下，**线性化**是一种**最新值保证**：读取操作一定能获取到最新写入的数据值。

However, if you have total order broadcast, you can build linearizable storage on topof it. For example, you can ensure that usernames uniquely identify user accounts.

不过，基于全序广播机制，我们可以构建出线性化存储。例如，利用这一方式能够确保用户名可以唯一标识用户账户。

Imagine that for every possible username, you can have a linearizable register with anatomic compare-and-set operation. Every register initially has the value null (indi‐ cating that the username is not taken). When a user wants to create a username, youexecute a compare-and-set operation on the register for that username, setting it tothe user account ID, under the condition that the previous register value is null. Ifmultiple users try to concurrently grab the same username, only one of the compare-and-set operations will succeed, because the others will see a value other than null (due to linearizability).

我们可以这样设想：为每一个可能被使用的用户名配置一个线性化寄存器，该寄存器支持**原子化比较并设置操作**。所有寄存器的初始值均为 `null`（表示对应的用户名尚未被占用）。当用户想要注册某一用户名时，就对该用户名对应的寄存器执行比较并设置操作 —— 若寄存器当前值为 `null`，则将其更新为该用户的账户 ID。

You can implement such a linearizable compare-and-set operation as follows byusing total order broadcast as an **append-only log** [62, 63]:

1. Append a message to the log, tentatively indicating the username you want to claim.
2. Read the log, and wait for the message you appended to be delivered back to you.xi
3. Check for any messages claiming the username that you want. If the first message for your desired username is your own message, then you are successful: you can commit the username claim (perhaps by appending another message to the log) and acknowledge it to the client. If the first message for your desired username is from another user, you abort the operation.

借助全序广播构建一个**追加式日志**，我们就能实现上述的线性化比较并设置操作，具体流程如下 [62, 63]：

1. 向日志中追加一条消息，暂存声明要占用的用户名相关信息。
2. 读取日志内容，并等待自己追加的这条消息被回传给自身。
3. 检查日志中是否存在其他声明占用该用户名的消息。
   - 若针对该用户名的第一条声明消息来自于自身，则操作成功：你可以提交用户名占用声明（方式之一是向日志中再追加一条确认消息），并向客户端返回操作成功的响应。
   - 若针对该用户名的第一条声明消息来自其他用户，则终止本次操作。

Because log entries are delivered to all nodes in the same order, if there are severalconcurrent writes, all nodes will agree on which one came first. Choosing the first ofthe conflicting writes as the winner and aborting later ones ensures that all nodesagree on whether a write was committed or aborted. A similar approach can be usedto implement **serializable multi-object transactions** on top of a log [62].

由于**日志条目**会以相同的顺序投递至所有节点，因此即便存在多笔并发写入操作，所有节点也会对这些操作的先后顺序形成一致共识。我们可以将存在冲突的写入操作中，排在首位的那一笔判定为执行成功，其余后续操作则终止执行。这种处理方式能够确保所有节点对某笔写入操作最终是提交还是终止，达成完全一致的结论。基于类似的思路，我们还可以在日志之上实现支持**可串行化的多对象事务**[62]。

While this procedure ensures linearizable writes, it doesn’t guarantee linearizablereads—if you read from a store that is asynchronously updated from the log, it maybe stale. (To be precise, the procedure described here provides **sequential consistency**[47, 64], sometimes also known as **timeline consistency** [65, 66], a slightly weakerguarantee than linearizability.) To make reads linearizable, there are a few options:

- You can sequence reads through the log by appending a message, reading the log,and performing the actual read when the message is delivered back to you. The message’s position in the log thus defines the point in time at which the read happens. (Quorum reads in etcd work somewhat like this [16].)
- If the log allows you to fetch the position of the latest log message in a linearizable way, you can query that position, wait for all entries up to that position to be delivered to you, and then perform the read. (This is the idea behind Zoo‐ Keeper’s sync() operation [15].)
- You can make your read from a replica that is synchronously updated on writes,and is thus sure to be up to date. (This technique is used in chain replication [63]; see also “Research on Replication” on page 155.)

上述流程虽能保障写入操作的线性化，但无法确保读取操作的线性化 —— 如果读取操作的数据源是一个通过日志异步更新的存储副本，那么读取到的数据就可能是过期的。（准确来说，此处描述的流程提供的是**顺序一致性**[47, 64]，该一致性模型有时也被称为**时间线一致性**[65, 66]，其保障强度略低于线性化一致性。）若要实现线性化读取，可采用以下几种方案：

1. 将读取操作也纳入日志的排序流程：先向日志中追加一条消息，随后读取日志内容，待这条消息被回传至自身时，再执行实际的读取操作。如此一来，该消息在日志中的位置，就定义了读取操作发生的时间点。（etcd 中的**仲裁读**机制，工作原理与此类似 [16]。）
2. 如果日志支持以线性化的方式获取最新日志条目的位置，那么可以先查询该位置，等待所有序号不大于该位置的日志条目全部投递至本地后，再执行读取操作。（这正是 ZooKeeper 中 `sync()` 操作的设计思路 [15]。）
3. 选择从一个**写入同步更新**的副本中读取数据，这类副本的数据状态可以确保是实时最新的。（该技术被应用于**链式复制**协议中 [63]；相关内容亦可参考第 155 页的《复制技术研究》。）

**Implementing total order broadcast using linearizable storage**

**基于线性化存储实现全序广播**

The last section showed how to build a linearizable compare-and-set operation from total order broadcast. We can also turn it around, assume that we have linearizable storage, and show how to build total order broadcast from it.

上一节介绍了如何基于全序广播实现线性化比较并设置操作。我们也可以**反过来**，假设已经具备线性化存储能力，再基于它来构建全序广播机制。

The easiest way is to assume you have a linearizable register that stores an integer andthat has an **atomic increment-and-get operation** [28]. Alternatively, an atomic compare-and-set operation would also do the job.

实现这一目标的最简方式，是假定存在一个存储整数的线性化寄存器，且该寄存器支持**原子化自增获取操作**[28]。当然，使用原子化比较并设置操作也能达成同样的效果。

The algorithm is simple: for every message you want to send through total orderbroadcast, you increment-and-get the linearizable integer, and then attach the valueyou got from the register as a sequence number to the message. You can then sendthe message to all nodes (resending any lost messages), and the recipients will deliverthe messages consecutively by sequence number.

对应的算法十分简洁：对于每一条需要通过全序广播发送的消息，先对这个线性化整数执行原子化自增获取操作，再将从寄存器中获取的数值作为**序列号**附加到消息上。随后，将这条消息发送至所有节点（并重发所有丢失的消息），接收方则按照序列号的顺序依次投递消息。

Note that unlike Lamport timestamps, the numbers you get from incrementing the linearizable register form a **sequence with no gaps**. Thus, if a node has delivered mes‐sage 4 and receives an incoming message with a sequence number of 6, it knows thatit must wait for message 5 before it can deliver message 6. The same is not the case with Lamport timestamps—in fact, this is the key difference between total order broadcast and timestamp ordering.

需要注意的是，与兰波特时间戳不同，通过线性化寄存器自增得到的数值，生成的是一个**无间隙的连续序列**。因此，若某个节点已经投递了序列号为 4 的消息，此时收到一条序列号为 6 的消息，就知道必须先等待消息 5 投递完成，再处理消息 6。而兰波特时间戳则不具备这一特性 —— 实际上，这正是全序广播与时间戳排序的**核心区别**。

How hard could it be to make a linearizable integer with an atomic increment-and-get operation? As usual, if things never failed, it would be easy: you could just keep itin a variable on one node. The problem lies in handling the situation when networkconnections to that node are interrupted, and restoring the value when that node fails[59]. In general, if you think hard enough about linearizable sequence number gener‐ators, you inevitably end up with a **consensus algorithm**.

实现一个支持原子化自增获取操作的线性化整数寄存器，难度究竟有多大？和大多数分布式问题一样，如果系统永远不会发生故障，这件事会非常简单：只需在单个节点上用一个变量存储该整数即可。真正的难点在于，如何处理与该节点的网络连接中断的情况，以及节点故障后如何恢复该数值 [59]。通常来说，只要深入研究线性化序列号生成器的实现方案，最终都会不可避免地触及**共识算法**。

This is no coincidence: it can be proved that a **linearizable compare-and-set (orincrement-and-get) register** and **total order broadcast** are both **equivalent to consensus** [28, 67]. That is, if you can solve one of these problems, you can transform it intoa solution for the others. This is quite a profound and surprising insight!

这并非偶然现象：已有相关证明表明，支持原子化比较并设置（或自增获取）操作的线性化寄存器、全序广播，这两者在本质上都**与共识问题等价**[28, 67]。也就是说，只要能解决其中任意一个问题，就能将其转化为解决另外两个问题的方案。这是一个深刻且出人意料的结论！

### Distributed Transactions and Consensus

**分布式事务与共识**

 In this section we will first examine the atomic commit problem in more detail. Inparticular, we will discuss the two-phase commit (2PC) algorithm, which is the mostcommon way of solving atomic commit and which is implemented in various data‐bases, messaging systems, and application servers. It turns out that 2PC is a kind ofconsensus algorithm—but not a very good one [70, 71].

在本节中，我们将首先深入探讨**原子提交问题**。具体而言，我们会介绍**两阶段提交（2PC）算法**—— 这是解决原子提交问题最常用的方案，已在各类数据库、消息系统及应用服务器中落地实现。事实证明，2PC 本质上属于一种共识算法，只是其性能与可靠性表现并不算出色 [70, 71]。

By learning from 2PC we will then work our way toward better consensus algorithms,such as those used in ZooKeeper (Zab) and etcd (Raft).

我们将从 2PC 的设计思路与局限性中汲取经验，进而介绍性能更优的共识算法，例如 ZooKeeper 所采用的 Zab 算法与 etcd 所采用的 Raft 算法。

#### Atomic Commit and Two-Phase Commit (2PC)

**原子提交与两阶段提交（2PC）**

In Chapter 7 we learned that the purpose of **transaction atomicity** is to provide sim‐ple semantics in the case where something goes wrong in the middle of making several writes. The outcome of a transaction is either a **successful commit**, in which caseall of the transaction’s writes are made durable, or an **abort**, in which case all of thetransaction’s writes are rolled back (i.e., undone or discarded).

在第 7 章中我们已经了解到，**事务原子性**的设计目标，是在多笔写入操作执行过程中发生异常时，为系统提供简洁清晰的执行语义。事务的最终结果只有两种可能：要么**成功提交**，此时事务内的所有写入操作都会被持久化；要么**执行回滚**，此时事务内的所有写入操作都会被撤销（即取消或丢弃已执行的修改）。

Atomicity prevents failed transactions from littering the database with half-finished results and half-updated state. This is especially important for **multi-object transactions** (see “Single-Object and Multi-Object Operations” on page 228) and databasesthat maintain secondary indexes. Each secondary index is a separate data structurefrom the primary data—thus, if you modify some data, the corresponding changeneeds to also be made in the secondary index. Atomicity ensures that the secondaryindex stays consistent with the primary data (if the index became inconsistent withthe primary data, it would not be very useful).

原子性能够避免未完成的操作结果和半更新状态充斥数据库，这一点对于**多对象事务**（详见第 228 页《单对象与多对象操作》）以及维护二级索引的数据库而言，尤为关键。每一个二级索引都是独立于主数据的单独数据结构 —— 因此，当主数据被修改时，对应的二级索引也必须同步更新。原子性保障了二级索引与主数据的一致性（若索引与主数据出现不一致，其本身的价值就会大打折扣）。

**From single-node to distributed atomic commit**

**从单节点原子提交到分布式原子提交**

For transactions that execute at a single database node, atomicity is commonly imple‐mented by the storage engine. When the client asks the database node to commit thetransaction, the database makes the transaction’s writes durable (typically in a write-ahead log; see “Making B-trees reliable” on page 82) and then appends a **commit record** to the log on disk. If the database crashes in the middle of this process, thetransaction is recovered from the log when the node restarts: if the commit recordwas successfully written to disk before the crash, the transaction is considered com‐mitted; if not, any writes from that transaction are rolled back.

对于仅在单个数据库节点上执行的事务，原子性通常由存储引擎直接实现。当客户端向数据库节点发起事务提交请求时，数据库会先将事务的写入操作持久化（通常是写入预写式日志，详见第 82 页《保障 B 树的可靠性》），随后在磁盘日志中追加一条**提交记录**。若数据库在这一过程中发生崩溃，节点重启时会从日志中恢复事务状态：如果崩溃发生前，提交记录已成功写入磁盘，则判定该事务已提交；反之，则回滚该事务的所有写入操作。

Thus, on a single node, transaction commitment crucially depends on the order inwhich data is durably written to disk: first the data, then the commit record [72]. Thekey deciding moment for whether the transaction commits or aborts is the momentat which the disk finishes writing the commit record: before that moment, it is stillpossible to abort (due to a crash), but after that moment, the transaction is commit‐ted (even if the database crashes). Thus, it is a single device (the controller of one par‐ticular disk drive, attached to one particular node) that makes the commit atomic.

由此可见，在单节点场景下，事务能否成功提交，关键取决于数据持久化到磁盘的顺序：必须先写入业务数据，再写入提交记录 [72]。事务提交或回滚的**核心判定节点**，是磁盘完成提交记录写入的那一刻：在此之前，事务仍有因系统崩溃而被回滚的可能；而在此之后，无论数据库是否崩溃，该事务都已被判定为提交状态。因此，单节点事务的原子提交，实际上是由单个设备（即与该节点相连的某一磁盘驱动器的控制器）来保证的。

However, what if multiple nodes are involved in a transaction? For example, perhapsyou have a multi-object transaction in a partitioned database, or a term-partitionedsecondary index (in which the index entry may be on a different node from the pri‐mary data; see “Partitioning and Secondary Indexes” on page 206). Most “NoSQL”distributed datastores do not support such distributed transactions, but various clus‐tered relational systems do (see “Distributed Transactions in Practice” on page 360).

但如果事务涉及多个节点，情况又会如何？例如，在分区数据库中执行多对象事务，或是操作按词条分区的二级索引（索引条目与主数据可能存储在不同节点上，详见第 206 页《分区与二级索引》）。大多数 “非关系型” 分布式数据存储系统不支持此类分布式事务，但许多集群式关系型数据库系统对此提供了支持（详见第 360 页《实践中的分布式事务》）。

In these cases, it is not sufficient to simply send a commit request to all of the nodesand independently commit the transaction on each one. In doing so, it could easilyhappen that the commit succeeds on some nodes and fails on other nodes, whichwould violate the atomicity guarantee:

- Some nodes may detect a constraint violation or conflict, making an abort necessary, while other nodes are successfully able to commit.
- Some of the commit requests might be lost in the network, eventually aborting due to a timeout, while other commit requests get through.
- Some nodes may crash before the commit record is fully written and roll back on recovery, while others successfully commit.

在分布式场景中，简单地向所有节点发送提交请求、并让各节点独立提交事务的做法是行不通的。这种方式极易导致部分节点提交成功、部分节点提交失败，从而违背原子性保障，具体原因如下：

1. 部分节点可能检测到约束违规或数据冲突，必须执行回滚操作，而其他节点却能够成功提交事务。
2. 部分提交请求可能在网络传输中丢失，最终因超时而触发回滚，而其他提交请求则成功送达并执行。
3. 部分节点可能在提交记录完全写入磁盘前发生崩溃，重启后会回滚事务，而其他节点则成功完成提交。

If some nodes commit the transaction but others abort it, the nodes become inconsis‐tent with each other (like in Figure 7-3). And once a transaction has been committedon one node, it cannot be retracted again if it later turns out that it was aborted onanother node. For this reason, a node must only commit once it is certain that allother nodes in the transaction are also going to commit.

若部分节点提交了事务，而另一些节点执行了回滚，节点之间的状态就会出现不一致（如图 7-3 所示）。而且，事务一旦在某一节点提交，即便后续发现其他节点执行了回滚，也无法撤销该节点的提交操作。正因如此，任一节点都必须在确认**事务涉及的所有其他节点均会提交**后，才能执行自身的提交操作。

A transaction commit must be irrevocable—you are not allowed to change yourmind and retroactively abort a transaction after it has been committed. The reasonfor this rule is that once data has been committed, it becomes visible to other transac‐tions, and thus other clients may start relying on that data; this principle forms thebasis of read committedisolation, discussed in “Read Committed” on page 234. If atransaction was allowed to abort after committing, any transactions that read thecommitted data would be based on data that was retroactively declared not to haveexisted—so they would have to be reverted as well.

事务的提交操作必须是**不可撤销**的 —— 事务提交后，不允许再改变决策，对其进行回溯性回滚。制定这条规则的原因在于：事务提交后，其修改的数据会对其他事务可见，其他客户端可能会基于这些数据执行新的操作；这一原则正是**读已提交隔离级别**的设计基础（详见第 234 页《读已提交》）。若允许事务提交后再执行回滚，所有读取过该事务提交数据的其他事务，就会基于 “事后被宣告为不存在” 的数据进行操作 —— 这些事务同样需要被回滚，这会造成连锁反应。

(It is possible for the effects of a committed transaction to later be undone byanother, compensating transaction [73, 74]. However, from the database’s point ofview this is a separate transaction, and thus any cross-transaction correctnessrequirements are the application’s problem.)

（当然，已提交事务产生的影响，后续可通过另一个独立的**补偿事务**来抵消 [73,74]。但从数据库的角度来看，补偿事务属于全新的独立事务，因此，跨事务的一致性保障需求，需要由业务应用层自行处理。）



**Coordinator failure**

**协调者故障**

We have discussed what happens if one of the participants or the network fails during2PC: if any of the prepare requests fail or time out, the coordinator aborts the trans‐action; if any of the commit or abort requests fail, the coordinator retries them indefinitely. However, it is less clear what happens if the coordinator crashes.

我们已经讨论过，在两阶段提交（2PC）过程中，若某个参与者或网络发生故障会出现何种情况：若任一预提交请求失败或超时，协调者则会中止该事务；若任一提交或中止请求失败，协调者会无限重试这些请求。但协调者若发生崩溃，后续的处理逻辑则相对复杂。

If the coordinator fails before sending the prepare requests, a participant can safelyabort the transaction. But once the participant has received a prepare request andvoted “yes,” it can no longer abort unilaterally—it must wait to hear back from thecoordinator whether the transaction was committed or aborted. If the coordinatorcrashes or the network fails at this point, the participant can do nothing but wait. Aparticipant’s transaction in this state is called in doubtor uncertain.

如果协调者在发送预提交请求之前崩溃，参与者可以安全地中止该事务。但一旦参与者收到预提交请求并投票同意，它就不能再单方面中止事务 —— 必须等待协调者反馈，确认该事务最终是提交还是中止。若此时协调者崩溃或网络发生故障，参与者除了等待外别无选择。处于这种状态的参与者事务，被称为**疑态事务**或**未决事务**。

The situation is illustrated in Figure 9-10. In this particular example, the coordinatoractually decided to commit, and database 2 received the commit request. However,the coordinator crashed before it could send the commit request to database 1, and sodatabase 1 does not know whether to commit or abort. Even a timeout does not helphere: if database 1 unilaterally aborts after a timeout, it will end up inconsistent withdatabase 2, which has committed. Similarly, it is not safe to unilaterally commit,because another participant may have aborted.

这种情况可通过图 9-10 来阐释。在这个具体示例中，协调者实际上已经决定提交事务，且数据库 2 也已收到提交请求。但协调者在向数据库 1 发送提交请求前发生崩溃，导致数据库 1 无法确定应该提交还是中止事务。此时，即使等待超时也无济于事：如果数据库 1 在超时后单方面中止事务，会与已执行提交操作的数据库 2 产生数据不一致；同理，单方面提交也存在风险，因为其他参与者有可能已经中止了事务。

![微信图片_20260122232117_189_109](../../images/distribuide_system/Figure-9-10.jpg)

Without hearing from the coordinator, the participant has no way of knowingwhether to commit or abort. In principle, the participants could communicate amongthemselves to find out how each participant voted and come to some agreement, butthat is not part of the 2PC protocol.

在未收到协调者反馈的情况下，参与者无法判断应该执行提交还是中止操作。理论上，参与者之间可以互相通信，确认彼此的投票结果并达成一致决议，但这并不属于两阶段提交协议的范畴。

The only way 2PC can complete is by waiting for the coordinator to recover. This iswhy the coordinator must write its commit or abort decision to a transaction log ondisk before sending commit or abort requests to participants: when the coordinatorrecovers, it determines the status of all in-doubt transactions by reading its transac‐tion log. Any transactions that don’t have a commit record in the coordinator’s logare aborted. Thus, the commit point of 2PC comes down to a regular single-nodeatomic commit on the coordinator.

两阶段提交协议能够完成事务处理的唯一方式，就是等待协调者恢复。这也是为什么协调者必须在向参与者发送提交或中止请求之前，将自身的提交 / 中止决策写入磁盘上的事务日志：当协调者恢复后，会通过读取事务日志来确定所有疑态事务的状态。凡是在协调者日志中没有提交记录的事务，一律视为中止。由此可见，两阶段提交的提交点，最终取决于协调者节点上一次常规的单节点原子提交操作。



#### Fault-Tolerant Consensus

**容错共识**

Informally, consensus means getting several nodes to agree on something. For exam‐ple, if several people concurrently try to book the last seat on an airplane, or the same seat in a theater, or try to register an account with the same username, then a consensus algorithm could be used to determine which one of these mutually incompatible operations should be the winner.

通俗来讲，共识的含义是让多个节点就某一事项达成一致意见。例如，当多个人同时尝试预订某架飞机的最后一个座位、某剧院的同一个座位，或是注册同一个用户名时，就可以借助共识算法来判定，在这些互斥的操作中哪一个能够最终生效。

The consensus problem is normally formalized as follows: one or more nodes mayproposevalues, and the consensus algorithm decides on one of those values. In theseat-booking example, when several customers are concurrently trying to buy the lastseat, each node handling a customer request may propose the ID of the customer it isserving, and the decision indicates which one of those customers got the seat.

共识问题的形式化定义通常如下：一个或多个节点可以**提议**某个值，共识算法则从这些提议的值中选定一个作为最终决议。以座位预订的场景为例，当多名客户同时抢购最后一个座位时，每个处理客户请求的节点都可以提议自己所服务客户的 ID，而算法的最终决议则会明确哪一位客户成功订到该座位。

In this formalism, a consensus algorithm must satisfy the following properties [25]:

- **Uniform agreemen**t No two nodes decide differently.
- **Integrity** No node decides twice.
- **Validity** If a node decides value v, then v was proposed by some node.
- **Termination** Every node that does not crash eventually decides some value.

在这一形式化定义下，一个共识算法必须满足以下四个特性 [25]：

1. **统一一致性**：所有节点的最终决议结果完全一致，不存在分歧。
2. **完整性**：任何节点都不会做出两次及以上的决议。
3. **有效性**：若某节点决议的值为`v`，则`v`必定是由某个节点提出的提议值。
4. **终止性**：所有未发生崩溃的节点，最终都会得出一个确定的决议。

The uniform agreement and integrity properties define the core idea of consensus:everyone decides on the same outcome, and once you have decided, you cannotchange your mind. The validity property exists mostly to rule out trivial solutions: forexample, you could have an algorithm that always decides null, no matter what wasproposed; this algorithm would satisfy the agreement and integrity properties, butnot the validity property.

统一一致性与完整性定义了共识的核心内涵：所有参与者的决议结果保持一致，且一旦做出决议，便不可更改。有效性这一特性的存在，主要是为了排除无意义的方案。例如，存在这样一种算法，无论节点提出何种提议值，它始终将`null`作为决议结果 —— 该算法虽然满足一致性和完整性，但并不满足有效性。

The **termination** property formalizes the idea of fault tolerance. It essentially says thata consensus algorithm cannot simply sit around and do nothing forever—in otherwords, it must make progress. Even if some nodes fail, the other nodes must stillreach a decision. (Termination is a liveness property, whereas the other three aresafety properties—see “Safety and liveness” on page 308.) 

终止性则是对**容错性**的形式化描述。其核心要义是，共识算法不能无限期地处于停滞状态，换句话说，它必须能够持续推进流程。即使部分节点发生故障，其余正常节点仍需达成最终决议。（终止性属于**活性属性**，而另外三个特性则属于**安全性属性**—— 参见第 308 页的 “安全性与活性”）。

The system model of consensus assumes that when a node “crashes,” it suddenly dis‐appears and never comes back. (Instead of a software crash, imagine that there is anearthquake, and the datacenter containing your node is destroyed by a landslide. Youmust assume that your node is buried under 30 feet of mud and is never going tocome back online.) In this system model, any algorithm that has to wait for a node torecover is not going to be able to satisfy the termination property. In particular, 2PCdoes not meet the requirements for termination.

共识算法的系统模型假定，当一个节点发生 “崩溃” 时，会直接停止运行且永不恢复。（这里可以抛开软件崩溃的场景想象一下：假如发生地震，承载节点的机房因山体滑坡被摧毁，你必须认定这个节点被埋在 30 英尺深的淤泥下，再也无法上线运行）。在该系统模型中，任何需要等待故障节点恢复后才能继续推进的算法，都无法满足终止性要求。**两阶段提交（2PC）** 正是如此，它不符合终止性的相关要求。

Of course, if all nodes crash and none of them are running, then it is not possible forany algorithm to decide anything. There is a limit to the number of failures that analgorithm can tolerate: in fact, it can be proved that any consensus algorithm requiresat least a majority of nodes to be functioning correctly in order to assure termination[67]. That majority can safely form a quorum (see “Quorums for reading and writ‐ing” on page 179).

当然，如果所有节点全部崩溃且无一正常运行，那么任何算法都无法做出任何决议。算法的容错能力存在上限：事实上，经证明，任何共识算法要想保证终止性，都需要至少**超过半数的节点保持正常运行**[67]。这部分占多数的节点能够可靠地构成一个**法定人数**（参见第 179 页的 “读写操作的法定人数机制”）。

Thus, the termination property is subject to the assumption that fewer than half ofthe nodes are crashed or unreachable. However, most implementations of consensusensure that the safety properties—agreement, integrity, and validity—are always met,even if a majority of nodes fail or there is a severe network problem [92]. Thus, alarge-scale outage can stop the system from being able to process requests, but it can‐not corrupt the consensus system by causing it to make invalid decisions.

因此，终止性的成立，是以**发生崩溃或无法连通的节点数量不超过总数的一半**为前提的。不过，绝大多数共识算法的实现都能确保，即便超过半数节点发生故障或出现严重的网络问题，**安全性属性**（一致性、完整性、有效性）也始终能够得到满足 [92]。也就是说，大规模故障可能会导致系统无法处理请求，但绝不会使共识系统做出无效决议，进而破坏系统的一致性。

**Consensus algorithms and total order broadcast**

**共识算法与全序广播**

The best-known fault-tolerant consensus algorithms are **Viewstamped Replication(VSR)** [94, 95], **Paxos** [96, 97, 98, 99], **Raft** [22, 100, 101], and **Zab** [15, 21, 102]. Thereare quite a few similarities between these algorithms, but they are not the same [103].In this book we won’t go into full details of the different algorithms: it’s sufficient tobe aware of some of the high-level ideas that they have in common, unless you’reimplementing a consensus system yourself (which is probably not advisable—it’shard [98, 104]).

最知名的容错共识算法包括**Viewstamped Replication，VSR**[94, 95]、**Paxos**[96, 97, 98, 99]、**Raft**[22, 100, 101] 以及 **Zab **[15, 21, 102]。这些算法之间存在诸多相似之处，但并非完全相同 [103]。本书不会深入探讨各类算法的完整细节 —— 只要了解它们共通的核心设计思路就足够了，除非你需要亲自实现一个共识系统（通常并不推荐，因为这项工作的难度极高 [98, 104]）。

Most of these algorithms actually don’t directly use the formal model described here(proposing and deciding on a single value, while satisfying the agreement, integrity,validity, and termination properties). Instead, they decide on a sequence of values,which makes them **total order broadcast** algorithms, as discussed previously in thischapter (see “Total Order Broadcast” on page 348).

事实上，这些算法大多并未直接采用前文所述的形式化模型（即对单一值进行提议与决议，同时满足一致性、完整性、有效性和终止性这四项特性）。相反，它们会对**一系列值**进行决议，这就使它们具备了全序广播算法的属性，相关内容已在本章前文提及（参见本书第 348 页的 “全序广播” 一节）。

Remember that total order broadcast requires messages to be delivered exactly once,in the same order, to all nodes. If you think about it, this is equivalent to performingseveral rounds of consensus: in each round, nodes propose the message that theywant to send next, and then decide on the next message to be delivered in the totalorder [67].

回顾一下，全序广播的核心要求是：**每条消息均仅投递一次，且所有节点收到的消息顺序完全一致**。细究起来，这一要求等价于执行多轮共识过程：在每一轮共识中，各节点提议自己接下来要发送的消息，然后共同决议出下一条要按全序投递的消息 [67]。

So, **total order broadcast is equivalent to repeated rounds of consensus** (each consen‐sus decision corresponding to one message delivery):

- Due to the **agreement property** of consensus, all nodes decide to deliver the same messages in the same order.
- Due to the **integrity property**, messages are not duplicated.
- Due to the **validity property**, messages are not corrupted and not fabricated out of thin air.
- Due to the **termination property**, messages are not lost.

由此可见，**全序广播等价于重复执行多轮共识**（每一次共识决议对应一条消息的投递），具体对应关系如下：

1. 得益于共识算法的**一致性**特性，所有节点会按照完全相同的顺序投递相同的消息。
2. 得益于共识算法的**完整性**特性，消息不会被重复投递。
3. 得益于共识算法的**有效性**特性，消息不会被篡改，也不会凭空生成无中生有的消息。
4. 得益于共识算法的**终止性**特性，消息不会丢失。

Viewstamped Replication, Raft, and Zab implement total order broadcast directly,because that is more efficient than doing repeated rounds of one-value-at-a-timeconsensus. In the case of Paxos, this optimization is known as Multi-Paxos.

Viewstamped Replication、Raft 与 Zab 均直接实现了全序广播功能，相比重复执行单值共识的方式，这种设计的效率更高。而在 Paxos 算法中，此类优化被称为**Multi-Paxos**。

**Single-leader replication and consensus**

**单主复制与共识**

In Chapter 5 we discussed single-leader replication (see “Leaders and Followers” onpage 152), which takes all the writes to the leader and applies them to the followers inthe same order, thus keeping replicas up to date. Isn’t this essentially total orderbroadcast? How come we didn’t have to worry about consensus in Chapter 5?

在本书第 5 章中，我们探讨过单主复制机制（参见第 152 页的 “主节点与从节点” 一节）。该机制会将所有写操作都路由至主节点，再按相同顺序同步至所有从节点，从而保证所有副本数据一致。这本质上不就是全序广播吗？那为什么在第 5 章中，我们完全不需要考虑共识相关的问题呢？

The answer comes down to how the leader is chosen. If the leader is manually chosenand configured by the humans in your operations team, you essentially have a “con‐sensus algorithm” of the dictatorial variety: only one node is allowed to accept writes(i.e., make decisions about the order of writes in the replication log), and if that nodegoes down, the system becomes unavailable for writes until the operators manuallyconfigure a different node to be the leader. Such a system can work well in practice,but it does not satisfy the termination property of consensus because it requireshuman intervention in order to make progress.

答案的核心在于**主节点的选举方式**。如果主节点是由运维人员手动选定并配置的，那么这种模式本质上就是一种**集权式 “共识算法”**：仅允许单个节点接收写操作（即由该节点决定复制日志中写操作的执行顺序）；一旦该主节点发生故障，系统的写服务就会陷入不可用状态，直到运维人员手动将另一个节点配置为主节点为止。这类系统在实际场景中可以稳定运行，但它并不满足共识算法的终止性要求 —— 因为系统的持续运转需要人工介入。

**Epoch numbering and quorums**

**纪元编号与法定人数**

All of the consensus protocols discussed so far internally use a leader in some form oranother, but they don’t guarantee that the leader is unique. Instead, they can make aweaker guarantee: the protocols define an **epoch number**(called the **ballot number** in Paxos, **view number** in Viewstamped Replication, and **term number** in Raft) and guarantee that within each epoch, the leader is unique.

前文讨论的所有共识协议，在内部都会以某种形式引入主节点，但这些协议并不保证主节点的唯一性。相反，它们只能做出一个较弱的保证：协议会定义一个**纪元编号**（在Paxos中被称为**表决编号**，在Viewstamped Replication中被称为**视图编号**，在Raft中被称为**任期编号**），并保证在同一个纪元内，主节点是唯一的。

Every time the current leader is thought to be dead, a vote is started among the nodesto elect a new leader. This election is given an incremented epoch number, and thus **epoch numbers are totally ordered and monotonically increasing**. If there is a conflictbetween two different leaders in two different epochs (perhaps because the previousleader actually wasn’t dead after all), then **the leader with the higher epoch number prevails**.

每当集群认为当前主节点已失效时，节点之间会启动一轮投票，选举新的主节点。这轮选举会被赋予一个递增的纪元编号，因此纪元编号是**全序且单调递增**的。如果两个不同纪元的主节点之间出现冲突（可能是因为前一任主节点实际上并未失效），那么**纪元编号更大的主节点拥有优先权**。

Before a leader is allowed to decide anything, it must first check that there isn’t someother leader with a higher epoch number which might take a conflicting decision.How does a leader know that it hasn’t been ousted by another node? Recall “TheTruth Is Defined by the Majority” on page 300: a node cannot necessarily trust itsown judgment—just because a node thinks that it is the leader, that does not neces‐sarily mean the other nodes accept it as their leader.

主节点在获准做出任何决议之前，必须首先确认不存在纪元编号更大的其他主节点 —— 毕竟这些节点可能会做出与之冲突的决议。那么，主节点如何确认自己没有被其他节点取代呢？回顾本书第 300 页的 **“真理由多数派定义”** 一节：一个节点不能仅凭自身判断下定论 —— 仅仅因为某个节点自认为是主节点，并不代表其他节点也承认它的主节点身份。

Instead, it must collect votes from a quorumof nodes (see “Quorums for reading andwriting” on page 179). For every decision that a leader wants to make, it must sendthe proposed value to the other nodes and wait for a quorum of nodes to respond infavor of the proposal. The quorum typically, but not always, consists of a majority ofnodes [105]. A node votes in favor of a proposal only if it is not aware of any otherleader with a higher epoch.

相反，主节点必须**收集法定人数节点的投票**（参见本书第 179 页的 “读写操作的法定人数机制”）。对于主节点想要做出的每一项决议，它都必须将提议值发送给其他节点，并等待法定人数的节点对该提案投出赞成票。通常（但并非绝对），法定人数由**多数节点**构成 [105]。只有当节点不知道存在纪元编号更大的其他主节点时，才会对该提案投赞成票。

Thus, we have two rounds of voting: once to choose a leader, and a second time tovote on a leader’s proposal. The key insight is that the quorums for those two votesmust overlap: if a vote on a proposal succeeds, at least one of the nodes that voted forit must have also participated in the most recent leader election [105]. Thus, if thevote on a proposal does not reveal any higher-numbered epoch, the current leadercan conclude that no leader election with a higher epoch number has happened, andtherefore be sure that it still holds the leadership. It can then safely decide the pro‐posed value.

由此可见，整个过程包含两轮投票：第一轮用于选举主节点，第二轮用于对主节点提出的提案进行表决。核心要点在于，**这两轮投票的法定人数集合必须存在交集**：如果一项提案的投票获得通过，那么投赞成票的节点中，至少有一个节点同时参与了最近一次的主节点选举 [105]。如此一来，若提案投票未发现任何更高编号的纪元，当前主节点即可断定，尚未出现更高纪元的主节点选举，进而确认自己的主节点身份仍然有效。此时，主节点就可以安全地敲定该提案的决议值。

This voting process looks superficially similar to two-phase commit. The biggest dif‐ferences are that in 2PC the coordinator is not elected, and that fault-tolerant consen‐sus algorithms only require votes from a majority of nodes, whereas 2PC requires a“yes” vote from every participant. Moreover, consensus algorithms define a recoveryprocess by which nodes can get into a consistent state after a new leader is elected,ensuring that the safety properties are always met. These differences are key to thecorrectness and fault tolerance of a consensus algorithm.

这一投票流程表面上与两阶段提交颇为相似。二者最大的区别在于：两阶段提交中的协调者无需选举产生；且容错共识算法仅需获得多数节点的投票即可，而两阶段提交则要求**所有参与者都投赞成票**。此外，共识算法还定义了一套恢复流程，当新主节点当选后，各节点可通过该流程恢复至一致状态，从而确保安全性属性始终得到满足。这些差异，正是共识算法具备正确性与容错能力的关键所在。

**Limitations of consensus**

**共识算法的局限性**

Consensus algorithms are a huge breakthrough for distributed systems: they bringconcrete safety properties (agreement, integrity, and validity) to systems where every‐thing else is uncertain, and they nevertheless remain fault-tolerant (able to make pro‐gress as long as a majority of nodes are working and reachable). They provide totalorder broadcast, and therefore they can also implement linearizable atomic opera‐tions in a fault-tolerant way (see “Implementing linearizable storage using total orderbroadcast” on page 350).

共识算法堪称分布式系统领域的一项重大突破：在一个处处充满不确定性的系统中，它能够提供明确的**安全性属性**（一致性、完整性与有效性），同时还能保持容错能力 —— 只要多数节点处于正常工作且可连通的状态，系统就能持续推进业务流程。共识算法可实现全序广播，因此也能以容错的方式实现**线性化原子操作**（参见本书第 350 页的 “基于全序广播实现线性化存储” 一节）。

Nevertheless, they are not used everywhere, because the benefits come at a cost.

尽管优势显著，共识算法却并未在所有场景中得到应用，这是因为其收益的背后需要付出相应的代价。

The process by which nodes vote on proposals before they are decided is a kind ofsynchronous replication. As discussed in “Synchronous Versus Asynchronous Repli‐cation” on page 153, databases are often configured to use asynchronous replication.In this configuration, some committed data can potentially be lost on failover—butmany people choose to accept this risk for the sake of better performance.

节点在对提案做出决议之前，需要先通过投票达成共识，这一过程本质上属于**同步复制**。正如本书第 153 页 “同步复制与异步复制” 一节所述，数据库通常会被配置为异步复制模式。在这种配置下，发生故障转移时可能会丢失部分已提交的数据 —— 但为了换取更优的性能，许多人选择接受这种风险。

Consensus systems always require a strict majority to operate. This means you need aminimum of three nodes in order to tolerate one failure (the remaining two out ofthree form a majority), or a minimum of five nodes to tolerate two failures (theremaining three out of five form a majority). If a network failure cuts off some nodesfrom the rest, only the majority portion of the network can make progress, and therest is blocked (see also “The Cost of Linearizability” on page 335).

共识系统的运行始终需要**严格多数**的节点支持。这意味着，若要容忍 1 个节点故障，集群至少需要部署 3 个节点（3 个节点中剩余 2 个即可构成多数派）；若要容忍 2 个节点故障，则集群至少需要部署 5 个节点（5 个节点中剩余 3 个即可构成多数派）。一旦发生网络故障，导致部分节点与集群失联，那么只有处于多数派分区的节点能够继续推进业务，其余节点则会陷入阻塞状态（另可参见本书第 335 页的 “线性化的代价” 一节）。

Most consensus algorithms assume a fixed set of nodes that participate in voting,which means that you can’t just add or remove nodes in the cluster. Dynamic mem‐bership extensions to consensus algorithms allow the set of nodes in the cluster tochange over time, but they are much less well understood than static membershipalgorithms.

多数共识算法会假定参与投票的节点集合是固定的，这意味着无法随意向集群中添加或移除节点。针对共识算法的**动态节点成员机制**扩展方案，允许集群的节点集合随时间变化，但这类方案的成熟度远不及静态节点成员机制。

Consensus systems generally rely on timeouts to detect failed nodes. In environmentswith highly variable network delays, especially geographically distributed systems, itoften happens that a node falsely believes the leader to have failed due to a transientnetwork issue. Although this error does not harm the safety properties, frequentleader elections result in terrible performance because the system can end up spend‐ing more time choosing a leader than doing any useful work.

共识系统通常依靠**超时机制**来检测故障节点。在网络延迟波动极大的环境中，尤其是在地理分布式系统里，常常会出现这样的情况：某个节点会因**临时性网络故障**，错误地判定主节点已经失效。虽然这类误判不会损害系统的安全性属性，但过于频繁的主节点选举会导致系统性能急剧下降 —— 因为系统可能会将更多时间耗费在选举主节点上，而非执行实际的业务工作。

Sometimes, consensus algorithms are particularly sensitive to network problems. Forexample, Raft has been shown to have unpleasant edge cases [106]: if the entire net‐work is working correctly except for one particular network link that is consistentlyunreliable, Raft can get into situations where leadership continually bounces betweentwo nodes, or the current leader is continually forced to resign, so the system effec‐tively never makes progress. Other consensus algorithms have similar problems, anddesigning algorithms that are more robust to unreliable networks is still an openresearch problem.

在某些场景下，共识算法对网络问题的敏感度会尤为突出。例如，有研究表明 Raft 算法存在一些棘手的**边界情况**[106]：即便整个网络的大部分链路都正常工作，只要有某一条特定的网络链路持续不稳定，Raft 集群就可能陷入这样的困境 —— 主节点身份在两个节点之间频繁切换，或者现任主节点被迫频繁退位，最终导致系统实际上完全无法推进业务。其他共识算法也存在类似问题，因此，设计对不稳定网络环境鲁棒性更强的共识算法，至今仍是一个开放的研究课题。

#### Membership and Coordination Services

**成员管理与协调服务**

ZooKeeper and etcd are designed to hold small amounts of data that can fit entirely in memory (although they still write to disk for durability)—so you wouldn’t want tostore all of your application’s data here. That small amount of data is replicatedacross all the nodes using a fault-tolerant total order broadcast algorithm. As dis‐cussed previously, total order broadcast is just what you need for database replica‐tion: if each message represents a write to the database, applying the same writes inthe same order keeps replicas consistent with each other.

ZooKeeper 与 etcd 的设计定位是存储**少量可完全载入内存的数据**（尽管为了保证持久性，它们仍会将数据写入磁盘）—— 因此，你不会希望将应用的全部数据都存储在这里。这些少量数据会通过**容错全序广播算法**在所有节点间实现复制。正如前文所述，全序广播恰好满足数据库复制的需求：如果每条消息都代表一次数据库写操作，那么所有节点按相同顺序执行这些写操作，就能保证各副本之间的数据一致性。

ZooKeeper is modeled after Google’s Chubby lock service [14, 98], implementing notonly total order broadcast (and hence consensus), but also an interesting set of otherfeatures that turn out to be particularly useful when building distributed systems:

ZooKeeper 的设计借鉴了谷歌的 Chubby 锁服务 [14, 98]，它不仅实现了全序广播（进而实现了共识机制），还提供了一系列其他实用特性，这些特性在构建分布式系统的过程中被证明价值极高：

**Linearizable atomic operations** Using an atomic compare-and-set operation, you can implement a lock: if several nodes concurrently try to perform the same operation, only one of them will suc‐ ceed. The consensus protocol guarantees that the operation will be atomic and linearizable, even if a node fails or the network is interrupted at any point. A dis‐ tributed lock is usually implemented as a lease, which has an expiry time so that it is eventually released in case the client fails (see “Process Pauses” on page 295).

**线性化原子操作** 借助原子比较并设置（CAS）操作，你可以实现分布式锁：当多个节点并发执行同一操作时，仅有一个节点能够成功。共识协议可以保证，即便操作过程中发生节点故障或网络中断，该操作依然具备原子性与线性化特性。分布式锁通常会以**租约**的形式实现，并设置过期时间 —— 这样一来，即便客户端发生故障，锁最终也会被自动释放（参见本书第 295 页的 “进程暂停” 一节）。

**Total ordering of operations** As discussed in “The leader and the lock” on page 301, when some resource is protected by a lock or lease, you need a fencing token to prevent clients from con‐ flicting with each other in the case of a process pause. The fencing token is some number that monotonically increases every time the lock is acquired. ZooKeeper provides this by totally ordering all operations and giving each operation a **monotonically increasing transaction ID (zxid)** and **version number (cversion)** [15].

**操作全序性** 正如本书第 301 页 “主节点与锁” 一节所述，当某一资源被锁或租约保护时，需要引入**围栏令牌**来避免进程暂停场景下的客户端冲突问题。围栏令牌是一个递增数值，每一次获取锁操作都会生成一个比之前更大的令牌。ZooKeeper 通过对所有操作进行全序排序来实现这一机制，它会为每一项操作分配一个**单调递增的事务 ID（zxid）** 与**版本号（cversion）**[15]。

**Failure detection** Clients maintain a **long-lived session** on ZooKeeper servers, and the client and server periodically exchange heartbeats to check that the other node is still alive. Even if the connection is temporarily interrupted, or a ZooKeeper node fails, the session remains active. However, if the heartbeats cease for a duration that is longer than the session timeout, ZooKeeper declares the session to be dead. Any locks held by a session can be configured to be automatically released when the **session times out** (ZooKeeper calls these **ephemeral nodes**).

**故障检测** 客户端会与 ZooKeeper 服务器建立**长连接会话**，客户端与服务器之间会定期交换心跳包，以确认对方是否处于存活状态。即便连接发生临时中断，或是某一 ZooKeeper 节点发生故障，会话依然会保持有效。但如果心跳包的中断时长超过会话超时阈值，ZooKeeper 就会判定该会话已失效。会话持有的所有锁都可以被配置为**会话超时时自动释放**（ZooKeeper 将这类锁对应的节点称为**临时节点**）。

**Change notifications** Not only can one client read locks and values that were created by another client,but it can also watch them for changes. Thus, a client can find out when another client joins the cluster (based on the value it writes to ZooKeeper), or if another client fails (because its session times out and its ephemeral nodes disappear). By subscribing to notifications, a client avoids having to frequently poll to find out about changes.

**变更通知** 客户端不仅可以读取其他客户端创建的锁与数据，还能为这些数据注册**变更监听**。这样一来，当有新客户端加入集群时（可通过其写入 ZooKeeper 的数据判断），或是某一客户端发生故障时（因会话超时导致临时节点消失），监听客户端都能及时感知。通过订阅变更通知，客户端无需通过频繁轮询来获取数据变化。

Of these features, only the linearizable atomic operations really require consensus. However, it is the combination of these features that makes systems like ZooKeeperso useful for distributed coordination.

在上述特性中，只有**线性化原子操作**真正依赖共识机制实现。但正是这些特性的组合，才让 ZooKeeper 这类系统在分布式协调场景中具备了不可替代的价值。

### Summary

We saw that achieving **consensus** means deciding something in such a way that allnodes agree on what was decided, and such that the decision is irrevocable. Withsome digging, it turns out that a wide range of problems are actually reducible toconsensus and are equivalent to each other (in the sense that if you have a solutionfor one of them, you can easily transform it into a solution for one of the others).Such equivalent problems include:

- **Linearizable compare-and-set registers** The register needs to atomically decide whether to set its value, based on whether its current value equals the parameter given in the operation.

- **Atomic transaction commit** A database must decide whether to commit or abort a distributed transaction.

- **Total order broadcas**t The messaging system must decide on the order in which to deliver messages.

- **Locks and leases** When several clients are racing to grab a lock or lease, the lock decides which one successfully acquired it.

- **Membership/coordination service** Given a failure detector (e.g., timeouts), the system must decide which nodes are alive, and which should be considered dead because their sessions timed out.

- **Uniqueness constraint** When several transactions concurrently try to create conflicting records with the same key, the constraint must decide which one to allow and which should fail with a constraint violation.

我们已经明确，**达成共识**的内涵是：以一种能让所有节点对决议结果形成一致认可的方式做出决策，且该决策一旦确定便不可撤销。深入探究后不难发现，分布式领域内的诸多问题，实际上都可归结为共识问题，且这些问题彼此等价 —— 也就是说，只要能解决其中一个问题，就能轻松将解决方案转化为其他问题的解决思路。这类等价问题包括：

1. **线性化比较并设置寄存器**：寄存器需要基于自身当前值是否与操作传入的参数值相等，来原子性地决定是否更新其值。
2. **原子事务提交**：数据库必须决定是提交还是中止一个分布式事务。
3. **全序广播**：消息系统必须决定消息的投递顺序。
4. **锁与租约**：当多个客户端竞争获取同一把锁或租约时，由锁来决定哪一个客户端能够成功获取。
5. **成员管理 / 协调服务**：基于故障检测器（如超时机制），系统必须判定哪些节点处于存活状态，哪些节点因会话超时应被标记为失效。
6. **唯一性约束**：当多个事务并发尝试创建具有相同主键的冲突记录时，由约束机制决定允许其中哪一个事务执行，哪一个事务因违反约束而失败。

All of these are straightforward if you only have a single node, or if you are willing toassign the decision-making capability to a single node. This is what happens in asingle-leader database: all the power to make decisions is vested in the leader, whichis why such databases are able to provide linearizable operations, uniqueness con‐straints, a totally ordered replication log, and more.

如果系统只有单个节点，或者你愿意将决策能力完全赋予单个节点，那么解决上述所有问题都会变得十分简单。单主数据库正是采用了这种模式：所有决策权限都集中在主节点手中，这也是此类数据库能够提供线性化操作、唯一性约束、全序复制日志等功能的原因所在。

However, if that single leader fails, or if a network interruption makes the leaderunreachable, such a system becomes unable to make any progress. There are threeways of handling that situation:

1. Wait for the leader to recover, and accept that the system will be blocked in the meantime. Many XA/JTA transaction coordinators choose this option. This approach does not fully solve consensus because it does not satisfy the termina‐ tion property: if the leader does not recover, the system can be blocked forever.
2. Manually fail over by getting humans to choose a new leader node and reconfig‐ ure the system to use it. Many relational databases take this approach. It is a kind of consensus by “act of God”—the human operator, outside of the computer sys‐ tem, makes the decision. The speed of failover is limited by the speed at which humans can act, which is generally slower than computers.
3. Use an algorithm to automatically choose a new leader. This approach requires a consensus algorithm, and it is advisable to use a proven algorithm that correctly handles adverse network conditions [107].

然而，一旦这个唯一的主节点发生故障，或是网络中断导致主节点无法被访问，这类系统就会陷入无法推进业务的停滞状态。针对这种情况，有三种应对方案：

1. **等待主节点恢复**，同时接受系统在此期间处于阻塞状态的现实。许多 XA/JTA 事务协调器都会选择这种方案。但该方案并未彻底解决共识问题，因为它不满足共识的**终止性**要求 —— 如果主节点永远无法恢复，系统就会被永久阻塞。
2. **手动执行故障转移**，由运维人员选定一个新的主节点，并重新配置系统使其成为新的主节点。许多关系型数据库采用的就是这种方案。这相当于一种**人为干预式共识**—— 决策由计算机系统之外的运维人员做出。故障转移的速度受制于人工操作的效率，通常要慢于计算机自动处理的速度。
3. **使用算法自动选举新主节点**。这种方案需要依赖共识算法，且建议选用**经过实践验证的算法**，以确保其能正确应对各类恶劣网络状况 [107]。

