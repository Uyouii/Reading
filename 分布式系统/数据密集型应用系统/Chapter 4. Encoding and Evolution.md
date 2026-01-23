[toc]

## Chapter 4. Encoding and Evolution

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