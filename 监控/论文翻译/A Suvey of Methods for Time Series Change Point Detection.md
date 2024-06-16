# A Suvey of Methods for Time Series Change Point Detection

**Samaneh Aminikhanghahi** and **Diane J. Cook**

## **Abstract**

变点是时间序列数据中的突变。这种突变可能表示状态之间发生的过渡。变点的检测在时间序列的建模和预测中非常有用，并在医疗状况监测、气候变化检测、语音和图像分析以及人类活动分析等应用领域中有所应用。这篇综述文章列举、分类并比较了许多用于检测时间序列中变点的方法。所研究的方法包括已经引入和评估的监督和无监督算法。我们引入了几项标准来比较这些算法。最后，我们提出了一些供社区考虑的重大挑战。

## Keywords

Change point detection; Time series data; Segmentation; Machine learning; Data mining

## 1 INTRODUCTION

时间序列分析在包括医学、航空航天、金融、商业、气象和娱乐在内的各个领域变得越来越重要。时间序列数据是描述系统行为的随时间变化的测量序列。这些行为可能由于外部事件和/或内部系统动力学/分布的变化而随时间变化。变点检测（CPD）是发现数据中属性发生突变的问题。分割、边缘检测、事件检测和异常检测是一些类似的概念，有时也会与变点检测一起应用。变点检测与众所周知的变点估计或变点挖掘问题密切相关。然而，与CPD不同，变点估计试图建模和解释已知的时间序列变化，而不是识别变化的发生。变点估计的重点是描述已知变化的性质和程度。

在本文中，我们对变点检测这一主题进行了综述，并研究了该领域的最新研究。变点检测在数据挖掘、统计学和计算机科学领域已经研究了几十年。这个问题涵盖了广泛的现实世界问题。以下是一些示例。

**医疗状况监测**：对患者健康的连续监测涉及对生理变量（如心率、脑电图（EEG）和心电图（ECG））中的趋势检测，以实现自动化、实时监测。研究还探讨了特定医疗问题（如睡眠问题、癫痫、磁共振成像（MRI）解读以及对脑活动的理解）的变点检测。 

**气候变化检测**：由于气候变化的可能发生和大气中温室气体的增加，利用变点检测的气候分析、监测和预测方法在过去几十年变得越来越重要。 

**语音识别**：语音识别是将口语转换为文字或文本的过程。变点检测方法在这里被应用于音频分割和识别沉默、句子、单词和噪音之间的边界。 

**图像分析**：研究人员和从业者随着时间收集图像数据或视频数据，用于基于视频的监控。检测突发事件（如安全漏洞）可以被表述为变点问题。在这里，每个时间点的观测值是图像的数字编码。 

**人类活动分析**：基于从智能家居或移动设备观测到的传感器数据的特征，检测活动断点或过渡可以被表述为变点检测。这些变点对于分割活动、在最小化干扰的情况下与人类交互、提供活动感知服务以及检测行为变化（从而提供健康状态的见解）非常有用。

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
where $x_i$ is a d-dimensional data vector arriving at time stamp i

**Definition 2: ** A ***stationary time series*** is a finite variance process whose statistical properties are all constant over time. This definition assumes that

- The mean value function $μ_t = E (x_t ) $​ is constant and does not depend on time t .
- The **auto covariance function** $γ(s , t ) = cov (x_s , x_t ) = E [(x_s − μ_s )(x_t − μ_t )]$ depends on time stamps s and t only through their time difference, or |s – t| .

**Definition 3: ** ***Independent and identically distributed (i.i.d.) (独立同分布) variables*** are mutually independent of each other, and are identically distributed in the sense that they are drawn from the same probability distribution. An i.i.d. time series is a special case of a stationary time series.

**Definition 4:** Given a time series $T$ of fixed length $m$ (a subset of a time series data stream) and $x_t$ as a series sample at time $t$ , a matrix $WM$ of all possible subsequences of length $k$ can be built by moving a sliding window of size $k$ across $T$ and placing subsequence $X_p = \{x_p ,x_{p +1}, … , x_{p +k} \}$ (Figure 2) in the $p^{th}$ row of $WM$ . The size of the resulting matrix $WM$ is $(m − k + 1) × n $

![image-20240616185649643](../../images/monitor/image-20240616185649643.png)

**Definition 5:** In a time series, using sliding window $X_t$ as a sample instead of $x_t$ , an ***interval $χ_t$*** with Hankel matrix $\{X_t , X_{t +1}, … , X_{t +n –1}\}$ as shown in Figure 2 will be a set of $n$ retrospective subsequence samples starting at time t 

**Definition 6: ** A ***change point*** represents a transition between different states in a process that

generates the time series data.

**Definition 7:** Let $\{x_m, x_{m+1}, . . , x_n \}$ be a sequence of time series variables. ***Change point detection (CPD)*** can be defined as the problem of hypothesis testing between two alternatives, the null hypothesis $H_0$: “No change occurs” and the alternative hypothesis $H_A$ : “A change occurs” 

1. $H_0$: $ℙ_{X_m} = ⋯ = ℙ_{X_k} = ⋯ = ℙ_{X_n}$.
2. $H_A$ : There exists  $m < k^* < n$ such that $ℙ_{X_m} = ⋯ = ℙ_{X_{k^*}} \neq ℙ_{X_{k^* + 1}} = ⋯ = ℙ_{X_n}$.

  where $ℙ_{X_i}$ is the probability density function of the sliding window start at point $x_i$ and $k^* $is a change point.

### 2.2 Criteria

在上一节中，我们对传统的变点检测进行了正式介绍。然而，变点检测的实际应用引入了一些需要解决的新挑战。这里我们介绍并描述其中的一些挑战。

#### **2.2.1 Online detection**

