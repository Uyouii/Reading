[toc]

# Part III. Derived Data

On a high level, systems that store and process data can be grouped into two broadcategories:

- **Systems of record** A system of record, also known as source of truth, holds the authoritative version of your data. When new data comes in, e.g., as user input, it is first written here. Each fact is represented exactly once (the representation is typically normalized). If there is any discrepancy between another system and the system of record,then the value in the system of record is (by definition) the correct one.
- **Derived data systems** Data in a derived system is the result of taking some existing data from another system and transforming or processing it in some way. If you lose derived data,you can recreate it from the original source. A classic example is a cache: data can be served from the cache if present, but if the cache doesn’t contain what you need, you can fall back to the underlying database. Denormalized values, indexes,and materialized views also fall into this category. In recommendation systems,predictive summary data is often derived from usage logs.

从宏观层面划分，存储与处理数据的系统可分为两大类

- **记录系统** 记录系统也被称为**权威数据源**，存储的是数据的**权威版本**。当有新数据产生时（例如用户输入的数据），会优先写入该系统。系统内的**每项数据事实仅需唯一表征**（其数据结构通常为范式化形式）。若其他系统与记录系统的数据存在不一致，根据定义，记录系统中的数据值即为正确值。
- **衍生数据系统** 衍生数据系统中的数据，是通过对其他系统的已有数据执行某种转换或处理操作后得到的结果。即便衍生数据丢失，也可从原始数据源重新生成。 一个典型示例是**缓存**：若缓存中存在目标数据，则直接从中读取；若缓存未存储所需数据，则可以回源至底层数据库查询。此外，**反范式化数据**、**索引**以及**物化视图**也都属于衍生数据的范畴。在推荐系统中，用于预测分析的汇总数据，通常也是从用户行为日志这类原始数据中衍生而来。

Most databases, storage engines, and query languages are not inherently either a sys‐tem of record or a derived system. A database is just a tool: how you use it is up toyou. The distinction between system of record and derived data system depends noton the tool, but on how you use it in your application.

大多数数据库、存储引擎和查询语言，**本质上既不属于记录系统，也不属于衍生数据系统**。数据库本身只是一种工具，具体如何使用完全取决于你。记录系统与衍生数据系统的区别，**并不取决于工具本身，而在于你在应用程序中对它的使用方式**。

By being clear about which data is derived from which other data, you can bringclarity to an otherwise confusing system architecture. This point will be a runningtheme throughout this part of the book.

明确哪些数据是从其他哪些数据衍生而来，你就能理清原本可能混乱不堪的系统架构。这一点，将作为**贯穿本书本部分内容的核心主题**。

## Chapter 10. Batch Processing

**Services (online systems)** A service waits for a request or instruction from a client to arrive. When one is received, the service tries to handle it as quickly as possible and sends a response back. Response time is usually the primary measure of performance of a service,and availability is often very important (if the client can’t reach the service, the user will probably get an error message).

**服务型系统（在线系统）** 服务型系统会等待客户端的请求或指令抵达。一旦接收到请求，系统会以最快速度处理并返回响应。**响应时间**通常是衡量服务性能的核心指标，而**可用性**也至关重要 —— 如果客户端无法连接到服务，用户很可能会收到错误提示。

**Batch processing systems (offline systems)** A batch processing system takes a large amount of input data, runs a job to pro‐ cess it, and produces some output data. Jobs often take a while (from a few minutes to several days), so there normally isn’t a user waiting for the job to fin‐ ish. Instead, batch jobs are often scheduled to run periodically (for example, once a day). The primary performance measure of a batch job is usually throughput (the time it takes to crunch through an input dataset of a certain size). We dis‐ cuss batch processing in this chapter.

**批处理系统（离线系统）** 批处理系统接收大量输入数据，运行任务对其进行处理，最终生成输出数据。这类任务的执行往往需要一定时间（从数分钟到数天不等），因此通常不会有用户等待任务完成。相反，批处理任务一般会被设置为周期性运行（例如每天一次）。衡量批处理任务性能的核心指标通常是**吞吐量**，即处理完指定规模输入数据集所需的时间。本章将围绕批处理展开讨论。

**Stream processing systems (near-real-time systems)** Stream processing is somewhere between online and offline/batch processing (so it is sometimes called near-real-timeor nearline processing). Like a batch pro‐ cessing system, a stream processor consumes inputs and produces outputs (rather than responding to requests). However, a stream job operates on events shortly after they happen, whereas a batch job operates on a fixed set of input data. This difference allows stream processing systems to have lower latency than the equivalent batch systems. As stream processing builds upon batch process‐ ing, we discuss it in Chapter 11.

