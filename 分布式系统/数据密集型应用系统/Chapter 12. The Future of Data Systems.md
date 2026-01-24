[toc]

## Chapter 12. The Future of Data Systems

### Data Integration

#### Batch and Stream Processing

**批处理与流处理**

**The Lambda architecture**

**Lambda 架构**

If batch processing is used to reprocess historical data, and stream processing is usedto process recent updates, then how do you combine the two? The lambda architec‐ture [12] is a proposal in this area that has gained a lot of attention.

若采用批处理对历史数据进行重处理，同时采用流处理应对近期数据更新，那么该如何将这两种处理模式结合起来呢？**Lambda 架构**正是针对这一问题提出的方案，它在业内受到了广泛关注 [12]。

The core idea of the lambda architecture is that incoming data should be recorded byappending immutable events to an always-growing dataset, similarly to event sourc‐ing (see “Event Sourcing” on page 457). From these events, read-optimized views arederived. The lambda architecture proposes running two different systems in parallel:a batch processing system such as Hadoop MapReduce, and a separate stream-processing system such as Storm.

Lambda 架构的核心思想是，参考事件溯源模式（详见本书第 457 页的《事件溯源》一节），将流入的数据以**追加不可变事件**的方式，记录到一个持续增长的数据集中。基于这些事件，系统会生成读优化视图。Lambda 架构建议并行运行两套独立的系统：一套是 Hadoop MapReduce 这类批处理系统，另一套则是 Storm 这类流处理系统。

In the lambda approach, the stream processor consumes the events and quickly pro‐duces an approximate update to the view; the batch processor later consumes thesame set of events and produces a corrected version of the derived view. The reason‐ing behind this design is that batch processing is simpler and thus less prone to bugs,while stream processors are thought to be less reliable and harder to make fault-tolerant (see “Fault Tolerance” on page 476). Moreover, the stream process can usefast approximate algorithms while the batch process uses slower exact algorithms.

在 Lambda 架构的处理流程中，流处理器会消费事件并快速生成视图的**近似更新结果**；之后批处理器会消费同一批事件，生成衍生视图的修正版本。这种设计的背后逻辑是，批处理的实现更为简单，因此出现缺陷的概率更低；而流处理器则被认为可靠性欠佳，且更难实现容错能力（详见本书第 476 页的《容错性》一节）。此外，流处理流程可采用运算速度较快的近似算法，而批处理流程则可采用运算速度较慢但结果精确的算法。

The lambda architecture was an influential idea that shaped the design of data sys‐tems for the better, particularly by popularizing the principle of deriving views ontostreams of immutable events and reprocessing events when needed. However, I alsothink that it has a number of practical problems:

- Having to maintain the same logic to run both in a batch and in a stream pro‐ cessing framework is significant additional effort. Although libraries such as Summingbird [13] provide an abstraction for computations that can be run in either a batch or a streaming context, the operational complexity of debugging,tuning, and maintaining two different systems remains [14].
- Since the stream pipeline and the batch pipeline produce separate outputs, they need to be merged in order to respond to user requests. This merge is fairly easy if the computation is a simple aggregation over a tumbling window, but it becomes significantly harder if the view is derived using more complex opera‐ tions such as joins and sessionization, or if the output is not a time series.
- Although it is great to have the ability to reprocess the entire historical dataset,doing so frequently is expensive on large datasets. Thus, the batch pipeline often needs to be set up to process incremental batches (e.g., an hour’s worth of data at the end of every hour) rather than reprocessing everything. This raises the prob‐ lems discussed in “Reasoning About Time” on page 468, such as handling strag‐ glers and handling windows that cross boundaries between batches. Incrementalizing a batch computation adds complexity, making it more akin to the streaming layer, which runs counter to the goal of keeping the batch layer as simple as possible.

Lambda 架构是一个极具影响力的理念，它推动了数据系统设计的发展与完善，尤其是普及了两项核心原则：基于不可变事件流生成视图，以及在需要时对事件进行重处理。不过在我看来，该架构也存在不少实际应用层面的问题：

