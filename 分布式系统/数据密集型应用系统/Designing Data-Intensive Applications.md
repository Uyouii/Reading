[toc]

## Chapter 1. Reliable, Scalable, and Maintainable Applications

第一章. 可靠，可扩张和和维护的应用程序

### Reliability

**Reliability** The system should continue to work correctly (performing the correct function at the desired level of performance) even in the face of adversity (hardware or soft‐ ware faults, and even human error)

**可靠性（Reliability）**：系统即使在面临不利情况时（包括硬件或软件故障，甚至人为错误），也应当能够继续**正确地运行**，并在**期望的性能水平**下完成其应有的功能。

Scalability As the system grows (in data volume, traffic volume, or complexity), there should be reasonable ways of dealing with that growth.

**可扩展性（Scalability）**：随着系统规模的增长（例如数据量、流量规模或系统复杂度的提升），应当有**合理可行的方式**来应对这种增长。

Maintainability Over time, many different people will work on the system (engineering and oper‐ ations, both maintaining current behavior and adapting the system to new use cases), and they should all be able to work on it productively

**可维护性（Maintainability）**：随着时间推移，许多不同的人都会参与到系统的工作中（包括工程和运维人员，既要维护现有行为，也要将系统适配到新的使用场景），并且他们都应当能够**高效、富有成效地**开展工作。

#### Hardware Faults

Hard disks are reported as having a mean time to failure (MTTF) of about 10 to 50years [5, 6]. Thus, on a storage cluster with 10,000 disks, we should expect on averageone disk to die per day.

硬盘通常被报告其**平均无故障时间（MTTF）**约为 **10 到 50 年** [5, 6]。因此，在一个拥有 **10,000 块磁盘**的存储集群中，**平均每天都会有一块磁盘发生故障**。

### Maintainability

It is well known that the majority of the cost of software is not in its initial develop‐ment, but in its ongoing maintenance—fixing bugs, keeping its systems operational,investigating failures, adapting it to new platforms,modifying it for new use cases,repaying technical debt, and adding new features.

众所周知，**软件成本的大头并不在最初的开发阶段**，而是在其**持续的维护过程中**——包括修复缺陷、保障系统持续运行、排查故障、适配新的平台、支持新的使用场景、偿还技术债务以及添加新功能。

Operability Make it easy for operations teams to keep the system runningsmoothly.

**可运维性（Operability）**： 使运维团队能够**轻松地**保障系统**平稳、持续地运行**。

Simplicity Make it easy for new engineers to understand the system, byremoving as muchcomplexity as possible from the system. (Note this is notthe same as simplicityof the user interface.)

**简单性（Simplicity）**：通过尽可能消除系统中的复杂性，使**新工程师能够容易地理解系统**。（注意：这并不等同于用户界面的简单性。）

EvolvabilityMake it easy for engineers to make changes to the system in thefuture, adaptingit for unanticipated use cases as requirements change. Alsoknown as extensibil‐ity, modifiability, or plasticity.

**可演进性（Evolvability）**：使工程师能够在未来**方便地对系统进行修改**，以适应需求变化下**事先未预料到的使用场景**。
 也称为**可扩展性（extensibility）**、**可修改性（modifiability）\**或\**可塑性（plasticity）**。



One of the best tools we have for removing accidental complexity is abstraction. Agood abstraction can hide a great deal of implementationdetail behind a clean,simple-to-understand façade. A good abstraction canalso be used for a wide range ofdifferent applications. Not only is this reusemore efficient than reimplementing asimilar thing multiple times, but it alsoleads to higher-quality software, as qualityimprovements in the abstractedcomponent benefit all applications that use it.

我们用于消除**偶然复杂性**的最佳工具之一是**抽象**。一个良好的抽象能够将大量的实现细节隐藏在**清晰、易于理解的外观（接口）\**之后。
好的抽象还可以被\**广泛应用于不同的场景**。这种复用不仅比多次重新实现类似功能更加高效，而且还能带来**更高质量的软件**，因为对被抽象组件所做的质量改进，会**惠及所有使用该组件的应用**。

## Chapter 2. Data Models and Query Languages

第二章 数据模型和查询语言

### Relational Model Versus Document Model 

关系模型和文档模型

The advantage of using an ID is that because it has no meaning to humans,it neverneeds to change: the ID can remain the same, even if the informationit identifieschanges. Anything that is meaningful to humans may need tochange sometime inthe future—and if that information is duplicated, all theredundant copies need to beupdated. That incurs write overheads, and risksinconsistencies (where some copiesof the information are updated butothers aren’t). Removing such duplication is thekey idea behind normalization in databases

使用标识符（ID）的优势在于，**它对人类不具备任何语义含义**，因此永远无需修改：即便其标识的信息发生变化，ID 也可以保持不变。任何对人类有语义含义的信息，未来都有可能需要修改 —— 而且如果这类信息存在重复存储的情况，那么所有冗余副本都需要逐一更新。这不仅会产生**写入开销**，还会带来**数据不一致的风险**（即部分信息副本完成了更新，其他副本却未同步更新）。**消除此类数据冗余**，正是数据库**规范化**设计的核心理念。



## Chapter 3. Storage and Retrieval

第三章. 存储和检索

### Data Structures That Power Your Database

This is an important trade-off in storage systems: well-chosen indexesspeed up readqueries, but every index slows down writes.

这是存储系统中的一个重要权衡：合理选择的索引可以加速读取查询，但每个索引都会减慢写入操作。



### Chapter 4. Encoding and Evolution

第 四章. 编码与进化

### Modes of Dataflow

However, there is an additional snag. Say you add a field to a record schema, and thenewer code writes a value for that new field to the database. Subsequently, an olderversion of the code (which doesn’t yet know about the new field) reads the record,updates it, and writes it back. In this situation, the desirable behavior is usually forthe old code to keep the new field intact, even though it couldn’t be interpreted.

然而，这里还有一个额外的陷阱。假设你向记录模式中添加了一个字段，较新的代码会将该字段的值写入数据库。随后，旧版本的代码（尚未知晓新字段）读取该记录、更新并重新写回。在这种情况下，理想的行为通常是旧代码应保持新字段的完整性，即使它无法解析该字段。

The encoding formats discussed previously support such preservation of unknownfields, but sometimes you need to take care at an application level, as illustrated inFigure 4-7. For example, if you decode a database value into model objects in theapplication, and later reencode those model objects, the unknown field might be lostin that translation process. Solving this is not a hard problem; you just need to beaware of it.

前面讨论的编码格式支持保留未知字段的功能，但在某些情况下你需要在应用程序层面特别注意，如图4-7所示。例如，如果将数据库值解码为应用程序中的模型对象，随后又重新编码这些模型对象时，未知字段可能会在转换过程中丢失。这个问题的解决方案并不困难，你只需要意识到它的存在即可。



Schema evolution thus allows the entire database to appear as if it was encoded with asingle schema, even though the underlying storage may contain records encoded withvarious historical versions of the schema.

因此，模式演变使得整个数据库看起来仿佛是使用单一模式编码的，即使其底层存储可能包含使用不同历史版本模式编码的记录。



The actor model is a programming model for concurrency in a single process. Ratherthan dealing directly with threads (and the associated problems of race conditions,locking, and deadlock), logic is encapsulated in actors. Each actor typically representsone client or entity, it may have some local state (which is not shared with any otheractor), and it communicates with other actors by sending and receiving asynchro‐nous messages. Message delivery is not guaranteed: in certain error scenarios, mes‐sages will be lost. Since each actor processes only one message at a time, it doesn’tneed to worry about threads, and each actor can be scheduled independently by theframework.

Actor模型是一种用于单个进程内并发的编程模型。它**而不是直接处理线程**（以及由此产生的竞态条件、锁和死锁等问题），而是将逻辑封装在Actor中。每个Actor通常代表一个客户端或实体，它可能拥有某些**局部状态**（该状态不会与其他Actor共享），并通过发送和接收**异步消息**与其他Actor通信。消息传递**不保证可靠**：在某些错误场景下，消息可能会丢失。由于每个Actor一次只处理一个消息，因此它**无需担心线程问题**，且每个Actor都可以由框架**独立调度**。

## Chapter 5. Replication

第 5 章 复制

### Leaders and Followers

You could make the files on disk consistent by locking the database (making itunavailable for writes), but that would go against our goal of high availability. Fortu‐nately, setting up a follower can usually be done without downtime. Conceptually,the process looks like this:

1. Take a consistent snapshot of the leader’s database at some point in time—if pos‐ sible, without taking a lock on the entire database. Most databases have this fea‐ ture, as it is also required for backups. In some cases, third-party tools are needed, such as innobackupex for MySQL.
2. Copy the snapshot to the new follower node.
3. The follower connects to the leader and requests all the data changes that have happened since the snapshot was taken. This requires that the snapshot is associ‐ ated with an exact position in the leader’s replication log. That position has vari‐ ous names: for example, PostgreSQL calls it the log sequence number, and MySQL calls it the binlog coordinates.
4. When the follower has processed the backlog of data changes since the snapshot,we say it has caught up. It can now continue to process data changes from the leader as they happen.

你可以通过锁定数据库（使其无法写入）来使磁盘上的文件保持一致，但这会违背我们追求高可用性的目标。幸运的是，通常可以在不中断服务的情况下完成从库的搭建。从概念上看，具体流程如下：

1. **获取主库的一致快照**：在某个时间点对主库数据库创建一个一致性的快照——**尽可能避免对整个数据库加锁**。大多数数据库都支持此功能（因为备份时也需要）。在某些情况下需要第三方工具，例如 MySQL 的 `innobackupex`。
2. **复制快照到新从库节点**：将快照文件完整复制到新的从库节点。
3. **同步增量数据**：从库连接主库，请求从快照创建时刻起**所有后续的数据变更**。这要求快照必须关联到主库复制日志中的一个精确位置，不同数据库对此位置有不同的称呼：
   - PostgreSQL 称其为 **日志序列号（LSN）**
   - MySQL 称其为 **二进制日志坐标（binlog 坐标）**
4. **完成数据同步**：当从库处理完快照创建后积累的所有数据变更时，我们称其已**追上主库进度**。此后，从库即可持续接收并处理主库实时产生的数据变更。



Leader failure: Failover

**领导者故障：故障转移**

Handling a failure of the leader is trickier: one of the followers needs to be promotedto be the new leader, clients need to be reconfigured to send their writes to the newleader, and the other followers need to start consuming data changes from the newleader. This process is called **failover**.

处理领导者故障更为复杂：需要将某个**从库提升为新的领导者**，客户端需重新配置以向新领导者发送写请求，其他从库需开始从新领导者消费数据变更。这一过程称为**故障转移**。

Failover can happen manually (an administrator is notified that the leader has failedand takes the necessary steps to make a new leader) or automatically. An automaticfailover process usually consists of the following steps:

