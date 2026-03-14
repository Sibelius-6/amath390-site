---
title: "EP21: From Markov to Diffusion — Sixty Years of AI Composition"
subtitle: "Markov链, Transformer注意力, 分数匹配/扩散"
episode: 21
date: 2026-02-27
duration: "8:35"
domains:
  - "Statistics/ML"
  - "Information Theory"
key_theorems:
  - "Markov Chain Stationary Distribution (Perron-Frobenius)"
  - "Softmax Attention as Dynamic Transition Matrix"
  - "DDPM Forward Process Reparameterization"
  - "Score Matching Equivalence"
callbacks: [4, 7]
forward_refs: [22, 23, 24]
weight: 21
draft: false
---

## Overview

Three mathematical frameworks have dominated algorithmic music composition over sixty years: **Markov chains** (1957), **Transformer attention** (2017), and **diffusion models** (2020). Each replaces its predecessor not by discarding the core idea — sampling from a learned probability distribution over musical events — but by changing *which* probability distribution and *how* it is parameterized.

> *中文:* "它们在解同一个数学问题。这个问题的答案，七十年里只换了三次。从骰子，到注意力，到噪声。"

This companion page formalizes the mathematics the video sketches: transition matrices on {{< m >}}\mathbb{Z}_{12}{{< /m >}}, the softmax attention mechanism as a content-dependent stochastic matrix, and the DDPM forward/reverse processes with score matching.

---

## Prerequisites

- {{< episode-ref ep="4" >}}Cyclic groups and ℤ₁₂ (EP04){{< /episode-ref >}} — pitch classes as elements of the cyclic group
- {{< episode-ref ep="7" >}}Probability and entropy basics (EP07){{< /episode-ref >}} — probability distributions, expectation
- Linear algebra: matrix multiplication, eigenvalues, positive semi-definiteness
- Basic multivariate calculus: gradients, Gaussian densities

---

## Part I: Markov Chains on ℤ₁₂

> *中文:* "1957年，希勒和艾萨克森在伊利诺伊大学的Illiac计算机上做了一个实验。他们把十二个音高排成一圈。第四期讲过，这就是Z 12，十二元循环群。然后给每对音之间分配一个转移概率。"

### 1.1 Definitions

{{< definition name="Time-Homogeneous Markov Chain on a Finite State Space" label="Definition 21.1" >}}
Let {{< m >}}S = \{s_1, \ldots, s_n\}{{< /m >}} be a finite set of states. A **time-homogeneous Markov chain** on {{< m >}}S{{< /m >}} is a sequence of random variables {{< m >}}(X_0, X_1, X_2, \ldots){{< /m >}} taking values in {{< m >}}S{{< /m >}} such that for all {{< m >}}t \geq 0{{< /m >}} and all states {{< m >}}i, j \in S{{< /m >}}:
{{< dm >}}P(X_{t+1} = j \mid X_t = i, X_{t-1}, \ldots, X_0) = P(X_{t+1} = j \mid X_t = i) =: p_{ij}{{< /dm >}}

The constant {{< m >}}p_{ij}{{< /m >}} is called the **transition probability** from state {{< m >}}i{{< /m >}} to state {{< m >}}j{{< /m >}}.
{{< /definition >}}

**Example (Illiac Suite, 1957)**: Set {{< m >}}S = \mathbb{Z}_{12} = \{C, C\sharp, D, \ldots, B\}{{< /m >}}, the twelve pitch classes (see {{< episode-ref ep="4" >}}EP04{{< /episode-ref >}}). Hiller and Isaacson assigned transition probabilities such as {{< m >}}p_{C,E} = 0.3{{< /m >}} and {{< m >}}p_{C,G} = 0.4{{< /m >}}. To generate a melody: start at some pitch {{< m >}}X_0{{< /m >}}, sample {{< m >}}X_1{{< /m >}} from row {{< m >}}X_0{{< /m >}} of the transition matrix, then sample {{< m >}}X_2{{< /m >}} from row {{< m >}}X_1{{< /m >}}, and so on.

> *中文:* "生成旋律的方法：站在当前音，按概率掷骰子，跳到下一个音。重复。这就是马尔可夫链。本质上，1957年的AI作曲，就是在Z 12上掷加权骰子。"

{{< definition name="Stochastic (Transition) Matrix" label="Definition 21.2" >}}
The **transition matrix** {{< m >}}P \in \mathbb{R}^{n \times n}{{< /m >}} of a Markov chain on {{< m >}}n{{< /m >}} states has entries {{< m >}}P_{ij} = p_{ij}{{< /m >}} satisfying:

1. **Non-negativity**: {{< m >}}P_{ij} \geq 0{{< /m >}} for all {{< m >}}i,j{{< /m >}}.
2. **Row-stochastic**: {{< m >}}\sum_{j=1}^{n} P_{ij} = 1{{< /m >}} for every row {{< m >}}i{{< /m >}}.

A matrix satisfying both conditions is called a **(row-)stochastic matrix**.
{{< /definition >}}

**Worked example**: A toy {{< m >}}3 \times 3{{< /m >}} transition matrix on states {{< m >}}\{C, E, G\}{{< /m >}}:
{{< dm >}}P = \begin{pmatrix} 0.2 & 0.3 & 0.5 \\ 0.1 & 0.4 & 0.5 \\ 0.3 & 0.3 & 0.4 \end{pmatrix}{{< /dm >}}

Row 1: from C, probability 0.2 to stay on C, 0.3 to jump to E, 0.5 to jump to G. Each row sums to 1.

### 1.2 Multi-Step Transitions

