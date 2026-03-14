---
title: "EP23: Can AI Understand Music? Latent Space and Information Bottleneck"
subtitle: "潜空间几何, 码本探测, 信息瓶颈"
episode: 23
date: 2026-02-27
duration: "7:48"
domains:
  - "Statistics/ML"
  - "Information Theory"
key_theorems:
  - "t-SNE KL Minimization"
  - "Information Bottleneck Optimality"
  - "Linear Probe Sufficiency"
  - "Emergent Specialization under Prediction Loss"
callbacks: [4, 8, 14, 21, 22]
forward_refs: [25]
weight: 23
draft: false
---

## Overview

> *中文:* "数学能量出形状，量不出意义。"

The previous episode ({{< episode-ref ep="22" >}}EP22{{< /episode-ref >}}) showed how EnCodec compresses audio into a discrete codebook of 2048 vectors in {{< m >}}\mathbb{R}^{128}{{< /m >}}. This episode asks the next question: **what did the model learn to encode?** Tonal structure? Rhythmic patterns? Something humans cannot name?

We develop three mathematical frameworks to answer this:

1. **t-SNE** reduces the 128-dimensional codebook to a 2D map, revealing that codewords cluster by musical key --- without any supervision.
2. **Linear probes** formalize the notion of "linearly decodable information" in learned representations.
3. **Information Bottleneck theory** explains *why* a model forced to compress discovers musically meaningful structure: it must discard irrelevant detail while preserving predictive content.

The episode closes with Adam Neely's challenge: even if the geometry is real, **structure is not meaning**. Jazz cannot be interpolated from blues and ragtime, and individually generated music cannot replace communal listening. The central thesis:

> **AI learns the geometric structure of music. Whether that constitutes understanding depends on what we mean by the word.**

---

## Prerequisites

- {{< episode-ref ep="4" >}}All-Interval Rows and {{< m >}}\mathbb{Z}_{12}{{< /m >}} (EP04){{< /episode-ref >}} --- cyclic group of pitch classes, circle of fifths
- {{< episode-ref ep="8" >}}Entropy and Information (EP08){{< /episode-ref >}} --- Shannon entropy, KL divergence
- {{< episode-ref ep="14" >}}Tonnetz Hodge Duality (EP14){{< /episode-ref >}} --- Tonnetz topology, torus structure of pitch space
- {{< episode-ref ep="21" >}}From Markov to Diffusion (EP21){{< /episode-ref >}} --- attention mechanism, Transformer architecture
- {{< episode-ref ep="22" >}}EnCodec and RVQ (EP22){{< /episode-ref >}} --- codebook vectors, residual vector quantization

---

## Part I: Probing the Codebook

### 23.1 t-SNE: Visualizing High-Dimensional Structure

> *中文:* "人眼看不见128维空间，但有一种叫t分布随机近邻嵌入的方法，可以把高维向量投影到一张二维图上。"

The EnCodec codebook consists of {{< m >}}N = 2048{{< /m >}} vectors in {{< m >}}\mathbb{R}^{128}{{< /m >}}. We need a method that faithfully represents local neighborhood relationships in two dimensions.

{{< definition name="Pairwise Affinity (High-Dimensional)" label="Definition 23.1" >}}
Given points {{< m >}}x_1, \ldots, x_N \in \mathbb{R}^{128}{{< /m >}}, define the conditional similarity of {{< m >}}x_j{{< /m >}} to {{< m >}}x_i{{< /m >}} as

{{< dm >}}p_{j|i} = \frac{\exp\!\bigl(-\|x_i - x_j\|^2 / 2\sigma_i^2\bigr)}{\sum_{k \neq i} \exp\!\bigl(-\|x_i - x_k\|^2 / 2\sigma_i^2\bigr)}{{< /dm >}}

where {{< m >}}\sigma_i{{< /m >}} is chosen so that the perplexity of the conditional distribution {{< m >}}P_i{{< /m >}} equals a user-specified target (typically 5--50). The **symmetrized affinity** is

{{< dm >}}p_{ij} = \frac{p_{j|i} + p_{i|j}}{2N}{{< /dm >}}

**Worked example.** Suppose {{< m >}}N = 4{{< /m >}} points with {{< m >}}\sigma_i = 1{{< /m >}} for all {{< m >}}i{{< /m >}}. If {{< m >}}\|x_1 - x_2\| = 1{{< /m >}}, {{< m >}}\|x_1 - x_3\| = 5{{< /m >}}, {{< m >}}\|x_1 - x_4\| = 5{{< /m >}}, then

{{< dm >}}p_{2|1} = \frac{e^{-1/2}}{e^{-1/2} + 2e^{-25/2}} \approx \frac{0.607}{0.607 + 2(3.7 \times 10^{-6})} \approx 1.000{{< /dm >}}

Nearly all probability mass concentrates on the nearest neighbor. This is precisely the "local neighborhood preservation" property.
{{< /definition >}}

{{< definition name="Pairwise Affinity (Low-Dimensional)" label="Definition 23.2" >}}
For the embedding coordinates {{< m >}}y_1, \ldots, y_N \in \mathbb{R}^2{{< /m >}}, define

{{< dm >}}q_{ij} = \frac{(1 + \|y_i - y_j\|^2)^{-1}}{\sum_{k \neq l} (1 + \|y_k - y_l\|^2)^{-1}}{{< /dm >}}

This is a **Student-t distribution with 1 degree of freedom** (i.e., a Cauchy kernel).

