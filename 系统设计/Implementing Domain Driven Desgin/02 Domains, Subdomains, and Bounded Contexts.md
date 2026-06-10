## 02 Domains, Subdomains, and Bounded Contexts

### Big Picture

#### Focus on Core Domain

With an understanding of Subdomains and Bounded Contexts,consider an abstract view of a different Domain found in Figure 2.2.This could repre-sent any domain, perhaps even the one you workin. I’ve removed the explicit names so you can mentally fill in theblanks. Naturally, our business goals are on a path of continuousrefinement and expansion reflected by ever-changing Subdomains and the models within. This diagram only captures the whole business Domain at a moment in time with a specificperspective, and one that could be somewhat short-lived.

在理解**子域**与**限界上下文**的基础上，我们来看图 2.2 中另一个领域的抽象视图。它可以指代任意领域，甚至是你实际工作中所处的领域。我已隐去具体名称，方便你在脑海中自行填充对应内容。我们的业务目标本就处在持续优化与拓展的过程中，这一点体现在不断迭代变化的子域及其内部模型上。该图表仅从特定视角，捕捉了整个业务领域在某一时刻的状态，而这样的视角往往时效性有限。

![image-20260413155120260](../../images/auto/image-20260413155120260.png)

Now look at the top of the Domain boundary in Figure 2.2 and you’ll see the Subdomain labeled *Core Domain*. Introduced earlier, this is another aspect of DDD of major importance. A **Core Domain** is a part of the busi- ness Domain that is of primary importance to the success of the organization. Strategically speaking, the business must *excel* with its Core Domain. It is of utmost importance to the ongoing success of the business. That project gets the highest priority, one or more domain experts with deep knowledge of that Subdomain, the best developers, and as much leeway and leverage as possible to give the close-knit team an unobstructed success path. Most of your DDD project efforts will be focused on the Core Domain.

现在来看图 2.2 中**领域边界**的顶部，你会看到标注为**核心域（Core Domain）**的子域。前文已经提及，这是领域驱动设计（DDD）中另一项至关重要的内容。**核心域**是业务领域里对组织成功起核心作用的部分。从战略角度来说，企业必须在核心域上做到**出类拔萃**。它对业务的持续成功至关重要。核心域相关项目会被赋予最高优先级，配备一名或多名深耕该子域的领域专家、最优秀的开发人员，并尽可能提供充足的灵活空间与资源支持，为这支紧密协作的团队扫清障碍、铺就顺畅的成功路径。你在 DDD 项目中的大部分投入，都将聚焦在核心域上。

Two other kinds of Subdomains are found in Figure 2.2, *Supporting Sub- domain* and *Generic Subdomain.* Sometimes a Bounded Context is created or acquired to support the business. If it models some aspect of the business that is essential, yet not Core, it is a **Supporting Subdomain**. The business creates a Supporting Subdomain because it is somewhat specialized. Otherwise, if it captures nothing special to the business, yet is required for the overall business solution, it is a **Generic Subdomain**. Being Supporting or Generic doesn’t mean unimportant. These kinds of Subdomains are important to the success of the business, yet there is no need for the business to excel in these areas. It’s the Core Domain that requires excellence in implementation, since it will provide distinct advantages to the business.

图 2.2 中还出现了另外两类子域：**支撑子域（Supporting Subdomain）**和**通用子域（Generic Subdomain）**。企业有时会构建或引入限界上下文，用以支撑业务运转。如果某个子域所建模的业务环节不可或缺，但并非核心业务，那么它就是**支撑子域**。企业之所以打造支撑子域，是因为这类业务具备一定的专属特性。反之，如果该子域不具备企业独有的业务特色，却又是整体业务解决方案的必要组成部分，那么它就是**通用子域**。

归为支撑子域或通用子域，并不代表其无关紧要。这类子域对业务成功同样重要，只是企业无需在这些领域做到极致出众。唯有核心域需要在落地实现上精益求精，因为它能为企业带来独特的竞争优势。

### **Real-World Domains and Subdomains**

I have something more to tell you about domains. They have both a *problem space* and a *solution space.* The problem space enables us to think of a stra- tegic business challenge to be solved, while the solution space focuses on how we will implement the software to solve the problem of the business challenge. Here’s how that fits into what you’ve already learned:

- The problem space is the parts of the Domain that need to be developed to deliver a new Core Domain. Assessing the problem space involves exam- ining Subdomains that *already exist and those that are needed*. Thus,your problem space is the combination of the Core Domain and the Sub- domains it must use. The Subdomains in the problem space are usually different from project to project since they are used to explore a current strategic business problem. This makes Subdomains a very useful tool in assessing the problem space*.* Subdomains allow us to rapidly view differ- ent parts of the Domain that are necessary to solve a specific problem.
- The solution space is one or more Bounded Contexts, a set of specific software models. That’s because the Bounded Context ***is a specific solution*, a *realization view***, once developed. The Bounded Context is used to realize a solution as software.