**流处理系统（准实时系统）** 流处理介于在线系统与离线 / 批处理系统之间（因此有时也被称为**准实时处理**或**准在线处理**）。与批处理系统类似，流处理器会消费输入数据并生成输出数据（而非响应请求）。但两者的区别在于，流处理任务会**在事件发生后极短时间内对其进行处理**，而批处理任务则针对固定的输入数据集进行操作。这一差异让流处理系统的延迟低于同等场景下的批处理系统。由于流处理是基于批处理发展而来，相关内容将在本书第 11 章中探讨。

### Batch Processing with Unix Tools

#### The Unix Philosophy

Doug McIlroy, the inventor of Unix pipes, first described them like this in 1964 [11]:“We should have some ways of connecting programs like [a] garden hose—screw inanother segment when it becomes necessary to massage data in another way. This isthe way of I/O also.” 

Unix 管道的发明者道格・麦克罗伊（Doug McIlroy）早在 1964 年就对其做出了这样的描述 [11]：

> 我们应当找到一种方式，像连接花园水管一样拼接程序 —— 当需要以新的方式处理数据时，直接接入一段新的程序即可。这同样也是输入输出（I/O）的运作之道。

The plumbing analogy stuck, and the idea of connecting programs with pipes became part of what is now known as the Unix philosophy—a set ofdesign principles that became popular among the developers and users of Unix. Thephilosophy was described in 1978 as follows [12, 13]:

1. Make each program do one thing well. To do a new job, build afresh rather than complicate old programs by adding new “features”.
2. Expect the output of every program to become the input to another, as yet unknown, program. Don’t clutter output with extraneous information. Avoid stringently columnar or binary input formats. Don’t insist on interactive input.
3. Design and build software, even operating systems, to be tried early, ideally within weeks. Don’t hesitate to throw away the clumsy parts and rebuild them.
4. Use tools in preference to unskilled help to lighten a programming task, even if you have to detour to build the tools and expect to throw some of them out after you’ve finished using them.

这个 “管道” 的比喻沿用至今，而**用管道连接程序**的理念，也成为了如今广为人知的 **Unix 哲学**的核心组成部分。这套设计原则在 Unix 的开发者与用户群体中备受推崇，并在 1978 年被归纳为以下四条 [12,13]：

1. 让每个程序只做好一件事。若要完成新任务，应重新开发一个全新的程序，而非为旧程序添加新功能使其变得臃肿。
2. 假定每个程序的输出，都将成为另一个未知程序的输入。不要用无关信息污染输出内容，避免使用严格的列格式或二进制输入格式，同时不强制要求交互式输入。
3. 软件（甚至操作系统）的设计与开发应追求尽早试用，理想情况下几周内就能产出原型。对于设计拙劣的部分，要果断舍弃并重新构建。
4. 优先使用工具来减轻编程任务的负担，哪怕为此需要先绕道开发工具，且预计部分工具在使用完毕后就会被弃用。

This approach—**automation**, **rapid prototyping**, **incremental iteration**, **being friendly to experimentation**, and **breaking down large projects into manageable chunks**—sounds remarkably like the Agile and DevOps movements of today. Surprisingly littlehas changed in four decades.

这种强调**自动化、快速原型设计、增量迭代、鼓励实验，以及将大型项目拆解为可管理的小模块**的方法论，听起来与如今的敏捷开发（Agile）和 DevOps 运动惊人地相似。时隔四十年，软件开发的核心思路竟几乎没有改变。

A Unix shell like bashlets us easily compose these small programs into surprisinglypowerful data processing jobs. Even though many of these programs are written bydifferent groups of people, they can be joined together in flexible ways. What doesUnix do to enable this composability?

像 bash 这样的 Unix Shell，能让我们轻松地将这些小巧的程序组合成功能强大的数据处理任务。尽管许多程序由不同团队开发，但它们仍能以灵活的方式协同工作。那么，Unix 究竟是通过哪些设计，实现了这种**可组合性**的呢？

**A uniform interface**

**统一接口**

If you expect the output of one program to become the input to another program,that means those programs must use the same data format—in other words, a com‐patible interface. If you want to be able to connect anyprogram’s output to any pro‐gram’s input, that means that all programs must use the same input/output interface.

