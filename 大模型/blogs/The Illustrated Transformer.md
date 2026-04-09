## The Illustrated Transformer

原版文章链接：https://jalammar.github.io/illustrated-transformer/

In the [previous post, we looked at Attention](https://jalammar.github.io/visualizing-neural-machine-translation-mechanics-of-seq2seq-models-with-attention/) – a ubiquitous method in modern deep learning models. Attention is a concept that helped improve the performance of neural machine translation applications. In this post, we will look at **The Transformer** – a model that uses attention to boost the speed with which these models can be trained. The Transformer outperforms the Google Neural Machine Translation model in specific tasks. The biggest benefit, however, comes from how The Transformer lends itself to parallelization. It is in fact Google Cloud’s recommendation to use The Transformer as a reference model to use their [Cloud TPU](https://cloud.google.com/tpu/) offering. So let’s try to break the model apart and look at how it functions.

在上一篇文章中，我们讲解了**注意力机制（Attention）**—— 这是现代深度学习模型中极为通用的一种方法。注意力机制有效提升了神经机器翻译任务的模型性能。本文中，我们将深入解析**Transformer 模型**：这是一种依托注意力机制、大幅提升模型训练速度的架构。Transformer 在特定任务上的表现超越了谷歌神经机器翻译模型，而它最核心的优势，在于**天生适配并行化计算**。事实上，谷歌云官方也推荐将 Transformer 作为其**云 TPU**服务的参考模型。接下来，我们就拆解这个模型，剖析它的运行原理。

The Transformer was proposed in the paper [Attention is All You Need](https://arxiv.org/abs/1706.03762). A TensorFlow implementation of it is available as a part of the [Tensor2Tensor](https://github.com/tensorflow/tensor2tensor) package. Harvard’s NLP group created a [guide annotating the paper with PyTorch implementation](http://nlp.seas.harvard.edu/2018/04/03/attention.html). In this post, we will attempt to oversimplify things a bit and introduce the concepts one by one to hopefully make it easier to understand to people without in-depth knowledge of the subject matter.

Transformer 模型出自论文《**Attention Is All You Need**》（《注意力机制足矣》）。该模型的 TensorFlow 实现版本已集成在**Tensor2Tensor**工具包中。哈佛大学自然语言处理团队还制作了一份**附带 PyTorch 代码逐行注释的论文解读指南**。本文会尽量简化复杂概念，逐一拆解讲解，希望能让没有深厚专业背景的读者也轻松理解。

### A High-Level Look

