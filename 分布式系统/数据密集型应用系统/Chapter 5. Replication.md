[toc]

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
- If your replicas are distributed across multiple datacenters (for geographical proximity to users or for availability), there is additional complexity. Any request that needs to be served by the leader must be routed to the datacenter that con‐ tains the leader.

**在基于主节点的复制系统中，我们该如何实现写后读一致性呢？具体有多种可行的技术方案，以下列举其中几种：**

- 当读取用户**可能已修改过**的数据时，从主节点读取；其余情况下，从从节点读取。这要求系统具备一种判断逻辑 —— 无需实际查询数据，就能确定某条数据是否有可能被修改。例如，社交网络中的用户资料通常只有账号所有者可以编辑，其他用户无权修改。基于这一特点，我们可以制定一条简单规则：**始终从主节点读取用户自己的资料**，而从从节点读取其他用户的资料。
- 若应用中的大部分数据都存在被用户修改的可能，那么上述方案的效果就会大打折扣 —— 因为绝大多数读取请求都需要路由到主节点，这样就会**抵消读扩展带来的优势**。这种情况下，就需要借助其他判断标准来决定读取请求的路由目标。例如，系统可以记录每条数据的**最后更新时间戳**，在数据更新后的一分钟内，所有针对该数据的读取请求都定向到主节点；也可以实时监控从节点的**复制延迟**，一旦某个从节点与主节点的延迟超过一分钟，就暂时禁止向该从节点发送查询请求。
- 客户端可以记录自己**最近一次写入操作的时间戳**，之后系统就需要确保：为该用户提供读取服务的副本，至少包含该时间戳之前的所有更新数据。如果某个副本的数据同步进度未达标，那么要么将读取请求转发至其他同步完成的副本，要么让该查询请求**等待副本追平数据后再执行**。这里的时间戳可以是**逻辑时间戳**（用于标记写入操作顺序的标识，比如日志序列号），也可以是实际的系统时钟时间（这种情况下，**时钟同步就会变得至关重要**，详见第 287 页的 “不可靠时钟” 章节）。
- 若数据库副本分布在**多个数据中心**（此举或是为了让服务地理位置更贴近用户，或是为了提升系统可用性），则会引入额外的复杂度。所有需要由主节点处理的请求，都必须精准路由到**主节点所在的数据中心**。

Another complication arises when the same user is accessing your service from mul‐tiple devices, for example a desktop web browser and a mobile app. In this case youmay want to provide cross-device read-after-write consistency: if the user enters someinformation on one device and then views it on another device, they should see theinformation they just entered.

当同一用户通过多台设备访问服务时（例如桌面端网页浏览器和移动端应用），会衍生出另一个复杂问题。这种情况下，你可能需要实现**跨设备写后读一致性**：如果用户在一台设备上录入了某些信息，之后用另一台设备查看，应该能看到自己刚录入的内容。

In this case, there are some additional issues to consider:

-  Approaches that require remembering the timestamp of the user’s last update become more difficult, because the code running on one device doesn’t know what updates have happened on the other device. This metadata will need to be centralized.
-  If your replicas are distributed across different datacenters, there is no guarantee that connections from different devices will be routed to the same datacenter. (For example, if the user’s desktop computer uses the home broadband connec‐ tion and their mobile device uses the cellular data network, the devices’ network routes may be completely different.) If your approach requires reading from the leader, you may first need to route requests from all of a user’s devices to the same datacenter.

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