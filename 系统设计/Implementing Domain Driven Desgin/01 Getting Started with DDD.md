## 01 Getting Started with DDD

### Why Should you Do DDD

**How DDD Helps**

DDD is an approach to developing software that focuses on thesethree primary aspects:

领域驱动设计是一种软件开发方法，主要聚焦于以下三大核心维度：

1. DDD brings domain experts and software developers together inorder to develop software that reflects the mental model of thebusiness experts. This does not mean that effort is spent onmodeling the “real world.” Rather, DDD delivers a model that is themost useful to the business. Sometimes useful and realistic models      happen to intersect, but to the degree that they diverge, DDDchooses useful.

   With this aspect the efforts of domain experts and softwaredevelopers are devoted to jointly developing a Ubiquitous Languageof the areas of the business that they are focused on modeling. TheUbiquitous Language is developed with full team agreement, isspoken, and is directly captured in the model of the software. It isworth reiterating that the team is com-posed of both domainexperts and software developers. It’s never “us and them.” It’salways us. This is a key business value that allows business know-how to outlive the relatively short initial development efforts thatdeliver the first few versions of the software, and the teams thatproduce it. It’s the point where the cost of developing software is a  justifiable busi-ness investment, not just a cost center.

   This entire effort unifies domain experts who initially disagree witheach other, or who simply lack core knowledge of the domain.Further, it strengthens the close-knit team by spreading deepdomain insight among all team members, including softwaredevelopers. Consider this the hands-on training that every companyshould invest in its knowledge workers.

1 DDD 将领域专家与软件开发人员紧密协作，共同打造能够反映业务专家心智模型的软件。这并非意味着要耗费精力去建模 “现实世界”；恰恰相反，DDD 所交付的模型，是对业务最具实用价值的模型。实用型模型与写实型模型有时会相互契合，但当二者出现分歧时，DDD 始终优先选择实用性。

基于这一核心思路，领域专家与软件开发人员将合力为所聚焦建模的业务领域构建**通用语言**。这套通用语言需经团队全体成员达成一致共识，既用于团队口头沟通，也直接映射到软件模型之中。需要再次强调的是，团队由领域专家和软件开发人员共同组成，绝非 “我们与他们” 的对立关系，而是始终一体的整体。这是一项关键的业务价值：它让业务专业知识能够超越软件最初几个版本交付阶段相对短暂的初始开发工作，也超越负责开发的团队本身而长久留存。正是在这一层面，软件开发的成本成为合理的业务投资，而非单纯的成本消耗项。

这项整体工作还能统一原本彼此意见相左，或是对核心领域知识存在欠缺的领域专家。此外，通过向包括软件开发人员在内的所有团队成员传递深度领域洞察，进一步打造出凝聚力更强的紧密团队。这可视为每家企业都应为知识型员工投入的实操性培训。

2. DDD addresses the strategic initiatives of the business. Whilethis stra-tegic design approach naturally includes technicalanalysis, it is more concerned with the strategic direction of thebusiness. It helps define the best inter-team organizationalrelationships and provides early-warning systems for recognizingwhen a given relationship could cause software and even projectfailure. The technical aspects of strategic design have the goal ofcleanly bounding systems and business concerns, which pro-tectseach business-level service. This provides meaningful motivations         for how an overall service-oriented architecture or business-drivenarchi-tecture is achieved.

2 DDD 着眼于业务的战略规划。尽管这种战略设计思路天然包含技术分析，但其更关注业务的战略发展方向。它有助于界定团队间最优的组织协作关系，并建立预警机制，及时识别特定协作关系可能引发软件乃至项目失败的风险。战略设计的技术目标，是清晰划分系统边界与业务关注点，从而保障各业务级服务的独立性。这也为如何搭建整体的面向服务架构，或是业务驱动型架构，提供了明确的落地指引。

3. DDD meets the real technical demands of the software by usingtacti-cal design modeling tools to analyze and develop theexecutable software deliverables. These tactical design tools allowdevelopers to produce soft-ware that is a correct codification ofthe domain experts’ mental model, is highly testable, is less errorprone (a provable statement), performs to service-level agreements(SLAs), is scalable, and allows for distrib-uted computing. DDDbest practices generally address a dozen or more higher-levelarchitectural and lower-level software design concerns, with afocus on recognizing true business rules and data invariants, andpro-tecting the rules from error situations.

   Using this approach to software development, you and your teamcan succeed in delivering true business value.

3  DDD 运用战术设计建模工具分析并开发可执行的软件交付成果，以此满足软件实际的技术需求。这些战术设计工具能够帮助开发人员打造出精准实现领域专家心智模型的软件产品：这类软件具备极高的可测试性，出错率更低（可验证），满足服务等级协议（SLA）的性能要求，拥有良好的可扩展性，同时支持分布式计算。DDD 最佳实践通常会解决十余个高层架构与底层软件设计问题，核心聚焦于识别真实的业务规则与数据不变量，并保障这些规则在异常场景下不被破坏。

