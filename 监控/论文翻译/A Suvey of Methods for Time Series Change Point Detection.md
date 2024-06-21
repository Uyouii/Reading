# A Suvey of Methods for Time Series Change Point Detection

**Samaneh Aminikhanghahi** and **Diane J. Cook**

## **Abstract**

变点是时间序列数据中的突变。这种突变可能表示状态之间发生的过渡。变点的检测在时间序列的建模和预测中非常有用，并在医疗状况监测、气候变化检测、语音和图像分析以及人类活动分析等应用领域中有所应用。这篇综述文章列举、分类并比较了许多用于检测时间序列中变点的方法。所研究的方法包括已经引入和评估的监督和无监督算法。我们引入了几项标准来比较这些算法。最后，我们提出了一些供社区考虑的重大挑战。

## Keywords

Change point detection; Time series data; Segmentation; Machine learning; Data mining

## 1 INTRODUCTION

时间序列分析在包括医学、航空航天、金融、商业、气象和娱乐在内的各个领域变得越来越重要。时间序列数据是描述系统行为的随时间变化的测量序列。这些行为可能由于外部事件和/或内部系统动力学/分布的变化而随时间变化[1]。变点检测（CPD）是发现数据中属性发生突变的问题[2]。分割、边缘检测、事件检测和异常检测是一些类似的概念，有时也会与变点检测一起应用。变点检测与众所周知的变点估计或变点挖掘问题密切相关[3] [4] [5]。然而，与CPD不同，变点估计试图建模和解释已知的时间序列变化，而不是识别变化的发生。变点估计的重点是描述已知变化的性质和程度。

在本文中，我们对变点检测这一主题进行了综述，并研究了该领域的最新研究。变点检测在数据挖掘、统计学和计算机科学领域已经研究了几十年。这个问题涵盖了广泛的现实世界问题。以下是一些示例。

**医疗状况监测**：对患者健康的连续监测涉及对生理变量（如心率、脑电图（EEG）和心电图（ECG））中的趋势检测，以实现自动化、实时监测。研究还探讨了特定医疗问题（如睡眠问题、癫痫、磁共振成像（MRI）解读以及对脑活动的理解）的变点检测 [6] [7] [8] [9]。 

**气候变化检测**：由于气候变化的可能发生和大气中温室气体的增加，利用变点检测的气候分析、监测和预测方法在过去几十年变得越来越重要[10] [11] [12]。 

**语音识别**：语音识别是将口语转换为文字或文本的过程。变点检测方法在这里被应用于音频分割和识别沉默、句子、单词和噪音之间的边界。 

**图像分析**：研究人员和从业者随着时间收集图像数据或视频数据，用于基于视频的监控。检测突发事件（如安全漏洞）可以被表述为变点问题。在这里，每个时间点的观测值是图像的数字编码 [15]。 

**人类活动分析**：基于从智能家居或移动设备观测到的传感器数据的特征，检测活动断点或过渡可以被表述为变点检测。这些变点对于分割活动、在最小化干扰的情况下与人类交互、提供活动感知服务以及检测行为变化（从而提供健康状态的见解）非常有用 [13 - 20] 。

在本综述中，我们将解释变点检测问题，并探讨如何使用不同的监督和无监督方法来检测时间序列数据中的变点。我们将基于它们的成本、限制和性能对所研究的技术进行比较和对比。最后，我们讨论研究中的空白，总结变点应用中出现的挑战，并提供继续研究的建议。

## 2 BACKGROUND

图1绘制了包含多个变点的时间序列示例。数据展示了1899年至2010年期间斯瓦尔巴群岛的长期平均年温度趋势。这些数据可以用于气候变化检测。该图突显了在此期间斯瓦尔巴群岛的气候经历了六个不同的阶段。我们将时间序列的这些部分称为时间序列的状态，或者称为过程参数不变的时间段。两个连续的不同状态由变点区分。变点检测的目标是通过发现这些变点来识别这些状态边界。

![image-20240616174004911](../../images/monitor/image-20240616174004911.png)

### 2.1 **Definitions and Problem Formulation**

我们首先介绍在本综述中使用的关键术语的定义。

**Definition 1: ** A time series data stream is an infinite sequence of elements
$$
S = \{x_1,...,x_i,... \}
$$
where $x_i$ is a d-dimensional data vector arriving at time stamp i [17]

**Definition 2: ** A ***stationary time series*** is a finite variance process whose statistical properties are all constant over time. This definition assumes that