1. Determining that the leader has failed. There are many things that could poten‐ tially go wrong: crashes, power outages, network issues, and more. There is no foolproof way of detecting what has gone wrong, so most systems simply use a timeout: nodes frequently bounce messages back and forth between each other,and if a node doesn’t respond for some period of time—say, 30 seconds—it is assumed to be dead. (If the leader is deliberately taken down for planned mainte‐ nance, this doesn’t apply.)
2. Choosing a new leader. This could be done through an election process (where the leader is chosen by a majority of the remaining replicas), or a new leader could be appointed by a previously elected controller node. The best candidate for leadership is usually the replica with the most up-to-date data changes from the old leader (to minimize any data loss). Getting all the nodes to agree on a new leader is a consensus problem, discussed in detail in Chapter 9.
3. Reconfiguring the system to use the new leader. Clients now need to send their write requests to the new leader (we discuss this in “Request Routing” on page 214). If the old leader comes back, it might still believe that it is the leader,not realizing that the other replicas have forced it to step down. The system needs to ensure that the old leader becomes a follower and recognizes the new leader.

故障转移可以是**人工**（管理员收到领导者故障通知后手动操作）或**自动**。自动故障转移通常包含以下步骤：

1. ***\*确认领导者故障\****. 潜在故障原因多样：崩溃、断电、网络问题等。无法100%可靠检测故障原因，因此多数系统采用**超时机制**：

   - 节点间频繁互发心跳包，若某节点在指定时间内（如30秒）无响应，则判定为故障。
   - **例外**：若领导者因计划性维护被主动下线，则不触发此机制。

2. ***\*选举新领导者\****

   - **选举机制**：剩余副本通过多数表决（majority）选出新领导者。
   - **指定机制**：由预选的控制器节点（controller node）直接任命。
   - **最优候选**：通常选择从旧领导者处**数据变更最完整**的副本（以最小化数据丢失风险）。
   - **共识问题**：所有节点需就新领导者达成一致，此问题在**第9章**详细讨论。

3. ***\*系统重新配置\****

   - **客户端路由**：客户端需将写请求重定向到新领导者（详见[第214页]的“请求路由”）。
   - **旧领导者恢复处理**：若旧领导者重新上线，可能仍自认为是领导者（未意识到已被强制下线）。系统需确保：
     - 旧领导者降级为从库
     - 旧领导者接受新领导者的权威



Failover is fraught with things that can go wrong:

- If asynchronous replication is used, the new leader may not have received all the writes from the old leader before it failed. If the former leader rejoins the cluster after a new leader has been chosen, what should happen to those writes? The new leader may have received conflicting writes in the meantime. The most common solution is for the old leader’s unreplicated writes to simply be discarded, which may violate clients’ durability expectations.
- Discarding writes is especially dangerous if other storage systems outside of the database need to be coordinated with the database contents. For example, in one incident at GitHub [13], an out-of-date MySQL follower was promoted to leader. The database used an autoincrementing counter to assign primary keys to new rows, but because the new leader’s counter lagged behind the old leader’s, itreused some primary keys that were previously assigned by the old leader. Theseprimary keys were also used in a Redis store, so the reuse of primary keys resul‐ted in inconsistency between MySQL and Redis, which caused some private datato be disclosed to the wrong users.
- In certain fault scenarios (see Chapter 8), it could happen that two nodes both believe that they are the leader. This situation is called split brain, and it is dan‐ gerous: if both leaders accept writes, and there is no process for resolving con‐ flicts (see “Multi-Leader Replication” on page 168), data is likely to be lost or corrupted. As a safety catch, some systems have a mechanism to shut down one node if two leaders are detected.ii However, if this mechanism is not carefully designed, you can end up with both nodes being shut down [14].
- What is the right timeout before the leader is declared dead? A longer timeout means a longer time to recovery in the case where the leader fails. However, if the timeout is too short, there could be unnecessary failovers. For example, a tempo‐ rary load spike could cause a node’s response time to increase above the timeout,or a network glitch could cause delayed packets. If the system is already strug‐ gling with high load or network problems, an unnecessary failover is likely to make the situation worse, not better.

**故障转移的过程中，往往潜藏着诸多容易导致异常的风险点：**

- 若采用**异步复制**机制，新主节点在旧主节点故障时，可能并未接收完旧主节点的所有写入操作。倘若旧主节点在新主节点当选后重新加入集群，这些未同步的写入操作该如何处理？在此期间，新主节点可能已经接收了与之冲突的写入操作。最常用的解决方案是直接丢弃旧主节点中未复制的写入操作，但这种做法可能会违背客户端对数据**持久性的预期**。
- 当数据库之外的其他存储系统需要与数据库中的数据保持协同一致时，丢弃写入操作的做法会格外危险。例如，GitHub 曾发生过这样一起事故 [13]：一台**数据滞后的 MySQL 从节点**被提升为主节点。该数据库原本依靠自增计数器为新数据行分配主键，而由于新主节点的计数器数值落后于旧主节点，它复用了一些旧主节点此前已经分配过的主键。这些主键同时也被用于 Redis 存储系统，主键的复用最终导致 MySQL 与 Redis 之间出现数据不一致，进而造成部分私密数据被泄露给错误的用户。
- 在某些故障场景下（详见第 8 章），可能会出现**两个节点均认为自己是主节点**的情况。这种现象被称为**脑裂**，具有极大的危险性：如果两个主节点都接收写入操作，且系统没有冲突解决机制（详见第 168 页的 “多主复制” 章节），数据很可能会丢失或损坏。作为一种安全兜底机制，部分系统会在检测到双主节点并存时，自动关闭其中一个节点。<sup>ii</sup> 但如果该机制的设计不够严谨，最终可能会导致**两个节点都被关闭** [14]。
- 判定主节点失效的**超时阈值设置为多少才合理**？超时阈值过长，意味着主节点故障后系统需要更长的时间才能完成恢复；但如果阈值过短，则可能引发不必要的故障转移。例如，临时的负载峰值可能导致节点响应时间超过阈值，或是网络瞬断会造成数据包延迟。如果系统本就正受困于高负载或网络问题，一次不必要的故障转移非但无法缓解问题，反而可能让情况雪上加霜。

### Problems with Replication Lag

复制延迟的问题

#### Reading Your Own Writes

Unfortunately, if an application reads from an asynchronous follower, it may see out‐dated information if the follower has fallen behind. This leads to apparent inconsis‐tencies in the database: if you run the same query on the leader and a follower at thesame time, you may get different results, because not all writes have been reflected inthe follower. This inconsistency is just a temporary state—if you stop writing to thedatabase and wait a while, the followers will eventually catch up and become consis‐tent with the leader. For that reason, this effect is known as **eventual consistency**

遗憾的是，如果应用程序从**异步从节点**读取数据，当从节点的数据同步滞后时，就可能获取到过期的信息。这会导致数据库出现**表面上的数据不一致**：倘若你同时在主节点和从节点上执行相同的查询，可能会得到不同的结果 —— 原因是从节点中尚未同步所有的写入操作。但这种不一致只是一种**临时状态**：如果停止向数据库写入数据，等待一段时间后，从节点最终会追平数据，与主节点保持一致。正是因为这一特性，这种现象被称为**最终一致性**。

 In this situation, we need **read-after-write consistency**, also known as **read-your-writes consistency** [24]. This is a guarantee that if the user reloads the page, they will alwayssee any updates they submitted themselves. It makes no promises about other users:other users’ updates may not be visible until some later time. However, it reassuresthe user that their own input has been saved correctly.

在这种情况下，我们就需要**写后读一致性**（也称为**读己写一致性**）[24]。这是一项保障机制：当用户刷新页面时，总能看到自己提交的所有更新内容。该机制不会对其他用户的操作做出承诺 —— 其他用户提交的更新，可能要等到一段时间后才能被看见。但它能让用户放心，自己输入的内容已经被正确保存。

How can we implement **read-after-write consistency** in a system with **leader-based replication**? There are various possible techniques. To mention a few:

- When reading something that the user may have modified, read it from the leader; otherwise, read it from a follower. This requires that you have some way of knowing whether something might have been modified, without actually querying it. For example, user profile information on a social network is nor‐ mally only editable by the owner of the profile, not by anybody else. Thus, a sim‐ ple rule is: always read the user’s own profile from the leader, and any other users’ profiles from a follower.
- If most things in the application are potentially editable by the user, that approach won’t be effective, as most things would have to be read from the leader (negating the benefit of read scaling). In that case, other criteria may be used to decide whether to read from the leader. For example, you could track the time of the last update and, for one minute after the last update, make all reads from the leader. You could also monitor the replication lag on followers and pre‐ vent queries on any follower that is more than one minute behind the leader.
- The client can remember the timestamp of its most recent write—then the sys‐ tem can ensure that the replica serving any reads for that user reflects updates at least until that timestamp. If a replica is not sufficiently up to date, either the read can be handled by another replica or the query can wait until the replica has  caught up. The timestamp could be a **logical timestamp** (something that indicates ordering of writes, such as the **log sequence number**) or the actual system clock(in which case clock synchronization becomes critical; see “Unreliable Clocks”on page 287).
-  If your replicas are distributed across multiple datacenters (for geographical proximity to users or for availability), there is additional complexity. Any request that needs to be served by the leader must be routed to the datacenter that con‐ tains the leader.

**在基于主节点的复制系统中，我们该如何实现写后读一致性呢？具体有多种可行的技术方案，以下列举其中几种：**

- 当读取用户**可能已修改过**的数据时，从主节点读取；其余情况下，从从节点读取。这要求系统具备一种判断逻辑 —— 无需实际查询数据，就能确定某条数据是否有可能被修改。例如，社交网络中的用户资料通常只有账号所有者可以编辑，其他用户无权修改。基于这一特点，我们可以制定一条简单规则：**始终从主节点读取用户自己的资料**，而从从节点读取其他用户的资料。
- 若应用中的大部分数据都存在被用户修改的可能，那么上述方案的效果就会大打折扣 —— 因为绝大多数读取请求都需要路由到主节点，这样就会**抵消读扩展带来的优势**。这种情况下，就需要借助其他判断标准来决定读取请求的路由目标。例如，系统可以记录每条数据的**最后更新时间戳**，在数据更新后的一分钟内，所有针对该数据的读取请求都定向到主节点；也可以实时监控从节点的**复制延迟**，一旦某个从节点与主节点的延迟超过一分钟，就暂时禁止向该从节点发送查询请求。
- 客户端可以记录自己**最近一次写入操作的时间戳**，之后系统就需要确保：为该用户提供读取服务的副本，至少包含该时间戳之前的所有更新数据。如果某个副本的数据同步进度未达标，那么要么将读取请求转发至其他同步完成的副本，要么让该查询请求**等待副本追平数据后再执行**。这里的时间戳可以是**逻辑时间戳**（用于标记写入操作顺序的标识，比如日志序列号），也可以是实际的系统时钟时间（这种情况下，**时钟同步就会变得至关重要**，详见第 287 页的 “不可靠时钟” 章节）。
- 若数据库副本分布在**多个数据中心**（此举或是为了让服务地理位置更贴近用户，或是为了提升系统可用性），则会引入额外的复杂度。所有需要由主节点处理的请求，都必须精准路由到**主节点所在的数据中心**。

Another complication arises when the same user is accessing your service from mul‐tiple devices, for example a desktop web browser and a mobile app. In this case youmay want to provide cross-device read-after-write consistency: if the user enters someinformation on one device and then views it on another device, they should see theinformation they just entered.