{{< theorem name="Chapman-Kolmogorov Equation" label="Theorem 21.1" >}}
Let {{< m >}}P{{< /m >}} be the transition matrix of a time-homogeneous Markov chain. The {{< m >}}n{{< /m >}}-step transition probabilities satisfy
{{< dm >}}P^{(n)} = P^n{{< /dm >}}
i.e., the probability of going from state {{< m >}}i{{< /m >}} to state {{< m >}}j{{< /m >}} in exactly {{< m >}}n{{< /m >}} steps is the {{< m >}}(i,j){{< /m >}}-entry of the matrix {{< m >}}P^n{{< /m >}}.
{{< /theorem >}}

{{< proof >}}
**Base case** ({{< m >}}n=1{{< /m >}}): {{< m >}}P^{(1)} = P^1 = P{{< /m >}} by definition.

**Inductive step**: Assume {{< m >}}P^{(n)} = P^n{{< /m >}}. For the {{< m >}}(n+1){{< /m >}}-step probability:
{{< dm >}}P^{(n+1)}_{ij} = P(X_{n+1} = j \mid X_0 = i) = \sum_{k \in S} P(X_{n+1} = j \mid X_n = k)\, P(X_n = k \mid X_0 = i){{< /dm >}}
{{< dm >}}= \sum_{k \in S} P_{kj} \cdot P^{(n)}_{ik} = \sum_{k \in S} P^n_{ik} \cdot P_{kj} = (P^n \cdot P)_{ij} = P^{n+1}_{ij}{{< /dm >}}