关于领域，我还有一些内容要补充说明。领域包含两个部分：**问题空间（problem space）** 和**解决方案空间（solution space）**。问题空间帮助我们明确需要解决的战略性业务挑战，而解决方案空间则聚焦于如何通过软件实现，来解决这一业务挑战。这与你之前所学的内容关联如下：

- 问题空间是领域中为实现新的核心域而需要开发的部分。评估问题空间时，需要考察**已存在的子域和所需新增的子域**。因此，你的问题空间是核心域与其必须借助的子域的结合体。问题空间中的子域通常因项目而异，因为它们用于应对当前的战略性业务问题。这使得子域成为评估问题空间的一个非常实用的工具 —— 子域能让我们快速看清解决特定问题所需的领域各个不同部分。
- 解决方案空间是一个或多个限界上下文，即一组特定的软件模型。这是因为限界上下文一旦开发完成，就是一个**具体的解决方案**、一种**实现视图**。限界上下文用于将解决方案以软件的形式落地实现。

When you have a good understanding of the problem space, you then turn to the solution space. The first assessment will contribute knowledge to the second. The solution space will be strongly influenced by the existing systems and technologies, and those that are to be newly created. Here we really need to think in terms of cleanly separated Bounded Contexts because we are look- ing at the Ubiquitous Language of each. Consider these crucial questions:

- What software assets already exist, and can they be reused?

- What assets need to be acquired or created?

- How are all of these connected to each other, or integrated?

- What additional integration will be needed?

- Given the existing assets and those that need to be created, what is the required effort?

- Do the strategic initiative and all supporting projects have a high proba- bility of success, or will any one of them cause the overall program to be delayed or even fail?

- Where are the terms of the Ubiquitous Languages involved completely different?

- Where is there overlap and sharing of concepts and data between Bounded Contexts?

- How are shared terms and/or overlapping concepts mapped and trans- lated between the Bounded Contexts?

- Which Bounded Context contains the concepts that address the Core Domain and which of the [Evans] tactical patterns will be used to model it?

Remember, the efforts in developing the solutions in the Core Domain are a key business investment!

当你对**问题域**形成清晰认知后，便可转向**解决方案域**。前一阶段的评估会为后一阶段提供知识支撑。解决方案域会深受现有系统、技术以及待新建的系统与技术的影响。在此环节，我们必须基于清晰划分的**限界上下文**展开思考，因为我们需要审视每个限界上下文所对应的**通用语言**。请思考以下核心问题：

- 现有哪些软件资产？其中哪些可被复用？
- 哪些资产需要外购或全新开发？
- 所有这些资产之间如何关联或集成？
- 还需要补充哪些集成工作？
- 结合现有资产与待开发资产，所需投入的工作量是多少？
- 该战略举措及所有配套项目成功的概率是否较高？是否存在某一项目会导致整体计划延期甚至失败？
- 各相关通用语言中的术语在哪些地方存在完全差异？
- 不同限界上下文之间在概念与数据上存在哪些重叠与共享？
- 共享术语及 / 或重叠概念在各限界上下文之间如何映射与转换？
- 哪个限界上下文包含支撑**核心域**的核心概念？将采用埃文斯提出的哪些**战术模式**对其进行建模？

切记，针对核心域开展解决方案研发的投入，是一项关键的商业投资！

  ### Real-World Domains and Subdomains

I have something more to tell you about domains. They have both a problem space and a solution space. The problem space enables us to think of a strategic business challenge to be solved, while the solution space focuses on how we will implement the software to solve the problem of the business challenge. Here’s how that fits into what you’ve already learned:

- The problem space is the parts of the Domain that need to be developed to deliver a new Core Domain. Assessing the problem space involves examining Subdomains that already exist and those that are needed. Thus, your problem space is the combination of the Core Domain and the Subdomains it must use. The Subdomains in the problem space are usually different from project to project since they are used to explore a current strategic business problem. This makes Subdomains a very useful tool in assessing the problem space. Subdomains allow us to rapidly view different parts of the Domain that are necessary to solve a specific problem.
- The solution space is one or more Bounded Contexts, a set of specific software models. That’s because the Bounded Context is a specific solution, a realization view, once developed. The Bounded Context is used to realize a solution as software.