1. 需要维护一套同时适用于批处理和流处理框架的业务逻辑，这会带来大量额外的开发与维护工作。尽管 Summingbird [13] 等类库提供了一层抽象，支持计算逻辑同时运行在批处理或流处理环境中，但调试、调优和维护两套独立系统所带来的运维复杂性依然存在 [14]。
2. 由于流处理管道与批处理管道会生成各自独立的输出结果，要响应用户请求，就必须对这两份结果进行合并。如果只是对滚动窗口执行简单聚合计算，结果合并的操作会相对容易；但如果视图是通过连接、会话划分等更复杂的操作生成的，或者输出结果并非时间序列数据，那么结果合并的难度就会大幅增加。
3. 尽管能够重处理全量历史数据集是一项优势，但对于大规模数据集而言，频繁执行全量重处理的成本极高。因此，批处理管道往往需要被配置为**增量批处理模式**（例如，每小时末处理该小时产生的数据），而非对全量数据进行重处理。这就会引出本书第 468 页《时间相关的推理》一节中讨论的各类问题，例如如何处理滞后事件、如何处理跨越批处理边界的窗口等。为批处理计算引入增量处理机制会增加系统复杂度，使其与流处理层的差异逐渐缩小，这与 “保持批处理层尽可能简洁” 的设计目标是相悖的。

**Unifying batch and stream processing**

**批处理与流处理的统一**

More recent work has enabled the benefits of the lambda architecture to be enjoyedwithout its downsides, by allowing both batch computations (reprocessing historicaldata) and stream computations (processing events as they arrive) to be implementedin the same system [15].

近期的技术进展实现了一种新方案：**在同一个系统中同时实现批处理计算（重处理历史数据）与流处理计算（实时处理到达的事件）**，以此兼得 Lambda 架构的优势，同时规避其弊端 [15]。

Unifying batch and stream processing in one system requires the following features,which are becoming increasingly widely available:

- The ability to replay historical events through the same processing engine that handles the stream of recent events. For example, log-based message brokers have the ability to replay messages (see “Replaying old messages” on page 451),and some stream processors can read input from a distributed filesystem like HDFS.
- Exactly-once semantics for stream processors—that is, ensuring that the output is the same as if no faults had occurred, even if faults did in fact occur (see “Fault Tolerance” on page 476). Like with batch processing, this requires discarding the partial output of any failed tasks.
- Tools for windowing by event time, not by processing time, since processing time is meaningless when reprocessing historical events (see “Reasoning About Time” on page 468). For example, Apache Beam provides an API for expressing such computations, which can then be run using Apache Flink or Google Cloud Dataflow.

要在单一系统中实现批处理与流处理的统一，需要具备以下几项功能，这些功能如今正得到越来越广泛的支持：

1. **支持通过同一处理引擎，既重放历史事件，又处理近期的事件流**。例如，基于日志的消息代理具备消息重放能力（详见本书第 451 页的《重放旧消息》一节）；部分流处理器也能够从 HDFS 等分布式文件系统中读取输入数据。
2. **流处理器需具备精确一次语义**—— 即即便实际发生故障，也能保证输出结果与无故障场景下的结果完全一致（详见本书第 476 页的《容错性》一节）。与批处理类似，这需要将故障任务的部分输出结果丢弃。
3. **支持基于事件时间而非处理时间进行窗口划分的工具**。因为在重处理历史事件时，处理时间不具备任何实际意义（详见本书第 468 页的《时间相关的推理》一节）。例如，Apache Beam 提供了一套用于描述此类计算逻辑的 API，该 API 的计算任务可基于 Apache Flink 或 Google Cloud Dataflow 运行。

### Unbundling Databases

**数据库的解耦**

Unix and relational databases have approached the information management prob‐lem with very different philosophies. Unix viewed its purpose as presenting program‐mers with a logical but fairly low-level hardware abstraction, whereas relationaldatabases wanted to give application programmers a high-level abstraction thatwould hide the complexities of data structures on disk, concurrency, crash recovery,and so on. Unix developed pipes and files that are just sequences of bytes, whereasdatabases developed SQL and transactions.

Unix 系统与关系型数据库在**信息管理问题的处理理念上存在显著差异**。Unix 的设计目标是为程序员提供一套**逻辑层面但偏向底层的硬件抽象**；而关系型数据库则希望为应用程序员提供**高层抽象**，以此屏蔽磁盘数据结构、并发控制、崩溃恢复等底层实现的复杂性。Unix 衍生出了管道与文件（本质是字节序列）的设计，而数据库则发展出了 SQL 与事务的相关机制。

The big advantage of log-based integration is **loose coupling** between the various components, which manifests itself in two ways:

1. **At a system level**, asynchronous event streams make the system as a whole more robust to outages or performance degradation of individual components. If a consumer runs slow or fails, the event log can buffer messages (see “Disk space usage” on page 450), allowing the producer and any other consumers to continue running unaffected. The faulty consumer can catch up when it is fixed, so it doesn’t miss any data, and the fault is contained. By contrast, the synchronous interaction of distributed transactions tends to escalate local faults into large- scale failures (see “Limitations of distributed transactions” on page 363).
2. **At a human level**, unbundling data systems allows different software components and services to be developed, improved, and maintained independently from each other by different teams. Specialization allows each team to focus on doing one thing well, with well-defined interfaces to other teams’ systems. Event logs provide an interface that is powerful enough to capture fairly strong consistency properties (due to durability and ordering of events), but also general enough to be applicable to almost any kind of data.