采用这种软件开发方法，你和你的团队将能够成功交付真正的业务价值。

### How to DDD

So how do you capture this all-important Ubiquitous Language?Here are some ways that work as experimentation leads to advancement:

-  Draw pictures of the physical and conceptual domain and labelthem with names and actions. These drawings are mostly informalbut may contain some aspects of formal software modeling. Even if your team does some formal modeling with Unified ModelingLanguage (UML), you want to avoid any kind of ceremony that willbog down discussions and stifle the creativity of the ultimateLanguage being sought.
- Create a glossary of terms with simple definitions. List alternativeterms, including the ones that show promise and the ones thatdidn’t work, and why. As you include definitions, you cannot helpbut develop reusable phrases for the Language because you areforced to write in the Language of the domain.
- If you don’t like the idea of a glossary, still capture some kind ofdoc-umentation that includes the informal drawings of importantsoftware concepts. Again, the goal here is to force additionalLanguage terms and phrases to surface.
- Since only one or a few team members may capture the glossaryor other written documents, circle back with the rest of the team toreview the resulting phrases. You won’t always, if ever, agree on all thecaptured lin-guistics, so be agile and ready to edit heavily.

那么，该如何提炼出这套至关重要的**通用语言**？随着实践探索逐步走向成熟，以下几种切实可行的方法可以参考：

- 绘制业务领域中实体与概念的示意图，并用领域里的名称和行为为其标注。这类图大多是非正式的，但也可以包含一部分规范软件建模的内容。即便你的团队会用统一建模语言（UML）做一些正式建模，也要避免任何形式的繁文缛节，否则会拖慢讨论节奏，扼杀最终要打造的通用语言的创造力。
- 编制一份**术语表**，为每个术语配上简单定义。列出备选说法，包括有潜力的、不合适的，并说明原因。在撰写定义的过程中，你自然而然会提炼出可复用的语言表达，因为你必须用领域本身的语言来书写。
- 如果你不喜欢术语表这种形式，也可以整理一份文档，收录重要软件概念的非正式示意图。核心目标依然是：让更多领域术语和短语被挖掘、浮现出来。
- 由于术语表或书面文档可能只由一两名团队成员整理，一定要回过头和团队其他人一起审核梳理出的表述。你们未必能（甚至永远不会）在所有语言表达上完全达成一致，因此要保持敏捷，做好大幅修改的准备。

**Ubiquitous, but Not Universal**

**通用语言，并非普世语言**

Some further clarification about the reach of a Ubiquitous Language is in order. There are a few basic concepts that we need to keep carefully in mind:

- Ubiquitous means “pervasive,” or “found everywhere,” as spokenamong the team and expressed by the single domain model thatthe team develops.
- The use of the word ubiquitous is not an attempt to describesome kind of enterprise-wide, company-wide, or worldwide,universal domain language.
- There is one Ubiquitous Language per Bounded Context.
- Bounded Contexts are relatively small, smaller than we might atfirst imagine. A Bounded Context is large enough only to capturethe complete Ubiquitous Language of the isolated business domain,and no larger.
- The Language is ubiquitous only within the team that is workingon the project that develops in an isolated Bounded Context.
- On a single project that develops a single Bounded Context, thereare always one or more additional isolated Bounded Contexts withwhich it integrates using Context Maps (3). Each of the multipleBounded Con-texts that integrate has its own UbiquitousLanguage, even though some terms of each may overlap.
-  If you try to apply a single Ubiquitous Language to an entireenterprise, or worse, universally among many enterprises, you willfail.

我们有必要进一步厘清 **通用语言（Ubiquitous Language）** 的适用范围。有几个核心概念需要时刻牢记：

- **通用**的含义是 “无处不在”“贯穿始终”，指在团队内部沟通时统一使用，并且体现在团队所构建的**单一领域模型**中。
- 使用 “通用” 一词，并非要描述某种企业级、全公司乃至全球范围的**普世领域语言**。
- 每个 **限界上下文（Bounded Context）** 对应一套独立的通用语言。
- 限界上下文的规模往往比我们最初想象的要小。它的大小只需恰好能覆盖一个独立业务领域的完整通用语言即可，无需更大。
- 这套语言仅在负责开发该独立限界上下文的项目团队内部 “通用”。
- 即便一个项目只开发一个限界上下文，它也总要通过 ** 上下文映射（Context Map）** 与一个或多个其他独立限界上下文进行集成。这些相互集成的限界上下文，各自都有专属的通用语言，即便部分术语存在重叠。
- 如果你试图把一套通用语言套用到整个企业，甚至更糟 —— 套用到多个企业之间作为普世标准，必然会失败。

