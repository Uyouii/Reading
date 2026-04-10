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

*Tactical modeling* is generally more complex than *strategic modeling*. Thus, if you intend to develop a domain model using the DDD tactical patterns (Aggre- gates, Services, Value Objects, Events, and so forth), doing so will require more careful thought and greater investment. Since this is so, how does an organiza- tion justify tactical domain modeling? What criteria can be used to qualify a given project for the extra investment needed to properly apply DDD from top to bottom?

**战术建模**通常比**战略建模**更为复杂。因此，若你打算运用领域驱动设计（DDD）的战术模式（聚合、服务、值对象、领域事件等）构建领域模型，就需要投入更缜密的思考与更多的成本。既然如此，企业该如何论证开展战术领域建模的合理性？又该依据哪些标准，判定某个项目值得追加投入，从头到尾完整落地 DDD 方法论？

Picture yourself leading an expedition through unfamiliar territory. You would want to understand the surrounding landmasses and borders. Your team would study maps, maybe even draw their own, and determine their stra- tegic approach. You would consider aspects of the terrain and how it could be used to your advantage. No matter how much planning is done, some facets of such an endeavor are going to be really difficult.

想象你正带领一支探险队穿越未知地域。你需要摸清周边的地貌与边界，团队会研读地图，甚至自行绘制专属地图，制定整体战略行进方案。你会考量地形特征，思考如何利用地形为己方创造优势。无论前期规划多么详尽，这类探险行动中总会有部分环节极具挑战性。

If your strategy indicated that you’d have to scale a vertical rock face, you’d need some fitting tactical tools and maneuvers for that ascent. Standing at the bottom and looking up, you might see some indication of specific challenges and perilous areas. Yet, you wouldn’t see every detail until you were on the rock face. You might need to drive pitons into slick rock, but you could use var- ious-size cams to wedge into natural cracks. To latch on to these climbing pro- tections, you’d bring along your carabiners. You would try to take as straight a path as possible but would have to make specific determinations point by point. Sometimes you might even have to backtrack and reroute depending on what the rock dictated. Many people think of climbing as a dangerous thrill sport, but those who actually climb will tell you it’s safer than driving a car or flying an airplane. Clearly, for that to be true, climbers need to understand the tools and techniques and how to judge the rock.

如果战略规划显示必须攀登一处垂直岩壁，你就需要配备适配的战术工具与攀爬技巧。站在山底向上眺望，或许能预判到部分具体挑战与危险区域，但唯有身处岩壁之上，才能看清所有细节。你可能需要在光滑的岩壁上打入岩钉，用不同尺寸的凸轮塞楔入天然裂缝；为扣住这些攀岩保护点，还会随身携带登山快挂。你会尽量选择最笔直的路线，却必须逐点做出具体判断；有时甚至需要根据岩壁实际情况折返、重新规划路线。很多人将攀岩视作危险的极限运动，但真正的攀岩者会告诉你，它比驾车或乘飞机更安全。显然，要实现这一点，攀岩者必须熟练掌握工具与技巧，学会判断岩壁状况。

If developing a given **Subdomain (2)** requires such a difficult, even precari- ous, ascent, we’d bring the DDD tactical patterns along for the climb. A busi- ness initiative that matches the criteria of the Core Domain should not quickly dismiss the use of the tactical patterns. The Core Domain is an unknown and complex area. The team is best protected against a disastrous mid-asset fall if using the right tactics.

若某个**子域 (2)**的开发如同这场艰难甚至凶险的攀登，我们就需要借助 DDD 的战术模式来完成这场 “攀爬”。符合**核心域**判定标准的业务项目，绝不应轻易放弃使用战术模式。核心域本身就是未知且复杂的业务领域，团队运用恰当的战术设计，才能最大程度避免项目推进过程中出现灾难性崩盘。

Here’s some practical guidance. I begin with the high-level ones and prog- ress to more details:

- If a Bounded Context is being developed as the Core Domain, it is stra- tegically vital to the success of the business. The core model is not well understood and will require lots of experimentation and refactoring. It likely deserves commitment to longevity with continuous enhancement. It may not always be your Core Domain. Nonetheless, if the Bounded Context is complex, innovative, and needs to endure for a long time as it undergoes change, strongly consider the use of the tactical patterns as an investment in the future of your business. This assumes that your Core Domain deserves the best developer resources with a high skill level.
- A domain that may become a **Generic Subdomain (2)** or Supporting Sub- domain to its consumers may actually be a Core Domain to your busi- ness. You don’t always judge a domain from the viewpoint of its ultimate consumers. If you are developing a Bounded Context as your chief business initiative, it is your Core Domain regardless of how it is viewed by customers outside your business. Strongly consider the use of the tactical patterns.
- If you are developing a Supporting Subdomain that, for various reasons, cannot be acquired as a third-party Generic Subdomain, it is possible that the tactical patterns would benefit your efforts. In this case consider the skill level of the team and whether or not the model is new and inno- vative. It is innovative if it adds specific business value, captures special knowledge, and is not just technically intriguing. If the team is capable of properly applying tactical design, and the Supporting Subdomain is inno- vative and must endure for years in the future, this is a good opportunity to invest in your software using tactical design. However, this does not make this model the Core Domain since in the eyes of the business it is merely Supporting.

这里提供一些实操性指导。我先从高层原则讲起，再逐步深入细节：