基于日志的集成方式的核心优势，在于实现了各个组件之间的**松耦合**，这一优势主要体现在两个方面：

1. **系统层面**：异步事件流使整个系统对单个组件的故障或性能下降具有更强的鲁棒性。如果某个消费者处理速度变慢或发生故障，事件日志可以对消息进行缓冲（详见本书第 450 页的《磁盘空间占用》一节），从而让生产者及其他消费者不受影响、继续运行。故障的消费者修复后可以追平数据，不会丢失任何信息，同时故障的影响范围也被限定在局部。相比之下，分布式事务的同步交互机制，往往会将局部故障升级为大规模故障（详见本书第 363 页的《分布式事务的局限性》一节）。
2. **人员协作层面**：数据系统解耦后，不同的软件组件与服务可由不同团队独立开发、优化和维护。这种专业化分工能让每个团队专注于把一件事做好，并通过与其他团队系统之间**定义清晰的接口**完成交互。事件日志所提供的接口，既具备足够强的能力（依托事件的持久性与有序性，能够实现较高的一致性特性），又具备极强的通用性，几乎适用于所有类型的数据。

#### Observing Derived State

From this example we can see that an index is not the only possible boundarybetween the write path and the read path. Caching of common search results is possi‐ble, and grep-like scanning without the index is also possible on a small number ofdocuments. Viewed like this, the role of caches, indexes, and materialized views issimple: they shift the boundary between the read path and the write path. They allowus to do more work on the write path, by precomputing results, in order to save efforton the read path.

从这个例子中我们可以看出，**索引并非读写路径之间唯一可能的边界**。我们既可以对常用搜索结果进行缓存，也可以在文档数量较少时，不借助索引直接执行类 grep 的扫描操作。从这个角度来看，缓存、索引和物化视图的作用十分简单：**它们会移动读写路径之间的边界**。通过在写路径上预计算结果，它们能让我们在写路径上多做一些工作，从而节省读路径的处理开销。

### Aiming for Correctness

#### The End-to-End Argument for Databases

**数据库的端到端论证**

**The end-to-end argument**

**端到端论证**

This scenario of suppressing duplicate transactions is just one example of a moregeneral principle called the end-to-end argument, which was articulated by Saltzer,Reed, and Clark in 1984 [55]:

抑制重复事务的这种场景，恰好印证了一项更具普适性的原理 ——**端到端论证**。该原理由萨尔茨泽（Saltzer）、里德（Reed）与克拉克（Clark）于 1984 年提出 [55]：

The function in question can completely and correctly be implemented only with theknowledge and help of the application standing at the endpoints of the communica‐tion system. Therefore, providing that questioned function as a feature of the commu‐nication system itself is not possible. (Sometimes an incomplete version of the functionprovided by the communication system may be useful as a performance enhance‐ment.)

只有借助位于通信系统两端的应用程序所掌握的信息并获得其协助，才能完整且正确地实现所讨论的功能。因此，将该功能直接作为通信系统的一项特性来提供是不可行的。（不过，通信系统提供的该功能简易版本，有时可作为性能优化手段发挥作用。）

In our example, the function in question was **duplicate suppression**. We saw that TCPsuppresses duplicate packets at the TCP connection level, and some stream process‐ors provide so-called **exactly-once** semantics at the message processing level, but thatis not enough to prevent a user from submitting a duplicate request if the first onetimes out. By themselves, TCP, database transactions, and stream processors cannotentirely rule out these duplicates. Solving the problem requires an end-to-end solution: a **transaction identifier** that is passed all the way from the end-user client to thedatabase.

在我们的例子中，所讨论的功能正是**重复抑制**。我们知道，TCP 会在 TCP 连接层面抑制重复数据包，部分流处理器也会在消息处理层面提供所谓的**精确一次语义**，但这些机制不足以防止用户在首次请求超时后提交重复请求。单靠 TCP、数据库事务和流处理器，无法彻底杜绝这类重复问题。要解决该问题，必须采用端到端的解决方案：使用一个从终端用户客户端一路传递至数据库的**事务标识符**。

The end-to-end argument also applies to checking the **integrity of data**: checksumsbuilt into Ethernet, TCP, and TLS can detect corruption of packets in the network,but they cannot detect corruption due to bugs in the software at the sending andreceiving ends of the network connection, or corruption on the disks where the datais stored. If you want to catch all possible sources of data corruption, you also needend-to-end checksums.

