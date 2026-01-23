[toc]

## Chapter 2. Data Models and Query Languages

第二章 数据模型和查询语言

### Relational Model Versus Document Model 

关系模型和文档模型

The advantage of using an ID is that because it has no meaning to humans,it neverneeds to change: the ID can remain the same, even if the informationit identifieschanges. Anything that is meaningful to humans may need tochange sometime inthe future—and if that information is duplicated, all theredundant copies need to beupdated. That incurs write overheads, and risksinconsistencies (where some copiesof the information are updated butothers aren’t). Removing such duplication is thekey idea behind normalization in databases

使用标识符（ID）的优势在于，**它对人类不具备任何语义含义**，因此永远无需修改：即便其标识的信息发生变化，ID 也可以保持不变。任何对人类有语义含义的信息，未来都有可能需要修改 —— 而且如果这类信息存在重复存储的情况，那么所有冗余副本都需要逐一更新。这不仅会产生**写入开销**，还会带来**数据不一致的风险**（即部分信息副本完成了更新，其他副本却未同步更新）。**消除此类数据冗余**，正是数据库**规范化**设计的核心理念。