**Worked example.** If {{< m >}}\|y_1 - y_2\| = 1{{< /m >}}, then the numerator is {{< m >}}(1 + 1)^{-1} = 0.5{{< /m >}}. If {{< m >}}\|y_1 - y_3\| = 10{{< /m >}}, the numerator is {{< m >}}(1 + 100)^{-1} \approx 0.0099{{< /m >}}. The heavy tail of the Student-t means that moderately distant points in high dimensions can be pushed far apart in 2D without paying a large cost --- solving the **crowding problem**.
{{< /definition >}}

{{< definition name="Perplexity" label="Definition 23.3" >}}
The **perplexity** of the conditional distribution {{< m >}}P_i{{< /m >}} is

{{< dm >}}\mathrm{Perp}(P_i) = 2^{H(P_i)} = 2^{-\sum_j p_{j|i} \log_2 p_{j|i}}{{< /dm >}}

It can be interpreted as the effective number of neighbors. Setting perplexity = 30 means each point "sees" roughly 30 neighbors. The bandwidth {{< m >}}\sigma_i{{< /m >}} is found by binary search so that {{< m >}}\mathrm{Perp}(P_i){{< /m >}} matches the target.
{{< /definition >}}

{{< theorem name="t-SNE KL Minimization" label="Theorem 23.1" >}}
The t-SNE embedding {{< m >}}y_1, \ldots, y_N{{< /m >}} minimizes the Kullback--Leibler divergence

{{< dm >}}\mathcal{C} = \mathrm{KL}(P \| Q) = \sum_{i \neq j} p_{ij} \log \frac{p_{ij}}{q_{ij}}{{< /dm >}}

where {{< m >}}P = \{p_{ij}\}{{< /m >}} is fixed from the high-dimensional data and {{< m >}}Q = \{q_{ij}\}{{< /m >}} depends on the embedding coordinates.
{{< /theorem >}}

{{< proof >}}
The gradient with respect to embedding point {{< m >}}y_i{{< /m >}} is

{{< dm >}}\frac{\partial \mathcal{C}}{\partial y_i} = 4 \sum_{j \neq i} (p_{ij} - q_{ij})(1 + \|y_i - y_j\|^2)^{-1}(y_i - y_j){{< /dm >}}

To derive this, write {{< m >}}\mathcal{C} = \sum_{i \neq j} p_{ij} \log p_{ij} - \sum_{i \neq j} p_{ij} \log q_{ij}{{< /m >}}. The first term is constant. For the second, substitute {{< m >}}q_{ij} = (1 + \|y_i - y_j\|^2)^{-1} / Z{{< /m >}} where {{< m >}}Z = \sum_{k \neq l}(1 + \|y_k - y_l\|^2)^{-1}{{< /m >}}, and differentiate both the numerator and the normalizer {{< m >}}Z{{< /m >}} with respect to {{< m >}}y_i{{< /m >}}. The chain rule through {{< m >}}\|y_i - y_j\|^2{{< /m >}} contributes the factor {{< m >}}2(y_i - y_j){{< /m >}}, the Cauchy kernel contributes {{< m >}}(1 + \|y_i - y_j\|^2)^{-1}{{< /m >}}, and combining with the normalizer terms yields the stated gradient.

Optimization proceeds by gradient descent (with momentum and early exaggeration). Since {{< m >}}\mathcal{C}{{< /m >}} is bounded below by 0 (achieved when {{< m >}}Q = P{{< /m >}}) and the gradient is well-defined for distinct points, the procedure converges to a local minimum. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Why Student-t instead of Gaussian?** In high dimensions, the volume of a thin spherical shell grows as {{< m >}}r^{d-1}{{< /m >}}, so most neighbors of a point are at nearly the same distance. Mapping these to 2D with a Gaussian kernel forces moderately-distant points into a crowded annulus. The heavy tail of the Student-t kernel {{< m >}}(1 + \|y_i - y_j\|^2)^{-1}{{< /m >}} decays as {{< m >}}\|y_i - y_j\|^{-2}{{< /m >}} rather than exponentially, providing room for moderately-distant points to spread out while keeping true neighbors close.

### 23.2 Tonal Clusters in the Codebook

> *中文:* "统计每个码字更常出现在哪些调性的音频片段里，然后按调性给点上色。C大调标红，G大调标蓝，D小调标绿。"

The procedure: (1) run t-SNE on the 2048 codebook vectors; (2) for each codeword, count which musical keys it most frequently encodes; (3) color by dominant key.

> *中文:* "结果很有意思：同一调性的码字，更容易落在相邻区域。"

The observation is that codewords associated with the same key form contiguous clusters in the t-SNE map. Moreover, the neighborhood structure echoes the circle of fifths from {{< episode-ref ep="4" >}}EP04{{< /episode-ref >}}: keys separated by a fifth (e.g., C major and G major) tend to have adjacent clusters, while tritone-related keys (e.g., C and F{{< m >}}\sharp{{< /m >}}) are distant.

> *中文:* "没有人告诉模型什么是大调小调。它只是在压缩音频的过程中，自己发现了调性的几何结构。"

### 23.3 Linear Probes: Testing What Is Linearly Decodable

{{< definition name="Linear Probe" label="Definition 23.4" >}}
Given a frozen encoder producing representations {{< m >}}h_i \in \mathbb{R}^d{{< /m >}} for input {{< m >}}x_i{{< /m >}} with label {{< m >}}y_i \in \{1, \ldots, K\}{{< /m >}}, a **linear probe** is a classifier {{< m >}}(W, b){{< /m >}} with {{< m >}}W \in \mathbb{R}^{K \times d}{{< /m >}}, {{< m >}}b \in \mathbb{R}^K{{< /m >}} trained by