若你希望将一个程序的输出，直接作为另一个程序的输入，就意味着这两个程序必须采用相同的数据格式 —— 换句话说，它们需要具备**兼容的接口**。而若要实现任意程序的输出与任意程序的输入相互对接，就意味着所有程序都必须遵循**统一的输入输出接口规范**。

In Unix, that interface is a **file** (or, more precisely, a file descriptor). A file is just an **ordered sequence of bytes**. Because that is such a simple interface, many differentthings can be represented using the same interface: an actual file on the filesystem, acommunication channel to another process (Unix socket, stdin, stdout), a devicedriver (say /dev/audioor /dev/lp0), a socket representing a TCP connection, and soon. It’s easy to take this for granted, but it’s actually quite remarkable that these verydifferent things can share a uniform interface, so they can easily be plugged together.ii

在 Unix 系统中，这套接口的载体是**文件**（更准确地说，是文件描述符）。文件的本质就是一个**有序的字节流**。正因为这一接口足够简单，大量截然不同的实体都能通过这套统一接口来表示：既可以是文件系统中的实际文件，也可以是与其他进程通信的信道（如 Unix 套接字、标准输入、标准输出），还可以是设备驱动程序（例如 `/dev/audio` 音频设备或 `/dev/lp0` 打印机设备），或是表示 TCP 连接的套接字，等等。我们很容易对此习以为常，但实际上，这些功能截然不同的实体能够共用一套统一接口，从而实现便捷的互联互通，这一点是非常了不起的。

### MapReduce and Distributed Filesystems

#### The Output of Batch Workflows

**Philosophy of batch process outputs**

**批处理输出的设计理念**

The Unix philosophy that we discussed earlier in this chapter (“The Unix Philoso‐phy” on page 394) encourages experimentation by being very explicit about dataflow:a program reads its input and writes its output. In the process, the input is leftunchanged, any previous output is completely replaced with the new output, andthere are no other side effects. This means that you can rerun a command as often asyou like, tweaking or debugging it, without messing up the state of your system.

本章前文探讨的 Unix 设计理念（详见本书第 394 页的《Unix 设计哲学》一节），通过**明确数据流走向**的方式鼓励开发者大胆尝试：程序读取输入数据，经处理后生成输出结果。在此过程中，输入数据保持**不可变**，原有输出会被全新输出完全覆盖，且不会产生任何其他副作用。这意味着你可以反复执行某条命令，不断调试、优化参数，而不必担心破坏系统状态。

The handling of output from MapReduce jobs follows the same philosophy. By treat‐ing inputs as immutable and avoiding side effects (such as writing to external data‐bases), batch jobs not only achieve good performance but also become much easier tomaintain:

- If you introduce a bug into the code and the output is wrong or corrupted, you can simply roll back to a previous version of the code and rerun the job, and the output will be correct again. Or, even simpler, you can keep the old output in a different directory and simply switch back to it. Databases with read-write trans‐ actions do not have this property: if you deploy buggy code that writes bad data to the database, then rolling back the code will do nothing to fix the data in the database. (The idea of being able to recover from buggy code has been called human fault tolerance [50].)
-  As a consequence of this ease of rolling back, feature development can proceed more quickly than in an environment where mistakes could mean irreversible damage. This principle of minimizing irreversibility is beneficial for Agile soft‐ ware development [51].
- If a map or reduce task fails, the MapReduce framework automatically re- schedules it and runs it again on the same input. If the failure is due to a bug in the code, it will keep crashing and eventually cause the job to fail after a few attempts; but if the failure is due to a transient issue, the fault is tolerated. This automatic retry is only safe because inputs are immutable and outputs from failed tasks are discarded by the MapReduce framework.
- The same set of files can be used as input for various different jobs, including monitoring jobs that calculate metrics and evaluate whether a job’s output has the expected characteristics (for example, by comparing it to the output from the previous run and measuring discrepancies).
- Like Unix tools, MapReduce jobs separate logic from wiring (configuring the input and output directories), which provides a separation of concerns and ena‐ bles potential reuse of code: one team can focus on implementing a job that does one thing well, while other teams can decide where and when to run that job.

MapReduce 任务对输出结果的处理方式，同样遵循这一设计理念。通过将输入视为不可变数据、避免产生副作用（例如向外部数据库写入数据），批处理任务不仅能获得出色的性能表现，还能大幅降低运维成本，具体体现在以下几点：

