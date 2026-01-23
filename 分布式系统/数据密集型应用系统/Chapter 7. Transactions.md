[toc]

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
- Isolation Concurrently running transactions shouldn’t interfere with each other. For example, if one transaction makes several writes, then another transaction should see either all or none of those writes, but not some subset.

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
-  Two-phase locking (see “**Two-Phase Locking (2PL)**” on page 257), which for several decades was the only viable option
-  Optimistic concurrency control techniques such as serializable snapshot isolation (see “**Serializable Snapshot Isolation (SSI)**” on page 261)

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
- Write throughput must be low enough to be handled on a single CPU core, or else transactions need to be partitioned without requiring cross-partition coordination.
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
-  If transaction A wants to insert, update, or delete any object, it must first check whether either the old or the new value matches any existing predicate lock. If there is a matching predicate lock held by transaction B, then A must wait until B has committed or aborted before it can continue.

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