The first equality uses the law of total probability and the Markov property. The inductive hypothesis gives {{< m >}}P^{(n)}_{ik} = P^n_{ik}{{< /m >}}. Therefore {{< m >}}P^{(n+1)} = P^{n+1}{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Musical meaning**: {{< m >}}P^n_{C,G}{{< /m >}} is the probability that a melody starting on C will be on G after exactly {{< m >}}n{{< /m >}} notes.

### 1.3 Stationary Distribution

{{< definition name="Stationary Distribution" label="Definition 21.3" >}}
A probability vector {{< m >}}\pi \in \mathbb{R}^n{{< /m >}} (with {{< m >}}\pi_i \geq 0{{< /m >}} and {{< m >}}\sum_i \pi_i = 1{{< /m >}}) is a **stationary distribution** of the Markov chain with transition matrix {{< m >}}P{{< /m >}} if
{{< dm >}}\pi P = \pi{{< /dm >}}
That is, {{< m >}}\pi{{< /m >}} is a left eigenvector of {{< m >}}P{{< /m >}} with eigenvalue 1.
{{< /definition >}}

{{< theorem name="Existence and Uniqueness of Stationary Distribution (Perron-Frobenius)" label="Theorem 21.2" >}}
Let {{< m >}}P{{< /m >}} be the transition matrix of an **irreducible, aperiodic** Markov chain on a finite state space. Then:

1. **Existence**: There exists a unique stationary distribution {{< m >}}\pi{{< /m >}} with {{< m >}}\pi P = \pi{{< /m >}} and {{< m >}}\pi_i > 0{{< /m >}} for all {{< m >}}i{{< /m >}}.
2. **Convergence**: For any initial distribution {{< m >}}\mu_0{{< /m >}}, {{< m >}}\lim_{n \to \infty} \mu_0 P^n = \pi{{< /m >}}.
3. **Long-run frequency**: With probability 1, the fraction of time spent in state {{< m >}}i{{< /m >}} converges to {{< m >}}\pi_i{{< /m >}}.
{{< /theorem >}}

{{< proof >}}
*(Sketch via Perron-Frobenius.)* An irreducible chain has {{< m >}}P^m > 0{{< /m >}} (entry-wise) for some {{< m >}}m{{< /m >}} (aperiodicity + irreducibility ensure this). The Perron-Frobenius theorem for positive matrices states that such a matrix has a unique largest eigenvalue {{< m >}}\lambda_1 = 1{{< /m >}} (since {{< m >}}P{{< /m >}} is stochastic, the all-ones vector is a right eigenvector with eigenvalue 1), and the corresponding left eigenvector {{< m >}}\pi{{< /m >}} can be chosen with all entries positive and summing to 1. All other eigenvalues satisfy {{< m >}}|\lambda_i| < 1{{< /m >}}, so {{< m >}}P^n \to \mathbf{1}\pi{{< /m >}} as {{< m >}}n \to \infty{{< /m >}}, which gives convergence and the frequency interpretation. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Musical meaning**: The stationary distribution {{< m >}}\pi{{< /m >}} gives the long-run frequency of each pitch class. If the Markov chain on {{< m >}}\mathbb{Z}_{12}{{< /m >}} has {{< m >}}\pi_C = 0.12{{< /m >}} and {{< m >}}\pi_G = 0.10{{< /m >}}, then in a long enough generated melody, roughly 12% of notes will be C and 10% will be G — regardless of which note started the chain. This is a *stylistic fingerprint* of the transition matrix.

**Worked example**: For the toy matrix above, solving {{< m >}}\pi P = \pi{{< /m >}} with {{< m >}}\pi_1 + \pi_2 + \pi_3 = 1{{< /m >}} gives the system {{< m >}}0.2\pi_1 + 0.1\pi_2 + 0.3\pi_3 = \pi_1{{< /m >}}, etc. The solution is {{< m >}}\pi \approx (0.194, 0.333, 0.472){{< /m >}}: G dominates in the long run.

### 1.4 Why Markov Chains Fail at Music

> *中文:* "结果听起来怎么样？局部像音乐，整体没记忆。因为马尔可夫链只看上一步。...副歌回来、主题发展——它全抓不住。"

{{< definition name="Mixing Time" label="Definition 21.4" >}}
The **mixing time** of an irreducible aperiodic Markov chain is the smallest {{< m >}}t{{< /m >}} such that the total variation distance between {{< m >}}\mu_0 P^t{{< /m >}} and {{< m >}}\pi{{< /m >}} is at most {{< m >}}1/4{{< /m >}} for any initial distribution {{< m >}}\mu_0{{< /m >}}:
{{< dm >}}t_{\mathrm{mix}} = \min\bigl\{t : \max_{\mu_0} \|\mu_0 P^t - \pi\|_{\mathrm{TV}} \leq 1/4\bigr\}{{< /dm >}}
{{< /definition >}}

The mixing time measures how quickly the chain "forgets" its starting state. For a first-order chain on {{< m >}}\mathbb{Z}_{12}{{< /m >}}, this is typically very small (a few steps), meaning the chain loses all memory of its beginning after a handful of notes.

One might try a **{{< m >}}k{{< /m >}}-th order Markov chain**: condition on the previous {{< m >}}k{{< /m >}} notes instead of just one. But this requires a transition matrix of size {{< m >}}12^k \times 12^k{{< /m >}}: for {{< m >}}k = 8{{< /m >}} (a single musical phrase), the state space has {{< m >}}12^8 \approx 4.3 \times 10^8{{< /m >}} states. The number of parameters grows exponentially, making estimation from finite training data intractable. This exponential blowup is the fundamental limitation.

{{< proposition label="Prop 21.1" name="Exponential State Space of k-th Order Chains" >}}
A {{< m >}}k{{< /m >}}-th order Markov chain on an alphabet of size {{< m >}}|S|{{< /m >}} requires a transition matrix with {{< m >}}|S|^k \cdot |S| = |S|^{k+1}{{< /m >}} parameters. For {{< m >}}|S| = 12{{< /m >}} and {{< m >}}k = 16{{< /m >}} (two bars of eighth notes), this exceeds {{< m >}}10^{17}{{< /m >}}.
{{< /proposition >}}

{{< proof >}}
The state space of a {{< m >}}k{{< /m >}}-th order chain is {{< m >}}S^k{{< /m >}} (all sequences of length {{< m >}}k{{< /m >}}), with {{< m >}}|S^k| = |S|^k{{< /m >}} states. Each state has {{< m >}}|S|{{< /m >}} possible next-state probabilities (one per element of {{< m >}}S{{< /m >}}), so the transition matrix has {{< m >}}|S|^k{{< /m >}} rows and {{< m >}}|S|{{< /m >}} free parameters per row (the last is determined by the row-sum constraint, but the matrix still has {{< m >}}|S|^k \times |S|{{< /m >}} entries). For {{< m >}}|S| = 12{{< /m >}}, {{< m >}}k = 16{{< /m >}}: {{< m >}}12^{17} \approx 2.2 \times 10^{18}{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

---

## Part II: Attention and Transformers

> *中文:* "真正的突破要等到2017年。Transformer的核心是注意力机制。关键直觉是这样的：马尔可夫链有一张固定的转移概率表，每行加起来等于一。注意力机制也有这样一张表——但它不是固定的，而是根据当前内容实时算出来的。"

### 2.1 Scaled Dot-Product Attention

{{< definition name="Query, Key, Value Projections" label="Definition 21.5" >}}
Let {{< m >}}X \in \mathbb{R}^{n \times d}{{< /m >}} be an input matrix whose {{< m >}}n{{< /m >}} rows are token embeddings of dimension {{< m >}}d{{< /m >}}. Define three learned weight matrices {{< m >}}W_Q, W_K \in \mathbb{R}^{d \times d_k}{{< /m >}} and {{< m >}}W_V \in \mathbb{R}^{d \times d_v}{{< /m >}}. The **query**, **key**, and **value** matrices are:
{{< dm >}}Q = XW_Q, \quad K = XW_K, \quad V = XW_V{{< /dm >}}
{{< /definition >}}

{{< definition name="Scaled Dot-Product Attention" label="Definition 21.6" >}}
Given {{< m >}}Q \in \mathbb{R}^{n \times d_k}{{< /m >}}, {{< m >}}K \in \mathbb{R}^{n \times d_k}{{< /m >}}, {{< m >}}V \in \mathbb{R}^{n \times d_v}{{< /m >}}, the **scaled dot-product attention** is:
{{< dm >}}\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right) V{{< /dm >}}
where softmax is applied row-wise: for row {{< m >}}i{{< /m >}}, {{< m >}}\mathrm{softmax}(z)_j = e^{z_j}/\sum_{\ell} e^{z_\ell}{{< /m >}}.
{{< /definition >}}

**Why the {{< m >}}\sqrt{d_k}{{< /m >}} scaling**: If the entries of {{< m >}}Q{{< /m >}} and {{< m >}}K{{< /m >}} are independent with mean 0 and variance 1, then the dot product {{< m >}}q_i \cdot k_j = \sum_{m=1}^{d_k} q_{im} k_{jm}{{< /m >}} has mean 0 and variance {{< m >}}d_k{{< /m >}}. Without scaling, for large {{< m >}}d_k{{< /m >}} the dot products grow large in magnitude, pushing softmax into saturation (one entry near 1, all others near 0). Dividing by {{< m >}}\sqrt{d_k}{{< /m >}} restores unit variance, keeping softmax in its informative regime.

**Worked example**: Let {{< m >}}n = 3{{< /m >}} (three tokens: C, E, G), {{< m >}}d_k = 2{{< /m >}}. Suppose after projection:
{{< dm >}}Q = \begin{pmatrix} 1 & 0 \\ 0 & 1 \\ 1 & 1 \end{pmatrix}, \quad K = \begin{pmatrix} 1 & 1 \\ 0 & 1 \\ 1 & 0 \end{pmatrix}{{< /dm >}}

Then {{< m >}}QK^T = \begin{pmatrix} 1 & 0 & 1 \\ 1 & 1 & 0 \\ 2 & 1 & 1 \end{pmatrix}{{< /m >}}. Dividing by {{< m >}}\sqrt{2} \approx 1.41{{< /m >}} and applying row-wise softmax gives a {{< m >}}3 \times 3{{< /m >}} matrix where each row sums to 1 — an attention weight matrix.

### 2.2 Multi-Head Attention

{{< definition name="Multi-Head Attention" label="Definition 21.7" >}}
Given {{< m >}}h{{< /m >}} attention heads, each with its own projections {{< m >}}W_Q^{(i)}, W_K^{(i)} \in \mathbb{R}^{d \times d_k}{{< /m >}} and {{< m >}}W_V^{(i)} \in \mathbb{R}^{d \times d_v}{{< /m >}}, define:
{{< dm >}}\mathrm{head}_i = \mathrm{Attention}(XW_Q^{(i)},\; XW_K^{(i)},\; XW_V^{(i)}){{< /dm >}}
{{< dm >}}\mathrm{MultiHead}(X) = \mathrm{Concat}(\mathrm{head}_1, \ldots, \mathrm{head}_h)\, W_O{{< /dm >}}
where {{< m >}}W_O \in \mathbb{R}^{hd_v \times d}{{< /m >}} is a learned output projection.
{{< /definition >}}

**Why multiple heads**: Each head can learn a different "type" of relationship. In music: one head might attend to rhythmic patterns, another to harmonic intervals, a third to melodic contour. Concatenating and projecting combines these views.

### 2.3 Attention as a Dynamic Transition Matrix

> *中文:* "换句话说，Transformer把固定概率表变成了动态概率表。"

{{< theorem name="Softmax Attention Yields a Row-Stochastic Matrix" label="Theorem 21.3" >}}
Let {{< m >}}A = \mathrm{softmax}(QK^T/\sqrt{d_k}) \in \mathbb{R}^{n \times n}{{< /m >}}. Then:

1. {{< m >}}A_{ij} > 0{{< /m >}} for all {{< m >}}i, j{{< /m >}}.
2. {{< m >}}\sum_{j=1}^{n} A_{ij} = 1{{< /m >}} for every row {{< m >}}i{{< /m >}}.

That is, {{< m >}}A{{< /m >}} is a **(strictly) positive row-stochastic matrix** — it satisfies the same algebraic properties as a Markov chain transition matrix. However, unlike a Markov chain, {{< m >}}A{{< /m >}} depends on the input {{< m >}}X{{< /m >}} and changes at every position.
{{< /theorem >}}

{{< proof >}}
**(1)** For any real vector {{< m >}}z \in \mathbb{R}^n{{< /m >}}, the softmax function outputs {{< m >}}\mathrm{softmax}(z)_j = e^{z_j}/\sum_{\ell=1}^n e^{z_\ell}{{< /m >}}. Since {{< m >}}e^{z_j} > 0{{< /m >}} for all {{< m >}}z_j \in \mathbb{R}{{< /m >}}, we have {{< m >}}\mathrm{softmax}(z)_j > 0{{< /m >}}.

**(2)** By definition, {{< m >}}\sum_{j=1}^n \mathrm{softmax}(z)_j = \sum_{j=1}^n \frac{e^{z_j}}{\sum_\ell e^{z_\ell}} = \frac{\sum_j e^{z_j}}{\sum_\ell e^{z_\ell}} = 1{{< /m >}}.

Applying this to each row {{< m >}}z_i = (QK^T)_{i,:}/\sqrt{d_k}{{< /m >}} establishes both properties for the matrix {{< m >}}A{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

The key conceptual shift: a Markov chain uses a **fixed** stochastic matrix {{< m >}}P{{< /m >}}, determined once from training data. Attention computes a **different** stochastic matrix {{< m >}}A(X){{< /m >}} for each input sequence {{< m >}}X{{< /m >}}. This allows the model to attend to distant positions when the content warrants it — capturing long-range dependencies like returning choruses and thematic development that Markov chains cannot.

| Property | Markov Chain | Attention |
|----------|-------------|-----------|
| Stochastic matrix | Fixed {{< m >}}P{{< /m >}} | Dynamic {{< m >}}A(X){{< /m >}} |
| Entries | {{< m >}}\geq 0{{< /m >}}, rows sum to 1 | {{< m >}}> 0{{< /m >}}, rows sum to 1 |
| Context window | 1 step (or {{< m >}}k{{< /m >}} for order-{{< m >}}k{{< /m >}}) | Entire sequence |
| Parameters | {{< m >}}O(|S|^2){{< /m >}} | {{< m >}}O(d^2){{< /m >}}, independent of sequence length |

---

## Part III: Diffusion Models (DDPM)

> *中文:* "第三次跳跃更反直觉。...扩散模型...从一整片纯噪声开始，一步一步去掉噪声，逐步还原出音乐的结构。"

### 3.1 The Forward Noising Process

{{< definition name="DDPM Forward Process" label="Definition 21.8" >}}
Let {{< m >}}x_0 \sim q(x_0){{< /m >}} be a data sample (e.g., a mel-spectrogram of music). The **forward (noising) process** is a Markov chain {{< m >}}x_0 \to x_1 \to \cdots \to x_T{{< /m >}} defined by:
{{< dm >}}q(x_t \mid x_{t-1}) = \mathcal{N}\!\left(x_t;\; \sqrt{1 - \beta_t}\, x_{t-1},\; \beta_t I\right){{< /dm >}}
where {{< m >}}\{\beta_t\}_{t=1}^T{{< /m >}} is a fixed **noise schedule** with {{< m >}}0 < \beta_t < 1{{< /m >}}.
{{< /definition >}}

> *中文:* "最反直觉的是：扩散的前向加噪过程，数学上就是一个马尔可夫链。...只不过状态不再是12个离散的音高，而是一整片连续的噪声。"

At each step, the signal is scaled down by {{< m >}}\sqrt{1-\beta_t}{{< /m >}} and Gaussian noise of variance {{< m >}}\beta_t{{< /m >}} is added. For large {{< m >}}T{{< /m >}}, {{< m >}}x_T{{< /m >}} is approximately pure Gaussian noise.

**Worked example**: For a one-dimensional signal {{< m >}}x_0 = 5{{< /m >}} with {{< m >}}\beta_1 = 0.01{{< /m >}}:
{{< dm >}}x_1 \sim \mathcal{N}(\sqrt{0.99} \cdot 5,\; 0.01) = \mathcal{N}(4.975,\; 0.01){{< /dm >}}
The signal is barely perturbed. After many steps, the signal is destroyed.

### 3.2 The Reparameterization Trick

{{< definition name="Cumulative Noise Schedule" label="Definition 21.9" >}}
Define {{< m >}}\alpha_t = 1 - \beta_t{{< /m >}} and the cumulative product:
{{< dm >}}\bar{\alpha}_t = \prod_{s=1}^{t} \alpha_s = \prod_{s=1}^{t}(1 - \beta_s){{< /dm >}}
Note {{< m >}}\bar{\alpha}_t{{< /m >}} is decreasing in {{< m >}}t{{< /m >}}, approaching 0 as {{< m >}}t \to T{{< /m >}}.
{{< /definition >}}

{{< theorem name="DDPM Forward Reparameterization" label="Theorem 21.4" >}}
For any {{< m >}}t \geq 1{{< /m >}}, the marginal {{< m >}}q(x_t \mid x_0){{< /m >}} can be written in closed form:
{{< dm >}}q(x_t \mid x_0) = \mathcal{N}\!\left(x_t;\; \sqrt{\bar{\alpha}_t}\, x_0,\; (1 - \bar{\alpha}_t)\, I\right){{< /dm >}}
Equivalently, we can sample {{< m >}}x_t{{< /m >}} directly from {{< m >}}x_0{{< /m >}} without iterating through intermediate steps:
{{< dm >}}x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1 - \bar{\alpha}_t}\, \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, I){{< /dm >}}
{{< /theorem >}}