{{< dm >}}\min_{W, b} \sum_{i=1}^{n} \mathcal{L}\!\bigl(\mathrm{softmax}(W h_i + b),\; y_i\bigr){{< /dm >}}

where {{< m >}}\mathcal{L}{{< /m >}} is the cross-entropy loss. The encoder weights are **not updated** during probe training.

**Worked example.** For a key-detection probe with {{< m >}}K = 24{{< /m >}} (12 major + 12 minor keys) and {{< m >}}d = 128{{< /m >}}, we train a matrix {{< m >}}W \in \mathbb{R}^{24 \times 128}{{< /m >}} and bias {{< m >}}b \in \mathbb{R}^{24}{{< /m >}}. If the probe achieves 85% accuracy on held-out data, we conclude that key information is **linearly separable** in the codebook space.
{{< /definition >}}

{{< theorem name="Linear Probe Sufficiency" label="Theorem 23.2" >}}
If a linear probe achieves accuracy {{< m >}}\alpha{{< /m >}} on task {{< m >}}Y{{< /m >}} from representation {{< m >}}h = f(x){{< /m >}}, then there exists a hyperplane arrangement in {{< m >}}\mathbb{R}^d{{< /m >}} that separates the classes with error rate {{< m >}}1 - \alpha{{< /m >}}. The information about {{< m >}}Y{{< /m >}} is **linearly decodable** from the representation.
{{< /theorem >}}

{{< proof >}}
The softmax classifier {{< m >}}\hat{y} = \arg\max_k (Wh + b)_k{{< /m >}} partitions {{< m >}}\mathbb{R}^d{{< /m >}} into {{< m >}}K{{< /m >}} convex polyhedral regions {{< m >}}R_k = \{h : (w_k - w_j)^\top h + (b_k - b_j) \geq 0 \;\forall j \neq k\}{{< /m >}}, where {{< m >}}w_k{{< /m >}} is the {{< m >}}k{{< /m >}}-th row of {{< m >}}W{{< /m >}}. Each boundary is a hyperplane {{< m >}}\{h : (w_k - w_j)^\top h + (b_k - b_j) = 0\}{{< /m >}}. The probe accuracy {{< m >}}\alpha = \Pr[\hat{y} = y]{{< /m >}} directly measures the fraction of representations correctly classified by this hyperplane arrangement. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Important caveat.** A low probe accuracy does **not** imply the information is absent. It may be encoded non-linearly. A representation could store key information in the *norms* of subvectors or in *interactions* between dimensions --- patterns invisible to a linear classifier but accessible to a nonlinear one. Linear probes test a sufficient condition, not a necessary one.

---

## Part II: Emergent Specialization

### 23.4 Attention Head Specialization

> *中文:* "注意力权重是一个矩阵，每一行告诉你当前位置关注了哪些历史位置。"

Recall from {{< episode-ref ep="21" >}}EP21{{< /episode-ref >}} that a Transformer layer computes attention weights {{< m >}}A \in \mathbb{R}^{T \times T}{{< /m >}} with {{< m >}}A_{ij} = \mathrm{softmax}_j(q_i^\top k_j / \sqrt{d_k}){{< /m >}}. In multi-head attention, each head {{< m >}}h_\ell{{< /m >}} has its own projection matrices {{< m >}}W_Q^{(\ell)}, W_K^{(\ell)}, W_V^{(\ell)}{{< /m >}} and thus its own attention pattern.

> *中文:* "不同的注意力头自动分了工。有些头的权重呈现周期性——每隔固定步数就高一些——像在数拍子。另一些头对和声变化特别敏感。"

{{< definition name="Emergent Specialization" label="Definition 23.5" >}}
A multi-head attention model exhibits **emergent specialization** if, after training on a single undifferentiated loss (e.g., next-token prediction), individual attention heads develop statistically distinct response profiles to different input features (rhythm, harmony, timbre, etc.) without any explicit supervision for those features.
{{< /definition >}}

{{< theorem name="Emergent Specialization under Prediction Loss" label="Theorem 23.3" >}}
Let {{< m >}}\mathcal{L}(\theta) = -\mathbb{E}[\log p_\theta(x_{t+1} | x_{\leq t})]{{< /m >}} be the next-token prediction loss. If the data distribution decomposes as a mixture of independent generative factors {{< m >}}x = g(z_1, z_2, \ldots, z_m){{< /m >}} where {{< m >}}z_k{{< /m >}} are statistically independent, then the gradient signal

{{< dm >}}\frac{\partial \mathcal{L}}{\partial W^{(\ell)}} = -\mathbb{E}\!\left[\frac{\partial \log p_\theta(x_{t+1} | x_{\leq t})}{\partial W^{(\ell)}}\right]{{< /dm >}}

decomposes into contributions from each factor. In an overparameterized network, gradient descent tends to assign different heads to different factors, producing modular internal structure.
{{< /theorem >}}

{{< proof >}}
Write {{< m >}}x_{t+1} = g(z_1^{(t+1)}, \ldots, z_m^{(t+1)}){{< /m >}}. By the chain rule of mutual information and the independence of the {{< m >}}z_k{{< /m >}}, predicting {{< m >}}x_{t+1}{{< /m >}} requires capturing {{< m >}}I(x_{\leq t}; z_k^{(t+1)}){{< /m >}} for each factor {{< m >}}k{{< /m >}} separately. The gradient {{< m >}}\partial \mathcal{L}/\partial W^{(\ell)}{{< /m >}} is a sum over contributions from each factor:

{{< dm >}}\frac{\partial \mathcal{L}}{\partial W^{(\ell)}} = \sum_{k=1}^{m} \underbrace{\frac{\partial \mathcal{L}}{\partial z_k} \cdot \frac{\partial z_k}{\partial W^{(\ell)}}}_{\text{factor } k \text{ contribution}}{{< /dm >}}

In an overparameterized regime, heads that are randomly initialized near the gradient direction of factor {{< m >}}k{{< /m >}} will specialize toward that factor, because the loss landscape admits many solutions and gradient descent follows the path of least resistance. This is analogous to the **lottery ticket hypothesis** (Frankle & Carlin, 2019): the overparameterized network contains sparse subnetworks, each specialized to a factor, and training selects them.

The specialization is not guaranteed to be clean or complete --- heads may partially respond to multiple factors --- but the statistical tendency toward modular decomposition is observed empirically across architectures. {{< m >}}\square{{< /m >}}
{{< /proof >}}

> *中文:* "没有人在训练时标注过'这是节奏'，或者'这是和声'。模型只有一个目标：预测下一个离散码元。从这一个目标出发，它自动涌现出了功能分化的内部结构。"

**Phase transitions in specialization.** Empirically, specialization does not emerge gradually. There is evidence of **phase transitions**: during training, heads remain unspecialized until the loss drops below a critical threshold, at which point distinct functional roles crystallize rapidly. This parallels phase transitions in statistical physics and may be related to the information-theoretic framework of Part III.

---

## Part III: Information Bottleneck Theory

### 23.5 Mutual Information

{{< definition name="Mutual Information" label="Definition 23.6" >}}
For random variables {{< m >}}X{{< /m >}} and {{< m >}}Y{{< /m >}} with joint distribution {{< m >}}p(x, y){{< /m >}}, the **mutual information** is

{{< dm >}}I(X; Y) = H(X) - H(X|Y) = H(Y) - H(Y|X) = \sum_{x,y} p(x,y) \log \frac{p(x,y)}{p(x)p(y)}{{< /dm >}}

Equivalently, {{< m >}}I(X; Y) = \mathrm{KL}(p(x,y) \| p(x)p(y)){{< /m >}} --- the divergence between the joint and the product of marginals.

**Worked example.** Let {{< m >}}X{{< /m >}} = audio frame (continuous), {{< m >}}Y{{< /m >}} = musical key (discrete, 24 values). If knowing the key reduces uncertainty about the audio spectrum by 2 bits, then {{< m >}}I(X; Y) = 2{{< /m >}} bits.
{{< /definition >}}

{{< proposition label="Prop 23.1" name="Data Processing Inequality" >}}
For any Markov chain {{< m >}}X \to T \to Y{{< /m >}} (i.e., {{< m >}}T{{< /m >}} is a function of {{< m >}}X{{< /m >}} and {{< m >}}Y{{< /m >}} depends on {{< m >}}X{{< /m >}} only through {{< m >}}T{{< /m >}}):

{{< dm >}}I(X; Y) \geq I(T; Y){{< /dm >}}

Processing cannot create information. If {{< m >}}\hat{Y}{{< /m >}} is a further function of {{< m >}}T{{< /m >}}, then {{< m >}}I(X; Y) \geq I(T; Y) \geq I(\hat{Y}; Y){{< /m >}}.
{{< /proposition >}}

{{< proof >}}
By the chain rule: {{< m >}}I(X; Y | T) \geq 0{{< /m >}} (mutual information is non-negative). Expanding: {{< m >}}I(X; Y | T) = I(X, T; Y) - I(T; Y){{< /m >}}. Since {{< m >}}X \to T \to Y{{< /m >}} forms a Markov chain, {{< m >}}I(X; Y | T) = 0{{< /m >}}. Therefore {{< m >}}I(X; Y) = I(X, T; Y) \geq I(T; Y){{< /m >}}, where the inequality uses {{< m >}}I(X, T; Y) \geq I(T; Y){{< /m >}} (conditioning reduces entropy). For the Markov chain case, we actually get equality: {{< m >}}I(X; Y) \geq I(T; Y){{< /m >}} with equality iff {{< m >}}T{{< /m >}} is a sufficient statistic for {{< m >}}Y{{< /m >}} given {{< m >}}X{{< /m >}}. The second inequality follows by applying the same argument to {{< m >}}T \to \hat{Y} \to Y{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

### 23.6 The Information Bottleneck

{{< definition name="Information Bottleneck" label="Definition 23.7" >}}
Given a Markov chain {{< m >}}X \to T \to Y{{< /m >}}, the **Information Bottleneck (IB) objective** seeks a stochastic mapping {{< m >}}p(t|x){{< /m >}} that solves

{{< dm >}}\min_{p(t|x)} \; I(X; T) - \beta \, I(T; Y){{< /dm >}}

where:
- {{< m >}}I(X; T){{< /m >}} = **compression term**: how much of the raw input is retained.
- {{< m >}}I(T; Y){{< /m >}} = **prediction term**: how much predictive information about the target is preserved.
- {{< m >}}\beta > 0{{< /m >}} = **Lagrange multiplier** controlling the trade-off.

**Worked example.** For EnCodec: {{< m >}}X{{< /m >}} = raw audio waveform, {{< m >}}T{{< /m >}} = quantized codebook index, {{< m >}}Y{{< /m >}} = next audio frame. The codec must compress (small {{< m >}}I(X; T){{< /m >}} means fewer bits) while preserving enough to reconstruct/predict (large {{< m >}}I(T; Y){{< /m >}}). At {{< m >}}\beta \to 0{{< /m >}}, the optimal {{< m >}}T{{< /m >}} is trivial (one cluster). At {{< m >}}\beta \to \infty{{< /m >}}, {{< m >}}T{{< /m >}} retains everything about {{< m >}}Y{{< /m >}}.
{{< /definition >}}

{{< theorem name="Information Bottleneck Optimality" label="Theorem 23.4" >}}
The optimal IB solution satisfies the self-consistent equations:

{{< dm >}}p(t|x) = \frac{p(t)}{Z(x, \beta)} \exp\!\bigl(-\beta \, \mathrm{KL}(p(y|x) \| p(y|t))\bigr){{< /dm >}}

where {{< m >}}Z(x, \beta){{< /m >}} is a normalizing constant. As {{< m >}}\beta{{< /m >}} varies, the optimal solutions trace the **IB curve** in the {{< m >}}(I(X;T), I(T;Y)){{< /m >}} plane. This curve is concave and monotonically non-decreasing.
{{< /theorem >}}

{{< proof >}}
Introduce the Lagrangian with the constraint that {{< m >}}p(t|x){{< /m >}} is a valid conditional distribution:

{{< dm >}}\mathcal{F} = I(X; T) - \beta \, I(T; Y) + \sum_x \lambda(x)\!\left(\sum_t p(t|x) - 1\right){{< /dm >}}

Taking the functional derivative {{< m >}}\delta \mathcal{F} / \delta p(t|x) = 0{{< /m >}}:

{{< dm >}}\frac{\partial}{\partial p(t|x)}\!\left[\sum_{x'} p(x') \sum_{t'} p(t'|x') \log \frac{p(t'|x')}{p(t')}\right] - \beta \frac{\partial}{\partial p(t|x)}\!\left[\sum_{t'} p(t') \sum_y p(y|t') \log \frac{p(y|t')}{p(y)}\right] + \lambda(x) = 0{{< /dm >}}