端到端论证同样适用于**数据完整性校验**场景：以太网、TCP 和 TLS 内置的校验和，能够检测数据包在网络传输中的损坏情况，但无法检测由网络连接收发两端的软件缺陷，或是数据存储磁盘故障所引发的数据损坏。若要排查所有可能导致数据损坏的源头，同样需要部署端到端的校验和机制。

Although the low-level features (TCP duplicate suppression, Ethernet checksums,WiFi encryption) cannot provide the desired end-to-end features by themselves, theyare still useful, since they reduce the probability of problems at the higher levels. Forexample, HTTP requests would often get mangled if we didn’t have TCP putting thepackets back in the right order. We just need to remember that the **low-level reliability features are not by themselves sufficient to ensure end-to-end correctness.**

尽管这类底层功能（TCP 重复抑制、以太网校验和、WiFi 加密）**无法单独提供所需的端到端功能**，但它们依然具备实用价值 —— 因为它们能够降低上层系统出现问题的概率。例如，若没有 TCP 将数据包重新按正确顺序排列，HTTP 请求往往会出现错乱。我们只需记住，**底层可靠性功能本身并不足以保障端到端的正确性**。

#### Enforcing Constraints

**约束执行**

**Multi-partition request processing**

**多分区请求处理**

Ensuring that an operation is executed atomically, while satisfying constraints,becomes more interesting when several partitions are involved. In Example 12-2,there are potentially three partitions: the one containing the request ID, the one con‐taining the payee account, and the one containing the payer account. There is no rea‐son why those three things should be in the same partition, since they are allindependent from each other.

当操作涉及多个分区时，如何在满足约束条件的前提下确保操作的原子性，就成为了一个更值得探讨的问题。在示例 12-2 中，操作可能涉及三个分区：存储请求 ID 的分区、存储收款账户的分区，以及存储付款账户的分区。这三类数据分属不同分区是完全合理的，因为它们在逻辑上相互独立。

In the traditional approach to databases, executing this transaction would require anatomic commit across all three partitions, which essentially forces it into a total orderwith respect to all other transactions on any of those partitions. Since there is nowcross-partition coordination, different partitions can no longer be processed inde‐pendently, so throughput is likely to suffer.

在传统的数据库处理方案中，要执行这类事务，就需要在所有三个分区之间完成**原子提交**。这实际上会强制该事务与涉及任一相关分区的其他所有事务形成一个**全序关系**。而一旦引入跨分区协调机制，不同分区就无法再独立处理事务，系统的吞吐量很可能会因此下降。

However, it turns out that equivalent correctness can be achieved with partitionedlogs, and without an atomic commit:

1. The request to transfer money from account A to account B is given a unique request ID by the client, and appended to a log partition based on the request ID.
2. A stream processor reads the log of requests. For each request message it emits two messages to output streams: a debit instruction to the payer account A (par‐ titioned by A), and a credit instruction to the payee account B (partitioned by B). The original request ID is included in those emitted messages.
3. Further processors consume the streams of credit and debit instructions, dedu‐ plicate by request ID, and apply the changes to the account balances.

不过，基于**分区日志**，我们其实可以在不依赖原子提交的前提下，实现同等的正确性保障。具体方案如下：

1. 客户端为一笔从账户 A 转账至账户 B 的请求生成一个唯一的请求 ID，并将该请求按请求 ID 分区，追加到对应的日志分区中。
2. 流处理器读取请求日志，针对每条请求消息，向输出流中发送两条指令：一条是面向付款账户 A 的扣款指令（按账户 A 分区），另一条是面向收款账户 B 的入账指令（按账户 B 分区）。这两条指令都会携带原始请求的 ID。
3. 下游的其他处理器分别消费入账指令流与扣款指令流，根据请求 ID 进行**去重**，再将指令对应的金额变动应用到账户余额中。

Steps 1 and 2 are necessary because if the client directly sent the credit and debitinstructions, it would require an atomic commit across those two partitions to ensurethat either both or neither happen. To avoid the need for a distributed transaction,we first durably log the request as a single message, and then derive the credit anddebit instructions from that first message. Single-object writes are atomic in almostall data systems (see “Single-object writes” on page 230), and so the request eitherappears in the log or it doesn’t, without any need for a multi-partition atomic commit.