{{< proof >}}
**Base case** ({{< m >}}t = 1{{< /m >}}): By definition, {{< m >}}q(x_1 \mid x_0) = \mathcal{N}(\sqrt{\alpha_1}\, x_0, \beta_1 I) = \mathcal{N}(\sqrt{\bar{\alpha}_1}\, x_0, (1 - \bar{\alpha}_1) I){{< /m >}} since {{< m >}}\bar{\alpha}_1 = \alpha_1{{< /m >}} and {{< m >}}\beta_1 = 1 - \alpha_1{{< /m >}}.

**Inductive step**: Assume {{< m >}}x_{t-1} = \sqrt{\bar{\alpha}_{t-1}}\, x_0 + \sqrt{1 - \bar{\alpha}_{t-1}}\, \varepsilon_1{{< /m >}} with {{< m >}}\varepsilon_1 \sim \mathcal{N}(0, I){{< /m >}}. Then:
{{< dm >}}x_t = \sqrt{\alpha_t}\, x_{t-1} + \sqrt{\beta_t}\, \varepsilon_2, \qquad \varepsilon_2 \sim \mathcal{N}(0, I),\; \varepsilon_2 \perp \varepsilon_1{{< /dm >}}
Substituting the inductive hypothesis:
{{< dm >}}x_t = \sqrt{\alpha_t}\bigl(\sqrt{\bar{\alpha}_{t-1}}\, x_0 + \sqrt{1 - \bar{\alpha}_{t-1}}\, \varepsilon_1\bigr) + \sqrt{\beta_t}\, \varepsilon_2{{< /dm >}}
{{< dm >}}= \sqrt{\alpha_t \bar{\alpha}_{t-1}}\, x_0 + \sqrt{\alpha_t(1 - \bar{\alpha}_{t-1})}\, \varepsilon_1 + \sqrt{\beta_t}\, \varepsilon_2{{< /dm >}}