The first term gives {{< m >}}p(x)[\log p(t|x) - \log p(t) + 1]{{< /m >}}. For the second term, since {{< m >}}p(y|t) = \sum_x p(y|x) p(x|t){{< /m >}} and {{< m >}}p(t) = \sum_x p(t|x)p(x){{< /m >}} both depend on {{< m >}}p(t|x){{< /m >}}, the variational derivative yields {{< m >}}\beta \, p(x) \sum_y p(y|x) \log[p(y|t)/p(y)]{{< /m >}} after applying Bayes' rule. Combining and solving:

{{< dm >}}\log p(t|x) = \log p(t) + \beta \sum_y p(y|x) \log \frac{p(y|t)}{p(y)} - 1 - \frac{\lambda(x)}{p(x)}{{< /dm >}}

Recognizing {{< m >}}\sum_y p(y|x) \log[p(y|t)/p(y)] = -\mathrm{KL}(p(y|x) \| p(y|t)) + \text{const}{{< /m >}} (the constant is {{< m >}}\sum_y p(y|x) \log[p(y|x)/p(y)]{{< /m >}}, independent of {{< m >}}t{{< /m >}}), and absorbing constants into the normalizer:

{{< dm >}}p(t|x) = \frac{p(t)}{Z(x,\beta)} \exp\!\bigl(-\beta \, \mathrm{KL}(p(y|x) \| p(y|t))\bigr){{< /dm >}}