当同一用户通过多台设备访问服务时（例如桌面端网页浏览器和移动端应用），会衍生出另一个复杂问题。这种情况下，你可能需要实现**跨设备写后读一致性**：如果用户在一台设备上录入了某些信息，之后用另一台设备查看，应该能看到自己刚录入的内容。

In this case, there are some additional issues to consider:

-  Approaches that require remembering the timestamp of the user’s last update become more difficult, because the code running on one device doesn’t know what updates have happened on the other device. This metadata will need to be centralized.
- If your replicas are distributed across different datacenters, there is no guarantee that connections from different devices will be routed to the same datacenter. (For example, if the user’s desktop computer uses the home broadband connec‐ tion and their mobile device uses the cellular data network, the devices’ network routes may be completely different.) If your approach requires reading from the leader, you may first need to route requests from all of a user’s devices to the same datacenter.

这种场景下，还需要考虑以下额外问题：

- 那些需要记录用户最近一次更新时间戳的方案，实施难度会有所增加。因为运行在某一台设备上的代码，无法知晓其他设备上发生过哪些更新操作。这类元数据必须进行**集中存储**。
- 若数据库副本分布在不同的数据中心，那么来自用户不同设备的请求，无法保证会被路由到同一个数据中心。（例如，用户的台式机使用的是家庭宽带网络，而移动设备使用的是蜂窝数据网络，两台设备的网络路由可能完全不同。）如果你的方案要求读取请求必须由主节点处理，那么首先需要将该用户所有设备的请求，**统一路由至同一个数据中心**。

#### Monotonic Reads

**Monotonic reads** [23] is a guarantee that this kind of anomaly does not happen. It’s alesser guarantee than strong consistency, but a stronger guarantee than eventual con‐sistency. When you read data, you may see an old value; monotonic reads only meansthat if one user makes several reads in sequence, they will not see time go backward—i.e., they will not read older data after having previously read newer data.

单调读 [23] 是一种保证，用来避免上述这类异常情况的发生。它比**强一致性**弱，但比**最终一致性**强。当你读取数据时，可能会看到旧值；单调读只保证：**如果同一个用户按顺序进行了多次读取，那么他们不会看到时间倒退**——也就是说，在已经读到较新数据之后，不会再读到更旧的数据。

One way of achieving monotonic reads is to make sure that each user always makestheir reads from the same replica (different users can read from different replicas).For example, the replica can be chosen based on a hash of the user ID, rather thanrandomly. However, if that replica fails, the user’s queries will need to be rerouted toanother replica.

实现单调读的一种方式是：确保每个用户始终从**同一个副本**读取数据（不同用户可以从不同的副本读取）。例如，可以根据用户 ID 的哈希值来选择副本，而不是随机选择。不过，如果该副本发生故障，用户的查询就需要被重定向到另一个副本。

#### Consistent Prefix Reads

一致前缀读

Preventing this kind of anomaly requires another type of guarantee: **consistent prefix reads** [23]. This guarantee says that if a sequence of writes happens in a certain order,then anyone reading those writes will see them appear in the same order.

要防止这种异常，需要另一种保证：**一致前缀读（consistent prefix reads）** [23]。这种保证意味着：**如果一系列写操作是按某个顺序发生的，那么任何读取这些写操作的读者，看到的结果也会按照同样的顺序出现**。

This is a particular problem in **partitioned (sharded) databases**, which we will discussin Chapter 6. If the database always applies writes in the same order, reads always seea consistent prefix, so this anomaly cannot happen. However, in many distributed databases, different partitions operate independently, so there is no global ordering ofwrites: when a user reads from the database, they may see some parts of the databasein an older state and some in a newer state.

这在**分区（分片）数据库**中是一个特别突出的问题，我们将在第 6 章中讨论。如果数据库总是以相同的顺序应用写操作，那么读操作总是能看到一个一致的前缀，因此这种异常就不会发生。然而，在许多分布式数据库中，不同的分区是彼此独立运行的，并不存在全局的写入顺序：当用户从数据库读取数据时，可能会看到数据库的某些部分仍处于较旧的状态，而另一些部分已经处于较新的状态。

### Multi-Leader Replicatoin

In a **multi-leader** configuration, you can have a leader in eachdatacenter. Figure 5-6shows what this architecture might look like. Within each datacenter, regular leader–follower replication is used; between datacenters, each datacenter’s leader replicatesits changes to the leaders in other datacenters.

在**多主（multi-leader）配置**中，可以在每个数据中心各自设置一个主节点。图 5-6 展示了这种架构的大致样子。在每个数据中心内部，使用常规的**主从复制（leader–follower replication）**；而在数据中心之间，则由各个数据中心的主节点将其变更复制到其他数据中心的主节点。

![639c2c17a1cb071e3a034d3d15cafcea](../../images/distribuide_system/ddia-5-6.jpg)

Let’s compare how the **single-leader** and **multi-leader** configurations fare in a multi-datacenter deployment:

下面对比一下**单主（single-leader）**和**多主（multi-leader）**配置在多数据中心部署下的表现：

**Performance** In a single-leader configuration, every write must go over the internet to the datacenter with the leader. This can add significant latency to writes and might contravene the purpose of having multiple datacenters in the first place. In a multi-leader configuration, every write can be processed in the local datacenter and is replicated **asynchronously** to the other datacenters. Thus, the inter- datacenter network delay is hidden from users, which means the perceived per‐ formance may be better.

**性能（Performance）**. 在单主配置中，每一次写入都必须通过互联网发送到主节点所在的数据中心。这会显著增加写入延迟，甚至可能违背部署多个数据中心的初衷。而在多主配置中，每次写入都可以在本地数据中心直接处理，然后再**异步**复制到其他数据中心。这样一来，跨数据中心的网络延迟对用户是不可感知的，因此用户感受到的性能通常会更好。

**Tolerance of datacenter outages** In a single-leader configuration, if the datacenter with the leader fails, failover can promote a follower in another datacenter to be leader. In a multi-leader con‐ figuration, each datacenter can continue operating independently of the others,and replication catches up when the failed datacenter comes back online.

**数据中心故障容忍性（Tolerance of datacenter outages）**. 在单主配置中，如果主节点所在的数据中心发生故障，需要通过故障转移（failover），将另一个数据中心中的某个从节点提升为主节点。在多主配置中，每个数据中心都可以独立于其他数据中心继续运行；当发生故障的数据中心恢复上线后，再通过复制机制将数据追赶同步。

**Tolerance of network problems** Traffic between datacenters usually goes over the public internet, which may be less reliable than the local network within a datacenter. A single-leader configu‐ ration is very sensitive to problems in this inter-datacenter link, because writes are made synchronously over this link. A multi-leader configuration with asyn‐ chronous replication can usually tolerate network problems better: a temporary network interruption does not prevent writes being processed.

**网络问题容忍性（Tolerance of network problems）**. 数据中心之间的通信通常经过公网，这往往比数据中心内部的本地网络更不可靠。单主配置对这种跨数据中心链路的问题非常敏感，因为写操作需要通过该链路**同步**完成。而采用**异步复制**的多主配置通常能更好地容忍网络问题：短暂的网络中断并不会阻止写操作的正常处理。

Although multi-leader replication has advantages, it also has a big downside: t**he same data may be concurrently modified in two different datacenters**, and those **write conflicts must be resolved** (indicated as “conflict resolution” in Figure 5-6). We willdiscuss this issue in “Handling Write Conflicts” on page 171.

尽管多主复制具有一些优势，但它也有一个很大的缺点：**同一份数据可能会在两个不同的数据中心被并发修改**，而这些**写冲突必须被解决**（在图 5-6 中以“冲突解决 / conflict resolution”标示）。我们将在第 171 页的“**处理写冲突（Handling Write Conflicts）**”一节中讨论这个问题。



#### Handling Write Conflicts

Conflict avoidance

避免冲突

The simplest strategy for dealing with conflicts is to **avoid** them: if the application canensure that **all writes for a particular record go through the same leader**, then conflicts cannot occur. Since many implementations of multi-leader replication handleconflicts quite poorly, **avoiding conflicts** is a frequently recommended approach [34].

处理写冲突最简单的策略是**避免冲突**：如果应用能够确保**某条记录的所有写操作都经过同一个主节点（leader）**，那么就不会发生冲突。由于许多多主复制的实现对冲突的处理能力相当有限，**避免冲突**因此成为一种经常被推荐的做法 [34]。

For example, in an application where a user can edit their own data, you can ensurethat requests from a particular user are always routed to the same datacenter and usethe leader in that datacenter for reading and writing. Different users may have differ‐ent “home” datacenters (perhaps picked based on geographic proximity to the user),but from any one user’s point of view the configuration is essentially **single-leader**.

例如，在一个用户只能编辑自己数据的应用中，可以保证来自某个用户的请求始终被路由到**同一个数据中心**，并使用该数据中心中的主节点进行读写。不同用户可以有不同的“**归属（home）数据中心**”（可能根据用户的地理位置就近选择），但从单个用户的视角来看，这种配置本质上仍然是**单主**的。

However, sometimes you might want to change the designated leader for a record—perhaps because one datacenter has failed and you need to reroute traffic to anotherdatacenter, or perhaps because a user has moved to a different location and is nowcloser to a different datacenter. In this situation, **conflict avoidance breaks down**, andyou have to deal with the possibility of concurrent writes on different leaders.

然而，有时你可能需要更改某条记录所指定的主节点——比如某个数据中心发生故障，需要将流量重新路由到另一个数据中心；或者用户迁移到了新的地点，离另一个数据中心更近。在这种情况下，**冲突避免机制就会失效**，你就必须面对在不同主节点上发生**并发写入**的可能性。



There are various ways of achieving **convergent conflict resolution**:

- **Give each write a unique ID** (e.g., a timestamp, a long random number, a UUID,or a hash of the key and value), **pick the write with the highest ID as the winner**,and throw away the other writes. If a timestamp is used, this technique is known as **last write wins (LWW)**. Although this approach is popular, **it is dangerously prone to data loss** [35]. We will discuss LWW in more detail at the end of this chapter (“Detecting Concurrent Writes” on page 184).
- **Record the conflict in an explicit data structure** that preserves all information,and write application code that resolves the conflict at some later time (perhaps by prompting the user).

实现**收敛型冲突解决（convergent conflict resolution）**有多种方式：

- **为每一次写入分配一个唯一 ID**（例如时间戳、一个较长的随机数、UUID，或者 key 与 value 的哈希值），然后选择 **ID 最大的写入作为最终结果**，并丢弃其他写入。如果使用的是时间戳，这种技术被称为**最后写入胜出（Last Write Wins，LWW）**。虽然这种方法很流行，但它**极易导致数据丢失** [35]。我们将在本章末尾的“**检测并发写入（Detecting Concurrent Writes）**”（第 184 页）中更详细地讨论 LWW。
- **用显式的数据结构记录冲突**，保留所有相关信息，然后通过应用层代码在之后的某个时间点来解决冲突（例如提示用户进行选择）。



### LeaderLess Replication

