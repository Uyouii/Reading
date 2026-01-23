[toc]

## Chapter 8. The Trouble With Distributed Systems

### Faults and Partial Failures

**故障与部分失效**

There is no fundamental reason why software on a single computer should be flaky:when the hardware is working correctly, the same operation always produces thesame result (it is deterministic). If there is a hardware problem (e.g., memory corrup‐tion or a loose connector), the consequence is usually a total system failure (e.g., ker‐nel panic, “blue screen of death,” failure to start up). An individual computer withgood software is usually either fully functional or entirely broken, but not somethingin between.

单台计算机上的软件本不该存在稳定性问题：在硬件正常运行的情况下，相同操作理应产生相同结果（即具备**确定性**）。若硬件出现故障（例如内存损坏或接口松动），后果通常是**系统完全瘫痪**（如内核崩溃、蓝屏死机、无法启动）。一台搭载优质软件的独立计算机，其状态通常只有**完全可用**和**彻底故障**两种，而非介于两者之间的中间状态。

This is a deliberate choice in the design of computers: if an internal fault occurs, weprefer a computer to crash completely rather than returning a wrong result, becausewrong results are difficult and confusing to deal with. Thus, computers hide the fuzzyphysical reality on which they are implemented and present an idealized systemmodel that operates with mathematical perfection. A CPU instruction always doesthe same thing; if you write some data to memory or disk, that data remains intactand doesn’t get randomly corrupted. This design goal of always-correct computationgoes all the way back to the very first digital computer [3].

这是计算机设计过程中一个**刻意为之的选择**：当内部故障发生时，我们更倾向于让计算机彻底崩溃，而非返回错误结果 —— 因为错误结果的处理难度大，且极易造成混乱。基于此，计算机屏蔽了底层硬件模糊的物理特性，对外呈现出一个理想化的系统模型，该模型能够以数学层面的完美状态运行。一条 CPU 指令的执行结果永远保持一致；向内存或磁盘写入的数据会完整留存，不会发生随机损坏。这种 **“始终正确计算”** 的设计目标，最早可以追溯到第一台数字计算机诞生的时代 [3]。

If we want to make distributed systems work, we must accept the possibility of partial failure and build fault-tolerance mechanisms into the software. In other words, we need to **build a reliable system from unreliable components**. (As discussed in “Relia‐bility” on page 6, there is no such thing as perfect reliability, so we’ll need to understand the limits of what we can realistically promise.) Even in smaller systems consisting of only a few nodes, it’s important to think aboutpartial failure. In a small system, it’s quite likely that most of the components areworking correctly most of the time. However, sooner or later, some part of the system  will become faulty, and the software will have to somehow handle it. The fault han‐dling must be part of the software design, and you (as operator of the software) needto know what behavior to expect from the software in the case of a fault.

若要让分布式系统稳定运行，我们就必须接受**部分失效**的可能性，并在软件中内置**容错机制**。换句话说，我们需要**用不可靠的组件构建可靠的系统**。（正如第 6 页 “可靠性” 一节所讨论的，绝对可靠的系统并不存在，因此我们需要清楚自己实际能承诺的可靠性边界。）即便是由少数节点构成的小型系统，考量部分失效问题也同样重要。在小型系统中，大多数组件多数时候都能正常工作，这种情况是很常见的。但无论如何，系统的某个部分迟早会出现故障，软件必须以某种方式对此进行处理。故障处理逻辑必须作为软件设计的一部分，而你（作为软件运维人员）需要清楚，当故障发生时，软件会呈现出怎样的行为。

**Building a Reliable System from Unreliable Components**

You may wonder whether this makes any sense—intuitively it may seem like a systemcan only be as reliable as its least reliable component (its weakest link). This is not thecase: in fact, it is an old idea in computing to construct a more reliable system from aless reliable underlying base [11]. For example:

- **Error-correcting codes** allow digital data to be transmitted accurately across a communication channel that occasionally gets some bits wrong, for example due to radio interference on a wireless network [12].
- IP (the Internet Protocol) is unreliable: it may drop, delay, duplicate, or reorder packets. TCP (the Transmission Control Protocol) provides a more reliable transport layer on top of IP: it ensures that missing packets are retransmitted,duplicates are eliminated, and packets are reassembled into the order in which they were sent.

你可能会疑惑，这种思路是否成立 —— 直观来看，系统的可靠性似乎至多等同于其**最不可靠组件**的可靠性（也就是 “木桶效应”）。但事实并非如此：实际上，通过可靠性较低的底层基础构建更可靠的系统，是计算机领域的一个古老理念 [11]。例如：