1. 若代码引入缺陷导致输出结果错误或损坏，你只需回滚到代码的历史版本并重新执行任务，即可生成正确的输出。更简单的做法是，将旧版输出文件保留在独立目录中，直接切换回旧版本即可。而支持读写事务的数据库则不具备这一特性：如果部署的缺陷代码向数据库写入了错误数据，仅回滚代码并不能修复数据库中的错误数据。（这种能够从缺陷代码引发的问题中恢复的设计思路，被称为**人为故障容错能力**[50]）。
2. 正因为回滚操作如此便捷，功能开发的迭代速度可以远超那些一次失误就可能造成不可逆损害的系统。这种**最小化不可逆操作**的原则，对敏捷软件开发 [51] 的实践大有裨益。
3. 若某个 Map 或 Reduce 任务执行失败，MapReduce 框架会自动重新调度该任务，并基于相同的输入数据再次运行。如果失败是由代码缺陷导致的，任务会持续崩溃，在多次重试后最终导致整个作业失败；但如果失败源于临时性故障（如网络抖动、节点短暂不可用），故障即可被容忍。这种自动重试机制之所以安全可靠，是因为输入数据是不可变的，且失败任务产生的输出会被 MapReduce 框架自动丢弃。
4. 同一组输入文件可被多个不同的任务复用，其中包括监控任务 —— 这类任务会计算相关指标，校验作业输出是否符合预期（例如将本次输出与上一次执行的输出对比，计算两者的差异值）。
5. 与 Unix 工具类似，MapReduce 任务将**业务逻辑与配置（即输入输出目录的设置）解耦**，实现了关注点分离，同时提升了代码的潜在复用性：一个团队可以专注于开发单一功能的任务，其他团队则可以自主决定该任务的运行时机与运行位置。

#### Comparing Hadoop to Distributed Databases

**对比 Hadoop 与分布式数据库**

Indiscriminate data dumping shifts the burden of interpreting the data: instead offorcing the producer of a dataset to bring it into a standardized format, the interpretation of the data becomes the consumer’s problem (the schema-on-read approach[56]; see “Schema flexibility in the document model” on page 39). This can be anadvantage if the producer and consumers are different teams with different priorities.There may not even be one ideal data model, but rather different views onto the datathat are suitable for different purposes. Simply dumping data in its raw form allowsfor several such transformations. This approach has been dubbed the **sushi principle**:“raw data is better” [57].

无差别地转储原始数据，相当于将数据解读的负担转嫁出去：它不再强制数据集的生产者将数据整理为标准化格式，而是把数据解读的工作交由数据消费者来完成（这一方式即**读时模式**[56]，详见本书第 39 页的 “文档模型中的模式灵活性” 一节）。如果数据的生产者与消费者分属不同团队，且各自的工作优先级不同，这种方式会显现出优势。面对同一批数据，或许并不存在唯一的理想数据模型，反而是不同的数据视图更适合不同的业务场景。直接以原始格式转储数据，就为多种数据转换需求提供了实现空间。这种理念也被戏称为**寿司原则**：“原始数据更有价值”[57]。

To understand the reasons for MapReduce’s sparing use of memory and task-levelrecovery, it is helpful to look at the environment for which MapReduce was originallydesigned. Google has mixed-use datacenters, in which online production services andoffline batch jobs run on the same machines. Every task has a resource allocation(CPU cores, RAM, disk space, etc.) that is enforced using containers. Every task alsohas a priority, and if a higher-priority task needs more resources, lower-priority taskson the same machine can be terminated (preempted) in order to free up resources.Priority also determines pricing of the computing resources: teams must pay for theresources they use, and higher-priority processes cost more [59].

想要理解 MapReduce 为何如此节省内存，又为何要设计任务级恢复机制，我们不妨先了解 MapReduce 的原生设计环境。谷歌采用的是**混合用途数据中心**，在线生产服务与离线批处理任务会运行在同一批物理机器上。每个任务都会被分配固定的资源配额（包括 CPU 核心数、内存、磁盘空间等），并通过容器技术强制执行资源限制。同时，每个任务都被赋予相应的优先级：当高优先级任务需要更多资源时，运行在同一台机器上的低优先级任务会被终止（即**抢占**），以释放资源。任务优先级还会与计算资源的计费挂钩：团队需要为其使用的资源付费，且高优先级进程的计费标准更高 [59]。