Since {{< m >}}\varepsilon_1{{< /m >}} and {{< m >}}\varepsilon_2{{< /m >}} are independent standard Gaussians, the sum {{< m >}}\sqrt{\alpha_t(1 - \bar{\alpha}_{t-1})}\, \varepsilon_1 + \sqrt{\beta_t}\, \varepsilon_2{{< /m >}} is Gaussian with mean 0 and variance:
{{< dm >}}\alpha_t(1 - \bar{\alpha}_{t-1}) + \beta_t = \alpha_t - \alpha_t \bar{\alpha}_{t-1} + 1 - \alpha_t = 1 - \bar{\alpha}_t{{< /dm >}}
using {{< m >}}\alpha_t \bar{\alpha}_{t-1} = \bar{\alpha}_t{{< /m >}} and {{< m >}}\beta_t = 1 - \alpha_t{{< /m >}}. Therefore:
{{< dm >}}x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1 - \bar{\alpha}_t}\, \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, I) \;\;\square{{< /dm >}}
{{< /proof >}}

**Musical significance**: This result means we can jump directly from a clean spectrogram {{< m >}}x_0{{< /m >}} to any noise level {{< m >}}t{{< /m >}} in one step — essential for efficient training where {{< m >}}t{{< /m >}} is sampled uniformly at random.

### 3.3 The Reverse (Denoising) Process

{{< definition name="DDPM Reverse Process" label="Definition 21.10" >}}
The **reverse process** is a learned Markov chain running backward from {{< m >}}x_T \sim \mathcal{N}(0, I){{< /m >}} to {{< m >}}x_0{{< /m >}}:
{{< dm >}}p_\theta(x_{t-1} \mid x_t) = \mathcal{N}\!\left(x_{t-1};\; \mu_\theta(x_t, t),\; \sigma_t^2 I\right){{< /dm >}}
where {{< m >}}\mu_\theta{{< /m >}} is a neural network predicting the denoised mean, and {{< m >}}\sigma_t^2{{< /m >}} is a fixed or learned variance schedule.
{{< /definition >}}