步骤 1 和步骤 2 的设计是必不可少的。原因在于，如果让客户端直接发送入账和扣款两条指令，就需要在这两个分区之间执行原子提交，才能确保两条指令要么都生效，要么都不生效。而通过先将请求作为单条消息持久化写入日志，再基于该日志派生出入账和扣款指令，我们就能规避分布式事务的需求。几乎所有数据系统都支持单对象写入的原子性（详见本书第 230 页的《单对象写入》一节），因此这条请求消息只会存在 “写入日志” 或 “未写入日志” 两种明确状态，无需借助跨分区原子提交来保障。

If the stream processor in step 2 crashes, it resumes processing from its last check‐point. In doing so, it does not skip any request messages, but it may process requestsmultiple times and produce duplicate credit and debit instructions. However, since itis deterministic, it will just produce the same instructions again, and the processors instep 3 can easily deduplicate them using the end-to-end request ID.

若步骤 2 中的流处理器发生崩溃，它会从最近一次的**检查点**恢复处理流程。恢复后，处理器不会跳过任何请求消息，但可能会对部分请求重复处理，进而生成重复的入账和扣款指令。不过，由于流处理器的处理逻辑是**确定性的**，重复处理生成的指令内容也完全一致。因此，步骤 3 中的处理器只需依据端到端的请求 ID，就能轻松完成指令去重。

If you want to ensure that the payer account is not overdrawn by this transfer, youcan additionally have a stream processor (partitioned by payer account number) thatmaintains account balances and validates transactions. Only valid transactions wouldthen be placed in the request log in step 1.

如果需要额外确保本次转账不会导致付款账户透支，我们还可以增设一个流处理器（按付款账户编号分区）。该处理器负责维护账户余额，并对每笔转账请求执行余额校验。只有通过校验的合法请求，才会被写入步骤 1 中的请求日志。

By breaking down the multi-partition transaction into two differently partitionedstages and using the end-to-end request ID, we have achieved the same correctnessproperty (every request is applied exactly once to both the payer and payee accounts),even in the presence of faults, and without using an atomic commit protocol. The idea of using multiple differently partitioned stages is similar to what we discussed in“Multi-partition data processing” on page 514(see also “Concurrency control” onpage 462).

通过将跨分区事务拆解为两个不同分区策略的处理阶段，并借助端到端的请求 ID，我们在不依赖原子提交协议的情况下，即便面对各类故障，依然实现了同等的正确性保障 —— 每笔请求对应的扣款和入账操作，都会被精确地执行一次。这种采用多阶段不同分区策略的设计思路，与本书第 514 页《多分区数据处理》一节的内容一脉相承（另见本书第 462 页的《并发控制》）。

#### Timeliness and Integrity

**时效性与完整性**

**Timeliness** Timeliness means ensuring that users observe the system in an up-to-date state. We saw previously that if a user reads from a stale copy of the data, they may observe it in an inconsistent state (see “Problems with Replication Lag” on page 161). However, that inconsistency is temporary, and will eventually be resolved simply by waiting and trying again.

**时效性** 时效性是指确保用户能够观察到系统的最新状态。我们此前提到，若用户读取的是过期的数据副本，就可能看到不一致的系统状态（详见本书第 161 页的《复制延迟引发的问题》一节）。不过，这类不一致是暂时的，通常只需等待片刻后重试，问题就会自行解决。

The CAP theorem (see “The Cost of Linearizability” on page 335) uses consis‐tency in the sense of **linearizability**, which is a strong way of achieving timeliness.Weaker timeliness properties like read-after-writeconsistency (see “ReadingYour Own Writes” on page 162) can also be useful.

CAP 定理（详见本书第 335 页的《线性一致性的代价》一节）中所提及的 “一致性”，指的是**线性一致性**，这是实现时效性的一种强保障方式。而相对较弱的时效性保障，例如**写后读一致性**（详见本书第 162 页的《读取自己的写入》一节），在实际应用中同样具有重要价值。

**Integrity** Integrity means absence of corruption; i.e., no data loss, and no contradictory or false data. In particular, if some derived dataset is maintained as a view onto some underlying data (see “Deriving current state from the event log” on page 458), the derivation must be correct. For example, a database index must cor‐ rectly reflect the contents of the database—an index in which some records are missing is not very useful.

**完整性** 完整性是指数据无损坏，即不存在数据丢失，也不存在矛盾或错误的数据。具体来说，若某一衍生数据集是基于底层数据构建的视图（详见本书第 458 页的《从事件日志推导当前状态》一节），那么该视图的生成逻辑必须保证准确无误。例如，数据库索引必须完整反映数据库的内容 —— 一个存在记录缺失的索引，其实际使用价值会大打折扣。