- **纠错码**技术能够让数字数据在存在偶发比特错误的通信信道上准确传输，比如无线网络中受无线电干扰影响的信道 [12]。
- 互联网协议（IP）本身是不可靠的：它可能会丢弃、延迟、重复或乱序发送数据包。而传输控制协议（TCP）在 IP 的基础上，提供了更可靠的传输层服务：它会确保丢失的数据包被重传、重复的数据包被剔除，并且数据包会按照发送顺序重新组装。

Although the system can be more reliable than its underlying parts, there is always alimit to how much more reliable it can be. For example, error-correcting codes candeal with a small number of single-bit errors, but if your signal is swamped by inter‐ference, there is a fundamental limit to how much data you can get through yourcommunication channel [13]. TCP can hide packet loss, duplication, and reorderingfrom you, but it cannot magically remove delays in the network.

尽管上层系统的可靠性可以高于底层组件，但这种可靠性的提升存在**本质上限**。例如，纠错码可以处理少量的单比特错误，但如果信号被干扰完全淹没，通信信道能够传输的数据量就会存在无法突破的极限 [13]。TCP 可以为你屏蔽丢包、重复和乱序的问题，却无法凭空消除网络延迟。

Although the more reliable higher-level system is not perfect, it’s still useful because ittakes care of some of the tricky low-level faults, and so the remaining faults are usu‐ally easier to reason about and deal with. We will explore this matter further in “Theend-to-end argument” on page 519.

虽然经过可靠性增强的上层系统并非尽善尽美，但它依然具备很高的实用价值：因为它已经处理了部分棘手的底层故障，剩下的故障通常更容易被分析和应对。关于这一点，我们将在第 519 页的 **“端到端原则”** 一节中展开进一步探讨。

### Knowledge, Truth, and Lies

**认知、真相与误判**

The moral of these stories is that a node cannot necessarily trust its own judgment ofa situation. A distributed system cannot exclusively rely on a single node, because anode may fail at any time, potentially leaving the system stuck and unable to recover.Instead, many distributed algorithms rely on a quorum, that is, voting among thenodes (see “Quorums for reading and writing” on page 179): decisions require someminimum number of votes from several nodes in order to reduce the dependence onany one particular node.

这些案例揭示的核心启示是：节点未必能信任自身对当前状况的判断。分布式系统不能完全依赖单个节点 —— 因为任一节点都可能随时发生故障，这有可能导致整个系统陷入停滞且无法恢复。恰恰相反，许多分布式算法的设计都依赖于**法定人数**机制，即通过节点间的投票达成决策（参见第 179 页 “读写操作的法定人数机制”）：决策的生效需要获取若干节点的最低票数支持，以此降低系统对单一节点的依赖。

That includes decisions about declaring nodes dead. If a quorum of nodes declaresanother node dead, then it must be considered dead, even if that node still very muchfeels alive. The individual node must abide by the quorum decision and step down.

这一机制同样适用于**节点失效状态的判定决策**。只要超过法定人数的节点判定某一节点已失效，无论该节点自身是否仍处于正常运行状态，都必须被认定为失效节点。该节点自身也必须遵从法定人数的决策结果，退出系统运行。

Most commonly, the quorum is an **absolute majority of more than half the nodes**(although other kinds of quorums are possible). A majority quorum allows the sys‐tem to continue working if individual nodes have failed (with three nodes, one failurecan be tolerated; with five nodes, two failures can be tolerated). However, it is stillsafe, because there can only be only one majority in the system—there cannot be twomajorities with conflicting decisions at the same time. We will discuss the use of quo‐rums in more detail when we get to **consensus** algorithmsin Chapter 9.

在实践中，法定人数通常指**超过半数节点的绝对多数派**（当然也存在其他类型的法定人数机制）。多数派法定人数机制允许系统在部分节点失效的情况下继续运行：3 个节点的集群可容忍 1 个节点失效，5 个节点的集群则可容忍 2 个节点失效。同时，这种机制具备安全性 —— 系统中同一时间只会存在一个多数派，不会出现两个持有冲突决策的多数派并存的情况。关于法定人数机制的具体应用，我们将在第 9 章探讨**共识算法**时展开详细论述。



 Let’s assume that every time the lock server grants a lock or lease, it also returns **afencing token**, which is a number that increases every time a lock is granted (e.g.,incremented by the lock service). We can then require that every time a client sends awrite request to the storage service, it must include its current fencing token.

我们不妨做这样的设定：**锁服务器**每次授予锁或租约时，都会同时返回一个**防护令牌**。这个令牌是一个数字，每授予一次锁就会递增（例如由锁服务负责递增）。基于此，我们可以要求客户端**每次向存储服务发送写入请求时**，都必须附带其当前持有的防护令牌。

