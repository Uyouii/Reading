# GFS文件系统

本文主要是对[**The Google File System**(2003)](https://github.com/Uyouii/MIT_6.824_2020_Project/blob/master/tutorial/LEC3%20GFS/gfs%202003.pdf)的翻译和总结。

## 1 简介 (INTRODUCTION)

GFS的全称就是Google Gile System，是Google实现一个分布式的大文件存储系统，运行在Linux上。Goole在2003年上述论文中公布了GFS的一些实现细节，但是没有将其开源。在2013年，Google公布了Colossus项目，作为下一代的Google文件系统。

下面是Google在设计GFS时基于的背景和出发点：

1. 首先，系统中的组件故障是一种常态。这个文件系统是由成百上千台存储机器组成，并且会有大量的客户端机器访问。这个系统机器组件的数量和质量实际上决定了它在任何时间都可能会遇到组件无法正常工作的情况，有些故障甚至无法恢复。例如应用程序或者操作系统的bug，人为的操作失误，机器磁盘、内存、网络或者电源故障。因此，监控、错误检测、容错机制和错误恢复是系统中不可或缺的一部分。
2. 其次，系统中的文件都很大。数个GB的文件在系统中很常见。当需要处理包含数十亿个对象，数个TB，并且快速增长的数据集时，即使操作系统可以支持这个量级的文件，管理数十亿个几KB的文件也不是一件容易的事情。所以一些参数和假设需要重新设计和实现，例如文件块的大小和系统的IO。
3. 第三，系统中的大多数文件都是追加操作，而不是修改和覆盖。系统中有些文件甚至没有随机写入的操作。数据一旦写入，文件只会被读取，而且通常只按顺序读取。很多数据模型都具有这些特征，有些可能是数据分析程序扫描的大型数据集，有些可能是应用程序不断产生的数据流，有些可能是档案数据。有些数据可能是在一台机器上产生，在另一台机器上等待处理的中间结果（例如MapReduce）。对于这种大文件的访问模式，对文件的追加写操作是性能优化和保证原子性的重点。
4. 第四，应用程序和文件系统采用协同设计（co-designing）使整个系统更加灵活。例如，通过放宽GFS的一致性模型，在不给应用系统造成负担的情况下极大的简化了文件系统。通过引入原子的追加写操作，支持多个客户端并发对同一个文件进行追加写，而且不需要在它们之间进行额外的同步操作。

## 2 整体设计 (DESIGN OVERVIEW)

### 2.1 假设 (Assumptions)

之前已经简单介绍了一些结论，下面会更加详细的阐述GFS文件系统的背景和需要解决的问题：

1. 这个系统由很多廉价的机器组成，组件会经常发生故障。它需要持续的系统监控，并且可以定期的检测出组件故障，并且从中快速恢复。
2. 系统会存储适量的大文件。预计会有几百万个文件，每个文件平均会有100MB甚至更大。几个GB的文件很常见。小文件也会支持，但是不需要额外的优化。
3. 系统主要包含两种读取方式：大型流式读取(streaming reads)和小型随机读取(random reads)。大型流式读取中，单个操作通常读取几百KB或者几MB。同一个客户端通常会连续读取一个文件中的连续区域。小型的随机读取会在文件的某个偏移量处读取几KB。
4. 系统的写入操作主要是对文件大量顺序的追加写操作。每次写入数据的大小和读取时相近。数据写入后，文件很少被修改。系统同样支持对文件任意位置进行小的写操作，但是不一定高效。
5. 系统需要支持多个客户端并行对文件的追加写操作。GFS中的文件通常用于生产者-消费者队列或者多路合并。会有数百台机器，每台机器上一个生产者，并行的追加写入到同一个文件。所以需要在最小开销的情况下保证原子性。
6. 高带宽比低延迟更重要。系统中大多数应用程序都更加看重以更高的速率处理数据，很少有应用程序对单次读取或者写入操作时间有严格的要求。

### 2.2 接口 (interface)

GFS提供了类似文件系统的接口，但是没有实现标准的APi，比如POSIX。文件系统同样包含目录，每个文件由路径名唯一标识。支持创建(create)、删除(delete)、打开(open)、关闭(close)、读取(read)和写入(write)文件这些常规操作。

GFS还支持快照(snapshot)和追加写(record append)。snapshot可以以低成本的方式创建文件或者目录的副本。record append支持多个客户端同时把数据追加写入到同一个文件，并且保证操作的原子性。这种类型的文件在构建大型分布式应用程序时会非常有用。

###  2.3 架构 (**Architecture**)

![ds2](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/distribuide_system/ds2.png)

一个GFS集群由一个Master和多个chunkserver组成，会有多个client同时访问，如上图所示。在同一台机器中同时运行chunkserver和client是可行的，只要机器的资源足够，并且可以容忍应用程序带来的不稳定性和低可靠性。

单个文件会分成固定大小的chunk。master在创建每个chunk时都会为其分配一个全局唯一的64位的chunk handle。chunkserver会把chunk存储在本机的linux磁盘上，通过chunk handle和字节偏移量访问其中的数据。同时为了提高可靠性，每个chunk都会在多个chunkserver中复制和备份。默认情况下，每个chunk都有三个副本，用户可以为不同空间下的文件设置不通的备份级别。

master会维护文件系统中所有文件的metadata(元数据)，包括命名空间，访问权限，文件和chunk的映射关系以及当前chunk所在的位置。master还会管理系统活动，例如chunk的租约(lease)管理，孤儿chunk的回收，chunk在chunkserver中的迁移等。master 会周期的通过HeaerBeat 消息和chunkserver进行通信，以便下发指令和收集chunkserver的状态。

每个应用程序会通过GFS client API对master和chunkserver进行交互，进行read和write操作。client在获取和修改元数据相关的操作时会和master进行交互，但是所有的文件数据都会直接从chunkserver获取。

client和chunkserver都不会缓存文件数据，也就不用考虑缓存带来的一致性问题。而且大部分client通过流传输的目录或者文件都很大，本地也无法缓存。不过client会缓存metadata。chunkserver同样也不需要缓存文件数据，因为chunk本身就在本地文件中，而且liunk中的文件缓冲也会把经常访问的文件数据放在内存中。

### 2.4 Single Master

single master可以极大的简化GFS文件系统的设计，所有文件的元数据都会在一个单独的master机器中管理，使得master可以全局的对chunk和chunkserver进行管控和复制。但是单一的master也会成为瓶颈，所以需要尽量减少它在client的read和write操作中的参与量。client不会从master中读取文件数据，而是通过master获取应该访问哪些chunkserver。client会在本地缓存这些元数据信息，并且直接和chunkserver进行文件数据相关的交互。

![gfs1](https://github.com/Uyouii/BookReading/blob/master/images/distribuide_system/gfs1.png?raw=true)

上图是简单的交互流程：

1. 因为chunk是固定的大小，所以client可以根据文件名和文件内的字节偏移转化为chunk的索引。
2. client向master发送文件名和chunk的索引。
3. master回复客户端chunk handle和chunk副本所在的chunk server。
4. client通过文件名和chunk 索引缓存下 chunk副本位置信息。
5. client向其中一个副本发送请求（有可能是距离最近的一个副本）。请求包括chunk handle和chunk内的字节范围。

client在本地缓存过期或者重新打开文件之前不会重新向master获取这些信息。client一般也会批量向master请求这些信息。

### 2.5 Chunk Size

chunk的大小是系统设计的关键点之一。目前GFS选择了64MB作为单个chunk的大小，比linux文件系统块(4K)要大很多。每个chunk的副本都是作为普通的linux文件存储在chunk server中。在chunkserver中chunk都是普通的linux文件，chunk文件也只在需要的时候才进行扩张。惰性空间分配(lazy space allocation)避免了内部碎片造成的空间浪费。

大的chunk的大小有几个重要的优势：

1. 减少了客户端和master之间的交互请求。因为对于同一个chunk的读写只需要向master发出一次请求获取chunk的位置信息。这可以有效的减少master的工作负载，因为大部分程序都是顺序读写大文件。对于小文件的随机读取，客户端也能请求缓存TB量级的chunk的位置信息。
2. 对于大的chunk，客户端在单个chunk中可以执行更多的操作，也可以减少和chunkserver之前的TCP连接带来的网络开销。
3. 大的chunk也减少了在master中存储的元数据的信息，使得我们可以把元数据信息保存在master的内存中，反过来也会带来2.6.1中的其他好处。

应一方面，大的块大小，即使使用了惰性空间分配(lazy space allocation)，也会有其他的缺点。例如一个小文件由比较少的chunk组成（也许只有一个）。如果有大量的客户端同时访问这个文件，存储这个文件的chunkserver可能会成为热点(hot spots)。不过在实践中，热点并不是GFS系统的主要问题，因为系统中的应用程序大多是顺序读写由多个chunk组成的大文件。

不过在实践中GFS也确实遇到了热点问题：在一个批处理队列系统(batch-queue system)中使用时，一个由单个chunk组成的可执行文件在数百个机器上同时启动时，储存这个文件的几个chunkserver因为数百个请求同时到达导致性能问题。通过给这个文件下的chunk设置更多的副本可以解决这个问题，不过一个长期的解决方案是允许一个客户端从其他客户端读取这个文件的数据（感觉像P2P）。

### 2.6 Metadata(元数据)

master存储了三种类型的元数据:

1. 文件和chunk的namespace
2. 文件和chunk的映射关系
3. 每个chunk和副本在chunkserver上的位置

所有的元数据信息都保存在master的内存中。文件的namespace以及文件和chunk的映射关系也会把operation log记录在磁盘中以保证持久性。operation log可以保证master中元数据更改的可靠性和持久性，以及防止在master奔溃后出现不一致的问题。

master不会持久存储chunk的位置信息。相反，它会在master启动时以及chunkserver新加入到集群中时向每个chunkserver询问它包含了哪些chunk。

#### 2.6.1 内存中的数据结构

因为元数据存储在内存中，所以master的操作速度很快。此外，master在后台定期扫描系统的整个状态也会很简单和高效。这些定期扫描用来实现chunk的垃圾收集，chunkserver故障时重新复制，以及chunk的迁移以平衡chunkserver之间的负载和磁盘空间的使用。

把元数据存储在内存中唯一的潜在风险是系统中chunk的数量和整个系统的容量会收到master内存的限制。不过在实践中并不是一个严重的问题。在元数据中，master为每个64M的chunk维护的数据少于64bytes。在系统中，大多数的chunk都是满的，只有文件中的最后一个chunk会被部分填充。同样，每个文件的namespace在存储上通过使用前缀压缩(prefix compression)，需要的数据通常少于64bytes。

如果有必要支持更大的文件系统，为master添加额外的内存相对代价并不大。但是通过把元数据存储在内存中，系统会更简单、高效、灵活。

#### 2.6.2 Chunk的位置

master不会永久记录chunk在chunkserver上的位置信息，而是在每次启动时轮询chunkserver获取这些信息。在启动后master会通过定期的HeartBeat消息来监视chunkserver以实时更新这些信息。

相比于将chunk的信息永久存储在master，每次重启时从chunkserver获取在实现上更为简单，而且解决了在chunkserver加入和离开集群、更改名称、失败和重启等保持master和chunkserver的同步问题。这些问题在拥有数百台服务器的集群中经常发生。

另一个点是chunkserver对于在它的磁盘上有没有chunk拥有最终决定权，所以在master中维护这样一个一致性视图意义不大。因为chunkserver上的错误可能导致chunk消失（例如磁盘损坏），或者管理员对一个chunkserver重命名。

#### 2.6.3 Operation Log

opertaion log包含了master中元数据更改的历史记录。它是GFS的核心。因为opertaion log不仅是元数据的唯一的持久化的记录，还是定义并发操作顺序的逻辑时间线。文件和chunk，以及它们的version，都由它们被创建的逻辑时间线唯一且永久标识。

由于operation log非常关键，所以必须保证存储可靠，并且当元数据的更改持久化之前，更改对客户端不可见（就是write ahead log）。否则可能会丢失整个文件系统或者客户端最近操作，即使这些chunk仍然存在。因此，我们把operation log复制到多台远程机器上，只有当本地和远程的机器都将对应的operation log刷新到磁盘上后才响应客户端的操作。master在将operation log刷新到磁盘上前会批量处理多条记录，来减少opertion log的刷新和复制操作对系统吞吐量的影响。

master通过重新执行operation log来恢复文件系统状态。为了减少重新启动的时间，需要保证operation log足够小。每当operation log增长超过一定大小时，master就对其当前的状态进行checkpoint。后续需要恢复状态时，只需要加载最新的checkpoint，并且只需要重放checkpoint之后的opertion log就可以恢复文件系统状态。checkpoint的结构是compact B-tree，可以直接映射到内存中进行文件namespace查找，无需额外的解析。这进一步加快了系统的恢复速度和可用性。

新建checkpoint可能会需要一定的时间，所以master内部实现可以通过不阻塞修改请求的情况下创建新的checkpoint。master会切断到一个新的operation log文件，并且在一个单独的线程中创建新的checkpoint。新的checkpoint会包含opertion log切换前所有的更改。在拥有几百万个文件的集群中，新的checkpoint可以在1min左右创建完成。随后会在本地和远程磁盘写入。

系统恢复时只需要最新的checkpint和之后的opertion log。旧的checkpoint和operation log可以自由删除，但是GFS保留了一些来防止意外发生。checkpoint期间的失败并不会影响系统的正确性，系统恢复时会检测并且跳过不完整的checkpoint。

### 2.7 一致性模型(Consistency Model)

GFS拥有一个相对宽松的一致性模型，可以很好的支持分布式系统的应用程序，而且实现起来也相对简单和高效。接下来会讨论GFS能保证的一致性及其对应用系统的意义，也会重点介绍GFS如何保证一致性。

#### 2.7.1 Guarantees by GFS

GFS中文件namespace的更改（例如创建文件）是原子(atomic)操作。在master中namespace lock保证了操作的原子性和正确性(4.1节)；在mater中的operation log定义了这些操作的全局顺序(2.6.3)。

![gfs2](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/distribuide_system/gfs2.png)

数据修改后文件区域的状态取决于数据修改的类型、操作是否成功以及是否存在并发(concurrent)操作。Table1总结了这些情况。

对于一个文件区域，如果所有的客户端看到的所有文件副本都是相同的数据，这个文件区域就是**一致的(consistent)**。在文件区域被修改后，如果文件区域是一致的，并且客户端可以确定全部的修改内容，这个文件区域就是**确定的(defined)**。（这段不太好理解，贴一下原文 A region is defined after a file data mutation if it is consistent and clients will see what the mutation writes in its entirety. )。如果对一个文件区域修改成功，并且没有并发的修改请求，那么这个区域的修改就是defined(defined一定是consistent): 所有的客户端会看到相同的写入内容。并发成功的修改会使这个文件区域处于一致但不确定的状态**(undefined but consistent**): 所有客户端看到相同的结果，但是不确定哪个客户端的修改会被写入，通常这种文件区域是由多个混合的修改组成。

一个失败的修改操作会使文件区域处于不一致(**inconsistent**)的状态(因此也是不确定的状态**undefined**)：不同的客户端可能会在不同的时间看到不同的数据。下面会介绍应用程序如何区分文件区域是确定(defined)或者是不确定的(undifiend)。

数据修改可以是writes或者record appends。write是指在文件的指定偏移处写入数据。record append可以使record至少原子的被追加写入一次，即使存在并发写入的情况下，但是具体的offset由GFS决定。(在GFS中，record append区别于普通的append操作，普通的append操作可以理解为是在文件末尾处的write操作。）record append完成后会把结果的offset返回给客户端，这个offset是写入的record的defined文件区域的起始位置。不过GFS可能会偶尔在其中插入一些padding或者重复的record，这些数据占据的区域被认为是inconsistent状态，不过这种数据相只占整体的数据量非常小的一部分。

在连续成功的修改操作之后，被修改的文件区域可以保证是defined，并且包含最后一次修改的数据。GFS通过以下设计来实现这点：

1. 对一个chunk的改动，GFS会保证以同样的操作顺序修改它所有的副本。
2. 通过使用chunk version number来检测chunk的副本是不是最新的(stale)，一个chunk的副本可能因为chunkserver在运行期间宕机错过了某些改动。

stale的副本不会再参与修改操作，master也不会提供给客户端stale chunk所在chunkserver的位置，它们会尽快的被垃圾回收。

由于客户端会缓存chunk的位置，所以它们可能会在缓存刷新之前从stale chunk中读取数据。在客户端缓存超时或者文件下一次打开时，客户端中文件相关的缓存就会被清空。此外，系统中的大部分文件都是仅有append操作，stale的副本一般返回的都是未完成的而不是过时的数据。并且当客户端重新从master获取时，可以立即获取该chunk最新的位置。

即使在修改操作成功很久之后，机器组件的故障仍然有可能损坏数据。GFS通过master和chunkserver之前定期的handshakes来识别故障的chunkserver，并且通过checksum校验数据的完成性(Section 5.2)。一旦出现问题，就会尽快从有效的副本中恢复数据(Section 4.3)。只有在GFS做出应对操作之前（通常在几分钟内），chunk所有的副本数据丢失，chunk里的数据才会不可逆的丢失。不过即使在这种情况下，chunk也只是变得不可用，而不是损坏：应用程序读取时会收到明确的错误而不是有问题的数据。

#### 2.7.2 对应用程序的影响

GFS中的应用程序可以通过一些简单的来适应这种relaxed consistency model：依赖append而不是overwrites，checkpoint，自我验证和识别等。

在实践中GFS中的应用程序都是通过append而不是overwrite来改变文件。在一个典型的例子中，一个wrtier从头到尾生成一个文件。在数据写入完成后自动将文件重命名为永久名称，或者定期对已经成功写入的数据做检查点。检查点还可能包含应用级程序的校验和。读取器仅验证和处理直到最后一个检查点的文件区域，该检查点之前的数据都处于defined状态。无论是一致性问题还是并发问题，这种方法都很有帮助。相比于ramdon writes，append操作会更高效，对于应用程序失败也很好处理。检查点可以让写者以增量的方式重新启动，并且防止读者处理已经成功写入文件中但是从应用程序角度看并不完整的数据。

在其他典型的应用中，许多wrtier并发地对文件进行追加操作并获取合并后的结果，或者作为一个生产者-消费者队列。record append操作的append-at-least-once语义保证了每个writer的输入。reader需要用如下的方法处理偶尔的padding和重复的写入。wrtier的每条record都包含例如checksum等额外信息，以便验证其有效性。reader可以使用checksum识别和丢弃额外的padding和record片段。如果应用程序不能容忍偶尔的重复（例如可能会触发非幂等的操作），可以考虑使用record中唯一的标识符把他们过滤掉。record reader在读取时会收到相同的记录队列，加上偶尔的重复。

## 3 系统交互(SYSTEM INTERACTIONS)

GFS设计上尽量在系统操作中减少master的参与。在这个背景下，我们现在来介绍client、master和chunkserver之间如何交互来实现数据更改，原子的record append和建立快照。

### 3.1  租约和mutation顺序(Leases and Mutation Order)

mutation是指修改chunk内容或者元数据的操作，例如write和append。每个mutation都会作用于chunk所有的副本。我们使用leases来保证不同副本间mutation的一致性。master会把lease授权给chunk的其中一个副本，这个副本被称作***primary***。primary会为决定在该chunk上所有mutation的顺序，所有副本在变更时都会遵循这个顺序。因此，全局的muation顺序由master授权的lease和在lease期限内primary分配的序列号决定。

lease机制的目的在于最大程度的减少master的管理开销。lease初始有效时间为60s。但是，只要chunk在发生变更，primary就可以一直请求master并续期。续期的请求和结果携带在master和chunkserver之间定时的HeartBeat消息中。master有时可能会在lease到期前尝试撤销（例如，当文件在被重命名时，master想禁止这个文件上的muation操作）。即使master和primary之间断开连接，也可以在就的lease到期后，向另一个副本授予新的lease。

![gfs3](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/distribuide_system/gfs3.png)



在Figure2中，我们通过图中的编号控制流程来说明此过程：

1. client询问master哪个chunkserver持有当前chunk的lease，以及该chunk其他副本的位置。如果当前该chunk没有lease，master就会选择一个副本作为primary授予lease。
2. master回复client该chunk primary和其他副本的位置。client会将这个信息缓存到本地。当primary不可访问，或者回复client其不再拥有lease时，client才会再次询问master。
3. Client将数据推送给chunk的所有副本。推送数据时可以按照任意顺序。每个chunkserver都会把数据缓存到LRU缓存中，直到数据被使用或者超时。这个流程中通过数据流和控制流的分离，可以基于网络拓扑(network topology )调度提高数据传输性能，而不用管哪个chunkserver是primary。
4. 当所有副本都确认收到数据后，client就会向primary发送写请求。这个请求中标识了之前推送的数据信息。primary会给它收到的所有muation请求分配连续的序列号（有可能是来自多个client的请求），保证了请求的顺序。primary会按照分配的序列号顺序来修改本地的数据状态。
5. primary把写请求转发给其他的secondary副本。每个副本都要根据primary分配的序列号来顺序更改。
6. secondary副本回复primary操作已经完成。
7. primary将结果返回给client。整个过程中任何副本中遇到的任何错误都会返回给客户端。如果返回错误，数据可能已经在primary和部分副本上成功写入(如果在primary失败，数据就不会被分配序列号，也不会转发给副本)。此时client的请求被认为失败，并且修改后的文件区域处于不一致的状态。client中的代码通过重试失败的mutation来处理此类错误。client会先在步骤(3)到步骤(7)中进行几次尝试，然后再退回到最开始的步骤重试

如果应用程序写入的数据量很大，或者待写入的数据跨越了chunk的边界，GFS的client码会将其拆分为多个write操作。这些write都会执行上述的控制流程，但是可能会和其他client的并发操作交叉和覆盖。因此，共享的文件区域可能最终包含来自不同client的数据片段，但是chunk不同副本中的数据都是相同的，因为所有的write操作在不同副本中都是以相同的顺序执行的。这使得文件区域处于一致但是不确定的状态(consistent but undefined)，如在2.7节中叙述的。

### 3.2 数据流(Data Flow)

在系统设计中将控制流和数据流解耦，可以更高效的利用网络。当控制指令从client到primary chunkserver，再到所有的secondary chunkserver时，数据则以流水线的方式(**pipelined fashion**)沿着精心挑选的chunkserver链式推送。我们的目标是充分利用每台机器的网络带宽，避免网络瓶颈和高延迟的链路，并最大程度的减少推送数据的延迟。

为了充分利用利用每台机器的网络带宽，数据沿着chunkserver链线性推送，而不是分布在其他拓扑接口中（比如树）。因此每台机器的全部出口带宽都用于尽可能快的传输数据，而不是在多个接收者之间分配。

为了尽可能避免网络瓶颈和高延迟链路，每台机器都将数据发送到网络拓扑中尚未接收到数据的最近的机器。假设client正在向chunkserver S1到S4推送数据，client首先将数据发送到最近的chunkserver，假设是S1。S1将它转发到距离最近的chunkserver，假设是S2。以此类推，S2把数据转发到S3或者S4，看哪个离它最近。GFS系统中的网络拓扑非常简单，可以根据机器的IP地址估算出服务器之间的距离。

最后，根据流水线上的TCP连接传输数据来最小化延迟。一旦chunkserver接收到一些数据，它就会立刻开始转发。在没有网络拥塞的情况下，把B个字节传输到R个副本的理想耗时是`B/T + RL`，其中T是网络吞吐量，L是两台机器间的网络延迟。系统中的网络链路通常为100Mbps(T)，而且L远低于1ms，因此，在理想情况下，可以在80ms左右传输1MB的数据到所有的副本。

### 3.3 Atomic Record Appends

GFS提供了一个称为**record append**的原子的append操作。在传统的写入请求中，client需要指定数据写入的偏移量。对文件中同一区域并发的写入操作会使得该区域可能包含来自多个client的数据片段。但是在record append操作中，客户端仅需要指定数据，GFS会将数据在GFS选择的偏移量处原子的append到file中至少一次（以连续的字节序列），并将该偏移量返回给client。有点类似于在Unix系统中以O APPEND模式打开文件，有多个写者在没有经常条件的情况下并发写入。

record append操作被大量应用于系统中的分布式程序中。在这些应用程序中，不同的client同时追加数据到一个文件。如果使用传统的wrtie操作，client需要进行额外的复杂的同步操作，例如分布式锁。

record append也是一种mutation操作，也会遵循3.1节中的控制流程，不同的是在primary中会有一点额外的逻辑。client将数据推送到文件最后一个chunk的所有的副本，然后把请求发送到primary。primary将会检查如果将请求的record append到当前的chunk是否会超过chunk的最大大小(64MB)。如果出现这种情况，它会填充padding使整个chunk变成最大大小，并且告诉secondaries节点也这么处理，并且回复客户端在下一个块上重试这个请求。record append请求的大小会被限制为chunk大小的1/4，以便于保持在最坏的情况下内部碎片处于可接受水平。最常见的情况是append后的chunk大小没有超过最大大小，primary会将数据写入到chunk中，并且告诉secondaries节点写入的具体偏移量，最后返回成功给client。

如果record append在任一副本上失败，client都会重试该操作。因此同一个chunk的副本可能会包含不同的数据，可能包含同一个record的全部或者部分的重复。GFS不保证chunk的所有副本都是完全相同的，它只保证record作为一个原子的单元被至少写入了一次。对于返回成功的操作，record必须在这个chunk的所有副本中以相同的偏移量写入。因此，即使以后其他的副本成为primary，以后的record都会分配更高的偏移量或者新的chunk。所以，就系统的一致性而言，成功的record append操作写入的数据是defined，(也是consistent)，而中间的区域是inconsistent(也是undefined)。应用程序可以像2.7.2节中讨论的方法来处于文件中不一致的区域。

### 3.4 快照(Snapshot)

快照操作几乎在瞬间就可以复制文件或者目录，同时最大程度的减少对正在进行的mutation操作的中断。用户可以利用快照建立庞大数据集的副本（递归的建立副本的副本），或者对当前文件建立checkpoint，以便后续进行commit或者rollback。

GFS使用copy-on-write技术来实现快照。当master收到一个快照请求时，它首先撤销需要建立快照操作文件中包含的chunk的lease，这一步保证了这些块的后续所有的写入操作都需要向master获取最新的lease，让master有机会先复制一个新的chunk。

当lease被撤销或者过期后，master会把operation log记录到磁盘，随后它会在内存中复制源文件或者目录的元数据。新创建的快照文件会指向与源文件相同的chunk。

当client在进行快照操作后第一次想写入chunk C时，它会想master发送请求来查找当前lease的持有者。mater会注意到chunk C的引用计数大于1。它会推迟处理client的请求，然后选择一个新的chunk C’。随后master要求所有拥有chunk C副本的chunkserver创建一个新的chunk C’。通过在与原数据相同的chunkserver上创建新的chunk，可以确保数据在本地复制，而不是通过网络(磁盘的复制速度大概是100Mb网络速度的3倍)。在此刻之后，client的请求处理和其他chunk没有什么不同：mater授予新的lease给C’的一个副本，并且回复给client。cleint可以正常地向chunk中写入请求，不会感知到这个chunk刚刚创建。

## 4 MASTER相关操作(MASTER OPERATION)

文件namespace相关的操作都由master来执行。master也负责管理GFS中chunk的副本：master会负责选择chunk副本的位置，创建新的chunk和它的副本，并且保证每个chunk拥有足够数量的副本，不同chunkserver之间的负载均衡以及回收存储空间。下面会一一讨论这些功能。

### 4.1 文件命名空间管理和锁(Namespace Management and Locking)

master的很多操作可能会花费很长时间：例如，建立快照时必须撤销快照覆盖的所有chunk上的lease。在执行这些操作时，并不想阻塞master上的其他操作。因此，GFS允许同时运行多个操作，并通过对文件的namesapce加锁来保证正确的执行顺序。

与传统的文件系统不同，GFS并没有维护能列出目录下所有文件的数据结构。也不支持对文件或者目录创建alias(类似于Unix文件系统中的硬连接和软连接)。在逻辑上，GFS会维护文件的完整路径映射到文件元数据的查找表，并且通过前缀压缩在内存中存储。文件命名空间树中的每个节点(文件或者目录的绝对路径)都会关联一个读写锁。

每次在master执行操作前都会获取一组锁。例如对文件或者目录`/d1/d2/.../dn/leaf`进行操作，master会在目录`/d1`、`/d1/d2`……`/d1/d2/.../dn`上获取读锁，`/d1/d2/.../dn/leaf`上获取读锁或者写锁。leaf节点根据具体的操作又可能是一个文件或者目录。

现在来说明这种锁定机制是如何防止在对`/home/user `目录建立快照`/save/user`时创建文件`/home/user/foo`。快照操作会获取`/home`和`/save`的读锁，`/home/user`和`/save/user`的写锁。文件创建操作在`/home`和`/home/user`上获取读锁，在`/home/user/foo`上获取写锁。这两个操作不能同时执行，因为对目录`/homse/user`上获得的锁存在冲突。文件创建时不需要对父目录加写锁，因为没有目录或类似linux系统inode的数据结构需要修改，而且在文件名上的读锁就足以保护父目录不被删除。

这种锁定方案的一个优点是允许对同一个文件目录并发的修改。例如，可以对同一个目录同时创建多个文件：每个新创建的文件都获取父目录的读锁和自身文件名的写锁。在目录名称上的读锁足以防止目录被删除、重命名或者进行快照操作。文件名上的写锁可以保证两次创建操作不能同时进行。

由于文件系统中会有很多节点，读写锁对象在需要的时候才会被分配(allocated lazily)，并且一旦不使用就会被立即删除。此外，文件系统会按照默认的顺序来获取锁以防止死锁。每个操作需要获取文件和目录的锁会先在文件树中按照目录层级排序，在同一层级中按照字典序排序。

### 4.2 Chunk副本位置(Replica Placement)

一个GFS集群会在不止一个维度上高度分布部署。通常一个集群会包含数百个chunkserver，并且分布在多个机器机架上。这些chunkserver又可以被来自不同机架上的数百个client访问。不同机架上的两台机器通信可能会跨越一个或者多个网络交换机。此外，机架的进出带宽可能小于机架上机器的总带宽。多个维度的分布对数据存储的扩展性(scalability)、可靠性(reliability)和可用性(availability)提出了独特的挑战。

chunk副本的放置策略有两个目的：最大化数据的可靠性和可用性，以及最大化网络带宽的利用率。对于这两点，仅仅把chunk副本分布不同机器上是不够的，这只能防止磁盘或者机器故障带来的影响，还需要跨机房部署chunk的副本。这么做可以保证整个机房损坏或者断线（例如：网络交换机故障或者机房断电），chunk依然有一些副本可用。块机房部署也意味着chunk的流量，尤其是读取操作，可以利用多个机房的总带宽。但是缺点是，写入时需要同时写入多个机房，这也是经过考虑做出的权衡。

### 4.3 Chunk的创建、重新复制和负载均衡(Creation, Re-replication, Rebalancing)

当master为新创建的chunk选择最初的空副本的位置时，考虑了以下几个因素：

1. 系统希望将新的chunk副本放置在磁盘空间利用率低于平均水平的chunkserver上。随着时间推移，这个操作可以平衡集群中chunkserver的磁盘空间利用率。
2. 希望限制每个chunkserver上最近创建的chunk副本数量。尽管创建操作本身比较简单，但是可以预测到即将到来的大量的写入流量，因为chunk只有在写入时才需要创建，而且在系统中，大部分的chunk在创建后都是只读的。
3. 根据上一节的考虑，chunk的副本需要跨机房分布。

一旦chunk的副本数量低于用户的设置，master就会对chunk进行re-replicates。发生这种情况的原因有很多：chunkserver服务器不可用，chunkserver报告副本已经损坏，chunkserver上的某个磁盘因为错误被禁用或者用户调大了chunk副本数量设置。每个需要re-replicates的chunk需要确定执行的优先级。

- 一个因素是当前副本的数量。例如，失去两个副本的chunk比失去一个副本的chunk具有更高的优先级。
- 此外，系统会优先复制存在的文件的chunk，而不是已经删除的文件的chunk。
- 最后，为了减少chunk故障对客户端的影响，系统会提高任何阻塞客户端操作的chunk的优先级。

在需要进行re-replicates操作时，master会选择此时最高优先级的chunk，并指示某些chunkserver从该chunk当前有效的副本“clone”它。放置新副本的目标与创建副本的目标类似：均衡chunkserver的磁盘空间利用率，并且限制单个chunkserver ”clone“相关的操作，以及跨机房分布副本。为了防止“clone”操作的流量淹没client的流量，master限制了GFS集群和每个chunkserver上正在进行的“clone”操作的数量。此外，每个chunkserver通过限制对源chunkserver的读请求来限制它在克隆操作上的带宽。

最后，master会定期的rebalance chunk的分布：它会检查当前系统的chunk 副本分布情况，通过移动chunk副本位置获得更好的磁盘空间利用率和负载均衡。同样通过这个过程，master会逐渐的填充一个新的chunkserver，而不是立即用新的chunk和大量的写入流量淹没它。新的chunk副本的放置标准和上面的规则类似。在rebalance操作后，master会删除现有的chunk副本。一般来说，master会优先删除chunkserver空闲空间低于平均水平的副本，以平衡chunkserver的磁盘空间利用率。

### 4.4 垃圾收集(Garbage Collection)

在文件被删除后，GFS不会立即回收磁盘空间，而是会在常规操作中执行文件和chunk的垃圾回收操作，因为这种方式实现起来更简单，也提高的系统的可靠性。

#### 4.4.1 Mechanism

当应用程序删除文件时，master会立即在operation log中记录删除操作，但是文件资源并没有立即被回收，而是被重命名为包含删除时间戳的一个隐藏文件。在master定时扫描文件系统的namespace时，如果发现被删除的隐藏文件已经存在了3天（超时时间可以配置），就会将其删除。在被删除之前，文件可以通过新名称访问，而且可以通过重命名回正常的文件名来取消删除。当隐藏文件从namespace中被删除时，其内存中的元数据也会被删除。元数据的删除也切断了文件和chunk的联系。

在对namespace的定时扫描中，master会识别出孤立的chunk（无法从任何文件访问的chunk），并删除这些chunk的元数据。在chunkserver与master定期通信的HeratBeat消息中，chunkserver会选择其包含的一部分chunk的信息报告给master，master则回复chunkserver所有不存在于master元数据的chunk的信息，chunkserver就可以删除这些chunk的副本。

#### 4.4.2 Discussion

尽管分布式系统的垃圾收集操作是一个难点，需要在编程语言的上下文中提供复杂的解决方案，但是在GFS中却非常简单。GFS可以很容易的识别出所有chunk的引用信息：位于master专门维护的从文件到chunk的映射中。GFS还可以很容易的识别所有块的副本：它们是chunkserver上指定目录下的linux文件。master不知道的所有chunk 副本都是待回收的垃圾。

相比于立即回收文件，垃圾收集有几个优点：

1. 首先，系统组件故障在大型分布式系统中很常见，chunk的创建可能在某些服务器上成功，但是在其他服务器上可能不成功，从而留下master可能感知不到的chunk副本。chunk副本的删除消息可能会丢失，master需要感知删除操作是否成功并且在失败时重新发送。而垃圾收集提供了一种统一并且可靠的方式清理任何未知的chunk副本。
2. 其次，存储的回收操作合并到了master的常规后台活动中，例如定期的扫描文件系统namesapce空间和与chunkserver的handshake。所以对文件的回收操作时分批进行的，不会出现热点问题。而且，垃圾回收操作只在master空闲的时候才执行，master可以更快速的响应client的请求。
3. 第三，延迟的删除操作提供了防止意外和不可逆删除的安全保障。

根据经验，垃圾回收的主要缺点就是在存储不够用时，用户对文件的删除调整可能用处不大。重复创建和删除临时文件的应用程序可能无法立即重新使用这些存储空间。如果已经删除的文件再次被明确的删除，GFS会加快对文件存储空间的回收。GFS还允许用户对文件namespace中不同的部分应用不同的复制和回收策略。例如，用户可以指定某个目录下的文件所有的chunk都在没有副本的情况下存储，并且删除文件都会立即并且不可逆的从系统中删除。

### 4.5 过时chunk副本检测(Stale Replica Detection)

如果chunkserver发生故障，并且在关闭时错过了对chunk的更改，chunk的副本会变得过时(stale)。对于每个chunk，master都会维护一个版本号来区分最新的和过时的副本。

当master给chunk授予新的lease时，它都会增加chunk的版本号并且通知最新的副本。这个操作发生在任何客户端被通知之前，因此是在写入chunk操作之前。如果有一个chunk的副本当前不可用，那么它的版本号不会变化。当chunkserver重启并向master报告它上面的chunk和它们相关的版本号时，master会检测出这个chunkserver上过时的chunk副本。如果master发现chunkserver上的版本号大于它记录中的版本号，master则会认为它在授予lease时失败了，因此会将更高的版本号更新为当前版本。

master会在垃圾收集操作中删除过时的chunk副本。在删除改副本之前，在它回复client对chunk信息的请求时，master会当作这个chunk没有这个过时的副本。另一个保护措施是，master在告诉client哪个chunkserver上的chunk持有lease时，或者它指示一个chunkserver对另一个chunkserver上的chunk执行clone操作时，它会带上这个版本号。client或者chunkserver在执行操作时会验证chunk的版本号，以便始终访问最新的数据。

## 5. 容错和诊断(FAULT TOLERANCE AND DIAGNOSIS)

在设计系统时面临的难点之一就是如何处理频繁的组件故障。系统里组件的数量和质量使这些问题更为常见：不能完全的信任机器，也不能完全信任磁盘。组件的故障可能导致系统不可用，更坏的结果是数据损坏。接下来会讨论如何应对这些难点，以及在系统中内置的诊断工具，以便在出现问题的时候进行诊断。

### 5.1 高可用(High Availability)

在GFS集群中的数百台服务器中，在任意时刻都可能有一些机器不可用。可以通过两个有效的策略来保证系统的高可用性：快速恢复和备份。

#### 5.1.1 快速恢复(Fast Recovery)

master和chunkserver都被设计成无论服务在什么情况下终止，都可以在几秒中内重启并恢复。实际上，系统并不能区分正常终止和异常终止，服务器通常是通过杀死进程关闭服务。客户端和其他服务器在发送或者连接一个重启的服务器时请求会超时，然后会重试。

#### 5.1.2 chunk备份(Chunk Replication)

如前所述，每个chunk都会备份到多个不同机房的chunkserver中。用户可以根据文件的命名空间来指定不同的备份级别，默认每个chunk会备份到三个chunkserver中。master在发现chunkserver断线或者通过对chunk副本校验和检测发现数据损坏时，会从现有可用的副本中clone新的副本。

#### 5.1.3 master备份(Master Replication)

为了保证系统的可靠性，也会对master进行备份。master中的operation log和checkpoint会在多台机器上备份。只有当一个mutation的opertion log在master本地和其他副本中都刷新到磁盘中之后，才认为opertion log状态是commited。为了系统实现更简单，只有一个master进程来负责所有的mutations和后台活动，例如垃圾收集。当master进程挂掉后，几乎可以立即重新启动。如果master的机器或者磁盘出现故障，GFS的外部监控程序会在master的备份机器上重新启动一个master进程。client在连接master时只使用master的DNS别名（例如gfs-test），在master在另一台机器上启动后可以修改DNS映射。

此外，master的“shadow”机器是只读的，即便primary master已经关掉。这些副本机器是“shadows”，不是“mirrors”，它们相对于primary master会滞后，通常是几分之一秒。它们增强了那些没有变更的文件或者对文件的实效性没有强制性的应用程序的读取效率。实际上，文件内容是从chuknserver中读取的，应用程序并不会读取到过时的内容。在短时间内过期的内容可能是文件的元数据，例如文件目录内容或者访问控制信息。

shadow master为了保持最新，它会读取operation log的副本，使用和primary master相同的顺序来更改其数据结构。与primary master一样，它也在启动时轮询chunkserver服务器并通过 handshake消息来监控它们的状态。chunk primary的创建，以及chunk副本的创建和删除都由primary master决定。

### 5.2 数据完整性(Data Integrity)

每个chunkserver都通过校验和来检测存储数据是否损坏。GFS集群通常有几百台服务器，几千个磁盘，它会经常遇到磁盘故障导致磁盘中的数据损坏或者丢失。这种情况可以通过chunk的其他副本来恢复，但是通过不同的chunkserver上的数据来检测chunk副本是否损坏不太可行。不同副本间数据可能会不同，但都是有效的：GFS mutation的语义，尤其是record append操作，并不保证chunk副本间的数据完全相同。因此，每个chunkserver必须通过维护校验和来验证自身chunk副本的数据完整性。

一个chunk会被拆分成64KB的block，每个block都有一个32位的校验和。与其他元数据一样，校验和保存在内存中，通过日志记录，与用户数据分开存储。

在数据读取时，chunkserver在把数据返回之前，都会验证与读取范围重叠的block的校验和，无论是client还是另一个chunkserver上的请求。因此，chunkserver并不会把损坏的数据传播到其他机器。如果一个block的校验和与记录的不匹配，chunkserver在请求中返回错误，并且会将不匹配的情况报告给master。请求方将会从其他副本中读取数据，master则会从另一个副本clone chunk的数据。在一个新的有效的chunk副本就绪后，master指示报告不匹配的chunkserver删除 chunk的副本。

校验和对读取性能几乎没有影响。大部分的读取请求都会跨越多个chunk，因此只需要读取少量的额外数据计算校验和来验证。GFS的客户端代码会尝试在对齐校验和的block边界，进一步减少了额外开销。此外，chunkserver上校验和的查找和比较是在没有任何I/O的情况下进行的，并且校验和的验证过程通常可以和I/O操作并行执行。

校验和针对附加到chunk末尾的写入进行了高度优化，因为大部分写入操作都是追加写入。GFS只是增量的更新最后最后一个block的校验和，并计算追加写入的block的校验和。即使当前chunk的最后一个block的校验和已经损坏，并且当前无法检测出，但是新计算的校验和也不会与存储的数据匹配，在下一次读取block中的数据时也会检测出校验和不匹配的问题。

相反，如果写入覆盖了chunk的已有的数据，我们必须先读取并验证写入数据覆盖的第一个block和最后一个block的校验和。如果不验证的话，又可能第一个block和最后一个block数据已经损坏，直接重新计算校验和可能会隐藏这个错误。

在chunkserver空闲期间会扫描和验证非活跃的chunk的内容，这样可以让我们检测到那些很少被读取的chunk的数据损坏的情况。一旦检测到数据损坏，master就会创建一个新的副本，并且删除损坏的副本。这么做可以防止那些很少用但是已经损坏的chunk副本欺骗master，让master误以为这些chunk当前有足够可用的副本。

### 5.3 诊断工具(Diagnostic Tools)

详细的诊断日志在问题检测、调试和性能分析方面提供了极大的帮助，同时并没有花费太多成本。没有日志的话，就很难理解机器之前短暂、不能复现的交互操作。GFS服务器会生成诊断日志，记录很多重要的事件（例如chunkserver的启动和关闭）和所有RPC的请求和回复。这些诊断日志可以随意删除，并且不影响系统的正确性。但是会尽量在空间允许的范围内保留这些日志。

RPC日志包含了详细的请求和响应信息（读取和写入的文件数据除外）。通过匹配请求和回复，以及整理不同机器上的RPC请求日志，就可以重现请求完整的交互历史来诊断问题。日志还会用作负载测试和性能分析。

记录日志对系统的性能影响很小，因为日志都是顺序异步写入的。最近的相关事件也会保存在内存中，可用于连续在线监控。



