On the other hand, in a **leaderless** configuration, failover does not exist. Figure 5-10shows what happens: the client (user 1234) sends the write to all three replicas in par‐allel, and the two available replicas accept the write but the unavailable replica missesit. Let’s say that it’s sufficient for two out of three replicas to acknowledge the write:after user 1234 has received two ok responses, we consider the write to be successful.The client simply ignores the fact that one of the replicas missed the write.

另一方面，在**无主（leaderless）配置**中，并不存在故障转移（failover）。图 5-10 展示了这种情况下会发生什么：客户端（用户 1234）将写请求**并行发送**给三个副本，其中两个可用副本接受了写入，而一个不可用的副本错过了这次写入。假设只要 **3 个副本中有 2 个确认（acknowledge）写入即可视为成功**：在用户 1234 收到两个 ok 响应之后，我们就认为这次写入已经成功。客户端会直接忽略有一个副本未能接收到写入这一事实。

![微信图片_20260119224728_175_109](../../images/distribuide_system/DDIA-5-10.jpg)

Now imagine that the unavailable node comes back online, and clients start readingfrom it. Any writes that happened while the node was down are missing from thatnode. Thus, if you read from that node, you may get stale (outdated) values asresponses.

现在设想那个不可用的节点重新上线，并且客户端开始从它读取数据。由于该节点宕机期间发生的写入都没有同步到它上面，因此这些写入在该节点上是缺失的。于是，如果你从这个节点读取数据，得到的可能是**陈旧的（过期的）值**。

To solve that problem, when a client reads from the database, it doesn’t just send itsrequest to one replica: read requests are also sent to several nodes in parallel. The cli‐ent may get different responses from different nodes; i.e., the up-to-date value fromone node and a stale value from another. Version numbers are used to determinewhich value is newer (see “Detecting Concurrent Writes” on page 184).

为了解决这个问题，当客户端从数据库读取数据时，并不会只向一个副本发送请求：**读请求同样会并行发送给多个节点**。客户端可能会从不同节点收到不同的响应，也就是说，可能从某个节点拿到最新值，而从另一个节点拿到旧值。此时可以通过**版本号**来判断哪个值更新（参见第 184 页“**检测并发写入**”）。

**Read repair and anti-entropy.** 

**读修复（Read repair）与反熵（Anti-entropy）**

The replication scheme should ensure that **eventually all the data is copied to everyreplica**. After an unavailable node comes back online, how does it catch up on thewrites that it missed?

复制机制需要确保：**最终所有数据都会被复制到每一个副本上**。当一个曾经不可用的节点重新上线后，它是如何补齐在宕机期间错过的写入的呢？

Two mechanisms are often used in Dynamo-style datastores:

在 **Dynamo 风格的数据存储系统**中，通常会使用两种机制：

**Read repair** When a client makes a read from several nodes in parallel, it can detect any stale responses. For example, in Figure 5-10, user 2345 gets a version 6 value from rep‐ lica 3 and a version 7 value from replicas 1 and 2. The client sees that replica 3 has a stale value and writes the newer value back to that replica. This approach works well for values that are frequently read.

**读修复（Read repair）**. 当客户端并行地从多个节点读取数据时，它可以检测到哪些响应是陈旧的。例如，在图 5-10 中，用户 2345 从副本 3 读到了版本 6 的值，而从副本 1 和副本 2 读到了版本 7 的值。客户端可以判断出副本 3 上的数据是过期的，于是将较新的值写回到该副本。这种方法对于**被频繁读取的数据**效果很好。

**Anti-entropy process** In addition, some datastores have a background process that constantly looks for differences in the data between replicas and copies any missing data from one replica to another. Unlike the replication log in leader-based replication, this anti-entropy process does not copy writes in any particular order, and there may be a significant delay before data is copied.

**反熵过程（Anti-entropy process）**. 此外，一些数据存储系统还会运行一个**后台进程**，不断检查各个副本之间的数据差异，并将缺失的数据从一个副本复制到另一个副本。与基于主节点复制的复制日志不同，这种反熵过程**不会按照特定的写入顺序复制数据**，而且在数据被完全复制之前，**可能会存在较长的延迟**。



**Detecting Concurrent Writes**

**检测并发写入**

For defining concurrency, **exact time doesn’t matter**: we simply call two operationsconcurrent if they are both unaware of each other, regardless of the physical time at which they **occurred**.

在定义并发时，**精确时间并不重要**：只要两个操作彼此互不感知，无论它们实际发生的物理时间如何，我们就将这两个操作称为**并发操作**。

Note that the server can determine whether two operations are concurrent by looking at the **version numbers**—it does not need to interpret the value itself (so the valuecould be any data structure). The algorithm works as follows:

- The server maintains a version number for every key, increments the version number every time that key is written, and stores the **new version number along with the value written**.
- When a client reads a key, the server returns **all values that have not been overwritten**, as well as the latest version number. **A client must read a key before writing.**
- When a client writes a key, it must include the version number from the prior read, and it must **merge together all values that it received in the prior read**. (The response from a write request can be like a read, returning all current values, which allows us to chain several writes like in the shopping cart example.)
- When the server receives a write with a particular version number, it can overwrite all values with t**hat version number or below** (since it knows that they have been merged into the new value), but it must keep all values with a **higher version number** (because those values are concurrent with the incoming write).
- When a write includes the version number from a prior read, that tells us which previous state the write is based on. If you make a write without including a versionnumber, it is concurrent with all other writes, so it will not overwrite anything—itwill just be returned as one of the values on subsequent reads.

需要注意的是，服务器只需通过**版本号**就能判断两个操作是否并发，无需解析值本身的内容（因此值可以是任意数据结构）。该算法的工作流程如下：

- 服务器为每个键维护一个版本号，每当该键被写入时，版本号就会递增，同时将**新版本号与写入的值一并存储**。
- 当客户端读取某个键时，服务器会返回该键**所有未被覆盖的值**，以及当前的最新版本号。**客户端在执行写入操作前，必须先读取对应键的数据**。
- 客户端写入某个键时，必须附带之前读取操作获取的版本号，同时需要将之前读取到的**所有值合并为一个新值**。（写入请求的响应可以仿照读取操作，返回当前的所有值，这一设计支持像购物车场景那样，将多次写入操作串联执行。）
- 当服务器接收到携带特定版本号的写入请求时，可以覆盖所有版本号**小于等于该值**的数据（因为服务器明确这些数据已被合并到新值中）；但必须保留所有版本号**高于该值**的数据（因为这些数据与本次写入请求属于并发关系）。
- 若写入请求中附带了之前读取操作的版本号，这就明确了本次写入基于的**历史状态版本**。如果写入时未附带版本号，则该操作会被判定为与所有其他写入操作并发，因此它不会覆盖任何已有数据 —— 只会在后续的读取操作中，作为其中一个值被返回。

### Summary

In this chapter we looked at the issue of **replication**. Replication can serve severalpurposes:

- **High availability** Keeping the system running, even when one machine (or several machines, or an entire datacenter) goes down
- **Disconnected operation** Allowing an application to continue working when there is a network interruption
- **Latency** Placing data geographically close to users, so that users can interact with it faster
- **Scalability** Being able to handle a higher volume of reads than a single machine could handle, by performing reads on replicas

在本章中，我们讨论了**复制（replication）**的问题。复制可以服务于多个目的：

- **高可用性（High availability）** 即使一台机器（或多台机器，甚至整个数据中心）发生故障，系统仍然能够继续运行。
- **离线/断连运行（Disconnected operation）** 在网络中断的情况下，仍然允许应用继续工作。
- **低延迟（Latency）** 将数据放置在地理位置上更接近用户的地方，使用户能够更快地与数据交互。
- **可扩展性（Scalability）** 通过在副本上执行读操作，来处理单台机器无法承受的高读请求量。

Despite being a simple goal—keeping a copy of the same data on several machines—replication turns out to be a remarkably tricky problem. It requires carefully thinkingabout concurrency and about all the things that can go wrong, and dealing with theconsequences of those faults. At a minimum, we need to deal with unavailable nodesand network interruptions (and that’s not even considering the more insidious kindsof fault, such as silent data corruption due to software bugs).

尽管目标看起来很简单——在多台机器上保存同一份数据的副本——**复制实际上是一个极其棘手的问题**。它需要我们非常谨慎地思考并发问题，以及各种可能出错的情况，并处理这些故障所带来的后果。至少，我们必须应对节点不可用和网络中断（更不用说那些更加隐蔽的故障类型，例如由于软件缺陷导致的静默数据损坏）。

We discussed three main approaches to replication:

- **Single-leader replication** Clients send all writes to a single node (the leader), which sends a stream of data change events to the other replicas (followers). Reads can be performed on any replica, but reads from followers might be stale.
- **Multi-leader replication** Clients send each write to one of several leader nodes, any of which can accept writes. The leaders send streams of data change events to each other and to any follower nodes.
- **Leaderless replication** Clients send each write to several nodes, and read from several nodes in parallel in order to detect and correct nodes with stale data.

我们讨论了三种主要的复制方式：

- **单主复制（Single-leader replication）** 客户端将所有写请求发送到单一节点（主节点），主节点再将数据变更事件流发送给其他副本（从节点）。读操作可以在任意副本上执行，但从节点上的读取可能是过期的。
- **多主复制（Multi-leader replication）** 客户端将写请求发送到多个主节点中的任意一个，这些主节点都可以接受写入。各个主节点之间，以及主节点与其从节点之间，都会相互复制数据变更事件流。
- **无主复制（Leaderless replication）** 客户端将每一次写入发送给多个节点，并在读取时并行地从多个节点读取，以检测并修复包含过期数据的节点。

Each approach has advantages and disadvantages. Single-leader replication is popularbecause it is fairly easy to understand and there is no conflict resolution to worryabout. Multi-leader and leaderless replication can be more robust in the presence offaulty nodes, network interruptions, and latency spikes—at the cost of being harderto reason about and providing only very weak consistency guarantees.

每种方式都有其优缺点。**单主复制**由于概念相对简单，而且不需要处理写冲突，因此非常流行。**多主复制**和**无主复制**在面对节点故障、网络中断以及延迟抖动时通常更加健壮，但代价是系统更难理解，只能提供**较弱的一致性保证**。

Replication can be synchronous or asynchronous, which has a profound effect on thesystem behavior when there is a fault. Although asynchronous replication can be fastwhen the system is running smoothly, it’s important to figure out what happenswhen replication lag increases and servers fail. If a leader fails and you promote anasynchronously updated follower to be the new leader, **recently committed data maybe lost**.

复制可以是**同步**的，也可以是**异步**的，而这在系统发生故障时会对行为产生深远影响。尽管异步复制在系统运行良好时速度很快，但当复制延迟增大、服务器发生故障时，必须认真考虑会发生什么。如果主节点发生故障，并将一个**异步更新的从节点**提升为新的主节点，那么**最近已经提交的数据可能会丢失**。

We looked at some strange effects that can be caused by replication lag, and we dis‐cussed a few consistency models which are helpful for deciding how an applicationshould behave under replication lag:

- Read-after-write consistency Users should always see data that they submitted themselves.
- Monotonic reads After users have seen the data at one point in time, they shouldn’t later see the data from some earlier point in time.
- Consistent prefix reads Users should see the data in a state that makes causal sense: for example, seeing a question and its reply in the correct order.