{{< theorem name="ELBO for Diffusion Models" label="Theorem 21.5" >}}
The log-likelihood of the data is bounded below by:
{{< dm >}}\log p_\theta(x_0) \geq \mathbb{E}_q\!\left[-\log \frac{p(x_T)}{q(x_T \mid x_0)} - \sum_{t=2}^{T} D_{\mathrm{KL}}\!\left(q(x_{t-1} \mid x_t, x_0) \;\|\; p_\theta(x_{t-1} \mid x_t)\right) + \log p_\theta(x_0 \mid x_1)\right]{{< /dm >}}

The key insight: the posterior {{< m >}}q(x_{t-1} \mid x_t, x_0){{< /m >}} is tractable (it is Gaussian), so each KL term can be computed in closed form. Training reduces to making each reverse step {{< m >}}p_\theta(x_{t-1} \mid x_t){{< /m >}} match the true posterior {{< m >}}q(x_{t-1} \mid x_t, x_0){{< /m >}}.
{{< /theorem >}}

{{< proof >}}
*(Sketch.)* Start with {{< m >}}\log p_\theta(x_0) = \log \int p_\theta(x_{0:T})\, dx_{1:T}{{< /m >}}. Introduce the forward process as a variational distribution:
{{< dm >}}\log p_\theta(x_0) = \log \int \frac{p_\theta(x_{0:T})}{q(x_{1:T} \mid x_0)} q(x_{1:T} \mid x_0)\, dx_{1:T} \geq \mathbb{E}_{q(x_{1:T} \mid x_0)}\!\left[\log \frac{p_\theta(x_{0:T})}{q(x_{1:T} \mid x_0)}\right]{{< /dm >}}
by Jensen's inequality. Factorizing both {{< m >}}p_\theta(x_{0:T}) = p(x_T)\prod_{t=1}^T p_\theta(x_{t-1} \mid x_t){{< /m >}} and {{< m >}}q(x_{1:T} \mid x_0) = \prod_{t=1}^T q(x_t \mid x_{t-1}){{< /m >}}, then rewriting the product using Bayes' rule {{< m >}}q(x_t \mid x_{t-1}) = q(x_{t-1} \mid x_t, x_0)\, q(x_t \mid x_0) / q(x_{t-1} \mid x_0){{< /m >}}, telescoping yields the stated decomposition into KL divergence terms. Each {{< m >}}q(x_{t-1} \mid x_t, x_0){{< /m >}} is Gaussian (as the product of two Gaussians), making the KL terms tractable. {{< m >}}\square{{< /m >}}
{{< /proof >}}

In practice, Ho et al. (2020) showed that the simplified loss
{{< dm >}}L_{\mathrm{simple}} = \mathbb{E}_{t, x_0, \varepsilon}\!\left[\|\varepsilon - \varepsilon_\theta(x_t, t)\|^2\right]{{< /dm >}}
(where {{< m >}}\varepsilon_\theta{{< /m >}} is a neural network predicting the noise {{< m >}}\varepsilon{{< /m >}} added at step {{< m >}}t{{< /m >}}) works well and corresponds to a reweighted version of the ELBO.

### 3.4 Score Function and Score Matching

{{< definition name="Score Function" label="Definition 21.11" >}}
The **score function** of a distribution {{< m >}}p_t(x){{< /m >}} at noise level {{< m >}}t{{< /m >}} is the gradient of the log-density:
{{< dm >}}s(x, t) = \nabla_x \log p_t(x){{< /dm >}}
A neural network {{< m >}}s_\theta(x, t){{< /m >}} trained to approximate the score is called a **score network**.
{{< /definition >}}

{{< theorem name="Score-Noise Equivalence" label="Theorem 21.6" >}}
The score function and the noise prediction network are related by:
{{< dm >}}s_\theta(x_t, t) = -\frac{\varepsilon_\theta(x_t, t)}{\sqrt{1 - \bar{\alpha}_t}}{{< /dm >}}
That is, predicting the score is equivalent to predicting the noise, up to a known scaling factor.
{{< /theorem >}}

{{< proof >}}
From the reparameterization {{< m >}}x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1 - \bar{\alpha}_t}\, \varepsilon{{< /m >}}, the conditional density is:
{{< dm >}}q(x_t \mid x_0) = \frac{1}{(2\pi(1 - \bar{\alpha}_t))^{d/2}} \exp\!\left(-\frac{\|x_t - \sqrt{\bar{\alpha}_t}\, x_0\|^2}{2(1 - \bar{\alpha}_t)}\right){{< /dm >}}

Taking the gradient with respect to {{< m >}}x_t{{< /m >}}:
{{< dm >}}\nabla_{x_t} \log q(x_t \mid x_0) = -\frac{x_t - \sqrt{\bar{\alpha}_t}\, x_0}{1 - \bar{\alpha}_t} = -\frac{\sqrt{1 - \bar{\alpha}_t}\, \varepsilon}{1 - \bar{\alpha}_t} = -\frac{\varepsilon}{\sqrt{1 - \bar{\alpha}_t}}{{< /dm >}}