If integrity is violated, the inconsistency is permanent: waiting and trying again isnot going to fix database corruption in most cases. Instead, explicit checking andrepair is needed. In the context of ACID transactions (see “The Meaning ofACID” on page 223), consistency is usually understood as some kind ofapplication-specific notion of integrity. Atomicity and durability are importanttools for preserving integrity.

一旦完整性遭到破坏，由此引发的不一致性将是永久性的：在大多数情况下，单纯等待和重试无法修复已损坏的数据库。此时，必须通过主动的检查与修复操作来解决问题。在 ACID 事务的语境下（详见本书第 223 页的《ACID 的含义》一节），“一致性” 通常被理解为一种**特定于应用的完整性定义**。而原子性与持久性，则是保障数据完整性的关键机制。

In slogan form: violations of timeliness are “eventual consistency,” whereas violationsof integrity are “perpetual inconsistency.” I am going to assert that in most applications, integrity is much more important thantimeliness. Violations of timeliness can be annoying and confusing, but violations ofintegrity can be catastrophic.

用一句口号来总结：时效性被破坏会导致**最终一致性**问题，而完整性被破坏则会引发**永久性不一致**问题。我认为，在绝大多数应用场景中，**完整性的重要性远高于时效性**。时效性受损可能会给用户带来困扰和迷惑，但完整性受损则可能引发灾难性的后果。



Exactly-onceor effectively-oncesemantics (see “Fault Tolerance” on page 476) is amechanism for preserving integrity. If an event is lost, or if an event takes effecttwice, the integrity of a data system could be violated. Thus, fault-tolerant messagedelivery and duplicate suppression (e.g., idempotent operations) are important formaintaining the integrity of a data system in the face of faults.

**精确一次语义**或**有效一次语义**（详见本书第 476 页的《容错性》一节）是保障数据完整性的一种机制。如果事件丢失，或同一事件生效两次，数据系统的完整性都可能遭到破坏。因此，容错消息投递与重复抑制机制（如幂等操作），对于在故障场景下维持数据系统的完整性至关重要。

As we saw in the last section, reliable stream processing systems can preserve integ‐rity without requiring distributed transactions and an atomic commit protocol,which means they can potentially achieve comparable correctness with much betterperformance and operational robustness. We achieved this integrity through a com‐bination of mechanisms:

- Representing the content of the write operation as a single message, which can easily be written atomically—an approach that fits very well with event sourcing (see “Event Sourcing” on page 457)
- Deriving all other state updates from that single message using deterministic derivation functions, similarly to stored procedures (see “Actual Serial Execution” on page 252and “Application code as a derivation function” on page 505)
- Passing a client-generated request ID through all these levels of processing, ena‐ bling end-to-end duplicate suppression and idempotence• Making messages immutable and allowing derived data to be reprocessed from time to time, which makes it easier to recover from bugs (see “Advantages of immutable events” on page 460)

正如我们在上一节中所见，可靠的流处理系统无需依赖分布式事务与原子提交协议，就能保障数据完整性。这意味着它们有望在实现同等正确性的同时，获得更优的性能与更强的运维鲁棒性。我们通过一套机制组合实现了这种完整性保障，具体如下：

- 将写入操作的内容封装为单条消息，这类消息可轻松实现原子性写入 —— 这种方式与事件溯源模式高度契合（详见本书第 457 页的《事件溯源》一节）
- 借助**确定性推导函数**，基于这条单消息派生所有其他状态更新操作，其原理与存储过程类似（详见本书第 252 页的《真正的串行执行》及第 505 页的《作为推导函数的应用代码》两节）
- 将客户端生成的请求 ID 贯穿所有处理环节，以此实现端到端的重复抑制与幂等性保障
- 将消息设为不可变，并允许衍生数据被定期重处理，这一设计能降低故障恢复的难度（详见本书第 460 页的《不可变事件的优势》一节）

This combination of mechanisms seems to me a very promising direction for build‐ing fault-tolerant applications in the future.

在我看来，这套机制组合为未来构建容错应用指明了一个极具前景的方向。

#### Trust, but Verify

All of our discussion of correctness, integrity, and fault-tolerance has been under theassumption that certain things might go wrong, but other things won’t. We call theseassumptions our **system model**(see “Mapping system models to the real world” onpage 309): for example, we should assume that processes can crash, machines cansuddenly lose power, and the network can arbitrarily delay or drop messages. But wemight also assume that data written to disk is not lost after fsync, that data in mem‐ory is not corrupted, and that the multiplication instruction of our CPU alwaysreturns the correct result.