我们还探讨了复制延迟可能引发的一些特殊问题，并介绍了几种一致性模型，这些模型有助于我们定义应用程序在复制延迟场景下应有的行为表现：

- **写后读一致性**：用户始终能够读取到自己提交的最新数据。
- **单调读一致性**：用户一旦读取到某个时间点的数据状态，后续读取操作就不会返回更早时间点的数据。
- **一致前缀读一致性**：用户读取的数据始终符合因果逻辑，比如能够按正确的先后顺序看到某条问题及其对应的回复。

Finally, we discussed the concurrency issues that are inherent in multi-leader andleaderless replication approaches: because they allow multiple writes to happen con‐currently, conflicts may occur. We examined an algorithm that a database might useto determine whether one operation happened before another, or whether they hap‐pened concurrently. We also touched on methods for resolving conflicts by mergingtogether concurrent updates.

最后，我们分析了多主复制和无主复制方案中固有的并发问题：由于这两种方案允许多个写入操作并行执行，因此很可能会引发冲突。我们介绍了一种数据库常用的算法，该算法能够判断一个操作是发生在另一个操作之前，还是与另一个操作属于并发关系。同时，我们也简要提及了通过合并并发更新来解决冲突的相关方法。

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

## Chapter 7. Transactions

### The Slippery Concept of a Transaction

**事务的模糊概念**

#### The Meaning of ACID

The safety guarantees provided by transactions are often described by the well-known acronym **ACID**, which stands for **Atomicity**, **Consistency**, **Isolation**, and **Durability**.

事务提供的安全保障通常用广为人知的缩写词 **ACID** 来描述，它分别代表**原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）和持久性（Durability）**。

(Systems that do not meet the ACID criteria are sometimes called **BASE**, whichstands for **Basically Available**, **Soft state**, and **Eventual consistency** [9]. This is evenmore vague than the definition of ACID. It seems that the only sensible definition ofBASE is “not ACID”; i.e., it can mean almost anything you want.)

（那些不符合 ACID 标准的系统有时被称为 **BASE** 系统，BASE 代表**基本可用（Basically Available）、软状态（Soft state）和最终一致性（Eventual consistency）**[9]。这个定义比 ACID 的定义还要模糊。似乎对 BASE 唯一合理的解读就是 “非 ACID 系统”—— 也就是说，它几乎可以指代任何你想要的系统类型。）

**Atomicity, isolation, and durability are properties of the database, whereas consis‐tency (in the ACID sense) is a property of the application.** The application may relyon the database’s atomicity and isolation properties in order to achieve consistency,but it’s not up to the database alone. Thus, the letter C doesn’t really belong in ACID.

**原子性、隔离性和持久性是数据库自身的特性，而一致性（就 ACID 的语境而言）则是应用程序的特性**。应用程序可能会依赖数据库的原子性与隔离性特性来实现一致性，但这并非仅靠数据库就能完成。因此，ACID 中的字母 C（即一致性）其实并不名副其实。

#### Single-Object and Multi-Object Operations

To recap, in ACID, atomicity and isolation describe what the database should do if aclient makes several writes within the same transaction:

- Atomicity If an error occurs halfway through a sequence of writes, the transaction should be aborted, and the writes made up to that point should be discarded. In other words, the database saves you from having to worry about partial failure, by giving an **all-or-nothing guarantee**.
-  Isolation Concurrently running transactions shouldn’t interfere with each other. For example, if one transaction makes several writes, then another transaction should see either all or none of those writes, but not some subset.

总而言之，在 ACID 特性中，原子性与隔离性描述了当客户端在同一个事务中执行多次写入操作时，数据库应当采取的处理规则：

- **原子性**：如果在一系列写入操作执行的过程中发生错误，事务应当被中止，且此前已完成的写入操作都应被撤销。换句话说，数据库通过提供 **“要么全部完成，要么全部不做”** 的保障机制，帮你规避了对部分失败情况的担忧。
- **隔离性**：并发执行的事务之间不应相互干扰。例如，若某个事务执行了多次写入操作，那么其他事务要么能看到该事务所有写入操作的结果，要么完全看不到，而不会出现只看到其中一部分写入结果的情况。

### Weak Isolation Levels

**弱隔离级别**

#### Read Committed

 How do we prevent dirty reads? One option would be to use the same lock, and torequire any transaction that wants to read an object to briefly acquire the lock andthen release it again immediately after reading. This would ensure that a readcouldn’t happen while an object has a dirty, uncommitted value (because during thattime the lock would be held by the transaction that has made the write).

如何防止脏读的发生呢？一种方案是使用同一把锁，要求所有需要读取某一数据对象的事务先短暂获取该锁，读取完成后立即释放。这种方式可以确保，当数据对象存在未提交的脏数据时，其他事务无法读取该对象（因为这段时间内，锁会被执行写入操作的事务持有）。

However, the approach of requiring read locks does not work well in practice,because one long-running write transaction can force many read-only transactions towait until the long-running transaction has completed. This harms the response timeof read-only transactions and is bad for operability: a slowdown in one part of anapplication can have a knock-on effect in a completely different part of the applica‐tion, due to waiting for locks.

但在实际场景中，这种强制加读锁的方案并不可行。因为一个长时间运行的写入事务，会迫使大量只读事务一直等待，直到该写入事务执行完毕。这会降低只读事务的响应速度，还会影响系统的可操作性：应用程序某一部分的性能下降，会因为锁等待机制，对应用完全无关的其他部分产生连锁影响。

![DDIA-7-4](../../images/distribuide_system/DDIA-7-4.jpg)

> Figure 7-4. No dirty reads: user 2 sees the new value for x only after user 1’s transaction has committed.

For that reason, most databasesvi prevent dirty reads using the approach illustrated in Figure 7-4: for every object that is written, the database remembers both the **old committed value** and the **new value** set by the transaction that currently holds the writelock. While the transaction is ongoing, any other transactions that read the object aresimply given the old value. Only when the new value is committed do transactionsswitch over to reading the new value.

正因为如此，大多数数据库会采用图 7-4 所示的方案来防止脏读：对于每一个被写入的数据对象，数据库会同时记录该对象的**旧版已提交值**，以及当前持有写锁的事务所设置的**新版值**。在该写入事务的执行过程中，其他所有读取该数据对象的事务，都会直接获取旧版值。只有当新版值被成功提交后，后续事务才会切换为读取新版值。

#### Snapshot Isolation and Repeatable Read

**快照隔离和可重复读**

**Snapshot isolation** [28] is the most common solution to this problem. The idea is that **each transaction reads from a consistent snapshot of the database**—that is, the transaction sees all the data that was committed in the database at the start of the transac‐tion. Even if the data is subsequently changed by another transaction, eachtransaction sees only the old data from that particular point in time.

**快照隔离（Snapshot Isolation）** [28] 是解决这一问题最常见的方法。其核心思想是：**每个事务都从数据库的一个一致性快照中读取数据**——也就是说，事务只能看到在**该事务开始时已经提交**到数据库中的所有数据。即使之后有其他事务对数据进行了修改，每个事务仍然只会看到**那个特定时间点上的旧数据**。

To implement **snapshot isolation**, databases use a generalization of the mechanismwe saw for preventing **dirty reads** in Figure 7-4. The database must potentially keep **several different committed versions of an object**, because various in-progress transactions may need to see the state of the database at different points in time. Because itmaintains several versions of an object side by side, this technique is known as **multi-version concurrency control (MVCC)**.

为了实现**快照隔离（snapshot isolation）**，数据库会使用一种机制的泛化版本，这种机制我们在图 7-4 中已经见过，用来防止**脏读（dirty reads）**。数据库可能需要同时保留**同一对象的多个已提交版本**，因为不同的正在执行中的事务，可能需要看到数据库在不同时间点的状态。由于这种技术会并排维护同一对象的多个版本，因此被称为**多版本并发控制（Multi-Version Concurrency Control，MVCC）**。

Each row in a table has a created_by field, containing the ID of the transaction that inserted this row into the table. Moreover, each row has a deleted_by field, which is initially empty. If a transaction deletes a row, the row isn’t actually deleted from thedatabase, but it is marked for deletion by setting the deleted_by field to the ID of the transaction that requested the deletion. At some later time, when it is certain that notransaction can any longer access the deleted data, a **garbage collection** **process** in thedatabase removes any rows marked for deletion and frees their space.

表中的**每一行**都有一个 `created_by` 字段，用来记录**插入该行的事务 ID**。此外，每一行还有一个 `deleted_by` 字段，初始为空。如果某个事务删除了一行，这一行并不会立刻从数据库中真正删除，而是通过将 `deleted_by` 字段设置为**发起删除操作的事务 ID**，来标记该行已被删除。等到确认再也没有任何事务可能访问这条已删除的数据之后，数据库中的**垃圾回收（garbage collection）进程**才会真正移除这些被标记删除的行，并释放它们所占用的空间。



**Visibility rules for observing a consistent snapshot**

**读取一致性快照的可见性规则**

When a transaction reads from the database, **transaction IDs** are used to decidewhich objects it can see and which are invisible. By carefully defining visibility rules,the database can present a **consistent snapshot** of the database to the application. Thisworks as follows:

1. At the start of each transaction, the database makes a list of all the other transac‐ tions that are in progress (not yet committed or aborted) at that time. Any writes that those transactions have made are ignored, even if the transactions subse‐ quently commit.
2. Any writes made by **aborted transactions** are ignored.
3. Any writes made by transactions with a **later transaction ID** (i.e., which started after the current transaction started) are ignored, regardless of whether those transactions have committed.
4. All other writes are visible to the application’s queries.

当事务从数据库中读取数据时，数据库会借助**事务 ID**来判定哪些数据对象对当前事务可见、哪些不可见。通过严谨定义可见性规则，数据库能够为应用程序呈现出一份**一致性的数据库快照**。其工作机制如下：

1. 每个事务启动时，数据库会生成一份清单，记录下此刻所有**正在执行中**（尚未提交或中止）的其他事务。无论这些事务后续是否提交，它们已执行的所有写入操作，对当前事务而言均视为不可见。
2. 所有**已中止事务**执行的写入操作，均视为不可见。
3. 所有**事务 ID 更大的事务**（即启动时间晚于当前事务的事务）执行的写入操作，无论是否提交，均视为不可见。
4. 除上述情况外，其他所有写入操作产生的数据，均对当前应用程序的查询请求可见。

A long-running transaction may continue using a snapshot for a long time, continu‐ing to read values that (from other transactions’ point of view) have long been over‐written or deleted. By never updating values in place but instead creating a newversion every time a value is changed, the database can provide a consistent snapshotwhile incurring only a small overhead.

一个长时间运行的事务可以持续使用某一份快照很长时间，始终读取那些**在其他事务看来早已被覆盖或删除**的数据值。数据库通过**从不原地更新数据值，而是在每次修改数据时都生成一个新版本**的设计，仅需产生少量额外开销，就能为事务提供一致性快照。

#### Preventing Lost Updates

Many databases provide **atomic update operations**, which remove the need to imple‐ment read-modify-write cycles in application code. They are usually the best solutionif your code can be expressed in terms of those operations. For example, the follow‐ing instruction is **concurrency-safe** in most relational databases:

许多数据库都支持**原子更新操作**，这就无需在应用代码中自行实现**读 - 改 - 写循环**的逻辑。如果业务逻辑可以通过这类操作来表达，原子更新操作通常是最优解决方案。例如，以下操作指令在大多数关系型数据库中都是**并发安全**的：

```mysql
UPDATE counters SET value=value+1 WHERE key='foo';
```

Atomic operations are usually implemented by taking an exclusive lock on the objectwhen it is read so that no other transaction can read it until the update has been.

原子操作的实现方式通常是：在读取目标数据对象时为其加**排他锁**，确保在更新操作完成前，其他事务无法读取该数据对象。

**Explicit locking**

**显式锁定**

Another option for preventing lost updates, if the database’s built-in atomic operations don’t provide the necessary functionality, is for the application to **explicitly lock** objects that are going to be updated. Then the application can perform a read-modify-write cycle, and if any other transaction tries to concurrently read the sameobject, it is forced to wait until the first read-modify-write cycle has completed.

若数据库内置的原子操作无法满足业务所需的功能，防止更新丢失的另一方案是由应用程序**显式锁定**即将被更新的数据对象。此时应用程序可执行读 - 改 - 写循环，而若有其他事务尝试并发读取同一数据对象，会被强制等待，直至第一个读 - 改 - 写循环执行完毕。

**Automatically detecting lost updates**

**自动检测更新丢失**

Atomic operations and locks are ways of preventing lost updates by forcing the read-modify-write cycles to happen sequentially. An alternative is to allow them to executein parallel and, if the transaction manager detects a lost update, abort the transactionand force it to retry its read-modify-write cycle.

原子操作与锁机制的核心逻辑是**强制读 - 改 - 写循环串行执行**，以此避免更新丢失。另一种思路则是允许这些循环并行执行：若事务管理器检测到更新丢失，便中止该事务，并强制其重新执行读 - 改 - 写循环。

An advantage of this approach is that databases can perform this check efficiently inconjunction with snapshot isolation. Indeed, PostgreSQL’s repeatable read, Oracle’sserializable, and SQL Server’s snapshot isolation levels automatically detect when alost update has occurred and abort the offending transaction. However, MySQL/InnoDB’s repeatable read does not detect lost updates [23]. Some authors [28, 30]argue that a database must prevent lost updates in order to qualify as providing snap‐shot isolation, so MySQL does not provide snapshot isolation under this definition.

这种方案的优势在于，数据库可结合**快照隔离**机制高效完成该检测。事实上，PostgreSQL 的可重复读隔离级别、Oracle 的串行化隔离级别，以及 SQL Server 的快照隔离级别，都会自动检测更新丢失的发生，并中止引发该问题的事务。但 MySQL/InnoDB 的可重复读隔离级别**不具备**更新丢失检测能力 [23]。有学者 [28,30] 提出，数据库若要被认定为提供 “快照隔离” 能力，必须具备防止更新丢失的特性 —— 按此定义，MySQL 并不满足快照隔离的要求。

Lost update detection is a great feature, because it doesn’t require application code touse any special database features—you may forget to use a lock or an atomic opera‐tion and thus introduce a bug, but lost update detection happens automatically and isthus less error-prone.

更新丢失检测是一项极具价值的特性：它无需应用代码调用任何特殊的数据库功能（你可能会因忘记使用锁或原子操作而引入漏洞），而更新丢失检测是**自动触发**的，因此出错概率更低。

**Compare-and-set**

**比较并设置（Compare-and-set，CAS）**

In databases that don’t provide transactions, you sometimes find an atomic compare-and-set operation (previously mentioned in “Single-object writes” on page 230). Thepurpose of this operation is to avoid lost updates by allowing an update to happenonly if the value has not changed since you last read it. If the current value does notmatch what you previously read, the update has no effect, and the read-modify-writecycle must be retried.

在**不提供事务**的数据库中，有时会提供一种**原子性的比较并设置（compare-and-set）操作**（此前已在第 230 页“**单对象写入（Single-object writes）**”中提到）。这种操作的目的是**避免更新丢失**：只有当某个值**自上次读取以来没有发生变化**时，更新才会生效。如果当前值与之前读取到的值不匹配，那么这次更新将**不会产生任何效果**，此时必须重新执行**读–修改–写（read–modify–write）**这一循环。



#### Write Skew and Phantoms

**写偏斜与幻读**

This anomaly is called **write skew** [28]. It is neither a dirty write nor a lost update,because the two transactions are updating two different objects (Alice’s and Bob’s on-call records, respectively). It is less obvious that a conflict occurred here, but it’s defi‐nitely a **race condition**: if the two transactions had run one after another, the seconddoctor would have been prevented from going off call. The anomalous behavior wasonly possible because the transactions ran concurrently.

这种异常被称为**写偏斜**[28]。它既不属于脏写，也不属于更新丢失，因为两个事务更新的是两个不同的数据对象（分别是爱丽丝和鲍勃的值班记录）。此处的冲突并不明显，但它无疑是一种**竞态条件**：若两个事务串行执行，第二个医生的离岗操作就会被阻止。这种异常行为的发生，完全是因为事务的并发执行。

You can think of write skew as a generalization of the lost update problem. Write skew can occur if two transactions read the same objects, and then update some ofthose objects (different transactions may update different objects). In the special casewhere different transactions update the same object, you get a dirty write or lostupdate anomaly (depending on the timing).

可以将写偏斜看作是更新丢失问题的**广义形式**。当两个事务读取了相同的数据对象，随后又更新了其中部分对象（不同事务可能更新不同的对象）时，就可能发生写偏斜。而在不同事务更新同一数据对象的特殊情况下，就会出现脏写或更新丢失异常（具体取决于操作的时序）。



If you can’t use a serializable isolation level, the second-best option in this case is probably to explicitly lock the rows that the transaction depends on. In the doc‐ tors example, you could write something like the following:

如果你无法使用可序列化的隔离级别，那么在这种情况下，次优的选择可能是明确地锁定那些该事务所依赖的行。在文档中的示例中，你可以编写类似以下的代码：

```mysql
BEGIN TRANSACTION;
SELECT * FROM doctors WHERE on_call=true AND shift_id=1234 FORUPDATE;
UPDATE doctors SET on_call=false WHERE name='Alice' AND shift_id=1234;
```



**Phantoms causing write skew**

**幻读引发的写偏斜**

All of these examples follow a similar pattern:

1. A SELECT query checks whether some requirement is satisfied by searching for rows that match some search condition (there are at least two doctors on call,there are no existing bookings for that room at that time, the position on the board doesn’t already have another figure on it, the username isn’t already taken,there is still money in the account).
2. Depending on the result of the first query, the application code decides how to continue (perhaps to go ahead with the operation, or perhaps to report an error to the user and abort).
3. If the application decides to go ahead, it makes a write (INSERT, UPDATE, or DELETE) to the database and commits the transaction.

所有这类场景都遵循相似的执行模式：

1. 执行一条 SELECT 查询，通过检索**匹配特定搜索条件的行**，判断某项业务要求是否得到满足（例如：至少有两名医生在值班、该会议室在指定时段暂无预订、棋盘上的某位置尚未放置棋子、用户名未被占用、账户内仍有余额）。
2. 应用程序代码根据第一步查询的结果，决定后续执行逻辑 —— 要么继续执行相关操作，要么向用户报错并中止事务。
3. 若应用程序决定继续执行，则向数据库**执行写入操作（INSERT、UPDATE 或 DELETE）**，并提交事务。

The effect of this write changes the precondition of the decision of step 2. Inother words, if you were to repeat the SELECT query from step 1 after commiting the write, you would get a different result, because the write changed the set ofrows matching the search condition (there is now one fewer doctor on call, themeeting room is now booked for that time, the position on the board is nowtaken by the figure that was moved, the username is now taken, there is now lessmoney in the account).

此次写入操作的结果，会改变第二步执行决策时依赖的**前置条件**。换句话说，若在写入操作提交后，重新执行第一步的 SELECT 查询，得到的结果会发生变化 —— 因为这次写入改变了**匹配搜索条件的行集合**（比如此时值班医生的人数减少了一名、会议室在该时段已有预订、棋盘上的目标位置已被占用、用户名变为已占用状态、账户余额相应减少）。

This effect, where a write in one transaction changes the result of a search query inanother transaction, is called a phantom [3]. Snapshot isolation avoids phantoms inread-only queries, but in read-write transactions like the examples we discussed,phantoms can lead to particularly tricky cases of write skew.

一个事务中的写入操作改变了另一个事务中搜索查询的结果，这种现象就称为**幻读**[3]。快照隔离机制能够避免只读查询出现幻读问题，但在我们讨论过的这类**读写事务**中，幻读则可能引发尤为棘手的写偏斜场景。

**Materializing conflicts**

**物化冲突**

If the problem of phantoms is that there is no object to which we can attach the locks,perhaps we can artificially introduce a lock object into the database?

幻读问题的症结在于没有可以附加锁的数据对象，那么或许我们可以主动在数据库中引入一个锁对象？

For example, in the meeting room booking case you could imagine creating a table oftime slots and rooms. Each row in this table corresponds to a particular room for aparticular time period (say, 15 minutes). You create rows for all possible combina‐tions of rooms and time periods ahead of time, e.g. for the next six months.

以会议室预订场景为例，你可以设想创建一张**时段 - 会议室对照表**。这张表中的每一行，对应某一间会议室在某一个特定时段（比如 15 分钟）的占用状态。你需要提前创建好未来一段时间内（例如半年）所有会议室与时段的组合记录。

Now a transaction that wants to create a booking can lock (SELECT FOR UPDATE) therows in the table that correspond to the desired room and time period. After it hasacquired the locks, it can check for overlapping bookings and insert a new booking asbefore. Note that the additional table isn’t used to store information about the book‐ing—it’s purely a collection of locks which is used to prevent bookings on the sameroom and time range from being modified concurrently.

如此一来，当某个事务想要创建一条预订记录时，就可以对目标会议室与目标时段对应的表行加锁（执行 `SELECT FOR UPDATE` 语句）。获取锁之后，事务就可以像之前一样检查是否存在重叠预订，再插入新的预订记录。需要注意的是，这张额外创建的表并非用于存储预订信息 —— 它仅作为**锁的集合**，用来防止同一间会议室在同一时段的预订请求被并发修改。

This approach is called **materializing conflicts**, because it takes a phantom and turns itinto a lock conflict on a concrete set of rows that exist in the database [11]. Unfortu‐nately, it can be hard and error-prone to figure out how to materialize conflicts, andit’s ugly to let a concurrency control mechanism leak into the application data model.For those reasons, materializing conflicts should be considered a last resort if noalternative is possible. A serializable isolation level is much preferable in most cases.

这种方案被称为**物化冲突**，其核心思路是将幻读问题转化为针对数据库中实际存在的一组行记录的锁冲突 [11]。但遗憾的是，设计和实现物化冲突的难度较大，且容易出错；同时，将并发控制机制侵入到应用数据模型中，这种做法也不够优雅。

### Serializability