关于**领域**，我再补充一些内容：领域可划分为**问题空间**与**解决方案空间**。问题空间帮助我们梳理待解决的战略性业务难题；而解决方案空间则聚焦于如何通过软件落地，攻克这些业务问题。结合你此前掌握的知识，二者的对应关系说明如下：

- **问题空间**：指为搭建全新**核心域**，所需开发的领域范畴。评估问题空间时，需要梳理现存子域以及业务所需的新增子域。因此，问题空间由**核心域**及其依赖的各类**子域**共同组成。由于子域是用来拆解当下战略性业务问题的，不同项目对应的问题空间，其所包含的子域通常也各不相同。这也让子域成为评估问题空间的实用工具，借助它能快速梳理出：解决某一特定问题，需要用到领域中的哪些模块。
- **解决方案空间**：由一个或多个**限界上下文**构成，对应一套具体的软件模型。这是因为限界上下文是开发完成后落地的具体方案，代表着**实现视角**，我们正是通过限界上下文，把业务解决方案转化为实际的软件系统。

It is a desirable goal to align Subdomains one-to-one with Bounded Contexts. Doing so expressly segregates domain models into well-defined areas of business by objective, melding the problem space with the solution space. In practice this is not always possible, but it can work in a greenfield effort. Considering a legacy system, and probably a Big Ball of Mud, however, Subdomains often intersect Bounded Contexts, similar to what we discussed regarding Figure 2.1. In a large and complex enterprise we can employ an assessment view to understand our problem space, which can save us from making costly mistakes. We can conceptually divide a single, large Bounded Context using two or more Subdomains, or multipls as part of a single Subdomain.

理想的设计目标，是让**子域与限界上下文一一对应**。这种模式能依据业务目标，将领域模型清晰划分至边界明确的业务单元中，实现问题空间与解决方案空间的融合统一。不过在实际项目中，该目标并非总能达成，但在**从零起步的全新项目**里完全可以落地。

反观遗留系统（大多属于典型的**大泥球架构**），子域和限界上下文往往会相互交叉重叠，这和我们此前结合图 2.1 探讨的情形一致。在架构庞大、业务复杂的企业中，我们可以借助**评估视角**梳理问题空间，从而规避成本高昂的设计失误。在概念层面，我们既可以用多个子域拆分一个体量庞大的限界上下文，也可以将多个限界上下文划归为同一个子域。



Before we can execute a specific solution, we need to make an assessment of the problem space and the solution space. Here are some questions that should be answered in order to steer your project in the right direction:

- What is the name of and vision for the strategic Core Domain?
- What concepts should be considered part of the strategic Core Domain?
- What are the necessary Supporting Subdomains and the Generic Subdomains?• 必需的辅助子域名和通用子域名有哪些？
- Who should do the work in each area of the domain?
-  Can the right teams be assembled?

在落地具体解决方案之前，我们需要先对**问题空间**和**解决方案空间**开展评估。为保障项目朝着正确方向推进，必须厘清以下问题：

- 该战略级**核心域**的名称与建设愿景是什么？
- 哪些业务概念应当归入此战略核心域范畴？
- 所需的**支撑子域**与**通用子域**分别有哪些？
- 领域内各模块的工作由谁负责承接？
- 是否能够组建适配的执行团队？

If we don’t understand the vision and goals of the Core Domain and the areas of the Domain that are needed to support it, we won’t be able to strategically take advantage of them and avoid associated pitfalls. Keep problem space assessment high-level, but make it thorough. Be sure that all stakeholders are aligned with and committed to successfully delivering on the vision.

倘若没能理解核心域的愿景、目标，以及为其提供支撑的各类领域模块，我们就无法从战略层面发挥它们的价值，也难以规避随之而来的各类风险。开展问题空间评估时，**要立足宏观视角，同时做到分析全面细致**。务必让所有项目干系人达成共识，并共同致力于落地既定愿景。



When you have a good understanding of the problem space, you then turn to the solution space. The first assessment will contribute knowledge to the second. The solution space will be strongly influenced by the existing systems and technologies, and those that are to be newly created. Here we really need to think in terms of cleanly separated Bounded Contexts because we are looking at the Ubiquitous Language of each. Consider these crucial questions:

- What software assets already exist, and can they be reused?
-  What assets need to be acquired or created?
- How are all of these connected to each other, or integrated?
- What additional integration will be needed?
-  Given the existing assets and those that need to be created,what is the required effort?
- Do the strategic initiative and all supporting projects have a high probability of success, or will any one of them cause the overall program to be delayed or even fail?
- Where are the terms of the Ubiquitous Languages involved completely different?
- Where is there overlap and sharing of concepts and data between Bounded Contexts?
-  How are shared terms and/or overlapping concepts mapped and translated between the Bounded Contexts?
- Which Bounded Context contains the concepts that address the Core Domain and which of the [Evans] tactical patterns will be used to model it?

