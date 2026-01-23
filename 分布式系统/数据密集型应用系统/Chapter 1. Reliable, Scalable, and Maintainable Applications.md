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