Most databases thatprovide serializability today use one of three techniques, which we will explore in therest of this chapter:

-  Literally executing transactions in a serial order (see “Actual Serial Execution” on page 252)
- Two-phase locking (see “**Two-Phase Locking (2PL)**” on page 257), which for several decades was the only viable option
- Optimistic concurrency control techniques such as serializable snapshot isolation (see “**Serializable Snapshot Isolation (SSI)**” on page 261)

如今，大多数提供串行化能力的数据库会采用以下三种技术方案之一，本章后续内容将对其展开详细探讨：

- 严格按照串行顺序执行事务（参见第 252 页的**实际串行执行**）
- 两阶段锁（2PL）（参见第 257 页的**两阶段锁（2PL）**）—— 该方案在数十年间都是实现串行化唯一可行的选择
- 乐观并发控制技术，例如可串行化快照隔离（SSI）（参见第 261 页的**可串行化快照隔离（SSI）**）

#### Actual Serial Execution

**实际串行执行**

With stored procedures and in-memory data, executing all transactions on a singlethread becomes feasible. As they don’t need to wait for I/O and they avoid the over‐head of other concurrency control mechanisms, they can achieve quite goodthroughput on a single thread.

借助**存储过程**与**内存数据**技术，让所有事务在单线程上执行的方案具备了可行性。由于这类方案无需等待 I/O 操作，还能规避其他并发控制机制带来的额外开销，因此在单线程下也能实现相当可观的吞吐量。

**Summary of serial execution**

**事务串行执行总结**

Serial execution of transactions has become a viable way of achieving **serializable isolation** within certain constraints:

- Every transaction must be **small and fast**, because it takes only one slow transac‐ tion to stall all transaction processing.
- It is limited to use cases where the active dataset can fit in memory. Rarely accessed data could potentially be moved to disk, but if it needed to be accessed in a single-threaded transaction, the system would get very slow. *x*
-  Write throughput must be low enough to be handled on a single CPU core, or else transactions need to be partitioned without requiring cross-partition coordination.
- Cross-partition transactions are possible, but there is a hard limit to the extent to which they can be used.

在特定约束条件下，事务的串行执行已成为实现**可串行化隔离**的一种可行方案：

1. 所有事务必须**短小且高效**，因为仅需一个执行缓慢的事务，就会阻塞所有事务的处理流程。
2. 该方案仅适用于**活跃数据集可完全放入内存**的场景。访问频率较低的数据可以酌情转移至磁盘存储，但如果单线程事务需要访问这些磁盘数据，系统性能会急剧下降。
3. 写入吞吐量需低至单个 CPU 核心即可处理的水平；否则，就需要对事务进行分片，且分片后的事务无需跨分片协调。
4. 跨分片事务可以执行，但其使用范围存在严格限制。

**x.** If a transaction needs to access data that’s not in memory, the best solution may be to abort the transac‐ tion, asynchronously fetch the data into memory while continuing to process other transactions, and then restart the transaction when the data has been loaded. This approach is known as **anti-caching**, as previouslymentioned in “Keeping everything in memory” on page 88.

> **补充说明**：若某个事务需要访问不在内存中的数据，最优方案或许是先中止该事务；在持续处理其他事务的同时，异步将目标数据加载到内存；待数据加载完成后，再重启这个事务。这种方法被称为**反缓存**，前文第 88 页的 “全内存数据存储” 部分也曾提及。

#### Two-Phase Locking (2PL)

**两阶段锁（2PL）**

2PL is not 2PC

Note that while **two-phase locking (2PL)** sounds very similar to **two-phase commit (2PC)**, they are completely different things. Wewill discuss 2PC in Chapter 9.

需要注意的是，尽管**两阶段锁（2PL）** 和**两阶段提交（2PC）** 名称听起来十分相似，但二者是完全不同的机制。关于两阶段提交的内容，我们将在第 9 章展开讨论。

We saw previously that locks are often used to prevent **dirty writes** (see “No dirtywrites” on page 235): if two transactions concurrently try to write to the same object,the lock ensures that the second writer must wait until the first one has finished itstransaction (aborted or committed) before it may continue.

前文我们提到，锁机制常被用于防止**脏写**（参见第 235 页 “禁止脏写”）：若两个事务尝试并发写入同一数据对象，锁会强制第二个写入事务等待，直至第一个写入事务完成全部操作（提交或中止）后，才能继续执行。

Two-phase locking is similar, but makes the lock requirements much stronger. Sev‐eral transactions are allowed to concurrently read the same object as long as nobodyis writing to it. But as soon as anyone wants to write (modify or delete) an object,exclusive access is required:

- If transaction A has read an object and transaction B wants to write to that object, B must wait until A commits or aborts before it can continue. (This ensures that B can’t change the object unexpectedly behind A’s back.)

- If transaction A has written an object and transaction B wants to read that object,B must wait until A commits or aborts before it can continue. (Reading an old version of the object, like in Figure 7-1, is not acceptable under 2PL.)

两阶段锁的原理与之类似，但对加锁的要求更为严格。在没有事务对数据对象执行写入操作的前提下，多个事务可以并发读取该数据对象。而一旦有事务要对数据对象执行写入操作（修改或删除），就必须获取该对象的**排他访问权**，具体规则如下：

1. 若事务 A 已读取某数据对象，此时事务 B 想要写入该对象，事务 B 必须等待，直至事务 A 提交或中止后，才能继续执行。（这一规则确保事务 B 不会在事务 A 不知情的情况下擅自修改该对象。）
2. 若事务 A 已写入某数据对象，此时事务 B 想要读取该对象，事务 B 必须等待，直至事务 A 提交或中止后，才能继续执行。（在两阶段锁机制下，像图 7-1 那样读取数据对象的旧版本是不被允许的。）

 In 2PL, writers don’t just block other writers; they also block readers and vice versa.Snapshot isolation has the mantra readers never block writers, and writers never blockreaders(see “Implementing snapshot isolation” on page 239), which captures this keydifference between snapshot isolation and two-phase locking. On the other hand,because 2PL provides serializability, it protects against all the race conditions dis‐cussed earlier, including lost updates and write skew.

在两阶段锁机制中，写入操作不仅会阻塞其他写入操作，还会阻塞读取操作，**反之亦然**。快照隔离则遵循 **“读不阻塞写，写不阻塞读”** 的准则（参见第 239 页 “快照隔离的实现”），这一点恰好体现了快照隔离与两阶段锁的核心差异。而另一方面，由于两阶段锁能够提供串行化隔离级别，因此它可以防范前文讨论过的所有竞态条件，包括更新丢失与写偏斜。

**Implementation of two-phase locking**

**两阶段锁的实现**

2PL is used by the serializable isolation level in MySQL (InnoDB) and SQL Server,and the repeatable read isolation level in DB2 [23, 36].

MySQL（InnoDB 引擎）和 SQL Server 的**串行化隔离级别**，以及 DB2 的**可重复读隔离级别**，均采用了两阶段锁机制 [23,36]。

The blocking of readers and writers is implemented by a having a lock on each objectin the database. The lock can either be **in shared mode** or **in exclusive mode**. The lockis used as follows:

- If a transaction wants to read an object, it must first acquire the lock in shared mode. Several transactions are allowed to hold the lock in shared mode simultaneously, but if another transaction already has an exclusive lock on the object,these transactions must wait.
- If a transaction wants to write to an object, it must first acquire the lock in exclusive mode. No other transaction may hold the lock at the same time (either in shared or in exclusive mode), so if there is any existing lock on the object, the transaction must wait.
- If a transaction first reads and then writes an object, it may upgrade its shared lock to an exclusive lock. The upgrade works the same as getting an exclusive lock directly.
- After a transaction has acquired the lock, it must continue to hold the lock until the end of the transaction (commit or abort). This is where the name “two- phase” comes from: the first phase (while the transaction is executing) is when the locks are acquired, and the second phase (at the end of the transaction) is when all the locks are released.

读写操作之间的阻塞逻辑，是通过为数据库中的每个数据对象配置一把锁来实现的。锁分为两种模式：**共享锁模式**与**排他锁模式**，其使用规则如下：

- 若事务需要读取某一数据对象，必须先获取该对象的共享锁。多个事务可以同时持有同一对象的共享锁；但如果该对象已被其他事务加了排他锁，这些事务就必须等待。
- 若事务需要写入某一数据对象，必须先获取该对象的排他锁。同一时间内，不允许其他任何事务持有该对象的锁（无论是共享锁还是排他锁），因此只要该对象上存在任何锁，当前事务就必须等待。
- 若事务先读取某一数据对象、随后又要写入该对象，可将持有的共享锁升级为排他锁。锁升级的执行逻辑与直接获取排他锁完全一致。
- 事务获取锁之后，必须持续持有该锁，直至事务结束（提交或中止）。这正是 “两阶段” 这一名称的由来：第一阶段（事务执行期间）为加锁阶段，第二阶段（事务结束时）为解锁阶段。

**Performance of two-phase locking**

**两阶段锁的性能表现**

The big downside of two-phase locking, and the reason why it hasn’t been used byeverybody since the 1970s, is performance: transaction throughput and responsetimes of queries are significantly worse under two-phase locking than under weakisolation.

两阶段锁的一大缺点，也是它自 20 世纪 70 年代起未能得到全面普及的原因，在于**性能问题**：在两阶段锁机制下，事务吞吐量与查询响应时间的表现，要显著劣于弱隔离级别下的表现。

This is partly due to the overhead of acquiring and releasing all those locks, but moreimportantly due to reduced concurrency. By design, if two concurrent transactionstry to do anything that may in any way result in a race condition, one has to wait forthe other to complete.

性能不佳的部分原因在于获取和释放大量锁所产生的开销，但更关键的因素是**并发度的降低**。从设计逻辑来看，只要两个并发事务执行的操作存在引发竞态条件的潜在可能，其中一个事务就必须等待另一个事务执行完毕后，才能继续推进。



**Predicate locks**

**谓词锁**

In the preceding description of locks, we glossed over a subtle but important detail.In “Phantoms causing write skew” on page 250we discussed the problem of phan‐toms—that is, one transaction changing the results of another transaction’s searchquery. A database with serializable isolation must prevent phantoms.

在之前对锁机制的描述中，我们略过了一个细微但至关重要的细节。在第 250 页 “幻读引发的写偏斜” 一节中，我们讨论了幻读问题 —— 即一个事务改变了另一个事务的搜索查询结果。提供串行化隔离级别的数据库必须防范幻读问题。

In the meeting room booking example this means that if one transaction hassearched for existing bookings for a room within a certain time window (seeExample 7-2), another transaction is not allowed to concurrently insert or updateanother booking for the same room and time range. (It’s okay to concurrently insertbookings for other rooms, or for the same room at a different time that doesn’t affectthe proposed booking.) How do we implement this? Conceptually, we need a predicate lock [3]. It works sim‐ilarly to the shared/exclusive lock described earlier, but rather than belonging to aparticular object (e.g., one row in a table), it belongs to all objects that match somesearch condition, such as:

以会议室预订场景为例，这意味着：若某个事务已查询了某间会议室在特定时间窗口内的现有预订记录（参见示例 7-2），则不允许其他事务并发插入或更新该会议室在同一时间范围内的另一笔预订记录。（而并发插入其他会议室的预订记录，或同一会议室在不影响当前待提交预订的其他时段的预订记录，是允许的。）该如何实现这一规则呢？从逻辑层面来说，我们需要一种**谓词锁**[3]。它的工作原理与前文所述的共享 / 排他锁类似，但核心区别在于：它并非归属某个特定的数据对象（例如表中的某一行），而是归属所有匹配某一搜索条件的对象，例如以下查询所覆盖的对象：

```mysql
SELECT * FROM bookings WHERE room_id=123 AND end_time>'2018-01-01 12:00' AND start_time<'2018-01-01 13:00';
```

A predicate lock restricts access as follows:

-  If transaction A wants to read objects matching some condition, like in that SELECT query, it must acquire a shared-mode predicate lock on the conditions of the query. If another transaction B currently has an exclusive lock on any object matching those conditions, A must wait until B releases its lock before it is allowed to make its query.
- If transaction A wants to insert, update, or delete any object, it must first check whether either the old or the new value matches any existing predicate lock. If there is a matching predicate lock held by transaction B, then A must wait until B has committed or aborted before it can continue.

谓词锁的访问限制规则如下：

- 若事务 A 想要读取匹配某一条件的对象（如上述 SELECT 查询），则必须为该查询的条件获取一把共享模式的谓词锁。如果另一事务 B 当前持有任何匹配该条件的对象的排他锁，那么 A 必须等待 B 释放锁后，才能执行该查询。
- 若事务 A 想要插入、更新或删除任一对象，则必须先检查该对象的旧值或新值是否匹配任何已存在的谓词锁。如果存在事务 B 持有的匹配谓词锁，那么 A 必须等待 B 提交或中止后，才能继续执行。

The key idea here is that a predicate lock applies even to objects that **do not yet existin the database, but which might be added in the future** (phantoms). If two-phaselocking includes predicate locks, the database prevents all forms of write skew andother race conditions, and so its isolation becomes serializable.

这里的核心思路是：谓词锁的作用范围甚至包括**尚未存在于数据库中、但未来可能被添加**的对象（即幻行）。如果两阶段锁机制中包含谓词锁，数据库就能防范所有形式的写偏斜及其他竞态条件，从而使其隔离级别达到串行化。



**Index-range locks**

**索引范围锁**

Unfortunately, predicate locks do not perform well: if there are many locks by activetransactions, checking for matching locks becomes time-consuming. For that reason,most databases with 2PL actually implement **index-range locking**(also known as **next-key locking**), which is a simplified approximation of predicate locking [41, 50].

遗憾的是，谓词锁的**性能表现不佳**：如果存在大量由活跃事务持有的锁，那么检查是否存在匹配锁的操作会变得十分耗时。正因如此，大多数采用两阶段锁的数据库，实际实现的是**索引范围锁**（也称为**临键锁**）—— 它是谓词锁的一种简化近似方案 [41,50]。

Either way, an approximation of the search condition is attached to one of theindexes. Now, if another transaction wants to insert, update, or delete a booking forthe same room and/or an overlapping time period, it will have to update the samepart of the index. In the process of doing so, it will encounter the shared lock, and itwill be forced to wait until the lock is released.

无论采用哪种实现方式，查询条件的近似范围都会关联到某一个索引上。此时，若另一个事务想要插入、更新或删除同一间会议室、且 / 或时间存在重叠的预订记录，就必须更新索引的同一部分。在执行该操作的过程中，该事务会遇到对应的共享锁，进而被强制等待，直至这把锁被释放。

This provides effective protection against phantoms and write skew. Index-rangelocks are not as precise as predicate locks would be (they may lock a bigger range of objects than is strictly necessary to maintain serializability), but since they have muchlower overheads, they are a good compromise.

这种机制能够有效防范幻读与写偏斜问题。索引范围锁的精准度不及谓词锁（为了维持串行化，它锁定的对象范围可能比严格所需的范围更大），但由于其开销要低得多，因此是一种很好的折中方案。

If there is no suitable index where a range lock can be attached, the database can fallback to a shared lock on the entire table. This will not be good for performance, sinceit will stop all other transactions writing to the table, but it’s a safe fallback position.

如果不存在可关联范围锁的合适索引，数据库会退而求其次，对整个表加共享锁。这种做法的性能表现并不好，因为它会阻止所有其他事务向该表写入数据，但却是一种安全的兜底方案。

#### Serializable Snapshot Isolation (SSI)

**可串行化快照隔离（SSI）**

**Decisions based on an outdated premise**

**基于过期前提的决策**

When we previously discussed write skew in snapshot isolation (see “Write Skew andPhantoms” on page 246), we observed a recurring pattern: a transaction reads somedata from the database, examines the result of the query, and decides to take someaction (write to the database) based on the result that it saw. However, under snap‐shot isolation, the result from the original query may no longer be up-to-date by thetime the transaction commits, because the data may have been modified in the mean‐time.

前文讨论快照隔离下的写偏斜问题时（参见第 246 页 “写偏斜与幻读”），我们发现了一种重复出现的模式：事务先从数据库中读取部分数据，分析查询结果，再基于所见的结果决定执行某些操作（向数据库写入数据）。但在快照隔离机制下，当事务提交时，初始查询得到的结果可能已经失效 —— 因为在此期间，相关数据可能已被修改。

Put another way, the transaction is taking an action based on a premise (a fact thatwas true at the beginning of the transaction, e.g., “There are currently two doctors oncall”). Later, when the transaction wants to commit, the original data may havechanged—the premise may no longer be true.

换一种说法，事务的操作是基于某一**前提**执行的（该前提在事务启动时成立，例如 “目前有两名医生在值班”）。而当事务准备提交时，原始数据可能已经发生变化，这个前提也就不再成立。

When the application makes a query (e.g., “How many doctors are currently oncall?”), the database doesn’t know how the application logic uses the result of thatquery. To be safe, the database needs to assume that any change in the query result(the premise) means that writes in that transaction may be invalid. In other words,there may be a causal dependency between the queries and the writes in the transac‐tion. In order to provide serializable isolation, the database must detect situations inwhich a transaction may have acted on an outdated premise and abort the transac‐tion in that case.

当应用程序发起查询（例如 “当前有多少名医生在值班？”）时，数据库并不知道应用程序的业务逻辑会如何利用该查询结果。为了保证安全性，数据库需要做出这样的假设：**查询结果（即前提）的任何变化，都可能导致该事务中的写入操作失效**。换句话说，事务中的查询操作与写入操作之间，可能存在一种**因果依赖**关系。

How does the database know if a query result might have changed? There are twocases to consider:

- Detecting reads of a stale MVCC object version (uncommitted write occurred before the read)
- Detecting writes that affect prior reads (the write occurs after the read)

数据库如何判断查询结果是否可能发生变化？需要考虑以下两种情况：

- 检测对**多版本并发控制（MVCC）过期数据版本**的读取操作（即读取操作发生前，已有未提交的写入操作存在）
- 检测会影响**历史读取结果**的写入操作（即写入操作发生在读取操作之后）

### Summary

**Dirty reads** One client reads another client’s writes before they have been committed. The **read committed** isolation level and stronger levels prevent dirty reads.

**脏读** 一个客户端读取了另一个客户端**尚未提交**的写入数据。**读已提交**及更高级别的隔离级别可以防止脏读。

**Dirty writes** One client overwrites data that another client has written, but not yet committed. Almost all transaction implementations prevent dirty writes.

**脏写** 一个客户端覆盖了另一个客户端**已写入但未提交**的数据。几乎所有事务实现都能防止脏写。

**Read skew (nonrepeatable reads)** A client sees different parts of the database at different points in time. This issue is most commonly prevented with snapshot isolation, which allows a transaction to read from a consistent snapshot at one point in time. It is usually implemented with multi-version concurrency control (MVCC).

**读偏斜（不可重复读）** 一个客户端在事务的不同时间点，读取到数据库中不一致的数据集。这个问题最常用**快照隔离**来解决，快照隔离允许事务读取某一时间点的一致性快照，通常基于**多版本并发控制（MVCC）** 实现。

**Lost updates** Two clients concurrently perform a read-modify-write cycle. One overwrites the other’s write without incorporating its changes, so data is lost. Some implemen‐ tations of snapshot isolation prevent this anomaly automatically, while others require a manual lock (SELECT FOR UPDATE).

**更新丢失** 两个客户端并发执行**读 - 改 - 写**循环，其中一个客户端的写入操作覆盖了另一个的写入结果，且未整合对方的修改，导致数据丢失。部分快照隔离的实现会自动防止这种异常，其他实现则需要手动加锁（如执行 `SELECT FOR UPDATE` 语句）。

**Write skew** A transaction reads something, makes a decision based on the value it saw, and writes the decision to the database. However, by the time the write is made, the premise of the decision is no longer true. **Only serializable isolation prevents this anomaly.**

**写偏斜** 一个事务读取某些数据后，基于所见的值做出决策，并将决策结果写入数据库。但当写入操作执行时，当初决策所依赖的前提条件已不再成立。**只有串行化隔离级别能够防止这种异常**。

**Phantom reads** A transaction reads objects that match some search condition. Another client makes a write that affects the results of that search. Snapshot isolation prevents straightforward phantom reads, but phantoms in the context of write skew require special treatment, such as **index-range locks**.

**幻读** 一个事务读取匹配某一搜索条件的对象，另一个客户端执行写入操作，改变了该搜索条件的结果集。快照隔离可以防止简单的幻读，但幻读引发的写偏斜问题需要特殊处理，例如使用**索引范围锁**。

Weak isolation levels protect against some of those anomalies but leave you, theapplication developer, to handle others manually (e.g., using explicit locking). Onlyserializable isolation protects against all of these issues. We discussed three differentapproaches to implementing serializable transactions:

弱隔离级别只能防范上述部分异常，其余异常需要应用开发者手动处理（例如使用显式锁）。**只有串行化隔离级别能够防范所有这些问题**。我们讨论过三种实现串行化事务的方案：

**Literally executing transactions in a serial order** If you can make each transaction very fast to execute, and the transaction throughput is low enough to process on a single CPU core, this is a simple and effective option.

**严格按串行顺序执行事务** 若能保证每个事务执行速度极快，且事务吞吐量低至单个 CPU 核心即可处理，这会是一种简单且高效的方案。

**Two-phase locking** For decades this has been the standard way of implementing serializability, but many applications avoid using it because of its performance characteristics.

**两阶段锁** 数十年来，这一直是实现串行化的标准方案，但由于其性能特性，许多应用会避免使用它。

**Serializable snapshot isolation (SSI)** A fairly new algorithm that avoids most of the downsides of the previous approaches. It uses an optimistic approach, allowing transactions to proceed without blocking. When a transaction wants to commit, it is checked, and it is aborted if the execution was not serializable.

**可串行化快照隔离（SSI）** 这是一种相对较新的算法，规避了前两种方案的大部分缺点。它采用**乐观并发控制**思路，允许事务无阻塞地执行；仅在事务提交阶段进行冲突检查，若检测到执行过程不满足串行化要求，则中止该事务并要求重试。



