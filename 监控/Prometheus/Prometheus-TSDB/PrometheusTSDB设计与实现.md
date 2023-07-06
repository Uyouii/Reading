# Prometheus简介

Prometheus是一个开源的监控报警工具, 在2016年继Kubernetes之后成为第二个正式加入CNCF基金会( [Cloud Native Computing Foundation](https://cncf.io/))的项目。

Prometheus存储时间序列数据(time series data), 包括数据指标(metrics), 时间戳(timesamp)和标签(label, optional key-value pairs)。

TSDB的全称就是Time Series Database，即时间序列数据库。

## 主要特性

- 支持通过metric name和 key/value pairs 来定义基于时间序列的多维[数据模型](https://prometheus.io/docs/concepts/data_model/)。
- 支持通过[PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/)灵活查询各个维度的数据。
- 不依赖分布式存储，单个服务节点是自治的(autonomous)。
- 基于HTTP协议和pull模型来收集时间序列数据。
- 支持通过[中间网关](https://prometheus.io/docs/instrumenting/pushing/)来推送数据。
- 支持通过服务发现(service discovery)或者静态配置管理监控目标。
- 支持多种形式的图形和监控表盘，最新的Grafana可视化工具也已经提供了完整的Prometheus支持。

## 组成

prometheus监控系统由多个可选的部分组成：

- 收集和存储时间序列数据的[Prometheus server](https://github.com/prometheus/prometheus)
- [客户端库](https://prometheus.io/docs/instrumenting/clientlibs/)
- 对于短期存在的服务，支持通过[推送网关](https://github.com/prometheus/pushgateway)收集数据
- 对于特定的服务（例如mysql，redis等）有专用的[exporters](https://prometheus.io/docs/instrumenting/exporters/)支持
- [alertmanager](https://github.com/prometheus/alertmanager)用来处理告警

Prometheus大部分组件都是通过Go语言编写，方便构建和部署。

## 架构

![prometheus01](https://github.com/Uyouii/BookReading/blob/master/images/prometheus/prometheus01.png?raw=true)

Promethues直接从监控目标或者Pushgateway中获取metrics数据。它会把抓取的数据存在本地时间序列数据库(TSDB)中，并且判断是否要生成告警信息。[Grafana](https://grafana.com/)或者其他API可以通过PromQL获取监控数据。

更多使用信息可以到[官网](https://prometheus.io/docs/introduction/overview/)查看。

# 时间序列数据

时间序列数据是由时间戳和值组成的元组(tuple)。时间戳是一个整数，值则是一个64位的浮点数。

时间序列随时间戳严格单调递增，通过mertic name和一组label(key value pairs)进行标识。

时间序列数据中每个样本(sample)都由三个部分组成：

1. 指标(metric)：metric name和描述当前样本特征的label sets;
2. 时间戳(timestamp)：一个精确到毫秒的时间戳;
3. 样本值(value)： 一个float64的浮点型数据表示当前样本的值。

在形式上，所有的指标(Metric)都通过如下格式标示：

```sh
<metric name>{<label name>=<label value>, ...}
```

例如下面的请求：

```sh
requests_total{path="/status", method="GET", instance=”10.0.0.1:80”}
requests_total{path="/status", method="POST", instance=”10.0.0.3:80”}
requests_total{path="/", method="GET", instance=”10.0.0.2:80”}
```

`requests_total`就是metric name，加上三个label(path, method, instance) 来标识不同的时间序列。

- 指标的名称(metric name)可以反映被监控样本的含义（比如，`http_request_total` - 表示当前系统接收到的HTTP请求总量）。指标名称只能由ASCII字符、数字、下划线以及冒号组成并必须符合正则表达式`[a-zA-Z_:][a-zA-Z0-9_:]*`。
- 标签(label)反映了当前样本的特征维度，通过这些维度Prometheus可以对样本数据进行过滤，聚合等。标签的名称只能由ASCII字符、数字以及下划线组成并满足正则表达式`[a-zA-Z_][a-zA-Z0-9_]*`。
- 其中以`__`作为前缀的标签，是系统保留的关键字，只能在系统内部使用。标签的值则可以包含任何Unicode编码的字符。在Prometheus的底层实现中指标名称实际上是以`__name__=<metric name>`的形式保存在数据库中的，因此以下两种方式均表示的同一条time-series：

```sh
api_http_requests_total{method="POST", handler="/messages"}
```

等同于：

```sh
{__name__="api_http_requests_total"，method="POST", handler="/messages"}
```

# TSDB

Promethues监控系统通过在本地实现TSDB来保存收集到的监控数据。

首先看一下TSDB在文件中的目录结构：

```sh
$ tree data
data
├── 01EM6Q6A1YPX4G9TEB20J22B2R
|   ├── chunks
|   |   ├── 000001
|   |   └── 000002
|   ├── index
|   ├── meta.json
|   └── tombstones
├── 01GTXMSC2WGMPZWGZKE1A7N0XP
│   ├── chunks
│   │   └── 000001
│   ├── index
│   ├── meta.json
│   └── tombstones
├── chunks_head
|   ├── 000001
|   └── 000002
└── wal
    ├── checkpoint.000003
    |   ├── 000000
    |   └── 000001
    ├── 000004
    └── 000005
```

TSDB由若干个`Block`(`01EM6Q6A1YPX4G9TEB20J22B2R` 就是一个Block), `chunks_head`(当前正在追加写入的Block) 和 `wal`(write ahead log)组成。

TSDB数据概览：

![image](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb1-9dce57fbe455a6163a84d68c9c73c7dd.svg)

Block就是存储数据的“块”（上图中灰色的部分），TSDB会包含很多个这样的Block。磁盘上保存的`Block`都是不变的，每个Block都是一个单独的数据库，包含自己的索引和元数据(meta.json)，接下来会详细介绍。

TSDB中唯一会变化的数据就是`chunks_head`（对应上图中的Head)，TSDB会通过mmap把`chunks_head`映射到内存中，并将当前收集到的时间序列数据写入`chunks_head`中，并且定期的将`chunks_head`中的数据保存到磁盘生成新的Block，保存在磁盘上的Block不会再写入新的样本数据。

随着数据库中数据的增加，TSDB会定期的合并多个Block减少数据库中的文件数量，提升查询的效率。

接下来会通过以下几个部分介绍TSDB的实现：

1. Head Block 和 mmap内存映射。
2. wal(write ahead log)和check point。
3. Block的存储逻辑和在磁盘上的架构。
4. Block的合并逻辑。
5. 数据的查询流程。

## Head Block

Head Block是TSDB内存中的部分。样本数据首先会写入到Head Block中，Head Block会定时将数据写入磁盘中并生成新的Block。

### Sample在Head Block中的流程

![tsdb2-3e96b764cc0a7e28988714462be15b02](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb2-3e96b764cc0a7e28988714462be15b02.svg)

Head Block会包含若干个`Chunk`, Sample会存储在Chunk中。Head Block中只会有一个活跃的Chunk（上图中红色的Chunk），这是TSDB中唯一写入Sample的地方。当把Sample被写入到Chunk前，TSDB会预写WAL(write ahead log)来保证数据的持久性。（程序崩溃或者服务器宕机重启时可以通过预写日志恢复内存中的数据）。

![tsdb3-fcc2a659bb9dc466f2ad51278b9ef940](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb3-fcc2a659bb9dc466f2ad51278b9ef940.svg)

Prometheus默认每个Chunk跨度是120个Samples，Sample的间隔是15s，所以每个Chunk的跨度是30min，此时这个Chunk被视为full。每当Chunk满了后，就会产生一个新块。

![tsdb4-5db3bd1d5402bab9a0804723ad2c79aa](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb4-5db3bd1d5402bab9a0804723ad2c79aa.svg)

每当切割出一个新的Chunk，旧Chunk就会被刷新到磁盘，并且使用mmap对其进行内存映射，同时在内存中只存储下对这个Chunk的引用。通过mmap可以在访问时将其动态地加载到内存中（操作系统提供的功能，缺页中断)。

![tsdb5-1d622e6852dde75dd1dbf97fa930dacf](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb5-1d622e6852dde75dd1dbf97fa930dacf.svg)

随着时间推移，新的Chunk会不断生成并存储在文件中。

![tsdb8-2143f3ae9296366a5998fb78ee2320d1](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb8-2143f3ae9296366a5998fb78ee2320d1.svg)

Prometheus默认2h为一个Block的跨度，被称为`chunkRange`。一段时间过后，Head Block如上图所示，此时磁盘中有5个已满的块，内存中的Chunk也基本已满。此时Head Block中有6个chunk，每个chunk跨度30min，所以head中有3h的数据。达到了`chunkRange*3/2`。

![tsdb9-73e001cb1662df81b619a2bafc33351d](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb9-73e001cb1662df81b619a2bafc33351d.svg)

当Head Block中的数据跨越`chunkRange*3/2`时，前`chunkRange`的的数据（默认为2h）被压缩为一个持久Block。此时，WAL也被截断，并且会创建一个新的`checkpoint`(后续会介绍)。

这个过程会随着时间推移不断进行，持久化的Block会不断产生。

### 磁盘上存储格式

#### 文件

Head Block中的块位于`chunks_head`目录下，单个chunk文件由从1开始的单调递增的序列号命名。

```sh
data
├── chunks_head
|   ├── 000001
|   └── 000002
└── wal
    ├── checkpoint.000003
    |   ├── 000000
    |   └── 000001
    ├── 000004
    └── 000005
```

单个文件的最大大小为128M。每个文件都包含一个8字节的Header。每个文件都包含一系列Chunk，这些Chunk通过一个uint64的索引访问，这个索引由4字节的文件内偏移（低字节）+4字节的文件序列号（高字节）组成。

```sh
┌──────────────────────────────┐
│  magic(0x0130BC91) <4 byte>  │
├──────────────────────────────┤
│    version(1) <1 byte>       │
├──────────────────────────────┤
│    padding(0) <3 byte>       │
├──────────────────────────────┤
│ ┌──────────────────────────┐ │
│ │         Chunk 1          │ │
│ ├──────────────────────────┤ │
│ │          ...             │ │
│ ├──────────────────────────┤ │
│ │         Chunk N          │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

`magic`是一个魔数，用来标识这个文件是mmap的Head Chunk类型的文件（作者用自己的生日做的魔数）。`version`用来标识如何解码改文件。`padding`是预留的三个字节的空间。

#### Chunks

Head Block文件中单个Chunk的格式如下:

```sh
┌─────────────────────┬───────────────────────┬───────────────────────┬───────────────────┬───────────────┬──────────────┬────────────────┐
| series ref <8 byte> | mint <8 byte, uint64> | maxt <8 byte, uint64> | encoding <1 byte> | len <uvarint> | data <bytes> │ CRC32 <4 byte> │
└─────────────────────┴───────────────────────┴───────────────────────┴───────────────────┴───────────────┴──────────────┴────────────────┘
```

- `series ref`: series(metric name + label set代表一个series)的id，标识该Chunk属于哪个series。
- `mint`和`maxt`是这个Chunk中样本开始和结束的毫秒时间戳。
- `encoding`是压缩Chunk的编码。
- `len`是`data`的长度。
- `data`是压缩后Chunk的数据。
- `CRC32`是上述数据的校验和。

Head Block中Chunk的存储格式和磁盘中Block Chunk的存储格式不同，相比于后者多了`series ref`,`mint`和`maxt`（后续会讲到磁盘中的Chunk格式）。这是因为Head Block并没有像磁盘中Block一样建立索引，所以需要额外存储这些信息。在通过`wal`恢复数据时为这些Chunk在内存中建立索引。

### 读取Head Block Chunk中的数据

对于每个Chunk，Head Block会通过内存中存储 mint、maxt和一个索引访问它。

内存中索引的长度是8个字节，其中前4个字节是Chunk所在的文件编号，后4个字节是改Chunk在文件中的偏移量。例如如果一个Chunk在文件`0093`中，并且改Chunk在文件中的启始位置是1234，这个Chunk的索引就是`(93 << 32) | 1234`。

通过存储mint和maxt在内存中，访问Head Block中的块时就无需访问磁盘中的文件。当需要查看Chunk中的数据时，直接根据索引找到磁盘中文件的位置访问数据。

同时通过mmap的方式（操作系统提供的一个特性），当需要访问文件时，操作系统只会将磁盘中的一部分加载到内存中，而不是整个文件。

### 垃圾回收

Head Block会定期地截断数据，并把持久化的Block存储在磁盘中。在Head Block截断时，TSDB会把截断出的Chunk在内存中的数据删除。

TSDB会在内存中会为每个文件维护一个当前数据的最大时间。当时间T之前的数据发生截断时，最大时间低于T的文件在内存中的数据会被删除。文件的删除会保证序列号的连续性（例如如果文件5 6 7 8中，文件 5 和 7最大时间低于时间T，只有文件5被删除，会保留下序列 6 7 8）。

在截断发生后，TSDB会关闭当前的mmap文件并启动一个新文件。

## WAL

WAL即write ahead log，即在进行数据库修改操作前，会首先将时间记录在log中，然后才在数据库中执行必要的操作。

当机器或者程序发生故障或者崩溃时，可以根据WAL中的记录重放在内存中还未持久化到磁盘中的数据，以防止数据库中内存中的数据丢失。在关系型数据库中，wal用来保证ACID中的D，也就是持久性(durability)。Prometheus也通过WAL来保证Head Block中数据的持久性。

在Promethues中，WAL仅用于在启动时恢复内存中的数据状态。

### TSDB中WAL格式

#### 类型

在TSDB的写请求中，主要包括[series](https://prometheus.io/docs/concepts/data_model/)的label set和它们关联的samples。所以在WAL中，数据主要有两种类型：`Series`和`Samples`。

`Series`记录包含了写请求中series所有的label。在创建`Series`时，会为其在内存中创建一个唯一的索引。`Samples`记录则会包含其对应的`Series`的索引。

还有一种类型是`Tombstones`，用于删除请求。主要包含两个部分，对应的`series`信息和一个时间范围。

WAL具体的格式和在磁盘中的存储可以在github中的[文档](https://github.com/prometheus/prometheus/blob/main/tsdb/docs/format/wal.md)查看。

#### 写入流程

每当写入请求来临时，请求中的sample都会在WAL中新增`Sample`记录，但是`Series`记录只会在第一次遇到对应的series时才会写入。当一个写入请求包含一个新的series时，`Series`记录会先于`Sample`记录写入，以便于通过WAL恢复数据时，所有的`Sample`记录都可以找到其对应的`Series`记录。

`Series`记录会在写入WAL前，先在Head Block中创建对应的索引，便于在记录中存储下对应索引。`Sample`记录则会先写入到WAL，随后添加到Head Block中。TSDB会将不同的series中的数据分组到一起。如果series已经存在于Head Block中，则只将sample记录到WAL。

Prometheus采用惰性删除的方式。当收到删除请求时，并不会直接删除内存中的数据，而是存储下`tombstones`，其中记录了需要删除记录的series和时间范围。tombstone请求同样是先写入WAL，再处理请求。

#### 磁盘中的文件

默认wal中的文件以单调递增的序列号命名，每个文件的默认上限大小为128M。

```sh
data
└── wal
    ├── 000000
    ├── 000001
    └── 000002
```

### WAL截断和Checkpointing

旧的WAL文件需要定期删除。如果不删除的话，无限增长的WAL文件最终会填满磁盘，其次，过大的WAL文件也会影响Prometheus Server的启动速度（重启时WAL中的事件需要重放以便恢复内存中的数据）。

#### WAL 截断(truncation)

WAL 截断 在Head Block 截断之后执行。写入请求的时间顺序可能是随机的，在不遍历WAL所有数据的前提下，并不能高效的确定WAL样本中的时间范围，所以每次WAL截断都会删除前2/3个文件（类似于Head Block 截断）。

```sh
data
└── wal
    ├── 000000
    ├── 000001
    ├── 000002
    ├── 000003
    ├── 000004
    └── 000005
```

例如上面的例子，在WAL 截断发生时， `000000` `000001` `000002` `000003` 文件会被删除。

这里有个问题，盲目的删除WAL文件可能会造成内存中数据对应的WAL记录丢失，TSDB为WAL引入了check point来解决这个问题。

#### Checkpointing

在WAL 截断操作前，需要为即将被删除的WAL文件创建一个checkpoint。可以理解为checkpoint就是被“过滤”的WAL文件。

例如时间点**T**之前的数据需要截断，根据上述的例子，Checkpointing操作需要依次遍历 `000000` `000001` `000002` `000003` 文件中的数据：

1. 丢弃所有的不在Head Block中的`Series`记录。
2. 丢弃所有的时间点T之前的`Sample`记录。
3. 丢弃所有的时间点T之前的`Tombstone`记录。
4. 保留按照和之前WAL文件一样的顺序保留剩下的`Series`、`Sample`和`Tombstone`记录。

通过Checkpointing操作就不会丢失目前仍在Head Block中的数据。checkpoint会以 `checkpoint.X` 的方式命令，`X`就是被截断的最后一个WAL文件的编号。（例如上述文件序列，X就是`000003`)

在经过WAL截断和Checkpointing操作之后，磁盘上的文件：

```sh
data
└── wal
    ├── checkpoint.000003
    |   ├── 000000
    |   └── 000001
    ├── 000004
    └── 000005
```

在进行`Checkpointing`操作之后，旧的`checkpint`文件也会被删除。

### 从WAL中恢复

在恢复数据时，首先从最后一个Checkpoint开始遍历记录。之后，会根据Checkpoint的编号来选择继续遍历的WAL文件。例如在上面的例子中，在重新执行 checkpoint.000003之后，我们从WAL 文件000004继续执行。

> 为什么需要在checkpoint中记录编号：因为checkpoint的创建操作和WAL的删除操作不是原子的，所以有可能出现checkpint成功创建但是旧的WAL文件没有删除的情况，所以根据checkpint编号来确定下一个需要执行的WAL文件。

对于具体的记录需要执行的操作：

- `Series`：对于series记录，会在内存中创建对应的记录以及索引。同一个`Series`数据在WAL文件中可能会包含多个记录。
- `Sample`：对于sample记录，需要添加到Head Block数据中。Sample记录中的series id用来判断该Sample属于哪个series。如果找不到对应的series，该sample记录则会被忽略。
-  `Tombstone`：类似于Sample将TombStone重新添加到Head Block数据中。

在数据恢复时，对于Head Block中在磁盘上已满的Chunk其实并不需要恢复，真正需要恢复的是仍在在写入的未满的Chunk。所以在启动时，TSDB会先遍历`chunks_head`中的所有的块，并在内存中构建`series ref -> [list of chunk references along with mint and maxt belonging to this series ref]` map。

所以当遇到`Series`记录时，会在上面的map中查找该series。如果存在，则将该series和上述的chunk 列表进行关联。当遇到sample记录时，如果其对应的series在上述map中存在对应的chunk列表，并且其时间戳被包含在上述chunk的时间范围中（表明该sample已经包含在已满的chunk中，不需要被恢复），就跳过该sample。

## 持久化的Block

磁盘上的Block是由一些列Chunks和它自身的索引组成，可以把每个Block理解为一个小型数据库。每个Block是一个文件目录，包含了多个文件。每个Block由一个UUID标识，通过 [Universally Unique Lexicographically Sortable Identifier (ULID)](https://github.com/oklog/ulid)生成。

持久化Block中的数据都是不可变的，如果需要更新、添加或者删除操作，就必须重写整个Block，并且重写的Block会有一个新的ID，和旧的Block没有关联。

在Head Block的实现中，当Head Block中包含了`chunkRange*3/2`时间范围的数据时，会将前`chunkRange`范围的数据转化为持久化的Block。

![tsdb8-2143f3ae9296366a5998fb78ee2320d1](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb8-2143f3ae9296366a5998fb78ee2320d1.svg)



![tsdb9-73e001cb1662df81b619a2bafc33351d](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb9-73e001cb1662df81b619a2bafc33351d.svg)



`chunkRange`也可以成为`BlockRange`，在Promethues中，从Head中截断出的Block默认跨度时2h。

![image](https://raw.githubusercontent.com/Uyouii/BookReading/master/images/prometheus/tsdb1-9dce57fbe455a6163a84d68c9c73c7dd.svg)

随着Block不断增多，多个Block会被压缩成一个新的Block，同时删除旧的Block。所以新的Block有两种生成方式，从Head Block中截断，或者从已有的Block中合并。

### Block中的内容

Block包含了4个部分：

1. `meta.json` (file): Block的元数据信息。
2. `chunks` (directory): 该目录包含了Chunk文件数据。
3. `index` (file): Block的索引文件。
4. `tombstones` (file): 删除标记，在Block合并或者查询去用于排除数据。

已 `01EM6Q6A1YPX4G9TEB20J22B2R` block ID为例：

```sh
data
├── 01EM6Q6A1YPX4G9TEB20J22B2R
|   ├── chunks
|   |   ├── 000001
|   |   └── 000002
|   ├── index
|   ├── meta.json
|   └── tombstones
├── chunks_head
|   ├── 000001
|   └── 000002
└── wal
    ├── checkpoint.000003
    |   ├── 000000
    |   └── 000001
    ├── 000004
    └── 000005
```

接下来分别看下这些文件具体的内容以及实现。 

### meta.json

meta.json基本包含了Block中需要的所有元数据信息，例如：

```sh
{
    "ulid": "01EM6Q6A1YPX4G9TEB20J22B2R",
    "minTime": 1602237600000,
    "maxTime": 1602244800000,
    "stats": {
        "numSamples": 553673232,
        "numSeries": 1346066,
        "numChunks": 4440437
    },
    "compaction": {
        "level": 1,
        "sources": [
            "01EM65SHSX4VARXBBHBF0M0FDS",
            "01EM6GAJSYWSQQRDY782EA5ZPN"
        ]
    },
    "version": 1
}
```

- `version` 用来标记如何解析meta文件。
- `ulid`: 虽然Block文件目录名也被设置为ULID，但是真正使用的是 `meta.json` 中`ulid`的信息，文件目录名可以是任意的
- `minTime` and `maxTime` 是Block中所有的Chunk的时间戳的跨度范围。
- `stats` 用来表明Block包含的series、samples和chunks的数量。
- `compaction`用来标记该Block的历史数据：
  - `level` 表明该Block合并的层级level。
  - `sources`表明该Block是从哪些Block中创建的 (比如从哪些Block合并来的)。如果该Block从Head Block中创建而来，那么sources会指向它自身。

### Chunks

`chunks`文件夹下也包含了一组通过递增序列号命名的文件。每个文件的上限大小是512MB。下面是这些文件在磁盘中的格式：

```sh
┌──────────────────────────────┐
│  magic(0x85BD40DD) <4 byte>  │
├──────────────────────────────┤
│    version(1) <1 byte>       │
├──────────────────────────────┤
│    padding(0) <3 byte>       │
├──────────────────────────────┤
│ ┌──────────────────────────┐ │
│ │         Chunk 1          │ │
│ ├──────────────────────────┤ │
│ │          ...             │ │
│ ├──────────────────────────┤ │
│ │         Chunk N          │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

文件格式和Head Block中的Chunk格式非常像。`magic`表明这个文件是一个Chunk文件。`version`用来标记如何解析该文件。`padding`用来字节对齐和为以后预留空间。接下来包含了一组Chunks数据。

下面是每个Chunk的格式：

```sh
┌───────────────┬───────────────────┬──────────────┬────────────────┐
│ len <uvarint> │ encoding <1 byte> │ data <bytes> │ CRC32 <4 byte> │
└───────────────┴───────────────────┴──────────────┴────────────────┘
```

同样和Head Block中Chunk的格式非常像，不同的是不包含`series ref`、 `mint` 和 `maxt`。Head Block中需要在重启时利用这些信息在内存中建立索引。但是持久化Block在索引中已经包含了这些信息，所以不需要在Chunk数据中额外添加`series ref`、 `mint` 和 `maxt`字段。

需要访问Chunk中的字段数据时，需要利用Chunk的索引ID。索引的长度是8个字节，其中前4个字节是Chunk所在的文件编号，后4个字节是改Chunk在文件中的偏移量。例如如果一个Chunk在文件`00093中`，并且改Chunk在文件中的启始位置是1234，这个Chunk的索引就是`(92 << 32) | 1234`。虽然文件的命名重1开始，但是块的索引从0开始。所以在计算索引时`00093`被转化为92。

具体的Block中的内容可以参考Github中的[文档](https://github.com/prometheus/prometheus/blob/main/tsdb/docs/format/chunks.md)。

### Index

Index就是查询Block中数据的索引。TSDB中的索引使用的是"inverted index"(倒排索引)。

下面是索引文件的整体布局：

 ```sh
 ┌────────────────────────────┬─────────────────────┐
 │ magic(0xBAAAD700) <4b>     │ version(1) <1 byte> │
 ├────────────────────────────┴─────────────────────┤
 │ ┌──────────────────────────────────────────────┐ │
 │ │                 Symbol Table                 │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                    Series                    │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                 Label Index 1                │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                      ...                     │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                 Label Index N                │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                   Postings 1                 │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                      ...                     │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                   Postings N                 │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │              Label Offset Table              │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │             Postings Offset Table            │ │
 │ ├──────────────────────────────────────────────┤ │
 │ │                      TOC                     │ │
 │ └──────────────────────────────────────────────┘ │
 └──────────────────────────────────────────────────┘
 ```

同样通过一个`magic`开头，来表明该文件是索引文件。`version`表明以何种格式来解析该文件。

索引文件的入口位置是`TOC`（Table of Contents），即目录。所以先从TOC开始介绍。

#### TOC

```sh
┌─────────────────────────────────────────┐
│ ref(symbols) <8b>                       │ -> Symbol Table
├─────────────────────────────────────────┤
│ ref(series) <8b>                        │ -> Series
├─────────────────────────────────────────┤
│ ref(label indices start) <8b>           │ -> Label Index 1
├─────────────────────────────────────────┤
│ ref(label offset table) <8b>            │ -> Label Offset Table
├─────────────────────────────────────────┤
│ ref(postings start) <8b>                │ -> Postings 1
├─────────────────────────────────────────┤
│ ref(postings offset table) <8b>         │ -> Postings Offset Table
├─────────────────────────────────────────┤
│ CRC32 <4b>                              │
└─────────────────────────────────────────┘
```

`TOC`标识了索引文件中各个部分的位置，即文件中的字节偏移量。如果在`TOC`中索引的值为0，表明对应的内容在索引中不存在。

由于`TOC`是固定大小的，所以可以将文件的最后52个字节作为TOC。

索引中每个组件都会由一个校验和结束，即CRC32，用于检查数据的完整性。

#### Symbol Table

符号表，这个部分包含了在Block中所有series包含label字符串的信息。例如一个series`{a="y", x="b"}`，对应的symbol包括 `"a", "b", "x", "y"`。

 ```sh
 ┌────────────────────┬─────────────────────┐
 │ len <4b>           │ #symbols <4b>       │
 ├────────────────────┴─────────────────────┤
 │ ┌──────────────────────┬───────────────┐ │
 │ │ len(str_1) <uvarint> │ str_1 <bytes> │ │
 │ ├──────────────────────┴───────────────┤ │
 │ │                . . .                 │ │
 │ ├──────────────────────┬───────────────┤ │
 │ │ len(str_n) <uvarint> │ str_n <bytes> │ │
 │ └──────────────────────┴───────────────┘ │
 ├──────────────────────────────────────────┤
 │ CRC32 <4b>                               │
 └──────────────────────────────────────────┘
 ```

 `len <4b>` 是该部分所占的字节数。 `#symbols`是该部分包含的symbol的数量。随后包含了 `#symbols`个`utf-8`编码的字符串。每个字符串都有一个长度前缀。

索引中的其他部分都可以引用符号表中的内容，而不是直接使用原始字符串来减少索引的大小。symbol的引用即为其在索引文件中的偏移量。

#### Series

这个部分包含了Block中所有的series信息，通过series中的lable set的字典序排序。

```sh
┌───────────────────────────────────────┐
│ ┌───────────────────────────────────┐ │
│ │   series_1                        │ │
│ ├───────────────────────────────────┤ │
│ │                 . . .             │ │
│ ├───────────────────────────────────┤ │
│ │   series_n                        │ │
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘
```

每个Series项都是16字节对齐的，也就是说每个Series开始的位置都可以被16字节整除。所以Series ID可以设置为`offset/ 16`。当需要获取Series信息时，可以通过`Series ID * 16`获取其在索引文件中的位置。

因为Series是按照字典序排序的，所以ID的顺序也就代表了Series的顺序。

我们可以看到索引中包含了N个Posting，每个Posting就可以认为代表了一个Series。（不知道为啥起名叫Posting）。

每个Series中都包含了其所有的label信息和其所有Chunk的引用。

```sh
┌──────────────────────────────────────────────────────┐
│ len <uvarint>                                        │
├──────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────┐ │
│ │            labels count <uvarint64>              │ │
│ ├──────────────────────────────────────────────────┤ │
│ │  ┌────────────────────────────────────────────┐  │ │
│ │  │ ref(l_i.name) <uvarint32>                  │  │ │
│ │  ├────────────────────────────────────────────┤  │ │
│ │  │ ref(l_i.value) <uvarint32>                 │  │ │
│ │  └────────────────────────────────────────────┘  │ │
│ │                       ...                        │ │
│ ├──────────────────────────────────────────────────┤ │
│ │            chunks count <uvarint64>              │ │
│ ├──────────────────────────────────────────────────┤ │
│ │  ┌────────────────────────────────────────────┐  │ │
│ │  │ c_0.mint <varint64>                        │  │ │
│ │  ├────────────────────────────────────────────┤  │ │
│ │  │ c_0.maxt - c_0.mint <uvarint64>            │  │ │
│ │  ├────────────────────────────────────────────┤  │ │
│ │  │ ref(c_0.data) <uvarint64>                  │  │ │
│ │  └────────────────────────────────────────────┘  │ │
│ │  ┌────────────────────────────────────────────┐  │ │
│ │  │ c_i.mint - c_i-1.maxt <uvarint64>          │  │ │
│ │  ├────────────────────────────────────────────┤  │ │
│ │  │ c_i.maxt - c_i.mint <uvarint64>            │  │ │
│ │  ├────────────────────────────────────────────┤  │ │
│ │  │ ref(c_i.data) - ref(c_i-1.data) <varint64> │  │ │
│ │  └────────────────────────────────────────────┘  │ │
│ │                       ...                        │ │
│ └──────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────┤
│ CRC32 <4b>                                           │
└──────────────────────────────────────────────────────┘
```

起始长度`len`和结束为止的`CRC32`和其他部分相同。`labels count`表明该Series包含的label数量，接下来存的标签的键值对。可以注意到这里存储的是符号表中的引用，而不是直接存储字符串信息。键值对同样通过字典序排序。

接下来是`chunks count`，表明该Series对应Chunk的数量。随后每个部分包含了其Chunk的`mint`(起始时间)，`maxt`(结束时间)，以及`ref`(Chunk的索引)，通过`mint`来排序。可以注意到，这里存储的时间戳和chunk 索引通过使用差值存储(当前块的`mint` - 上一个块的`maxt`），来减少索引文件占用的大小。

这里通过在索引中存储`mint`和`maxt`来查找时间范围所对应的Chunk文件位置。

#### `Label Offset Table` and `Label Index i`

两个部分在已经不在使用了，为了向后兼容而实现，在最新的Promethues中并不会使用。这里就不展开叙述了。

#### `Postings Offset Table` and `Postings i`

每个`Postings i`包含了一个Postings列表。`Posting Offset Table`是存储了通过一个label来对应的`Postings i`，也就是Postings的列表。（这里的Posting就是前面说的Series）。

这个部分主要是想存储下每个`label`所对应的Sereis有哪些。所以`Postings i `就是一个Series的引用列表，`Postings Offset Table`可以理解为是`label`->`posting i`，也就是`label`->`series list`的映射，类似于倒排索引。

##### **`Postings i`**

每个`Postings i`包含了一个有序的series列表。可以看下如下示例：

```sh
┌────────────────────┬────────────────────┐
│ len <4b>           │ #entries <4b>      │
├────────────────────┴────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ ref(series_1) <4b>                  │ │
│ ├─────────────────────────────────────┤ │
│ │ ...                                 │ │
│ ├─────────────────────────────────────┤ │
│ │ ref(series_n) <4b>                  │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ CRC32 <4b>                              │
└─────────────────────────────────────────┘
```

同样是以len开头和CRC32结尾，`#entries`代表了其对应的series数量。接下来是一个series的索引列表，对应上述`Series`部分的索引值。

举个例子，`{a="b", x="y1"}` 的 series ID是 `120`, `{a="b", x="y2"}` 的 series ID是 `145`。 `a="b"` 同时包含在两个series中，所以会对应series列表`[120,145]`。对于`x="y1"`和`x="y2"`分别只存在于一个series，所以它们分别对应列表`[120]`和`[145]`。

##### **`Postings Offset Table`**

 `Postings Offset Table` 中记录了一个key-value的`label`到`Postings i`的映射关系。

```sh
┌─────────────────────┬──────────────────────┐
│ len <4b>            │ #entries <4b>        │
├─────────────────────┴──────────────────────┤
│ ┌────────────────────────────────────────┐ │
│ │  n = 2 <1b>                            │ │
│ ├──────────────────────┬─────────────────┤ │
│ │ len(name) <uvarint>  │ name <bytes>    │ │
│ ├──────────────────────┼─────────────────┤ │
│ │ len(value) <uvarint> │ value <bytes>   │ │
│ ├──────────────────────┴─────────────────┤ │
│ │  offset <uvarint64>                    │ │
│ └────────────────────────────────────────┘ │
│                    . . .                   │
├────────────────────────────────────────────┤
│  CRC32 <4b>                                │
└────────────────────────────────────────────┘
```

`len`和`CRC32`同之前一样。`#entries`表明了该部分包含了多少项数据。`n`的值恒等于2，代表了接下来字符串的数量（label name 和label value)。这里预留了`n`便于以后扩展类似于多个label的形式（例如`(a="b", x="y1")`)，但是目前只有一个label的情况。

`n`后紧接着是`label name`和`lable value`的列表，这里使用实际字符串而没有使用符号表中的引用，主要有两点考虑：一是因为`label `的数量并不多，所以所占用的空间有限。二是这个表访问频率会非常高，直接存储字符串值可以提升效率。

`offset`对应`Posting i`的偏移量。

`Postings Offset Table`中的数据根据`label name`和`label value`排序。这么做的好处是，在内存中可以根据二分查找快速定位到label所在的位置，二是当查找一个label所有对应的可能`value`时，可以定位到该`label`所在的起始位置，然后顺序遍历。

`Postings Offset Table`和`Postings i`中的数据构成了倒排索引。对于每个label，可以快速定位到其对应的`Series`列表。

#### tombstones

`Tombstones`是删除标记，用来标识在查询时哪些部分需要忽略。这是在Block在创建后唯一会修改的文件。

该文件的结构：

```sh
┌────────────────────────────┬─────────────────────┐
│ magic(0x0130BA30) <4b>     │ version(1) <1 byte> │
├────────────────────────────┴─────────────────────┤
│ ┌──────────────────────────────────────────────┐ │
│ │                Tombstone 1                   │ │
│ ├──────────────────────────────────────────────┤ │
│ │                      ...                     │ │
│ ├──────────────────────────────────────────────┤ │
│ │                Tombstone N                   │ │
│ ├──────────────────────────────────────────────┤ │
│ │                  CRC<4b>                     │ │
│ └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

`magic`表明了该文件是一个`tombstones`文件。`version`标识如何解析该文件。接下来是一系列`Tombstone`记录，最后以CRC结尾。

`Tombstone i`的格式为:

```sh
┌────────────────────────┬─────────────────┬─────────────────┐
│ series ref <uvarint64> │ mint <varint64> │ maxt <varint64> │
└────────────────────────┴─────────────────┴─────────────────┘
```

第一个字段是这个tombstone对应的series索引，`mint`和`maxt`对应了需要删除的数据时间范围。每个series可以对应多个tombstone。

## Block的压缩和保存

### 压缩(Compaction)

压缩包括从一个或者多个先有的Block创建一个新的Block。随后删除源Block，并使用新的Block代替它们。

为什么需要压缩操作：

1. 所有的删除操作都存储在单独的tombstone文件中，待删除的数据仍然在存储在磁盘上。当tombstone中待删除的数据占据series中数据一定比例时，需要从磁盘中删除这些数据。
2. 索引数据在大部分相邻Block中都是相似的，通过合并相邻的块可以删除重复的索引数据，节约磁盘空间。
3. 当查询命中大于1个Block时，需要查询并合并多个Block中的结果获得最终的结果，会产生额外的开销。通过合并多个Block可以减少这种开销。
4. 如果存在重叠的Block，查询时需要对它们中重复的Sample进行合并和删除。合并Block可以避免重复删除数据。

Prometheus每隔1min就会执行一个压缩循环。压缩的过程可以分为两个步骤：生成Plan和执行Plan。循环在没有需要执行的Plan时退出。

#### 步骤 1: 生成 “Plan”

Plan是指需要执行合并的Block列表，会根据以下条件从高到低选择。当满足条件时就会生成一个Plan。当所有条件都不满足时Plan就是空的。

##### 条件1: 重叠的Block

重叠的Block会使查询变慢。Peometheus本身并不会产生重叠的Block，只有当将一些数据重新导入到Prometheus中才会出现。所以消除重叠的Block，把Prometheus恢复到生产状态是最高优先级。

每个Plan可以包含不止2个Block，例如：

```sh
|---1---|
            |---2---|
      |---3---|
                  |---4---|
```

这种情况就会使`1 2 3 4`包含到一个Plan中执行。

下面一种情况下一个Plan中会包含3个Block:

```sh
|-----1-----|
  |--2--|
     |----3----|  
```

##### 条件2: 预设的时间范围

Prometheus会根据预设的时间定期的合并Block。默认情况下的时间范围是 [2h 6h 18h 54h 162h 486h], 即从2h开始，每次乘3。

例如以6h为例。会将Unix时间划分为0-6h，6h-12h，12h-18h…的bucket。在同一个bucket中的Block会被合并为一个新的Block。

在Prometheus中，最大块的大小可以是31天（744小时），或者保留时间的1/10，以这两个值中较低的值为准。

##### 条件3: Tombstones覆盖了Series时间范围超过5%

如果存在Block，其中Tombstone覆盖了其中所有series时间跨度超过5%，则会对其进行压缩。其中Tombstone中覆盖的数据会从磁盘中删除（创建一个没有Tombstone的新Block）。这个Plan中只会含有一个Block。

#### 步骤2: 执行合并

持久的Block是不可更改的，如果需要修改，则需要创建一个新的Block。在压缩的过程中，即使源目标只有一个Block，也需要创建一个全新的Block。

在进行压缩时，多个Block中索引中重复的部分被删除。当Block没有发生重叠是，多个Block里的Chunk直接堆叠在一起。当Block发生重叠时，只有Block中重叠的Chunk被解析并且去重，并且重新压缩为Chunk存储到Block。同时保证Chunk的最大size为120个时间单位（120 * 15s）的样本数据。

每个Block都有一个压缩级别(compaction level)，用来标记这个Block经历了多少次压缩操作。

如果Block包含有tombstone，需要重写Chunk去除到Tombstone包含的时间范围。在压缩完成后，Block中不会含有tomnstone数据。

压缩操作本身并不会删除源Block，而是在meta.json将其标记为已删除。在压缩周期结束后，新Block的加载和源Block的删除由TSDB分别处理。

### Head 压缩

这是一种特殊的压缩操作，Head Block作为源Block，压缩操作将Head Block的一部分转化为持久化的Block，同时删除Tombstonte中包含的数据。

从Head Block中生成的块压缩级别（compaction level）为1。

### 保存(Retention)

TSDB允许设置在TSDB中存储的数据量。主要有两个维度：基于时间和基于数据量的大小。可以单独设置或者同时设置，同时设置时两个条件之间是OR的关系，即满足其中一个就会触发删除过时的数据。

#### 基于时间的保存

基于时间可以设置TSDB数据相对于最新的Block最大跨越的时间范围。当一个Block中的包含的数据完全超过了保留的时间范围（不是部分数据超过）时会将该Block删除。

#### 基于数据的保存

基于数据可以设置TSDB所占用总的数据量的大小，包括WAL，checkpoint，Head Block和持久化的Block。

相比于基于时间的删除策略，基于数据大小的删除策略更为严格。一旦占用的总的大小超过设置，TSDB就会删除最旧的Block。

## 查询

### TSDB查询类型

目前在持久Block上的查询主要有三种类型：

1. `LabelNames()`: 获取Block上的所有label name
2. `LabelValues(name)`: 返回Block中label name对应的所有可能的label value
3. `Select([]matcher)`: 返回Block中被matcher中指定的samples。

在进行samples查询前，需要为Block创建一个`Querier`，它指定了查询时间的范围（mint和maxt)。

### `LabelNames() `

获取Block上的所有label name。例如series `{a="b", c="d"}`，表签名就是  `"a"` 和 `"c"`.

`LabelNames()` 和 `LabelValues()` 在TSDB都是通过Block索引中的 `Postings Offset Table`获取的。

当Block的索引在加载时，我们会在内存中存储*`map[labelName][]postingOffset`*。map中postingOffset的列表并不会存储`Postings Offset Table`所有的项，目前是每隔32个项存储一个PostingOffset，包括第一个和最后一个。存储部分的PostingOffset有助于节约内存。

所以当需要获取所有的标签时，只需要迭代这个map就可以获取到。

### `LabelValues(name)`

跟上面map的存储，我们会把`Postings Offset Table`第一个和最后一个位置存储到map中，所以只需要遍历这两个位置间磁盘中所有的数据就可以获取到所有的标签值。

### `Select([]matcher)`

#### Matcher

matcher有四种类型：

1. Equal `labelName="<value>"`: labe name 和value 完全匹配。
2. Not Equal `labelName!="<value>"`: label name和value 完全不匹配
3. Regex Equal `labelName=~"<regex>"`: label name对应的value满足给定的正则表达式。
4. Regex Not Equal `labelName!~"<regex>"`:  label name对应的value不满足给定的正则表达式。

label name是完整的标签名称，不允许使用正则表达式。规定使用的正则表达式需要满足整个标签值的匹配而不是部分匹配，因为在运行前会补全`^(?:<regex>)$`。

例如有如下series：

- s1 = `{job="app1", status="404"}`
- s2 = `{job="app2", status="501"}`
- s3 = `{job="bar1", status="402"}`
- s4 = `{job="bar2", status="501"}`

给定了一些matcher：

- `status="501"` -> (s2, s4)
- `status!="501"` -> (s1, s3)
- `job=~"app.*"` -> (s1, s2)
- `job!~"app.*"` -> (s3, s4)

如果给定的matcher数量大于1，它们之前则是AND的关系：

- `job=~"app.*", status="501"` -> (s1, s2) ∩ (s2, s4) -> (s2)
- `job=~"bar.*", status!~"5.."` -> (s3, s4) ∩ (s1, s3) -> (s3)

#### Selecting samples

在获取samples前，首先需要根据matcher确定符合条件的series。方法是获取满足单个matcher的series列表，然后取交集。

根据索引中的`Postings Offset Table`，我们可以获取到单个标签对应的series 索引列表。

##### 获取单个matcher对应的postings

如果是Equal Matcher，例如`a=“b”` ，我们可以直接根据`Postings Offset Table`获取该标签值对应的postings列表。由于我们在内存中存储的*`map[labelName][]postingOffset`*只对应了部分标签值。所以在查询时会先定位到标签值“b”所在的区间，然后遍历`Postings Offset Table`中区间的位置来找到标签值“b”对应的postings列表的位置。如果找不到，则说明是空列表。

对于Regex Equal `a=~"<rgx>"`，需要遍历`Postings Offset Table`中label name对应的所有标签值，并且匹配正则表达式，将结果合并。例如上面的`job=~"app.*"`,找到`job="app1" -> (s1)`和 `job="app2" -> (s2)`后，合并得到最终结果：`job=~"app.*" -> (s1, s2)`。

对于Not Equal `a!="b"` 和Regex Not Equal `a!~"<rgx>"`，需要先将其转换为Equal and Regex Equal。得到结果后，再使用集合减法。

##### 多个matcher对应的postings

根据上面的方法，我们先获取单个matcher的postings列表，然后再对结果取交集。但是对于否定匹配器，则会取差集。

例如：

`job=~"bar.*", status!~"5.*"`

-> `(job=~"bar.*") ∩ (status!~"5.*")`

-> `(job=~"bar.*") - (status=~"5.*")`

-> `((job="bar1") ∪ (job="bar2")) - (status="501")`

-> `((s3) ∪ (s4)) - (s2, s4)`

-> `(s3, s4) - (s2, s4)` -> `(s3)`

类似对于 `a="b", c!="d", e=~"f.*", g!~"h.*"` 会得到  `((a="b") ∩ (e=~"f.*")) - (c="d") - (g=~"h.*")`。

##### 获取samples

当我们最终获取到需要的series ids(postings)后，需要逐个遍历它们：

1. 在索引中通过series id定位`Series`表中对应的Chunk列表。
2. 在Chunk列表中找到所有和目标时间重叠的Chunk。
3. 创建一个迭代器来从`chunks`目录下的文件中来访问`mint`和`maxt`时间范围中的samples。

`Select([]matcher)`最终根据标签排序返回matcher匹配到所有smaples。

### 查询多个Block

当查询的`mint`和`maxt`包含多个Block时，上述的3个查询方法的结果会进行合并：

1. `LabelNames()`: 从所有Block中获取到label names，然后进行N way merge.
2. `LabelValues(name)`:  从所有Block中获取到 label values，然后进行N way merge。
3. `Select([]matcher)`: 通过Select方法先从所有Block中获取到迭代器，并通过迭代器再进行N way merge。因为各个迭代器之间返回的结果也是根据标签对排序的。

### 查询Head Block

Head Block已经将所有的标签对和series 列表存储在了内存中（`map[labelName]map[labelValue]postingsList`)，在访问Head Block中的数据时和上述流程类似。

# 参考

1. [Writing a Time Series Database from Scratch](https://web.archive.org/web/20210803115658/https://fabxc.org/tsdb/)
1. [Prometheus TSDB (Part 1): The Head Block](https://ganeshvernekar.com/blog/prometheus-tsdb-the-head-block/)
1. [Prometheus Docs](https://prometheus.io/docs/introduction/overview/)
1. [prometheus-book](https://yunlzheng.gitbook.io/prometheus-book/)
1. [source code](https://github.com/prometheus/prometheus/tree/main/tsdb)