- The mean value function $μ_t = E (x_t ) $​ is constant and does not depend on time t .
- The **auto covariance function** $γ(s , t ) = cov (x_s , x_t ) = E [(x_s − μ_s )(x_t − μ_t )]$ depends on time stamps s and t only through their time difference, or |s – t| .

**Definition 3: ** ***Independent and identically distributed (i.i.d.) (独立同分布) variables*** are mutually independent of each other, and are identically distributed in the sense that they are drawn from the same probability distribution. An i.i.d. time series is a special case of a stationary time series.

**Definition 4:** Given a time series $T$ of fixed length $m$ (a subset of a time series data stream) and $x_t$ as a series sample at time $t$ , a matrix $WM$ of all possible subsequences of length $k$ can be built by moving a sliding window of size $k$ across $T$ and placing subsequence $X_p = \{x_p ,x_{p +1}, … , x_{p +k} \}$ (Figure 2) in the $p^{th}$ row of $WM$ . The size of the resulting matrix $WM$ is $(m − k + 1) × n $

![image-20240616185649643](../../images/monitor/image-20240616185649643.png)

**Definition 5:** In a time series, using sliding window $X_t$ as a sample instead of $x_t$ , an ***interval $χ_t$*** with Hankel matrix $\{X_t , X_{t +1}, … , X_{t +n –1}\}$ as shown in Figure 2 will be a set of $n$ retrospective subsequence samples starting at time t [2] [21] [22]

**Definition 6: ** A ***change point*** represents a transition between different states in a process that

generates the time series data.

**Definition 7:** Let $\{x_m, x_{m+1}, . . , x_n \}$ be a sequence of time series variables. ***Change point detection (CPD)*** can be defined as the problem of hypothesis testing between two alternatives, the null hypothesis $H_0$: “No change occurs” and the alternative hypothesis $H_A$ : “A change occurs”  [23] [24]

1. $H_0$: $ℙ_{X_m} = ⋯ = ℙ_{X_k} = ⋯ = ℙ_{X_n}$.
2. $H_A$ : There exists  $m < k^* < n$ such that $ℙ_{X_m} = ⋯ = ℙ_{X_{k^*}} \neq ℙ_{X_{k^* + 1}} = ⋯ = ℙ_{X_n}$.

  where $ℙ_{X_i}$ is the probability density function of the sliding window start at point $x_i$ and $k^* $is a change point.

### 2.2 Criteria

在上一节中，我们对传统的变点检测进行了正式介绍。然而，变点检测的实际应用引入了一些需要解决的新挑战。这里我们介绍并描述其中的一些挑战。

#### **2.2.1 Online detection**

变点检测算法传统上被分类为“在线”(online)或“离线”(offline)。离线算法一次考虑整个数据集，回溯时间以识别变点发生的位置。这种情况下的目标通常是在批处理模式下识别序列中的所有变点。相比之下，在线或实时算法与它们监控的过程同时运行，在每个数据点可用时立即处理，其目标是在变点发生后尽快检测到变点，理想情况下是在下一个数据点到来之前。[25]

实际上，没有变点检测算法能在完美的实时环境中运行，因为它们必须检查新数据后才能确定变点是否发生在旧数据和新数据点之间。然而，不同的在线算法在变点检测发生之前需要不同数量的新数据。基于这一观察，我们将在本文中定义一个新术语。我们将称需要至少 $\epsilon$ 个数据样本才能在新批数据中找到变点的在线算法为 $\epsilon$-***real time algorithm**。*然后，离线算法可以视为 $\infty$-real，而完全在线的算法是 1-real 的，因为它可以针对每个数据点预测是否在新数据点到来之前发生变点。较小的 $\epsilon$ 值可能导致更强、更具响应性的变点检测算法。

#### 2.2.2 Scalability

来自人类活动和遥感卫星等来源的现实世界时间序列数据在数据点数量和维度数量上都变得越来越大。变点检测方法需要设计得具有计算效率，以便能够扩展到海量数据规模[26]。因此，我们比较了不同 CPD 算法的计算成本，以确定哪种算法能尽可能快地达到最佳（或足够好）的解决方案。比较算法计算成本的一种方法是确定算法是参数化的还是非参数化的。区分参数化和非参数化方法很重要，因为非参数化方法在处理大规模数据集方面表现出更大的成功。此外，参数化方法的计算成本高于非参数化方法，并且在数据集规模增大时扩展性较差[23]。