我们此前关于正确性、完整性与容错性的所有讨论，都是基于这样一种假设：某些情况可能会发生，但另一些情况绝不会发生。我们将这些假设称为**系统模型**（详见本书第 309 页的《将系统模型映射到现实世界》一节）。例如，我们应当假定进程可能崩溃、服务器可能突然断电、网络可能任意延迟或丢弃消息；但同时，我们也可能假定：执行 `fsync` 操作后写入磁盘的数据不会丢失、内存中的数据不会损坏、CPU 的乘法指令总能返回正确结果。

These assumptions are quite reasonable, as they are true most of the time, and itwould be difficult to get anything done if we had to constantly worry about our computers making mistakes. Traditionally, system models take **a binary approach** toward faults: we assume that some things can happen, and other things can never happen.In reality, it is more a question of probabilities: some things are more likely, otherthings less likely. The question is whether violations of our assumptions happen oftenenough that we may encounter them in practice.

这些假设是相当合理的，因为它们在绝大多数情况下都成立。如果我们必须时刻担心计算机出现故障，那么几乎无法完成任何工作。传统上，系统模型对故障采取**二元化的界定方式**：我们假定某些情况可能发生，而另一些情况绝无可能发生。但在现实中，这更多是一个概率问题 —— 有些情况发生的概率较高，有些则较低。关键在于，违背假设的情况发生的频率，是否足以让我们在实际应用中遭遇。

We have seen that data can become corrupted while it is sitting untouched on disks(see “Replication and Durability” on page 227), and data corruption on the networkcan sometimes evade the TCP checksums (see “Weak forms of lying” on page 306).Maybe this is something we should be paying more attention to?

我们此前已经了解到，即便是存放在磁盘中未被访问的数据，也可能出现损坏（详见本书第 227 页的《复制与持久性》一节）；而网络传输中的数据损坏，有时也能逃过 TCP 校验和的检测（详见本书第 306 页的《轻度异常情况》一节）。或许，这是一个值得我们投入更多关注的问题？

One application that I worked on in the past collected crash reports from clients, andsome of the reports we received could only be explained by random bit-flips in thememory of those devices. It seems unlikely, but if you have enough devices runningyour software, even very unlikely things do happen. Besides random memory corrup‐tion due to hardware faults or radiation, certain pathological memory access patternscan flip bits even in memory that has no faults [62]—an effect that can be used tobreak security mechanisms in operating systems [63] (this technique is known asrowhammer). Once you look closely, hardware isn’t quite the perfect abstraction thatit may seem.

我过去参与过的一个项目，需要收集客户端的崩溃报告。我们收到的部分报告，只能用设备内存中的**随机位翻转**来解释。这种情况看似概率极低，但如果有足够多的设备运行你的软件，即便是可能性微乎其微的事件，也终将发生。除了硬件故障或辐射导致的随机内存损坏外，某些特殊的内存访问模式，甚至能让无故障的内存发生位翻转 [62]—— 这种效应还被用于破解操作系统的安全机制 [63]（这类技术被称为**行锤攻击**）。当你深入探究就会发现，硬件并非如它表面看起来的那样，是一种完美无缺的抽象组件。

To be clear, random bit-flips are still very rare on modern hardware [64]. I just wantto point out that they are not beyond the realm of possibility, and so they deservesome attention.

需要明确的是，在现代硬件中，随机位翻转的概率依然极低 [64]。我只是想指出，这类事件并非完全不可能发生，因此值得我们给予一定的关注。

**Designing for auditability**

**审计性设计**

If a transaction mutates several objects in a database, it is difficult to tell after the factwhat that transaction means. Even if you capture the transaction logs (see “ChangeData Capture” on page 454), the insertions, updates, and deletions in various tablesdo not necessarily give a clear picture of why those mutations were performed. Theinvocation of the application logic that decided on those mutations is transient andcannot be reproduced.

如果某笔事务修改了数据库中的多个对象，事后往往很难追溯该事务的业务含义。即便你捕获了事务日志（详见本书第 454 页的《变更数据捕获》一节），但各数据表中的插入、更新与删除操作，也未必能清晰地解释执行这些修改操作的原因。而决定执行这些修改的应用逻辑调用过程具有临时性，且无法复现。

By contrast, **event-based systems** can provide better auditability. In the event sourc‐ing approach, user input to the system is represented as a single immutable event,and any resulting state updates are derived from that event. The derivation can be made **deterministic and repeatable**, so that running the same log of events throughthe same version of the derivation code will result in the same state updates.

相比之下，**基于事件的系统**能够提供更优的审计性。在事件溯源模式中，系统的用户输入会被表示为单条不可变事件，所有由此产生的状态更新，均是基于该事件派生而来。这种派生过程可以被设计为**确定性且可重复的**—— 也就是说，使用同一版本的派生代码，重放同一批事件日志，最终得到的状态更新结果完全一致。