The concavity of the IB curve follows from the concavity of mutual information in the channel {{< m >}}p(t|x){{< /m >}} (a standard result in information theory). Monotonicity: increasing {{< m >}}\beta{{< /m >}} increases the weight on preserving {{< m >}}I(T;Y){{< /m >}}, so the optimal {{< m >}}I(T;Y){{< /m >}} is non-decreasing in {{< m >}}\beta{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Connection to rate-distortion theory.** The IB framework generalizes Shannon's rate-distortion theory. In rate-distortion, the objective is {{< m >}}R(D) = \min_{p(t|x) : \mathbb{E}[d(x,t)] \leq D} I(X; T){{< /m >}}, where {{< m >}}d{{< /m >}} is a distortion measure. The IB replaces the explicit distortion constraint with {{< m >}}I(T; Y){{< /m >}}, making the "relevant" aspects of {{< m >}}X{{< /m >}} task-dependent rather than reconstruction-dependent.

**Why this explains tonal clustering.** When the model compresses audio (minimizing {{< m >}}I(X;T){{< /m >}}) while preserving predictability of future audio (maximizing {{< m >}}I(T;Y){{< /m >}}), the optimal codebook groups acoustically different signals that make the same predictions about what comes next. Signals in the same key share harmonic expectations --- so key information is retained, while irrelevant timbral details are discarded. The tonal clusters in the t-SNE map are a visible consequence of this information-theoretic trade-off.

---

## Part IV: The Meaning Gap

### 23.7 The Convex Hull Argument

> *中文:* "如果爵士乐从未存在过，你能用布鲁斯和拉格泰姆的数据，让AI提示出爵士乐吗？不可能。"

{{< definition name="Convex Hull of a Distribution" label="Definition 23.8" >}}
Let {{< m >}}F : \mathcal{X} \to \mathbb{R}^d{{< /m >}} be a feature map (e.g., a neural network encoder). The **convex hull** of the training distribution {{< m >}}P_{\text{data}}{{< /m >}} in feature space is

{{< dm >}}\mathrm{conv}(P_{\text{data}}) = \left\{\sum_{i=1}^{n} \lambda_i F(x_i) : x_i \in \mathrm{supp}(P_{\text{data}}),\; \lambda_i \geq 0,\; \sum_i \lambda_i = 1 \right\}{{< /dm >}}

Generative models that interpolate in latent space produce samples whose representations lie in or near {{< m >}}\mathrm{conv}(P_{\text{data}}){{< /m >}}.
{{< /definition >}}

{{< theorem name="Neely's Jazz Impossibility (Convex Hull Formulation)" label="Theorem 23.5" >}}
Let {{< m >}}P_{\text{blues}}{{< /m >}} and {{< m >}}P_{\text{ragtime}}{{< /m >}} be training distributions and {{< m >}}F{{< /m >}} any feature map learned from this data. If jazz involves structural innovations --- harmonic substitutions (tritone subs), polyrhythmic superposition, modal interchange --- that are not expressible as convex combinations of blues and ragtime features, then

{{< dm >}}F(\text{jazz}) \notin \mathrm{conv}\!\bigl(\{F(x) : x \in \mathrm{supp}(P_{\text{blues}}) \cup \mathrm{supp}(P_{\text{ragtime}})\}\bigr){{< /dm >}}

No amount of interpolation or prompting can produce jazz from a model trained only on blues and ragtime.
{{< /theorem >}}

{{< proof >}}
The proof proceeds by contradiction. Suppose {{< m >}}F(\text{jazz}) = \sum_i \lambda_i F(x_i){{< /m >}} for some {{< m >}}x_i \in \mathrm{supp}(P_{\text{blues}} \cup P_{\text{ragtime}}){{< /m >}}, {{< m >}}\lambda_i \geq 0{{< /m >}}, {{< m >}}\sum_i \lambda_i = 1{{< /m >}}.

Consider the feature dimension corresponding to tritone substitution frequency. In blues and ragtime, the tritone substitution is either absent or extremely rare, so {{< m >}}F_{\text{tri}}(x_i) \approx 0{{< /m >}} for all training points. Then {{< m >}}F_{\text{tri}}(\text{jazz}) = \sum_i \lambda_i F_{\text{tri}}(x_i) \approx 0{{< /m >}}. But bebop jazz uses tritone substitutions systematically (e.g., substituting D{{< m >}}\flat{{< /m >}}7 for G7 in a ii-V-I), so {{< m >}}F_{\text{tri}}(\text{jazz}) \gg 0{{< /m >}}. Contradiction.

The argument generalizes: any structural feature absent from the training corpus that is present in the target genre creates a coordinate direction along which the target lies outside the convex hull. Since the convex hull is a closed convex set, the separating hyperplane theorem guarantees a linear functional that separates the target from the hull. {{< m >}}\square{{< /m >}}
{{< /proof >}}

This formalizes Neely's intuition: new musical genres are not interpolations --- they are **cultural jumps** to points outside the convex hull of existing data.

### 23.8 Structure versus Meaning

> *中文:* "模型内部有几何结构，没有问题。但如果没有人在真正地聆听、比较、传承——那结构和意义之间，就有一道鸿沟。"

{{< definition name="Syntactic Structure vs. Semantic Meaning" label="Definition 23.9" >}}
- **Syntactic structure**: measurable geometric properties of representations --- distances, clusters, spectral gaps, curvatures. Formally: any property computable from the metric space {{< m >}}(Z, d){{< /m >}} where {{< m >}}Z{{< /m >}} is the latent space and {{< m >}}d{{< /m >}} is a distance.
- **Semantic meaning**: requires grounding in embodied experience, social context, and cultural memory. Not computable from geometric properties alone.

This distinction echoes **Searle's Chinese Room argument** (1980): a system that manipulates symbols according to syntactic rules may pass any behavioral test for understanding, yet possess no semantic comprehension. Applied to music: a model that clusters keys, separates rhythms, and predicts the next token is performing syntactic operations on acoustic symbols --- operations that are geometrically sophisticated but semantically ungrounded.
{{< /definition >}}

> *中文:* "意义不住在向量里。意义住在共同体、传统和聆听里。"

> *中文:* "我会继续为自己和社区创作音乐，因为它让我快乐。但我害怕，它再也无法像以前那样，和别人产生联结。"

The **grounding problem** asks: can statistical co-occurrence alone give meaning? The IB framework shows that the model captures all the *predictively useful* structure. But predictive utility is not the same as meaning. A weather model captures the structure of atmospheric dynamics without understanding what rain feels like.

> *中文:* "和几千个陌生人一起唱过同一首歌？尼利说，当每个人消费的音乐都完全个性化，这种体验就消失了。"

Neely's deeper point is sociological: music's meaning emerges from **shared experience**. A concert where thousands sing the same melody creates a collective state that no individually generated playlist can replicate. The information-theoretic framework captures the structure of music but not the structure of community. This is not a failure of mathematics --- it is a boundary condition on what mathematical formalism can express.

---

## Numerical Examples

**Example 23.1: t-SNE on a toy codebook.** Consider {{< m >}}N = 6{{< /m >}} points in {{< m >}}\mathbb{R}^3{{< /m >}} representing codewords from two keys:

| Codeword | Vector | Key |
|----------|--------|-----|
| {{< m >}}c_1{{< /m >}} | {{< m >}}(1, 0, 0){{< /m >}} | C major |
| {{< m >}}c_2{{< /m >}} | {{< m >}}(1.1, 0.2, 0){{< /m >}} | C major |
| {{< m >}}c_3{{< /m >}} | {{< m >}}(0.9, -0.1, 0.1){{< /m >}} | C major |
| {{< m >}}c_4{{< /m >}} | {{< m >}}(0, 1, 0){{< /m >}} | F{{< m >}}\sharp{{< /m >}} major |
| {{< m >}}c_5{{< /m >}} | {{< m >}}(0.1, 1.1, -0.1){{< /m >}} | F{{< m >}}\sharp{{< /m >}} major |
| {{< m >}}c_6{{< /m >}} | {{< m >}}(-0.1, 0.9, 0.2){{< /m >}} | F{{< m >}}\sharp{{< /m >}} major |

Within-cluster distances: {{< m >}}\|c_1 - c_2\| = \sqrt{0.01 + 0.04} \approx 0.22{{< /m >}}.
Between-cluster distances: {{< m >}}\|c_1 - c_4\| = \sqrt{1 + 1} \approx 1.41{{< /m >}}.

With {{< m >}}\sigma = 0.5{{< /m >}}, the high-dimensional affinity {{< m >}}p_{2|1} \propto e^{-0.22^2/0.5} \approx e^{-0.097} \approx 0.91{{< /m >}}, while {{< m >}}p_{4|1} \propto e^{-1.41^2/0.5} \approx e^{-3.98} \approx 0.019{{< /m >}}. t-SNE will place {{< m >}}c_1, c_2, c_3{{< /m >}} close together and {{< m >}}c_4, c_5, c_6{{< /m >}} far away, reproducing the key-based clustering.

**Example 23.2: IB trade-off.** Suppose {{< m >}}X{{< /m >}} has {{< m >}}H(X) = 10{{< /m >}} bits (raw audio complexity) and {{< m >}}Y{{< /m >}} has {{< m >}}H(Y) = 4{{< /m >}} bits (next-frame prediction). By the data processing inequality, {{< m >}}I(T; Y) \leq I(X; Y) \leq 4{{< /m >}} bits. A codebook with {{< m >}}\log_2 2048 = 11{{< /m >}} bits of capacity can afford {{< m >}}I(X; T) \leq 11{{< /m >}} bits. The IB curve shows that with {{< m >}}I(X; T) \approx 6{{< /m >}} bits (substantial compression from 11), one can still achieve {{< m >}}I(T; Y) \approx 3.5{{< /m >}} bits --- retaining most predictive information while discarding 5 bits of irrelevant detail (noise, exact timbre, recording artifacts).

**Example 23.3: Convex hull failure.** In {{< m >}}\mathbb{R}^2{{< /m >}}, let blues = {{< m >}}\{(1,0), (2,0), (1.5, 0.5)\}{{< /m >}} and ragtime = {{< m >}}\{(0,1), (0,2), (0.5, 1.5)\}{{< /m >}}. Their convex hull is the union of two triangles near the axes. Jazz at {{< m >}}(2, 2){{< /m >}} is outside: any convex combination {{< m >}}\sum \lambda_i v_i{{< /m >}} with {{< m >}}\sum \lambda_i = 1{{< /m >}} satisfies {{< m >}}x + y \leq \max(x_i + y_i) = 2.5{{< /m >}} for training points, but {{< m >}}2 + 2 = 4 > 2.5{{< /m >}}.

---

## Musical Connection

{{< musical-connection >}}
**From the Tonnetz to the Codebook: The Geometry Persists**

The tonal clusters discovered by t-SNE in the EnCodec codebook echo the topological structure of the Tonnetz studied in {{< episode-ref ep="14" >}}EP14{{< /episode-ref >}}. In EP14, the twelve pitch classes form a simplicial complex on a torus, with Betti numbers {{< m >}}(1, 2, 1){{< /m >}} encoding two independent non-contractible loops: the circle of fifths and the major-third cycle. In the codebook, the same neighborhood relationships reappear: keys a fifth apart cluster nearby, and the circular ordering of key clusters reproduces the {{< m >}}\mathbb{Z}_{12}{{< /m >}} cyclic group structure from {{< episode-ref ep="4" >}}EP04{{< /episode-ref >}}.

> *中文:* "码本里浮现出来的局部邻居结构，和五度圈有相似之处。"

The circle of fifths defines an adjacency relation on keys: C is "near" G and F, "far" from F{{< m >}}\sharp{{< /m >}}. This same relation --- which {{< episode-ref ep="4" >}}EP04{{< /episode-ref >}} identified as a generator of {{< m >}}\mathbb{Z}_{12}{{< /m >}} --- emerges unsupervised in the codebook geometry. The model has rediscovered, through compression alone, a structure that took Western music theory centuries to articulate.

But the critical difference: the Tonnetz is a mathematical construction with known topology. The codebook geometry is empirical and depends on the training data, the architecture, and the compression rate. Whether the codebook consistently recovers the full torus topology (both generators, the correct Betti numbers) across different models and datasets is an open empirical question that connects to {{< episode-ref ep="25" >}}EP25{{< /episode-ref >}}'s study of robustness.

**The five-degree connection.** In EP14, two pitch classes connected by an edge of the Tonnetz are separated by a consonant interval (perfect fifth, major third, or minor third). The codebook t-SNE map recovers primarily the fifth-based adjacency. This is consistent with the IB framework: the perfect fifth (frequency ratio 3:2) is the strongest harmonic relationship after the octave, so it carries the most predictive information about harmonic context. The major-third axis (frequency ratio 5:4) is weaker, and its recovery in the codebook is less consistent --- a quantitative prediction that could be tested by measuring probe accuracy for fifth-related versus third-related key pairs.

**Attention heads as discrete differential operators.** In EP14, the Hodge Laplacian {{< m >}}L_1{{< /m >}} decomposed interval flows into gradient, curl, and harmonic components. Speculatively, the specialized attention heads of Part II may perform an analogous decomposition: rhythm heads detect periodic structure (analogous to divergence), harmony heads detect chord transitions (analogous to curl), and global context heads track large-scale tonal motion (analogous to harmonic flow). This analogy is suggestive but unproven.
{{< /musical-connection >}}

---

## Limits and Open Questions

{{< conjecture name="Codebook Topology Conjecture" >}}
For any audio codec trained with sufficient capacity on tonal music, the first codebook's t-SNE embedding recovers a neighborhood graph homeomorphic to a quotient of the circle of fifths. That is, the topological structure is **not** an artifact of a particular model but an inevitable consequence of the IB trade-off applied to tonal music.

**Status**: Unresolved. Requires systematic comparison across codecs (EnCodec, SoundStream, DAC) and training corpora.
{{< /conjecture >}}

{{< conjecture name="Specialization Phase Transition Conjecture" >}}
In a Transformer trained on music tokens, there exists a critical training loss {{< m >}}\mathcal{L}^*{{< /m >}} such that for {{< m >}}\mathcal{L} > \mathcal{L}^*{{< /m >}}, no attention head shows statistically significant specialization, while for {{< m >}}\mathcal{L} < \mathcal{L}^*{{< /m >}}, at least {{< m >}}m{{< /m >}} heads specialize to distinct musical features (where {{< m >}}m{{< /m >}} is the number of independent generative factors). The transition is sharp in the sense that the mutual information between head attention patterns and musical features has a discontinuous derivative at {{< m >}}\mathcal{L}^*{{< /m >}}.

**Status**: Partially supported by visualization studies. Formal proof requires a tractable model of the training dynamics.
{{< /conjecture >}}

**Open questions**:

1. **Non-linear probing**: If a linear probe fails but a two-layer MLP succeeds, what is the minimal geometric complexity of the encoding? Can we characterize this by the intrinsic dimension of the feature manifold?

2. **IB tightness**: How close do real codecs come to the IB curve? Is there a measurable gap, and does closing it improve downstream music generation quality?

3. **Grounding beyond syntax**: Can a model that interacts with embodied agents (e.g., a robot musician responding to audience reactions) develop something closer to semantic understanding? Or is the grounding problem fundamentally unsolvable for statistical models?

4. **Convex hull escape**: Are there architectures (e.g., neuro-symbolic systems, models with explicit rule-learning modules) that can generate samples outside the convex hull of their training data? What mathematical framework captures "genuine novelty" as opposed to interpolation? Forward reference: {{< episode-ref ep="25" >}}EP25{{< /episode-ref >}} explores related questions about generalization bounds.

5. **Perplexity sensitivity**: t-SNE visualizations depend strongly on the perplexity parameter. Do tonal clusters persist across the full range {{< m >}}\mathrm{Perp} \in [5, 50]{{< /m >}}? If clusters fragment at low perplexity and merge at high perplexity, the "true" cluster structure may be scale-dependent, requiring persistent homology (a tool from topological data analysis) to resolve.

6. **Cross-cultural codebooks**: The tonal clustering discussed here assumes Western tonal music. For music based on maqam (Arabic), raga (Indian), or pentatonic scales (Chinese), does the codebook geometry reflect the relevant scale structure? The {{< m >}}\mathbb{Z}_{12}{{< /m >}} circle of fifths is not universal --- other tuning systems would produce different geometric signatures.

---

## Academic References

1. van der Maaten, L. & Hinton, G. (2008). "Visualizing Data using t-SNE." *Journal of Machine Learning Research* 9, 2579--2605.
2. Tishby, N., Pereira, F. & Bialek, W. (2000). "The Information Bottleneck Method." *Proceedings of the 37th Allerton Conference*, 368--377.
3. Tishby, N. & Zaslavsky, N. (2015). "Deep Learning and the Information Bottleneck Principle." *IEEE Information Theory Workshop (ITW)*, 1--5.
4. Alain, G. & Bengio, Y. (2017). "Understanding Intermediate Layers Using Linear Classifier Probes." *ICLR Workshop*.
5. Searle, J. (1980). "Minds, Brains, and Programs." *Behavioral and Brain Sciences* 3(3), 417--424.
6. Frankle, J. & Carlin, M. (2019). "The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks." *ICLR 2019*.
7. Voita, E., Talbot, D., Moiseev, F., Sennrich, R. & Titov, I. (2019). "Analyzing Multi-Head Self-Attention: Specialized Heads Do the Heavy Lifting, the Rest Can Be Pruned." *ACL 2019*, 5797--5808.
8. Castellon, R., Donahue, C. & Liang, P. (2021). "Codified Audio Language Modeling Learns Useful Representations for Music Information Retrieval." *ISMIR 2021*.
9. Defossez, A., Copet, J., Synnaeve, G. & Adi, Y. (2023). "High Fidelity Neural Audio Compression." *ICLR 2023*.
10. Neely, A. (2024). "The Death of Music." YouTube. Accessed 2026-02-20.
11. Shannon, C. (1959). "Coding Theorems for a Discrete Source with a Fidelity Criterion." *IRE National Convention Record* 7(4), 142--163.
12. Cover, T. & Thomas, J. (2006). *Elements of Information Theory*, 2nd ed. Wiley.
13. Shwartz-Ziv, R. & Tishby, N. (2017). "Opening the Black Box of Deep Neural Networks via Information." *arXiv:1703.00810*.
14. Zeghidour, N., Luebs, A., Omran, A., Skoglund, J. & Tagliasacchi, M. (2022). "SoundStream: An End-to-End Neural Audio Codec." *IEEE/ACM Transactions on Audio, Speech, and Language Processing* 30, 495--507.