**参数化方法** (parametric approach)指定要由模型学习的特定函数形式，然后根据有标签的训练数据估计未知参数。一旦模型训练完成，训练示例可以被丢弃。相比之下，**非参数化方法** (nonparametric method)不对底层函数的形式做任何假设。相应的代价是，在进行推理时必须保留所有可用数据[27]。

成功的算法必须在决策质量和计算成本之间进行权衡。一种有前途的方法是使用任意时间（anytime）算法[28]，这种算法允许在任何时候中断执行并输出迄今为止获得的最佳解决方案。类似的方法是合同（contract）算法，这种算法也在计算时间和解决方案质量之间进行权衡，但在开始执行前预先指定允许的运行时间，作为一种合同约定。与任意时间算法不同，合同算法在执行前接收指定的允许执行时间参数。如果合同算法在分配时间完成之前被中断，可能不会产生任何有用的结果。可中断算法（例如任意时间算法）是一种执行时间不预先给定的算法，因此必须准备在任何时刻被中断，但它利用可用的时间不断提高其解决方案的质量。通常，每个可中断算法都是一个简单的合同算法，但反之则不成立[29。

#### 2.2.3 Algorithm constraints

变点检测（CPD）的方法还可以根据对输入数据和算法的要求进行区分。这些约束在选择适合特定数据序列的变点检测技术时非常重要。与时间序列数据性质相关的约束可能源于数据的平稳性、独立同分布（i.i.d.）、维度性或连续性[32]。

一些算法需要关于数据的信息，例如数据中的变点数量、系统中的状态数量以及系统状态的特征[33] [34]。参数化方法中的另一个重要问题是算法对初始参数值选择的敏感程度。

### **2.3 Performance Evaluation**

为了比较不同的 CPD 算法并估计预期的结果性能，需要性能衡量标准。已经引入了许多性能指标来评估变点检测算法，基于它们所做的决策类型[35]。CPD 算法的输出可能包含以下内容：

- Change-point yes/no decisions (the algorithm is a binary classifier)
- 不同精度水平的变点识别（即，变点发生在 x 时间单位内。此类型算法利用多类分类器或无监督学习方法）
- The time of the next change point (or the times of all change points in the series)

对于前两种类型的输出，可以利用评估监督学习算法的标准方法来评估变点检测器的性能。评估监督变点学习器性能的第一步是生成一个混淆矩阵，总结实际和预测的类别。表1展示了二元变点分类器的混淆矩阵。

![image-20240617193301477](../../images/monitor/image-20240617193301477.png)

- TP: True Positive，真正例
- FP: False Positive，假正例
- FN: False Negative，假负例
- TN: True Negative，真负例

以下是一些可以用来评估 CPD 算法的有用性能指标。这些指标虽然是在二元分类的背景下描述的，但可以通过独立或组合提供每个类别的衡量标准来扩展到更多类别的分类。

**准确率（Accuracy）**, calculated as the ratio of correctly-classified data points to total data points。这一指标提供了算法性能的高层次概念。其对应指标是错误率（Error Rate），计算公式为 1 - Accuracy。尽管准确率和错误率能够衡量总体性能，但它们并不能提供有关错误来源或错误在不同类别中的分布情况的见解。此外，对于类别不平衡的数据集（这在变点检测中很常见），它们在评估性能方面无效，因为它们认为不同类型的分类错误同样重要。在这种情况下，Sensitivity和 g-mean (几何平均数) 是有用的评估指标。
$$
Accurrancy = \frac{TP + TN}{TP + FP + FN + TN}
$$
**敏感性（Sensitivity）**, 也称为召回率（Recall）或真正例率（True Positive Rate, TP Rate）。这指的是目标类别（变点）中被正确识别的部分。
$$
Sensitivity = Recall = TP Rate = \frac{TP}{TP + FN}
$$
**G-mean（几何平均数）**。变点检测通常会导致类分布不平衡的学习问题，因为变点与总数据的比例很小。因此，G-mean 通常被用作变点检测性能的指标。它利用敏感性（Sensitivity）和特异性（Specificity）来评估算法的性能，既考虑了正类准确率（敏感性）也考虑了负类准确率（特异性）。
$$
G-mean = \sqrt{Sensitivity \times Specificity} = \sqrt{\frac{TP}{TP + FN} \times \frac{TN}{FP + TN}}
$$
**精确率（Precision）**。这是计算为真正例数据点（变点）与被分类为变点的总点数之比。
$$
Precision = \frac{TP}{TP + FP}
$$
**F-measure（也称为 f-score 或 f1 score）**。这种度量提供了一种结合精确率（Precision）和召回率（Recall）来衡量 CPD 算法整体有效性的方法。F-measure 计算为精确率和召回率的加权重要性比率。

![image-20240618122109397](../../images/monitor/image-20240618122109397.png)

**接收者操作特征曲线（Receiver Operating Characteristics Curve, ROC）**。基于 ROC 的评估有助于明确分析真正例率和假正例率之间的权衡。这是通过绘制一个二维图来实现的，横轴表示假正例率，纵轴表示真正例率。一个 CPD 算法会产生一个 (TP_Rate, FP_Rate) 对应于 ROC 空间中的一个点。通常，如果一个算法的点比另一个算法的点更接近 (0,1) 坐标（左上角），则该算法被认为优于另一个算法。为了评估算法的整体性能，可以看 ROC 曲线下的面积，称为 **AUC（Area Under the Curve）**。一般来说，我们希望假正例率低而真正例率高。这意味着 AUC 值越接近 1，算法越强。另一个可以从 ROC 曲线中导出的有用度量是等错误率**（Equal Error Rate, EER）**，这是假正例率和假负例率相等的点。一个强大的算法会使这个点保持在较低水平。

**精确率-召回率曲线（Precision-Recall Curve, PR Curve）**。可以生成 RPC 并用来比较不同的 CPD 算法。PR 曲线将精确率（Precision）作为召回率（Recall）的函数进行绘制。与在 ROC 曲线中理想的算法性能由位于空间的左上角的点表示不同，在 PR 空间中理想的性能是在右上角。与 ROC 曲线类似，可以计算 PRC下的面积来比较两个算法并尝试优化 CPD 性能。特别是当类别分布高度不均衡时，PR 曲线提供了有见地的分析。

如果将检测到的变点（Change Point, CP）与实际变点之间的时间差作为性能衡量标准（使用监督或无监督的 CPD 方法），那么上述指标就不再适用。评估这些算法的性能不像前一种情况那么简单，因为没有单一的标签来衡量算法的性能。然而，对于这种情况，仍然存在许多有用的指标，包括：

**平均绝对误差（Mean Absolute Error, MAE）**。这直接衡量预测的变点（CP）与实际变点的接近程度。预测的变点时间与实际变点时间的差的绝对值被求和，并在每个变点上进行归一化。

![image-20240620152129889](../../images/monitor/image-20240620152129889.png)

**均方误差（Mean Squared Error, MSE）** 是 MAE 的一个著名替代指标。在这种情况下，由于误差被平方，结果度量在分类数据中如果存在一些显著的异常值时将会非常大。

![image-20240620152508889](../../images/monitor/image-20240620152508889.png)

**平均符号差（Mean Signed Difference, MSD）**。除了计算预测变点与实际变点之间的差异外，该度量还考虑了误差的方向（预测在实际变点时间之前或之后）。

![image-20240620152632755](../../images/monitor/image-20240620152632755.png)

**均方根误差（Root Mean Squared Error, RMSE）**。它聚合了预测误差和实际误差之间的差异，并对每个差异进行平方以消除符号因素。最终计算平方根以抵消对单个差异进行平方的缩放因素。

![image-20240620152742867](../../images/monitor/image-20240620152742867.png)

**归一化均方根误差（Normalized Root Mean Squared Error, NRMSE）**。该度量消除了预测值单位大小对误差值的敏感性。NRMSE 使不同数据集之间的误差比较更加直接，并有助于解释误差度量。两种常见的方法是将误差归一化到观察到的变点的范围，或归一化到观察到的变点的均值。

![image-20240620153157394](../../images/monitor/image-20240620153157394.png)

## 3 Review

许多机器学习算法已经被设计、增强和改编用于变点检测。在这里，我们概述了一些常用于变点检测问题的基本算法。这些技术包括监督和无监督的方法，选择依据是算法的预期结果。

### 3.1 Supervised Methods

监督学习算法(Supervised learning algorithm) 是机器学习算法，通过从输入数据到数据目标属性（通常是类别标签）的映射来学习。图3概述了用于变点检测的监督方法。当采用监督方法进行变点检测时，机器学习算法可以被训练为二元或多类分类器。如果指定了状态数量，变点检测算法将被训练以找到每个状态边界。滑动窗口通过数据移动，将每两个数据点之间的每个可能划分视为一个潜在的变点。虽然这种方法的训练阶段较为简单，但需要提供足够数量和多样性的训练数据来表示所有类别。另一方面，分别检测每个类别提供了足够的信息，以找到检测到的变化的性质和数量。各种分类器可以用于这个学习问题。例如，决策树 (decision tree) [33] [34] [36] [37]、朴素贝叶斯(naive Bayes) [33]、贝叶斯网络(Bayesian net) [34]、支持向量机(support vector machine) [33] [34]、最近邻(nearest neighbor) [33] [20]、隐马尔可夫模型(hidden Markov model) [38] [39] [33]、条件随机场(donditional random field) [34] 和高斯混合模型（Gaussian mixture model, GMM）[38] [39]。

![image-20240620154306500](../../images/monitor/image-20240620154306500.png)

另一种方法是将变点检测视为二元分类问题(binary class problem)，其中所有可能的状态转换（change point）序列代表一类，所有状态内的序列代表另一类。虽然在这种情况下只需要学习两类，但如果可能的转换类型数量很大，这将是一个更复杂的学习问题。与前一种监督方法一样，在这种学习方法中，输入向量中的每个特征都表示可能变化的来源 [35]。因此，任何生成可解释模型（如决策树[decision tree) 或规则学习器[rule learner]）的监督学习算法不仅会识别变化，还会描述变化的性质。支持向量机(support vector machines) [21] [40]、朴素贝叶斯(naive bayes) [21]和逻辑回归(logistic regression) [21]已经使用这种方法进行了测试。由于通常状态内的序列比变点序列多得多，这类问题也会受到极端类不平衡的影响。

另一种监督方法是使用虚拟分类器（Virtual Classifier，VC）[4]。这种方法不仅仅是检测变化，而是实际解释发生在两个连续窗口之间的变化。虚拟分类器为第一个窗口中的每个样本附加一个假设标签（+1），为第二个窗口中的每个样本附加（-1），然后使用任何基于标记数据点的监督方法训练虚拟分类器(VC)。如果在两个窗口之间存在变点，它们应该被分类器正确分类，并且分类准确率 $p$ 应显著高于随机噪声 $p_{rand} = 0.5$。为了测试变化得分的显著性，使用二项分布(binomial distribution)的逆生存(inverse survival)函数来确定临界值(critical value), $p_{critical}$，在该值处伯努利试验(Berniulli trials) 预计以 $\alpha$ confidence level超过 $p_{rand}$。最后，如果 $p > p_{critical}$，则两个窗口之间存在显著变化。一旦检测到变点，使用两个相邻窗口中的所有样本重新训练分类器。如果某些特征在分类器中起主导作用，那么它们就是表征差异的特征。

### 3.2 Unsupervised Methods

无监督学习算法(unsupervised learning algorithms) 通常用于在未标记数据中发现模式。在变点检测的背景下，这些算法可以用于分割时间序列数据，从而基于数据的统计特征找到变点。无监督分割具有吸引力，因为它可以处理各种不同的情况，而不需要为每种情况进行事先训练。图4概述了用于变点检测的无监督方法。早期的方法利用**似然比(likelihood ratio)**，基于这样的观察：如果两个连续区间属于同一状态，则它们的概率密度(probability density) 相同。另一种传统解决方案是**子空间建模(subspace modelling)**，它使用状态空间(state space) 表示时间序列，从而通过预测状态空间参数检测变点。**概率(probabilistic)方法**基于自上一个候选变点以来观察到的数据估计新区间的概率分布(probability distributions)。相比之下，**基于核的方法(kernel-based methods)** 将观测映射到更高维的特征空间(feature space)，并通过比较每个子序列的同质性(homogeneity)来检测变点。**基于图的方法(graph based technique)**是新引入的方法，它将时间序列观测表示为图，并应用统计检验(statistical tests)基于这种表示来检测变点。最后，**聚类方法(clustering methods)**将时间序列数据分组到各自的状态中，并通过识别状态特征之间的差异来发现变化。

![image-20240621120706772](../../images/monitor/image-20240621120706772.png)

#### 3.2.1 Likelihood Ratio Methods

典型的统计变点检测公式是分析候选变点(dandidate change point)前后数据的概率分布(probability distributions)，如果这两个分布显著不同，则将该候选点识别为变点。在这些方法中，通过监测时间序列数据中两个连续区间之间的似然比的对数(logarithm of the likelihood ratio) 来检测变点[2]。

这种策略需要两个步骤。首先，分别计算两个连续区间的概率密度(probability density)。其次，计算这些概率密度的比率。最常见的变点算法是**累积和（Cumulative Sum, CUSUM**）[41] [42] [43] [44]，该算法相对于指定目标累积偏差( accumulates deviations relative)，当累积和超过指定阈值时，指示存在变点。

**Change Finder** [2] [45] [22] 是另一种常用的方法，它将变点检测问题转化为基于时间序列的异常检测。此方法将**自回归（Auto Regression, AR）**模型拟合到数据上，以表示时间序列的统计行为，并逐步更新其参数估计，从而逐渐折扣(gradually discounted) 过去样本的影响。考虑时间序列 $xt$，我们可以使用 k 阶自回归模型(AR mode of kth) 来对时间序列建模：
$$
x_t = wx^{t-1}_{t-k} + \varepsilon
$$
Where $x^{t-1}_{t-k} = (x_{t-1}, x_{t-2},...,x_{t-k})$ are previous observation,  $\omega = (\omega_1, \dots, \omega_k) \in \mathbb{R}^k$ 是常数，$\epsilon$ 是按照高斯分布生成的类似白噪声的正态随机变量。通过更新模型参数，可以在时间 $t$ 计算概率密度函数(probability density function)，并得到一系列概率密度 $\{p_t : t = 1, 2, \dots\}$。接下来，通过给每个数据点评分生成一个辅助时间序列(auniliary time-series) $y_t$。这个评分函数定义为对数似然的平均值(average of the log-likelihood)，$Score(y_t) = -\log p_{t-1}(y_t)$，或统计偏差(statistical deviation)，即 $Score(y_t) = d(p_{t-1}, p_t)$，其中 $d(*, *)$是由各种距离函数提供的，包括变差距离(variation distance)、Hellinger 距离(Hellinger distance)或二次距离(quadratic distance)。新的时间序列数据表示每对连续时间序列区间之间的差异。为了检测变点，需要知道两对连续差异之间是否存在突变。为此，再拟合一个自回归模型(AR Model)到基于差异的时间序列，并构建一个新的概率密度函数序列 $\{q_t : t = 1, 2, \dots \}$。变点评分使用前述的评分函数定义。较高的评分表示变点的可能性较高。

由于这些方法依赖于预先设计的参数模型，因此在实际的变点检测场景中灵活性较差，一些最近的研究引入了更灵活的非参数变体，通过直接估计概率密度比率来避免进行密度估计。这种密度比率估计 (density-ratio estimation)的基本原理是，了解两个密度意味着了解密度比率，但反之则不然：知道比率并不一定意味着知道两个密度，因为这种分解不是唯一的。因此，直接密度比率估计比密度估计要简单得多。基于这一思想，已经开发了直接密度比率估计的方法[2] [22]。这些方法通过非参数高斯核模型 (non-parametric Gaussian kernel model) 来建模两个连续区间 $\chi$  和 $\chi'$之间的密度比率，如下所示：

![image-20240621152814250](../../images/monitor/image-20240621152814250.png)

其中，$p(\chi)$ 是区间 $\chi$ 的概率分布，$ \theta = (\theta_1, \dots, \theta_n)^T $ 是从数据样本中学习到的参数，$X$ 是滑动窗口，且 $\sigma > 0$是核心参数。在训练阶段，通过最小化不相似度 (dissimilarity measure)来确定参数 $\theta$。在测试阶段，给定一个密度比率估计器(density-ratio estimator) $g(\chi)$，计算两个样本 $\chi_t$ 和 $\chi_{t+n}$ 之间不相似度的近似值。不相似度越高，该点越有可能是变点[2] [22]。

一种常用的不相似度量方法是 **Kullback-Leibler（KL）散度**：

![image-20240621154345600](../../images/monitor/image-20240621154345600.png)

Kullback-Leibler 重要性估计程序 (KLIEP) 使用 KL divergence 来估计密度比率。这个问题是一个凸优化问题(convex optimization problem)，因此可以通过梯度投影法 (gradient projection method) 简单地获得唯一的全局最优解 $θ$。投影梯度下降在每一步都朝负梯度方向移动，并投影到可行参数上。KL divergence的近似值由以下公式给出[2] [22]。

![image-20240621155236031](../../images/monitor/image-20240621155236031.png)

另一种直接密度比率估计器是**无约束最小二乘重要性拟合（uLSIF, Unconstrained Least-Squares Importance Fitting）**，它使用皮尔逊（PE, Pearson）散度作为不相似度量(dissimilarity measure)，表示如下：

![image-20240621155513744](../../images/monitor/image-20240621155513744.png)

作为 uLSIF 训练准则的一部分，密度比率模型(density-ratio model) 在平方损失(squared loss)下拟合到真实的密度比率。皮尔逊散度(approximator of the PE) 的近似值如下【22】：

![image-20240621155811551](../../images/monitor/image-20240621155811551.png)

根据第二个区间密度 $p' (x)$ 的条件，密度比率值可能是无界的。为了克服这个问题，采用 $0 \leq \alpha < 1 $的 α-relative PE 散度作为不相似度量，这种方法称为**Relative uLSIF (Relative uLSIF, RuLSIF)**。RuLSIF 度量如下：

![image-20240621160628000](../../images/monitor/image-20240621160628000.png)

当 α = 0 时，α-relative density ratio 简化为普通密度比率，并且随着 α 的增大，密度比率趋于“平滑”(smoother)。RuLSIF 的新颖之处在于其始终有上界 $\frac{1}{α}$，并且已经证明，相对密度比率估计的收敛速度比 uLSIF 更快 [22] [46]。

最近提出了一种**基于 Kullback-Leibler 统计的半参数变点检测器（Semi-Parametric Log-Likelihood Change Detector，SPLL）**[47] [48] [49]。假设变点前的数据（窗口 $W_1$）来自高斯混合模型(Gaussian mixture) $p_1(x)$。变点检测准则使用第二窗口 $W_2$ 中数据对数似然(log-likelihood)的上界，通过计算 $x$ 与其中心之间的最小平方马氏距离(squared Mahalanobis) 的分量索引来导出。如果 $W_2$ 不来自与 $W_1$ 相同的分布，那么距离的均值将偏离 n（其中 n 是特征空间[dimensionality of the feature space]的维度）。SPLL 的值大于或小于指定范围将表示变点。需要注意的是，所有这些估计方法的准确性都会受到数据噪声的影响  [46]。

#### **3.2.2 Subspace Model Methods**

另一项研究基于子空间 (subsapce) 分析进行变点检测，其中时间序列序列受到约束。这种方法与系统辨识方法有很强的联系，后者在控制理论领域得到了深入研究 [2]。

其中一种子空间模型方法称为**子空间辨识（Subspace Identification, SI）** [22] [50]。SI 基于系统的状态空间模型，并明确考虑了噪声因素。
$$
x(t + 1) = Ax(t) + Ke(t) \\
y(t) = Cx(t) + e(t)
$$
这里 $C$ 和 $A$ 是系统矩阵，$e(t)$ 表示系统噪声，K 是稳定的卡尔曼增益 (stationary Kalman gain)。在子空间方法中，我们使用不同的符号表示。由于在这些方法中 $x$ 表示模型状态，我们用 $y$ 表示时间序列。

在系统辨识中，扩展可观测矩阵是衡量系统的内部状态 $x(t)$ 如何通过其外部输出 $y(t)$ 来推断的一个指标。在这里，我们使用扩展可观测矩阵作为时间序列数据受约束的子空间的表示。

扩展可观测矩阵 (extended observability matrix)定义如下：

![image-20240621174107750](../../images/monitor/image-20240621174107750.png)

对于每个区间（如第2.1节所述），SI 使用 **LQ 分解 (LQ factorization)** 和标准化条件协方差(normalized conditional covariance)的**奇异值分解（SVD, Singular Value Decomposition）**来估计可观测矩阵。LQ 分解是将矩阵正交分解 (orthogonal decomposition)为下梯形矩阵 (lower trapezoidal matrices)。矩阵 $A$ 的 SVD 是将 $A$ 分解为三个矩阵的乘积 $A=UDV^T$，其中 $U$ 和 $V$ 的列是正交的 (orthonormal)，矩阵 $D$ 是对角 (diagonal) 矩阵，其对角线上的元素为正实数。在下一步中，计算子空间之间的差距，并将其用作衡量时间序列序列变化的度量。这一变化度量 $D$ 可以与指定的阈值进行比较，以确定当前点是否为变点。

![image-20240621175422997](../../images/monitor/image-20240621175422997.png)

这里，$\chi$ 表示新区间的 Hankel 矩阵，$U$ 通过对前一区间估计的扩展可观测矩阵进行 SVD 计算得出。

接下来我们将讨论的子空间模型方法称为**奇异谱变换（Singular Spectrum Transformation，SST）** [11] [22] [30]。SST 同样基于状态空间模型(state space model)，但与 SI 模型不同，它不考虑系统噪声。SST 将基于每个窗口的解释 Hankel 矩阵定义***轨迹矩阵 (trajectory matrix)***，如下公式所示：

![image-20240621180707156](../../images/monitor/image-20240621180707156.png)

其中，$L$ 是窗口长度，$K$ 是窗口数量。轨迹矩阵可以使用 SVD 分解为子矩阵。这些子矩阵由奇异值经验正交函数（singular value empirical orthogonal functions, EOF 函数）和主成分组成。基于距离的变点评分通过比较两个连续区间的轨迹矩阵的奇异谱(singular spectrums)来定义。

虽然这两种子空间模型方法都是基于预定义模型 (predefined model)的，但 SST 不考虑噪声对系统的影响。因此，与 SI 相比，它对参数值的选择更为敏感，并且在某些数据集上的准确性较低 [22] [50]。

#### **3.2.3 Probabilistic Methods**

早期的贝叶斯变点检测方法是离线的（∞ - real time），并且基于回顾性分割 (retrospective segmentation) [51] [52]。其中一种最早的在线**贝叶斯变点检测（BCPD, Bayesian change point detection）**方法是在假设一系列观测可以被划分为不重叠的状态分区的前提下提出的，并且时间序列中每个状态 ρ 内的数据是从某种概率分布 $P(x_t | \eta_{\rho})$ 独立同分布（i.i.d.）的 [31]。

与之前只考虑连续样本对的方法相比，BCPD 将新的滑动窗口特征与基于同一状态下所有先前区间的估计进行比较。BCPD 通过定义一个辅助变量 *运行长度* (*run-length*, $r_t$）来估计后验分布 (posterior distribution)，该变量表示自上一个变点以来经过的时间。给定时间点 $t$ 的运行长度，下一时间点的运行长度可以重置为 0（如果此时发生变点），或者增加 1（如果当前状态继续一个时间单位）。基于贝叶斯定理的运行长度分布可以表示为：

![image-20240621182214940](../../images/monitor/image-20240621182214940.png)

其中，$x^{(r)}_t$表示与运行长度 $r_t$ 相关联的观测集合，$P(r_t | r_{t-1})$、$P(x_t|r_{t-1},x^{(r)}_t)$和 $ P(r_{t-1}, x_{1:t-1}) $ 分别是该方程的先验(prior)、似然 (likelihood) 和递归 (recursive) 组件。条件先验在仅两个结果（$r_t = 0$ 或 $r_t = r_{t-1} + 1$）时为非零，从而简化了方程。

![image-20240621183007944](../../images/monitor/image-20240621183007944.png)

在这个方程中，$ H(\tau) = \frac{P(\tau)}{\sum_{t=\tau}^{∞} P(t)} $ 是一个风险函数 (hazard function)，定义为运行期间概率密度与概率密度总值的比率 [31] [53] [54]。似然项 (likelihood term) 表示最新数据属于当前运行的概率。这是最难计算的一项，当使用共轭指数模型 (conjugate exponential model)时，它往往是计算效率最高的 [31]。

在计算运行长度分布并更新相应的统计数据后，通过比较概率值进行变点预测。如果 $r_t$ 在分布中具有最高概率，则表示发生了变点，并且运行长度重置为 $r_t = 0$。如果没有发生变点，则运行长度加一，即  $ r_t = r_{t-1} + 1 $ [31] [53]。

这种方法后来通过在方程中结合不同子序列数据的似然性扩展到了非独立同分布（non i.i.d.）时间序列的一般情况。此外，通过使用简单近似，提出了一种简化方法，将算法复杂度从 $n^2$ 降低到 $n$。其关键思想是仅计算固定数量节点的联合概率权重 (joint probability weights)，而不是计算所有 $ \frac{n(n - 1)}{2} $ 节点的权重 [7]。

高斯过程（Gaussian Process, GP）是另一种用于平稳时间序列分析和预测的概率方法 [55]。高斯过程(GP) 是高斯分布的推广，定义为一组随机变量，其中任意有限数量的变量具有联合高斯分布 [56] [57]。在这种方法中，时间序列观测值 $\{x_t\}$ 被定义为高斯分布函数值 $f(t)$ 的噪声版本。
$$
x_t = f(t) + \varepsilon_t
$$
在这个高斯分布函数中，$\varepsilon_t$ 是噪声项，通常假设为高斯噪声项，且 $ \mathcal{N}(0, \sigma^2_n)$ 和 $ f(t) = \mathcal{GP}(0, K) $ 是由均值为零和协方差(covariance)函数 $K$ 指定的高斯过程分布函数。通常，协方差函数是使用一组超参数指定的。一种广泛使用的协方差函数是：

![image-20240621185628851](../../images/monitor/image-20240621185628851.png)