In Figure 8-5, client 1 acquires the lease with a token of 33, but then it goes into along pause and the lease expires. Client 2 acquires the lease with a token of 34 (thenumber always increases) and then sends its write request to the storage service,including the token of 34. Later, client 1 comes back to life and sends its write to thestorage service, including its token value 33. However, the storage server remembersthat it has already processed a write with a higher token number (34), and so it rejectsthe request with token 33.

在图 8-5 的场景中，客户端 1 获取了防护令牌为 33 的租约，但随后进入长时间停滞状态，租约也随之过期。客户端 2 紧接着获取了防护令牌为 34 的租约（令牌数值始终保持递增），并向存储服务发送写入请求，请求中附带了令牌 34。一段时间后，客户端 1 恢复正常运行，也向存储服务发送写入请求，附带的令牌数值为 33。但存储服务器会记录自己已经处理过令牌数值更高（34）的写入请求，因此会**拒绝携带令牌 33 的这次请求**。

![Figure 8-5](../../images/distribuide_system/DDIA-8-5.jpg)

> Figure 8-5. Making access to storage safe by allowing writes only in the order of increasing fencing tokens

#### Byzantine Faults

**拜占庭故障**

**The Byzantine Generals Problem**

**拜占庭将军问题**

The Byzantine Generals Problem is a generalization of the so-called Two Generals Problem[78], which imagines a situation in which two army generals need to agreeon a battle plan. As they have set up camp on two different sites, they can only com‐municate by messenger, and the messengers sometimes get delayed or lost (like pack‐ets in a network). We will discuss this problem of consensusin Chapter 9.

拜占庭将军问题是**两军问题**[78] 的泛化扩展，该问题构想了这样一种场景：两位军队将领需要就作战计划达成共识。由于他们分别扎营在两处不同的营地，只能通过信使传递消息，而信使可能会出现延误或失踪的情况（就像网络中的数据包丢失一样）。关于这个共识问题，我们将在第 9 章展开讨论。

In the Byzantine version of the problem, there are n generals who need to agree, andtheir endeavor is hampered by the fact that there are some traitors in their midst.Most of the generals are loyal, and thus send truthful messages, but the traitors maytry to deceive and confuse the others by sending fake or untrue messages (while try‐ing to remain undiscovered). It is not known in advance who the traitors are.

在拜占庭将军问题的设定中，共有n位将领需要达成共识，而他们的行动受制于一个情况 —— 队伍中存在叛徒。大多数将领是忠诚的，会传递真实的消息，但叛徒可能会发送伪造或虚假的消息，以此欺骗、混淆其他将领的判断，同时还会设法隐藏自己的身份。叛徒的身份在事前是未知的。

A system is Byzantine fault-tolerant if it continues to operate correctly even if someof the nodes are malfunctioning and not obeying the protocol, or if malicious attack‐ers are interfering with the network. This concern is relevant in certain specific circumstances

若一个系统**即便在部分节点发生故障、不遵守协议，或遭遇恶意攻击者的网络干扰时，仍能保持正确运行**，那么这个系统就具备**拜占庭容错能力**。这类问题仅在一些特定场景下才需要重点考量。

#### System Model and Reality

**系统模型与现实**

**Correctness of an algorithm**

To define what it means for an algorithm to be correct, we can describe its properties.For example, the output of a sorting algorithm has the property that for any two dis‐tinct elements of the output list, the element further to the left is smaller than the ele‐ment further to the right. That is simply a formal way of defining what it means for alist to be sorted.

要定义一个算法的正确性，我们可以描述它应具备的**特性**。例如，排序算法的输出具有这样的特性：对于输出列表中的任意两个不同元素，左侧的元素始终小于右侧的元素。这是对 “列表已排序” 这一概念的一种形式化定义方式。

Similarly, we can write down the properties we want of a distributed algorithm todefine what it means to be correct. For example, if we are generating fencing tokensfor a lock (see “Fencing tokens” on page 303), we may require the algorithm to havethe following properties:

- **Uniqueness** No two requests for a fencing token return the same value.
- **Monotonic sequence** If request xreturned token tx, and request yreturned token ty, and x completed before ybegan, then tx< ty.
- **Availability** A node that requests a fencing token and does not crash eventually receives a response.

同理，我们也可以通过列举期望的特性，来定义一个分布式算法的正确性。例如，在为锁生成防护令牌时（参见第 303 页 “防护令牌”），我们可能要求该算法具备以下特性：