This architecture allows non-production (low-priority) computing resources to beovercommitted, because the system knows that it can reclaim the resources if neces‐sary. Overcommitting resources in turn allows better utilization of machines andgreater efficiency compared to systems that segregate production and non-production tasks. However, as MapReduce jobs run at low priority, they run the riskof being preempted at any time because a higher-priority process requires theirresources. Batch jobs effectively “pick up the scraps under the table,” using any com‐puting resources that remain after the high-priority processes have taken what theyneed.

这种架构允许对非生产环境（低优先级）的计算资源进行**超配**，因为系统明确知道，必要时可以回收这些资源。相比那些将生产任务与非生产任务严格隔离的系统，资源超配能够提升机器利用率，实现更高的运行效率。但问题在于，MapReduce 任务通常以低优先级运行，因此随时可能因高优先级进程需要资源而被抢占终止。从本质上讲，批处理任务就是在 “捡漏式” 利用资源 —— 它们只会占用高优先级进程分配剩余的计算资源。

At Google, a MapReduce task that runs for an hour has an approximately 5% risk ofbeing terminated to make space for a higher-priority process. This rate is more thanan order of magnitude higher than the rate of failures due to hardware issues,machine reboot, or other reasons [59]. At this rate of preemptions, if a job has 100tasks that each run for 10 minutes, there is a risk greater than 50% that at least onetask will be terminated before it is finished.

在谷歌的环境中，一个运行时长为 1 小时的 MapReduce 任务，因需要为高优先级进程腾出空间而被终止的概率约为 5%。这一概率，比因硬件故障、机器重启或其他原因导致的任务失败率高出一个数量级 [59]。按照这个抢占概率计算，如果一个作业包含 100 个任务，每个任务运行 10 分钟，那么至少有一个任务会在完成前被终止的概率将超过 50%。

And this is why MapReduce is designed to tolerate frequent unexpected task termina‐tion: it’s not because the hardware is particularly unreliable, it’s because the freedomto arbitrarily terminate processes enables better resource utilization in a computing cluster.

这也正是 MapReduce 被设计为能够容忍频繁的意外任务终止的原因所在：这并非因为硬件本身特别不可靠，而是因为**允许系统任意终止进程**，才能在计算集群中实现更优的资源利用率。

### Beyound MapReduce

**Dataflow engines**

**数据流引擎**

In order to fix these problems with MapReduce, several new execution engines fordistributed batch computations were developed, the most well known of which areSpark [61, 62], Tez [63, 64], and Flink [65, 66]. There are various differences in theway they are designed, but they have one thing in common: they handle an entireworkflow as one job, rather than breaking it up into independent subjobs.

为解决 MapReduce 存在的诸多问题，多款新一代分布式批处理执行引擎应运而生，其中最具代表性的有 Spark [61,62]、Tez [63,64] 以及 Flink [65,66]。这些引擎的设计细节虽各有不同，但存在一个核心共性：**它们会将整个数据处理工作流作为单个作业来处理，而非拆分为多个相互独立的子作业**。

Since they explicitly model the flow of data through several processing stages, thesesystems are known as dataflow engines. Like MapReduce, they work by repeatedlycalling a user-defined function to process one record at a time on a single thread.They parallelize work by partitioning inputs, and they copy the output of one func‐tion over the network to become the input to another function.

由于这类系统会显式地对多处理阶段间的数据流进行建模，因此被称为**数据流引擎**。与 MapReduce 类似，数据流引擎的工作原理也是通过反复调用用户自定义函数，在单线程上逐条处理数据记录。它们通过对输入数据进行分区来实现并行计算，并将一个函数的输出结果通过网络传输，作为另一个函数的输入。

Unlike in MapReduce, these functions need not take the strict roles of alternatingmap and reduce, but instead can be assembled in more flexible ways. We call these functions **operators**, and the dataflow engine provides several different options forconnecting one operator’s output to another’s input:

- One option is to repartition and sort records by key, like in the shuffle stage of MapReduce (see “Distributed execution of MapReduce” on page 400). This fea‐ ture enables sort-merge joins and grouping in the same way as in MapReduce.
- Another possibility is to take several inputs and to partition them in the same way, but skip the sorting. This saves effort on partitioned hash joins, where the partitioning of records is important but the order is irrelevant because building the hash table randomizes the order anyway.
- For broadcast hash joins, the same output from one operator can be sent to all partitions of the join operator.