当你对**问题空间**有了充分理解后，就可以开始分析**解决方案空间**。前一阶段的评估成果，也会为后续分析提供参考依据。解决方案空间会深受现有系统、技术，以及规划新建的系统与技术的影响。这一阶段务必以**边界清晰的限界上下文**为核心思路开展分析，因为我们需要逐一审视每个上下文对应的**统一语言**。

开展分析时，需要重点解答以下关键问题：

- 目前已存在哪些软件资产？这些资产是否可以复用？
- 哪些资产需要外部采购或自主开发？
- 所有资产之间如何对接与集成？
- 还需要补充哪些集成工作？
- 结合现有资产与待新建资产，整体需要投入多少工作量？
- 本次战略举措及所有配套项目的成功概率是否较高？是否存在任一环节导致整体项目群延期甚至失败的风险？
- 各套统一语言中，有哪些业务术语存在完全不一致的情况？
- 不同限界上下文之间，哪些业务概念与数据存在重叠、共用的现象？
- 对于共用术语和重叠概念，各个限界上下文之间如何完成映射与转译？
- 由哪个限界上下文承载核心域的业务概念？又将选用埃文斯提出的哪些**战术模式**来完成该领域的建模？

### Making Sense of Bounded Contexts

Some projects fall into the trap of attempting to create an all-inclusive model, one where the goal is to get the entire organization to agree on concepts with names that have only one global meaning. Approaching a modeling effort in this way is a pitfall. First, it will be nearly impossible to establish agreement among all stakeholders that all concepts have a single, pure, and distinct global meaning. Some organizations are so large and complex that you’d never be able to get all stakeholders together, let alone establish total meaningful agreement among them.Even if you are working in a smaller company with relatively few stakeholders, establishing an enduring definition of a single global concept is still unlikely. Thus, the best position to take is to embrace the fact that differences always exist and apply Bounded Context to separately delineate each domain model where differences are explicit and well understood.

有些项目会走入一个误区：试图构建一套**大而全的统一模型**，要求整个组织对各类业务概念达成一致，让每个术语在全局范围内拥有唯一释义。这种建模方式本身就是一个隐患。

首先，想要让所有项目干系人达成共识，确保每一个业务概念都具备单一、纯粹且边界清晰的全局定义，几乎是不可能完成的事。不少企业体量庞大、业务复杂，别说让所有人在概念认知上达成深度统一，就连召集全部相关人员都难以实现。即便在规模较小、干系人数量不多的公司，想要为某个全局业务概念制定一套长期稳定的统一定义，也同样不现实。

因此，更合理的思路是：正视概念差异始终存在的客观事实，通过**限界上下文**对不同领域模型进行拆分界定，让各类概念的差异被明确区分、清晰认知。

A Bounded Context does not dictate the creation of a single kind of project artifact. It’s not an individual component, document, or diagram.3 So it’s not a JAR or DLL, but these can be used to deploy a Bounded Context as described later in the chapter.

限界上下文并不对应某一种固定的项目产出物。它既不是独立的代码组件，也不是单一文档或架构图。所以限界上下文本身不等同于 JAR 包或 DLL 文件，但本章后续会讲到，我们可以借助这类程序包来完成限界上下文的部署。



When integrations are needed, mapping must be done between Bounded Contexts. This can be a complex aspect of DDD and calls for a corresponding amount of care. We don’t usually use an object instance outside its boundary, but related objects in multiple contexts may share some subset of common state.

当多个**限界上下文**之间需要集成时，就必须在彼此之间完成**模型映射**。这是领域驱动设计中复杂度较高的环节，需要格外谨慎对待。我们通常不会将对象实例跨边界使用，但不同上下文中的关联对象，可能会存在一部分共享状态。



A Bounded Context does not necessarily encompass only the domain model. True, the model is the primary occupant of the conceptual container. However, a Bounded Context is not limited to the model only.It often marks off a system, an application, or a business service.5Sometimes a Bounded Context houses less than this if, for example, a Generic Subdomain can be produced without much more than a domain model.

**限界上下文并非只包含领域模型**。诚然，领域模型是这个概念容器里最核心的组成部分，但限界上下文的范畴绝不局限于此。它的边界常常对应一整套系统、一个应用程序或是一项业务服务。也有些时候，限界上下文的覆盖范围会更小。例如搭建**通用子域**时，往往仅需实现领域模型即可，无需额外配套其他能力，这类场景下的限界上下文就仅承载模型本身。