- **唯一性**：任意两次防护令牌的请求，都不会返回相同的数值。
- **单调性序列**：若请求x返回的令牌为tx，请求y返回的令牌为ty，且请求x在请求y开始之前完成，则有 tx<ty。
- **可用性**：发起防护令牌请求且未发生崩溃的节点，最终都会收到响应。

An algorithm is correct in some system model if it always satisfies its properties in allsituations that we assume may occur in that system model. But how does this makesense? If all nodes crash, or all network delays suddenly become infinitely long, thenno algorithm will be able to get anything done.

若一个算法在某个系统模型所假设的**所有可能发生的场景**中，均能始终满足其既定特性，那么该算法在这个系统模型中就是正确的。但这一说法如何才能成立呢？如果所有节点都发生崩溃，或者所有网络延迟突然变得无限长，那么任何算法都无法完成任务。

**Safety and liveness**

**安全属性与活性属性**

To clarify the situation, it is worth distinguishing between two different kinds ofproperties: **safety** and **liveness** properties. In the example just given, **uniqueness** and **monotonic sequence** are safety properties, but **availability** is a liveness property.

为了厘清这一情况，我们有必要区分两类不同的属性：**安全属性**与**活性属性**。在刚才的示例中，**唯一性**与**单调性序列**属于安全属性，而**可用性**则属于活性属性。

What distinguishes the two kinds of properties? A giveaway is that liveness propertiesoften include the word “**eventually**” in their definition. (And yes, you guessed it—**eventual consistency is a liveness property** [89].)

这两类属性的区别是什么？一个显著特征是，活性属性的定义中往往包含 “最终” 一词。（没错，你可以猜到 ——**最终一致性**就是一种活性属性 [89]。）

Safety is often informally defined as **nothing bad happens,** and liveness as **something good eventually happens**. However, it’s best to not read too much into those informaldefinitions, because the meaning of good and bad is subjective. The actual definitionsof safety and liveness are precise and mathematical [90]:

- If a safety property is violated, we can point at a particular point in time at which it was broken (for example, if the uniqueness property was violated, we can iden‐ tify the particular operation in which a duplicate fencing token was returned). After a safety property has been violated, the violation cannot be undone—the damage is already done.
- A liveness property works the other way round: it may not hold at some point in time (for example, a node may have sent a request but not yet received a response), but there is always hope that it may be satisfied in the future (namely by receiving a response).

安全属性的通俗定义通常是 **“不会发生任何糟糕的情况”**，而活性属性则是**“好事最终总会发生”**。不过，我们不宜过度解读这些通俗定义，因为 “好” 与 “坏” 的界定具有主观性。安全属性与活性属性的准确定义，是严谨且具备数学依据的 [90]：

- 若某一安全属性被违反，我们可以明确指出它被破坏的**具体时间点**（例如，若唯一性属性被违反，我们能够定位到返回重复防护令牌的那次具体操作）。安全属性一旦被违反，这种违规状态便无法逆转 —— 损害已经造成。
- 活性属性的逻辑则恰好相反：它可能在某个时间点不成立（例如，某个节点已发送请求但尚未收到响应），但我们始终有理由相信，它在**未来某一时刻可以得到满足**（也就是通过接收响应来达成）。

An advantage of distinguishing between safety and liveness properties is that it helpsus deal with difficult system models. For distributed algorithms, it is common torequire that **safety properties always hold, in all possible situations of a system model**[88]. That is, even if all nodes crash, or the entire network fails, the algorithm mustnevertheless ensure that it does not return a wrong result (i.e., that the safety proper‐ties remain satisfied).

区分安全属性与活性属性的一大好处，在于它能帮助我们应对复杂的系统模型。对于分布式算法而言，一个常见的要求是：**安全属性必须在系统模型的所有可能场景下始终成立**[88]。也就是说，即便所有节点崩溃、或整个网络瘫痪，算法也必须保证不会返回错误结果（即安全属性始终得到满足）。

### Summary

 In this chapter we also went on some tangents to explore whether the unreliability ofnetworks, clocks, and processes is an inevitable law of nature. We saw that it isn’t: it is possible to give hard realtime response guarantees and bounded delays in networks, but doing so is very expensive and results in lower utilization of hardwareresources. Most non-safety-critical systems choose cheap and unreliable over expensive and reliable.

在本章中，我们还穿插探讨了一些延伸话题，旨在弄清**网络、时钟与进程的不可靠性是否属于不可规避的自然规律**。而我们得到的结论是：并非如此。硬实时响应保证与网络有界延迟**是可以实现的**，但这种实现的成本极其高昂，并且会导致硬件资源利用率降低。对于大多数**非安全关键系统**而言，它们更倾向于选择**廉价但不可靠**的方案，而非**昂贵但可靠**的方案。