但与 MapReduce 不同的是，这些函数无需严格扮演交替出现的 Map 与 Reduce 角色，而是可以通过更灵活的方式组合。我们将这些函数称为**operators**，数据流引擎提供了多种方式，用于实现算子输出与另一operator输入的对接：

1. 第一种方式是**按照 key 对记录进行重分区与排序**，与 MapReduce 的混洗阶段逻辑一致（详见本书第 400 页的 “MapReduce 的分布式执行” 一节）。该特性能够像 MapReduce 一样，支持排序合并连接与分组聚合操作。
2. 第二种方式是**对多个输入数据集采用相同的分区策略，但跳过排序步骤**。这种方式能为分区哈希连接节省大量开销 —— 在这类场景中，记录的分区方式至关重要，但顺序无关紧要，因为构建哈希表的过程本身就会打乱数据原有的顺序。
3. 针对**广播哈希连接**场景，可将某一个operator的输出结果，发送至连接operator的所有分区。

This style of processing engine is based on research systems like Dryad [67] andNephele [68], and it offers several advantages compared to the MapReduce model:

- Expensive work such as sorting need only be performed in places where it is actually required, rather than always happening by default between every map and reduce stage.
- There are **no unnecessary map tasks**, since the work done by a mapper can often be incorporated into the preceding reduce operator (because a mapper does not change the partitioning of a dataset).
- Because all joins and data dependencies in a workflow are explicitly declared, the scheduler has an overview of what data is required where, so it can make **locality optimizations**. For example, it can try to place the task that consumes some data on the same machine as the task that produces it, so that the data can be exchanged through a shared memory buffer rather than having to copy it overthe network.
- It is usually sufficient for intermediate state between operators to be kept in memory or written to local disk, which requires less I/O than writing it to HDFS (where it must be replicated to several machines and written to disk on each rep‐ lica). MapReduce already uses this optimization for mapper output, but dataflow engines generalize the idea to all intermediate state.
- Operators can start executing as soon as their input is ready; there is no need to wait for the entire preceding stage to finish before the next one starts.
- Existing Java Virtual Machine (JVM) processes can be reused to run new operators, reducing startup overheads compared to MapReduce (which launches a new JVM for each task).

这类处理引擎的设计理念源于 Dryad [67]、Nephele [68] 等学术研究系统，相比 MapReduce 模型，它具备多项显著优势：

1. **排序等开销高昂的操作仅在真正需要时执行**，而非像 MapReduce 那样，默认在每一个 Map 与 Reduce 阶段之间都执行排序。
2. **不存在多余的 Map 任务**—— 因为 mapper的处理逻辑通常可以并入前序的 Reduce operator中（这是由于 mapper 不会改变数据集的分区方式）。
3. 由于工作流中的所有连接操作与数据依赖关系都被显式声明，调度器能够全局掌握数据的需求分布，进而实现**本地化优化**。例如，调度器可以尝试将数据消费任务与数据生产任务部署在同一台机器上，这样数据就可以通过共享内存缓冲区进行交换，而无需通过网络传输。
4. operators之间的中间状态通常只需保存在内存中，或写入本地磁盘 —— 这种方式的 I/O 开销远低于写入 HDFS（HDFS 要求数据在多台机器上创建副本，且每个副本都需写入磁盘）。MapReduce 仅对 mapper的输出采用了这种优化，而数据流引擎则将这一思路推广到了所有中间状态。
5. **Operators一旦输入数据就绪即可开始执行**，无需等待前一处理阶段的所有任务全部完成。
6. 可以复用已有的 Java 虚拟机（JVM）进程来运行新的operators，相比 MapReduce（为每个任务都启动一个全新的 JVM 进程），大幅降低了进程启动开销。

You can use dataflow engines to implement the same computations as MapReduceworkflows, and they usually execute significantly faster due to the optimizationsdescribed here. Since operators are a generalization of map and reduce, the same processing code can run on either execution engine: workflows implemented in Pig,Hive, or Cascading can be switched from MapReduce to Tez or Spark with a simpleconfiguration change, without modifying code [64].

数据流引擎可以实现 MapReduce 工作流支持的所有计算任务，并且借助上述优化手段，执行速度通常会显著提升。由于operators是 Map 和 Reduce 功能的泛化形式，**相同的处理代码可以在任意一种执行引擎上运行**：例如，基于 Pig、Hive 或 Cascading 开发的工作流，只需简单修改配置，无需改动任何代码，就能从 MapReduce 引擎切换到 Tez 或 Spark 引擎 [64]。