Since the optimal noise predictor satisfies {{< m >}}\varepsilon_\theta(x_t, t) \approx \varepsilon{{< /m >}}, we have {{< m >}}s_\theta(x_t, t) \approx \nabla_{x_t} \log q(x_t \mid x_0) = -\varepsilon/\sqrt{1 - \bar{\alpha}_t}{{< /m >}}. Marginalizing over {{< m >}}x_0{{< /m >}} extends this to the unconditional score {{< m >}}\nabla_{x_t} \log p_t(x_t){{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Musical interpretation**: The score {{< m >}}\nabla_x \log p_t(x){{< /m >}} points toward regions of higher probability density — i.e., toward more "music-like" spectrograms. Denoising by following the score is equivalent to gradually sculpting noise into music by climbing the probability landscape.

### 3.5 The Landscape: Token vs Continuous

> *中文:* "横轴是开放还是闭源。纵轴是用离散token做自回归，还是用连续空间做扩散。"

{{< definition name="Autoregressive (Token-Based) Generative Model" label="Definition 21.12" >}}
Given a vocabulary {{< m >}}V{{< /m >}} (e.g., quantized audio tokens), an **autoregressive model** factorizes the joint distribution of a sequence {{< m >}}(x_1, \ldots, x_n){{< /m >}} as:
{{< dm >}}p(x_1, \ldots, x_n) = \prod_{i=1}^{n} p_\theta(x_i \mid x_1, \ldots, x_{i-1}){{< /dm >}}
Each conditional is parameterized by a Transformer that attends to all previous tokens. Sampling proceeds left-to-right.
{{< /definition >}}

{{< definition name="Continuous Diffusion Generative Model" label="Definition 21.13" >}}
A **diffusion model** defines {{< m >}}p_\theta(x){{< /m >}} implicitly via the reverse process (Definition 21.10). The data {{< m >}}x \in \mathbb{R}^d{{< /m >}} lives in a continuous space (e.g., a mel-spectrogram or a latent embedding). Sampling starts from {{< m >}}x_T \sim \mathcal{N}(0,I){{< /m >}} and iteratively denoises.
{{< /definition >}}

The fundamental mathematical distinction: autoregressive models operate on **discrete sequences** with an explicit likelihood via the chain rule of probability. Diffusion models operate on **continuous vectors** with an implicit likelihood accessible only through the ELBO. This is not merely an implementation choice — it determines the inductive bias: autoregressive models excel at capturing sequential dependencies but struggle with global coherence; diffusion models naturally capture global structure (the entire spectrogram is generated jointly) but must be coaxed into temporal coherence.

---

## Numerical Examples

### Example 21.1: Markov Chain Melody Generation

Consider a simple Markov chain on {{< m >}}\{C, D, E, F, G\}{{< /m >}} (a pentatonic subset) with transition matrix:

{{< dm >}}P = \begin{pmatrix} 0.1 & 0.3 & 0.2 & 0.1 & 0.3 \\ 0.2 & 0.1 & 0.3 & 0.2 & 0.2 \\ 0.1 & 0.2 & 0.1 & 0.3 & 0.3 \\ 0.3 & 0.1 & 0.2 & 0.1 & 0.3 \\ 0.2 & 0.2 & 0.2 & 0.2 & 0.2 \end{pmatrix}{{< /dm >}}

Starting at {{< m >}}X_0 = C{{< /m >}}: row 1 says we go to D with probability 0.3, to G with probability 0.3. Suppose we sample D. From D (row 2), we might sample E (probability 0.3). From E (row 3), we might sample G (probability 0.3). Generated melody fragment: C-D-E-G-...

The two-step transition {{< m >}}P^2{{< /m >}} entry {{< m >}}(C,G){{< /m >}} is: {{< m >}}\sum_k P_{Ck} P_{kG} = 0.1(0.3) + 0.3(0.2) + 0.2(0.3) + 0.1(0.3) + 0.3(0.2) = 0.24{{< /m >}}.

### Example 21.2: Forward Diffusion on a Spectrogram Pixel

Take one pixel of a mel-spectrogram: {{< m >}}x_0 = 3.0{{< /m >}} (log-amplitude). With a linear schedule {{< m >}}\beta_t = 0.0001 + (0.02 - 0.0001) \cdot t/T{{< /m >}} for {{< m >}}T = 1000{{< /m >}}:

- At {{< m >}}t = 1{{< /m >}}: {{< m >}}\bar{\alpha}_1 \approx 0.9999{{< /m >}}, so {{< m >}}x_1 \approx 0.99995 \cdot 3.0 + 0.01 \cdot \varepsilon \approx 3.0{{< /m >}} (nearly unchanged).
- At {{< m >}}t = 500{{< /m >}}: {{< m >}}\bar{\alpha}_{500} \approx 0.05{{< /m >}}, so {{< m >}}x_{500} \approx 0.22 \cdot 3.0 + 0.97 \cdot \varepsilon{{< /m >}} (mostly noise).
- At {{< m >}}t = 1000{{< /m >}}: {{< m >}}\bar{\alpha}_{1000} \approx 0{{< /m >}}, so {{< m >}}x_{1000} \approx \varepsilon{{< /m >}} (pure noise).

---

## Musical Connection

{{< musical-connection >}}
> *中文:* "三集，同一个问题：怎么把音乐变成概率模型能操作的对象？"

**The Representation War**: The narration frames the current landscape as a battle between two representations:

> *中文:* "今天的模型大战，本质是表示大战——音乐到底该写成token，还是雕成连续潜空间？"

| Approach | Representation | Framework | Examples |
|----------|---------------|-----------|----------|
| **Token-based** | Discrete tokens (MIDI, audio codecs) | Autoregressive | MusicLM, MusicGen |
| **Continuous** | Spectrograms, latent vectors | Diffusion | Riffusion, Stable Audio, ACE-Step |

The token-based approach factors the joint distribution as a product of conditionals:

{{< dm >}}p(x_1, \ldots, x_n) = \prod_{i=1}^{n} p(x_i \mid x_1, \ldots, x_{i-1}){{< /dm >}}

and predicts one token at a time. The continuous approach treats the entire musical signal as a point in a high-dimensional space and sculpts it from noise by reversing a Markov chain. Both are valid factorizations of the same underlying probability {{< m >}}p(x){{< /m >}}.

> *中文:* "Riffusion：先把声音变成频谱图——一张二维的图片。然后用图片扩散模型去生成新的频谱图..."

**The arc from EP21 to EP23**: This episode (EP21) asks *how the math changed*. {{< episode-ref ep="22" >}}EP22{{< /episode-ref >}} examines the specific architectures (EnCodec, RVQ, DiT). {{< episode-ref ep="23" >}}EP23{{< /episode-ref >}} addresses evaluation — how do we measure whether generated music is "good"?
{{< /musical-connection >}}

---

## Limits and Open Questions

1. **Markov chains are not dead**: Higher-order Markov models with clever state representations (e.g., learned embeddings rather than raw {{< m >}}k{{< /m >}}-grams) remain useful as baselines and components of hybrid systems.

2. **Attention complexity**: Standard attention is {{< m >}}O(n^2){{< /m >}} in sequence length. For long musical pieces (minutes of audio tokenized at high resolution), this is a bottleneck. Linear attention, sparse attention, and state-space models ({{< episode-ref ep="24" >}}EP24{{< /episode-ref >}}) are active research directions.

3. **Diffusion speed**: DDPM requires hundreds of denoising steps. Accelerated samplers (DDIM, consistency models, flow matching) reduce this to tens or single-digit steps — but the quality-speed tradeoff is not fully understood.

4. **The representation question is open**: Whether music is better represented as discrete tokens or continuous signals is an empirical question with no theoretical resolution. Hybrid models (e.g., diffusion in a discrete-token latent space) blur the boundary.

> *中文:* "七个模型，表面上各有各的招。但底层数学只有两条路：要么把音乐切成token一个一个预测，要么把音乐当作连续空间整体雕刻。"

5. **Controllability vs quality**: Markov chains offer full control (just edit the transition matrix) but poor quality. Diffusion models offer high quality but limited fine-grained control. Bridging this gap is the central engineering challenge of AI music generation.

---

## Historical Timeline

| Year | Development | Mathematical core |
|------|-------------|-------------------|
| 1906 | Markov formalizes dependent random variables | Transition matrix {{< m >}}P{{< /m >}} |
| 1957 | Hiller & Isaacson: *Illiac Suite* | Markov chain on {{< m >}}\mathbb{Z}_{12}{{< /m >}} |
| 1986 | Elman / Jordan: recurrent neural networks | Hidden state, backpropagation through time |
| 1997 | Hochreiter & Schmidhuber: LSTM | Gated memory cells |
| 2017 | Vaswani et al.: Transformer | Softmax attention = dynamic stochastic matrix |
| 2019 | Music Transformer | Long-range attention for symbolic music |
| 2020 | Ho et al.: DDPM | Score matching, forward/reverse diffusion |
| 2022 | Riffusion | Image diffusion on spectrograms |
| 2023 | MusicGen, MusicLM | Token-based autoregressive audio generation |
| 2024 | ACE-Step, Stable Audio | Full-song diffusion in latent space |

---

## Academic References

1. Hiller, L. & Isaacson, L. (1957). *Musical Composition with a High-Speed Digital Computer*. Experimental Music, McGraw-Hill.
2. Norris, J.R. (1997). *Markov Chains*. Cambridge University Press.
3. Seneta, E. (2006). *Non-negative Matrices and Markov Chains*, 3rd ed. Springer.
4. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, L. & Polosukhin, I. (2017). "Attention Is All You Need." *Advances in Neural Information Processing Systems* 30 (NeurIPS).
5. Huang, C.-Z.A., Vaswani, A., Uszkoreit, J., Shazeer, N., Simon, I., Hawthorne, C., Dai, A.M., Hoffman, M.D., Dinculescu, M. & Eck, D. (2019). "Music Transformer: Generating Music with Long-Term Structure." *ICLR 2019*.
6. Ho, J., Jain, A. & Abbeel, P. (2020). "Denoising Diffusion Probabilistic Models." *Advances in Neural Information Processing Systems* 33 (NeurIPS).
7. Song, Y. & Ermon, S. (2019). "Generative Modeling by Estimating Gradients of the Data Distribution." *NeurIPS 2019*.
8. Song, Y., Sohl-Dickstein, J., Kingma, D.P., Kumar, A., Ermon, S. & Poole, B. (2021). "Score-Based Generative Modeling through Stochastic Differential Equations." *ICLR 2021*.
9. Forsyth, S. (2022). *Riffusion — Stable Diffusion for Real-Time Music Generation*. https://www.riffusion.com
10. Copet, J., Kreuk, F., Gat, I., Remez, T., Kant, D., Synnaeve, G., Adi, Y. & Defossez, A. (2023). "Simple and Controllable Music Generation." *NeurIPS 2023*. (MusicGen)
11. Agostinelli, A., Denk, T.I., Borsos, Z., Engel, J., Verzetti, M., Tagliasacchi, A., Marafioti, A., Ye, Z., Le Roux, J. & Frank, J. (2023). "MusicLM: Generating Music From Text." *arXiv:2301.11325*.
12. Levin, D.A., Peres, Y. & Wilmer, E.L. (2009). *Markov Chains and Mixing Times*. AMS.
13. Sohl-Dickstein, J., Weiss, E., Maheswaranathan, N. & Ganguli, S. (2015). "Deep Unsupervised Learning using Nonequilibrium Thermodynamics." *ICML 2015*.
14. Hochreiter, S. & Schmidhuber, J. (1997). "Long Short-Term Memory." *Neural Computation* 9(8), 1735-1780.
15. Briot, J.-P., Hadjeres, G. & Pachet, F. (2020). *Deep Learning Techniques for Music Generation*. Springer.