**Being explicit about dataflow** (see “Philosophy of batch process outputs” on page413) makes the provenance of data much clearer, which makes integrity checkingmuch more feasible. For the event log, we can use hashes to check that the event storage has not been corrupted. For any derived state, we can rerun the batch and streamprocessors that derived it from the event log in order to check whether we get thesame result, or even run a redundant derivation in parallel.

**明确数据流走向**（详见本书第 413 页的《批处理输出的设计理念》一节），能够让数据溯源变得更加清晰，从而大幅提升完整性校验的可行性。对于事件日志，我们可以通过哈希值来校验事件存储未发生损坏；对于任何衍生状态，我们可以重新运行从事件日志派生出该状态的批处理与流处理程序，验证是否能得到相同的结果，甚至可以并行执行冗余的推导流程。

A deterministic and well-defined dataflow also makes it easier to debug and trace theexecution of a system in order to determine why it did something [4, 69]. If some‐thing unexpected occurred, it is valuable to have the diagnostic capability to repro‐duce the exact circumstances that led to the unexpected event—**a kind of time-travel debugging capability**.

一套确定性强、定义清晰的数据流，同样有助于系统的调试与执行轨迹追溯，便于定位系统异常行为的根因 [4,69]。当系统出现意外情况时，若具备复现该意外事件发生的完整场景的诊断能力 —— 也就是一种**时光回溯式调试能力**，将具有极高的价值。

### Doing the Right Thing

#### Privacy and Tracking

**隐私与追踪**

**Feedback loops**

**反馈循环**

Even with predictive applications that have less immediately far-reaching effects onpeople, such as recommendation systems, there are difficult issues that we must confront. When services become good at predicting what content users want to see, theymay end up showing people only opinions they already agree with, leading to **echochambers** in which stereotypes, misinformation, and polarization can breed. We arealready seeing the impact of social media echo chambers on election campaigns [91].

即便是对人类影响没有那么立竿见影的预测类应用（如推荐系统），也存在一些我们必须正视的棘手问题。当服务能够精准预测用户想看的内容时，最终可能只会向用户推送他们原本就认同的观点，进而催生**回声室效应**—— 刻板印象、虚假信息与观点极化现象都可能在这种环境中滋生蔓延。社交媒体的回声室效应对选举活动产生的影响，我们已经有目共睹 [91]。

When predictive analytics affect people’s lives, particularly pernicious problems arisedue to self-reinforcing feedback loops. For example, consider the case of employersusing credit scores to evaluate potential hires. You may be a good worker with a goodcredit score, but suddenly find yourself in financial difficulties due to a misfortuneoutside of your control. As you miss payments on your bills, your credit score suffers,and you will be less likely to find work. Joblessness pushes you toward poverty, whichfurther worsens your scores, making it even harder to find employment [87]. It’s adownward spiral due to poisonous assumptions, hidden behind a camouflage ofmathematical rigor and data.

当预测分析技术开始影响人们的生活时，自我强化的反馈循环会引发尤为恶劣的问题。例如，部分雇主会依据信用评分来评估潜在求职者。你或许原本是一名信用良好的优秀员工，却因一场无法掌控的意外陷入财务困境。随着账单逾期未付，你的信用评分会下降，进而降低你找到工作的概率。失业会将你推向贫困，而贫困又会进一步拉低你的信用评分，让就业变得愈发艰难 [87]。这便是一个由潜藏在数学严谨性与数据外衣之下的有害假设所引发的恶性循环。

We can’t always predict when such feedback loops happen. However, many consequences can be predicted by **thinking about the entire system** (not just the computer‐ized parts, but also the people interacting with it)—an approach known as systemsthinking [92]. We can try to understand how a data analysis system responds to dif‐ferent behaviors, structures, or characteristics. Does the system reinforce and amplifyexisting differences between people (e.g., making the rich richer or the poor poorer),or does it try to combat injustice? And even with the best intentions, we must bewareof unintended consequences.

我们无法总是预判这类反馈循环何时会出现。不过，通过**系统思维**的分析方法，考量整个系统的运行逻辑（不仅包括计算机化的组件，还涵盖与系统产生交互的人类群体），许多潜在后果是可以预见的 [92]。我们可以尝试去分析：数据分析系统会对不同的行为、结构或特征做出怎样的反应？该系统是在强化并放大人与人之间既存的差异（例如，让富人更富、穷人更穷），还是在试图消除不公？即便出发点再好，我们也必须警惕那些非预期的后果。