### The Business Value of Using DDD

Let’s consider the very realistic business value of employing DDD.Be sure to share this openly with your management, domainexperts, and technical team members. The value and benefits aresummarized here, then I will elaborate. I start off with the lesstechnical benefits.

我们来聊聊采用 **领域驱动设计（DDD）** 所能带来的、非常真实的业务价值。你可以放心地把这些价值分享给管理层、领域专家和技术团队成员。我先在这里汇总核心价值与收益，随后再逐一展开。我会从偏业务、非技术的收益开始说起。

1. The organization gains a useful model of its domain.
2.  A refined, precise definition and understanding of the business isdeveloped.
3. Domain experts contribute to software design.
4.  A better user experience is gained.
5.  Clean boundaries are placed around pure models.
6. Enterprise architecture is better organized.
7. Agile, iterative, continuous modeling is used.
8. New tools, both strategic and tactical, are employed.

1. 组织能够获得一套真正可用的**领域模型**。
2. 形成更精炼、更精准的业务定义与业务认知。
3. 领域专家能够真正参与到软件设计中。
4. 带来更优的用户体验。
5. 为纯粹的领域模型划定清晰的边界。
6. 让企业架构更有条理、更易治理。
7. 采用敏捷、迭代、持续演进的建模方式。
8. 引入一系列新的**战略层面**与**战术层面**的设计工具。

### The Challenges of Applying DDD

As you implement DDD, you will encounter challenges. So haseveryone else who has succeeded at it. What are the commonchallenges and how do we jus-tify using DDD as we face them? Iwill discuss the more common ones:

- Allowing for the time and effort required to create a UbiquitousLanguage

- Involving domain experts at the outset and continuouslywith the project

- Changing the way developers think aboutsolutions in their domain


在落地领域驱动设计（DDD）的过程中，你必然会遇到各种挑战。所有成功实践 DDD 的团队，也都经历过同样的过程。

常见的挑战有哪些？面对这些难题时，我们又该如何论证使用 DDD 的合理性？我会针对几个最典型的问题展开说明：

- 投入必要的时间与精力，构建一套**通用语言**
- 在项目初期就引入领域专家，并让其持续参与项目全过程
- 转变开发人员看待领域解决方案的思维方式

One of the greatest challenges in using DDD can be the time and effort required to think about the business domain, research concepts and termi- nology, and converse with domain experts in order to discover, capture, and enhance the Ubiquitous Language rather than coding in techno-babble. If you want to apply DDD completely, with the greatest value to the business, it’s going to require more thought and effort, and it’s going to take more time. That’s the way it is, period.

使用 DDD 时，**最大的挑战之一**，就是要花大量时间与精力去思考业务领域、研究各类概念和术语，并与领域专家反复交流，从而发现、提炼并完善**通用语言**，而不是抱着一堆技术黑话直接埋头写代码。

如果你想完整落地 DDD，并让它为业务产生最大价值，就必须投入更多思考、更多精力，也必然需要更长的时间。**现实就是如此，没有捷径。**

It can also be a challenge to solicit the necessary involvement from domain experts. No matter how difficult it is, make sure you do. If you don’t get commitment from at least one real expert, you are not going to uncover deep knowledge of the domain. When you do get the domain experts’ involvement, the onus falls back on the developers. Developers must converse with and listen carefully to the true experts, molding their spoken language into software that reflects their mental model of the domain.

争取到领域专家的必要参与，同样是一大难题。但无论多难，都必须做到。

如果得不到哪怕一位真正专家的深度投入，你就不可能挖掘出领域里的深层知识。

而一旦专家参与进来，压力就回到了开发人员这边。开发者必须主动和专家沟通、认真倾听他们的表述，把专家口中的自然语言，转化成能够反映其**业务心智模型**的软件设计。

If the domain you are working in is truly distinguishing to your business, domain experts have the edge-knowledge locked up in their heads, and you need to draw it out. I’ve been on projects where the real domain experts are hardly around. Sometimes they travel a lot and it can be weeks between one- hour meetings with them. In a small business it can be the CEO or one of the vice presidents, and they have lots of other things to do that may seem more important.

如果你正在负责的领域，是公司真正具备核心竞争力的业务，那么领域专家脑子里就装着别人没有的**独门知识**，而你必须把这些知识 “挖” 出来。

我经历过不少项目，真正的领域专家几乎很难见到：他们经常出差，可能隔好几周才能凑出一小时开会。

在小公司里，这类专家往往就是 CEO 或某位副总裁，他们手上还有一大堆看起来更重要的事要做。

**Justification for Domain Modeling**