- 如果某个**限界上下文**被开发为**核心域**，那么它在战略层面对业务的成功至关重要。核心领域模型尚未被充分理解，需要大量的探索试验与重构迭代，这类模型通常值得长期投入并持续优化升级。它未必永远是你的核心域。但只要该限界上下文具备复杂性、创新性，且需要在持续变更中长期存续，就应强烈考虑采用战术模式，将其作为对业务未来的投资。这一判断的前提是，你的核心域能够调配到高水平、高能力的优质研发资源。
- 某个领域，对其使用者而言或许是**通用子域**或**支撑子域**，但对自身业务来说，它实则是核心域。判断一个领域，不能总站在最终使用者的视角。如果你将某个限界上下文作为核心业务项目来开发，那么无论企业外部的客户如何看待它，它都是你的核心域。对此应强烈考虑采用战术模式。
- 如果你正在开发一个支撑子域，且因种种原因无法通过采购第三方通用子域的方式替代，那么战术模式很可能会为你的开发工作带来增益。这种情况下，需要考量团队的技术水平，以及该领域模型是否新颖且具备业务创新性。所谓业务创新，是指能创造专属业务价值、沉淀特殊业务知识，而非仅在技术层面显得新颖有趣。如果团队有能力妥善落地战术设计，且该支撑子域具备业务创新性、需要在未来数年持续迭代维护，那么借助战术设计投入软件建设就是一个值得的选择。不过，即便如此，该模型也并非核心域 —— 在业务视角下，它始终只是支撑性的。

These guidelines may be somewhat confining if your business employs a good number of developers with vast experience in and a very high comfort level with domain modeling. Where experience is very high, and the engineers themselves believe the tactical patterns would be the best choice, it makes sense to trust their opinion. Honest developers, no matter how experienced, will indicate in a specific case that developing a domain model is, or is not, the best choice.

如果你的企业拥有大量在领域建模方面经验极其丰富、运用得心应手的开发人员，上述指导原则可能会显得有些局限。当团队经验水平极高，且工程师自身认为采用战术模式是最优选择时，采信他们的判断是合理的。即便经验再丰富，务实的开发人员也会针对具体场景，明确指出构建领域模型是否为最佳方案。

The type of business domain itself is not automatically the determining fac- tor for choosing a development approach. Your team should consider import- ant questions to help you make the final determination. Consider the following short list of more detailed decision parameters, which is more or less aligned with and expands on the preceding higher-level guidelines:

- Are domain experts available and are you committed to forming a team around them?
- Although the specific business domain is somewhat simple now, will it grow in complexity over time? There is risk in using Transaction Script1 for complex applications. If you use Transaction Script now, will the potential for refactoring to a behavioral domain model later on be practi- cal if/when the Context becomes complex?
- Will the use of the DDD tactical patterns make it easier and more prac- tical to integrate with other Bounded Contexts, whether third-party or custom developed?
- Will development really be simpler and require less code if you use Transaction Script? (Experience with both approaches proves that many times Transaction Script requires as much or more code. This is probably because the complexity of the domain and the innovation of the model were not well understood during project planning. Underestimating domain complexity and the innovation involved happens often.)
- Do the critical path and timeline allow for any overhead required for tac- tical investment?
- Will the tactical investment in a Core Domain protect the system from changing architectural influences? Transaction Script may leave it exposed. (Domain models are often enduring while architectural influences tend to be more disruptive to other layers.)
- Will clients/customers benefit from a cleaner, enduring design and devel- opment approach, or could their application be replaced by an off-the- shelf solution tomorrow? In other words, why would we ever develop this as a custom application/service in the first place?
- Will developing an application/service using tactical DDD be more diffi- cult than using other approaches such as Transaction Script? (Skill level and availability of domain experts is vital to answering this question.)
- If the team’s toolkit was complete with DDD enablers, would we consci- entiously choose to use another approach instead? (Some enablers make model persistence practical, such as using object-relational mapping, full Aggregate serialization and persistence, an Event Store, or a framework that supports tactical DDD. There may be other enablers, too.)

业务领域本身并非选择开发方式的绝对决定因素。你的团队应当结合关键问题来辅助做出最终决策。以下是一组更细化的决策参考指标，大致契合并进一步拓展了前述的高层指导原则：

- 是否有可用的领域专家，且你是否决心围绕这些专家组建团队？
- 即便当前具体业务领域相对简单，其复杂度未来是否会持续提升？在复杂应用中采用**事务脚本**模式存在风险。若现阶段使用事务脚本，当该限界上下文后续变得复杂时，后续重构为行为领域模型是否具备可行性？
- 采用 DDD 战术模式，是否能更简便、更实际地与其他限界上下文（无论是第三方还是自研的）完成集成？
- 使用事务脚本真的会让开发更简单、代码量更少吗？（两种方案的实践经验表明，很多情况下事务脚本的代码量与领域模型相当甚至更多。这大概率是因为项目规划阶段未能充分认知领域的复杂度与模型的创新性，低估领域复杂度与业务创新性是很常见的情况。）
- 项目关键路径与时间线，是否能容纳战术设计投入所需的额外开销？
- 对核心域进行战术设计投入，能否保护系统免受架构变更带来的冲击？（事务脚本模式可能会让系统暴露在这类风险中。领域模型通常具备长期稳定性，而架构变更往往会对其他层级造成更大的破坏性影响。）
- 客户是否能从更清晰、更具持续性的设计与开发方案中获益，还是其应用随时可以被现成解决方案替代？换言之，我们当初究竟为何要将其开发为定制化应用 / 服务？
- 采用 DDD 战术模式开发应用 / 服务，是否会比事务脚本等其他方案难度更高？（团队技能水平与领域专家的可用性，是回答该问题的关键。）
- 若团队的工具集已完备配备 DDD 支撑组件，我们是否仍会审慎选择其他方案？（部分支撑组件能让模型持久化更具可行性，例如对象关系映射、完整聚合的序列化与持久化、事件存储，或是支持 DDD 战术设计的框架，此外也可能存在其他支撑组件。）





