[toc]

## Chapter 6. Partitioning

### Partitioning and Replication

分区与复制

**Partitioning is usually combined with replication** so that copies of each partition arestored on multiple nodes. This means that, even though each record belongs toexactly one partition, it may still be stored on several different nodes for fault tolerance.

**分区通常会与复制结合使用**，这样一来，每个分区的副本就会存储在多个节点上。这意味着，尽管每条记录**只属于某一个分区**，但为了实现容错性，该记录仍可能被存储在多个不同的节点上。

A node may store more than one partition. If a leader–follower replication model isused, the combination of partitioning and replication can look like Figure 6-1. Eachpartition’s leader is assigned to one node, and its followers are assigned to othernodes. Each node may be the leader for some partitions and a follower for other partitions.

一个节点可以存储多个分区。若采用**主从复制模型**，分区与复制的结合方式可参见图 6-1。每个分区的主节点会被分配至某一个节点，而该分区的从节点则分配至其他节点。**每个节点既可以是某些分区的主节点，同时也可以是另一些分区的从节点**。

![微信图片_20260119232051_176_109](../../images/distribuide_system/DDIA-6-1.jpg)

### Partitioning of Key-Value Data

If the partitioning is unfair, so that some partitions have more data or queries thanothers, we call it **skewed**. The presence of skew makes partitioning much less effective.In an extreme case, all the load could end up on one partition, so 9 out of 10 nodesare idle and your bottleneck is the single busy node. **A partition with disproportionately high load is called a hot spot.**

若分区策略设计得不够均衡，导致部分分区的数据量或查询量远超其他分区，这种情况就称为**数据倾斜** 。数据倾斜的存在会大幅削弱分区策略的效果。

在极端情况下，所有负载最终都集中在某一个分区上，导致十台节点中有九台处于闲置状态，而系统的性能瓶颈就变成了这台超负荷运转的节点。**负载量异常偏高的分区，被称为热点分区**。

#### Skewed Workloads and Relieving Hot Spots

**倾斜的负载与热点缓解**

Today, most data systems are not able to automatically compensate for such a highlyskewed workload, so it’s the responsibility of the application to reduce the skew. Forexample, if one key is known to be very hot, a simple technique is to add a randomnumber to the beginning or end of the key. Just a two-digit decimal random numberwould split the writes to the key evenly across 100 different keys, allowing those keysto be distributed to different partitions.

如今，大多数数据系统都无法自动应对这类高度倾斜的负载，因此**减轻数据倾斜的责任需要由应用层来承担**。例如，若已知某个键是高频热点键，一种简单的解决办法是在该键的开头或结尾添加一个随机数。仅一个两位十进制随机数，就能将对原键的写入请求均匀分散到 100 个不同的键上，进而让这些键被分配至不同的分区。

However, having split the writes across different keys, any reads now have to do addi‐tional work, as they have to read the data from all 100 keys and combine it. This tech‐nique also requires additional bookkeeping: it only makes sense to append therandom number for the small number of hot keys; for the vast majority of keys withlow write throughput this would be unnecessary overhead. Thus, you also need someway of keeping track of which keys are being split.

但这种做法会给读取操作带来额外的工作量 —— 因为读取时需要从这 100 个键中分别获取数据，再将结果合并。同时，该方案还需要额外的记录工作：只有对少数热点键添加随机数才有意义；对于绝大多数写入吞吐量较低的普通键来说，这种操作只会造成不必要的开销。因此，应用层还需要有相应的机制，**记录哪些键是被拆分处理的热点键**。

### Request Routing

This is an instance of a more general problem called **service discovery**, which isn’tlimited to just databases. Any piece of software that is accessible over a network hasthis problem, especially if it is aiming for high availability (running in a **redundan tconfiguration** on multiple machines). Many companies have written their own in-house service discovery tools, and many of these have been released as open source[30].

这是一个更通用的问题 ——**服务发现**的具体体现，该问题并非数据库领域所独有。任何可通过网络访问的软件都会面临这个问题，尤其是那些追求高可用性（在多台机器上以**冗余配置**运行）的软件。许多企业都开发了自研的服务发现工具，其中不少已作为开源项目发布 [30]。

On a high level, there are a few different approaches to this problem (illustrated inFigure 6-7):

1. Allow clients to contact any node (e.g., via a **round-robin load balancer**). If that node coincidentally owns the partition to which the request applies, it can handle the request directly; otherwise, it forwards the request to the appropriate node,receives the reply, and passes the reply along to the client.
2. Send all requests from clients to a **routing tier** first, which determines the node that should handle each request and forwards it accordingly. This routing tier does not itself handle any requests; it only acts as a **partition-aware load balancer**.
3. Require that clients **be aware of the partitioning and the assignment of partitions to nodes**. In this case, a client can connect directly to the appropriate node,without any intermediary.

从宏观层面来看，解决该问题有以下几种不同方案（如图 6-7 所示）：

1. 允许客户端访问任意节点（例如，通过**轮询负载均衡器**）。如果该节点恰好负责请求对应的分区，就可以直接处理这个请求；否则，该节点会将请求转发至对应的目标节点，待接收目标节点的回复后，再将结果反馈给客户端。
2. 先将客户端的所有请求发送至**路由层**，由路由层确定每个请求应对应的处理节点，并完成请求转发。该路由层不处理任何业务请求，仅充当**感知分区的负载均衡器**。
3. 要求客户端**知晓分区情况以及分区与节点的对应关系**。这种情况下，客户端无需任何中间层，即可直接连接到对应的处理节点。

![Figure 6-7](../../images/distribuide_system/DDIA-6-7.jpg)

> Figure 6-7: Three different ways of routing a request to right nodes

Many distributed data systems rely on a **separate coordination service** such as **ZooKeeper** to keep track of this cluster metadata, as illustrated in Figure 6-8. Each noderegisters itself in ZooKeeper, and ZooKeeper maintains the authoritative mapping ofpartitions to nodes. Other actors, such as the routing tier or the partitioning-awareclient, can subscribe to this information in ZooKeeper. Whenever a partition changesownership, or a node is added or removed, ZooKeeper notifies the routing tier so thatit can keep its routing information up to date.

许多分布式数据系统会依赖 **ZooKeeper** 这类独立的**协调服务**，来维护集群的元数据信息（如图 6-8 所示）。每个节点会在 ZooKeeper 中完成自身注册，ZooKeeper 则负责维护**分区与节点之间的权威映射关系**。路由层、感知分区的客户端等其他角色，可以在 ZooKeeper 中订阅这些信息。每当某个分区的归属权发生变更，或是有节点新增、移除时，ZooKeeper 都会及时通知路由层，使其能够实时更新自身的路由信息。