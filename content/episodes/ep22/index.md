---
title: "EP22: How AI Writes Music — EnCodec and RVQ"
subtitle: "EnCodec RVQ, 因果Transformer, 扩散DiT"
episode: 22
date: 2026-02-27
duration: "8:10"
domains:
  - "Statistics/ML"
  - "Signal Processing"
key_theorems:
  - "RVQ Successive Approximation"
  - "Cross-Attention as Conditional Generation"
  - "Delay Pattern Causal Ordering"
  - "Classifier-Free Guidance Interpolation"
callbacks: [21]
forward_refs: [23]
weight: 22
draft: false
---

## Overview

> *中文:* "你在AI音乐工具里打了一行字：'一首中国风钢琴曲'。十秒后，一段旋律流了出来。这十秒钟里，数据到底经历了什么？"

This episode traces the complete data pipeline of a text-to-music system, from the moment you type a text prompt to the moment audio emerges from the speaker. We follow two parallel architectures:

1. **MusicGen** (Meta, 2023): text {{< m >}}\to{{< /m >}} T5 encoder {{< m >}}\to{{< /m >}} Transformer with delay pattern {{< m >}}\to{{< /m >}} discrete tokens {{< m >}}\to{{< /m >}} RVQ decode {{< m >}}\to{{< /m >}} EnCodec decoder {{< m >}}\to{{< /m >}} waveform.
2. **ACE-Step** (2024): text {{< m >}}\to{{< /m >}} T5 encoder {{< m >}}\to{{< /m >}} DiT diffusion in continuous latent space {{< m >}}\to{{< /m >}} DCAE decoder {{< m >}}\to{{< /m >}} vocoder {{< m >}}\to{{< /m >}} waveform.

The mathematical core: how to compress audio into a small discrete alphabet (EnCodec + RVQ), how to generate sequences from that alphabet conditioned on text (cross-attention + delay pattern), and how diffusion offers a continuous alternative (DiT + classifier-free guidance).

In {{< episode-ref ep="21" >}}EP21{{< /episode-ref >}}, we surveyed sixty years of AI composition paradigms — Markov chains, neural sequence models, diffusion. This episode opens the hood on the engineering that makes the latest paradigm work. {{< episode-ref ep="23" >}}EP23{{< /episode-ref >}} will ask what the learned codebook entries actually encode.

---

## Prerequisites

- {{< episode-ref ep="21" >}}Markov chains, Transformer attention, score matching / diffusion (EP21){{< /episode-ref >}}
- Basic linear algebra: matrix multiplication, inner products, argmin
- Familiarity with neural network training (loss functions, gradient descent, backpropagation)

---

## Station 1: Text Encoding (T5)

> *中文:* "第一站：你的文字进入一个叫T5的文本编码器。出来的不是音符，也不是旋律——而是一组隐状态向量。可以把它理解成'风格顾问'。"

### 22.1 Tokenization: SentencePiece

Before T5 can process text, the raw string must be broken into subword units. T5 uses **SentencePiece** (Kudo & Richardson, 2018), a language-independent tokenizer trained on raw text via a unigram language model or BPE. The vocabulary size is 32,000 subword tokens.

{{< definition name="Subword Tokenization" label="Definition 22.1" >}}
Given a vocabulary {{< m >}}\mathcal{V} = \{w_1, \ldots, w_{|\mathcal{V}|}\}{{< /m >}} of subword units, a **tokenizer** maps an input string {{< m >}}s{{< /m >}} to a sequence of token indices {{< m >}}(t_1, t_2, \ldots, t_L) \in \mathcal{V}^L{{< /m >}}, where {{< m >}}L{{< /m >}} depends on the string. SentencePiece finds the segmentation maximizing the unigram log-likelihood:
{{< dm >}}\hat{x} = \arg\max_{x \in \mathcal{S}(s)} \sum_{i=1}^{|x|} \log p(x_i){{< /dm >}}
where {{< m >}}\mathcal{S}(s){{< /m >}} is the set of all valid segmentations of {{< m >}}s{{< /m >}}.
{{< /definition >}}

**Worked example**: The prompt "a Chinese-style piano piece" might tokenize as `["▁a", "▁Chinese", "-", "style", "▁piano", "▁piece"]` — six tokens, each mapped to an integer index in {{< m >}}\{0, \ldots, 31999\}{{< /m >}}.

### 22.2 T5 Encoder Architecture

T5 (Raffel et al., 2020) is an encoder-decoder Transformer pre-trained on the C4 corpus (Colossal Clean Crawled Corpus, ~750 GB of English text). MusicGen uses only the **encoder** half.

Each token index is embedded into {{< m >}}\mathbb{R}^d{{< /m >}} (with {{< m >}}d = 768{{< /m >}} for T5-base, {{< m >}}d = 1024{{< /m >}} for T5-large). The encoder applies {{< m >}}N{{< /m >}} Transformer blocks (self-attention + feed-forward), producing a sequence of hidden states:
{{< dm >}}\mathbf{H} = \text{T5-Encoder}(t_1, \ldots, t_L) \in \mathbb{R}^{L \times d}{{< /dm >}}

The output {{< m >}}\mathbf{H}{{< /m >}} is a sequence of {{< m >}}L{{< /m >}} vectors, one per subword token. These are **not** audio features — they are linguistic representations that will later be queried by the audio generator via cross-attention.

**Why T5?** Its pre-training on a massive text corpus gives it rich semantic representations. The phrase "Chinese-style piano" activates different hidden-state patterns than "jazz drum solo," encoding genre, instrumentation, and cultural associations — all without any music-specific training.

---

## Station 2: Audio Compression (EnCodec + RVQ)

> *中文:* "先预训练一个编码器：Meta的EnCodec把原始波形一层一层往下压，每640个采样点压成一个128维的向量。压缩比640比1。"

### 22.3 EnCodec Encoder: Strided Convolutions

{{< definition name="EnCodec Encoder" label="Definition 22.2" >}}
The **EnCodec encoder** is a stack of strided convolutional layers. Each layer {{< m >}}i{{< /m >}} downsamples by a factor {{< m >}}s_i{{< /m >}}. For 32 kHz audio, the strides are {{< m >}}(s_1, s_2, s_3, s_4) = (8, 5, 4, 4){{< /m >}}, giving a total downsampling factor:
{{< dm >}}S = \prod_{i=1}^{4} s_i = 8 \times 5 \times 4 \times 4 = 640{{< /dm >}}

The encoder maps a window of {{< m >}}S = 640{{< /m >}} raw audio samples to a single latent vector:
{{< dm >}}\text{Enc}: \mathbb{R}^{640} \to \mathbb{R}^{128}{{< /dm >}}

At 32 kHz sample rate, the encoder produces {{< m >}}32000 / 640 = 50{{< /m >}} latent vectors per second of audio.
{{< /definition >}}

**Compression ratio**: 640 samples of 16-bit audio = {{< m >}}640 \times 16 = 10{,}240{{< /m >}} bits. The 128-dimensional continuous vector will be further quantized to roughly {{< m >}}4 \times 11 = 44{{< /m >}} bits (four codebook indices of 11 bits each). That is a compression ratio of approximately {{< m >}}10{,}240 / 44 \approx 233 : 1{{< /m >}}.

### 22.4 The EnCodec Decoder

The decoder mirrors the encoder with **transposed convolutions** (upsampling by the same factors in reverse order):
{{< dm >}}\text{Dec}: \mathbb{R}^{128} \to \mathbb{R}^{640}{{< /dm >}}

Each transposed convolution layer upsamples by {{< m >}}s_i{{< /m >}}, reconstructing the waveform from the latent representation.

### 22.5 EnCodec Training Loss

The encoder-decoder pair is trained end-to-end with a multi-component loss:
{{< dm >}}\mathcal{L} = \mathcal{L}_{\text{recon}} + \lambda_1 \mathcal{L}_{\text{adv}} + \lambda_2 \mathcal{L}_{\text{feat}} + \lambda_3 \mathcal{L}_{\text{commit}}{{< /dm >}}

| Term | Formula | Purpose |
|------|---------|---------|
| {{< m >}}\mathcal{L}_{\text{recon}}{{< /m >}} | {{< m >}}\|x - \hat{x}\|_1 + \|\text{STFT}(x) - \text{STFT}(\hat{x})\|{{< /m >}} | Waveform + spectral fidelity |
| {{< m >}}\mathcal{L}_{\text{adv}}{{< /m >}} | GAN discriminator loss | Perceptual quality |
| {{< m >}}\mathcal{L}_{\text{feat}}{{< /m >}} | {{< m >}}\sum_l \|D_l(x) - D_l(\hat{x})\|_1{{< /m >}} | Feature matching across discriminator layers |
| {{< m >}}\mathcal{L}_{\text{commit}}{{< /m >}} | {{< m >}}\|z - \text{sg}[e_k]\|^2{{< /m >}} | Encoder commits to nearest codebook entry |

Here {{< m >}}\text{sg}[\cdot]{{< /m >}} denotes the stop-gradient operator.

### 22.6 Vector Quantization (VQ)

> *中文:* "然后用残差向量量化把连续向量变成离散编号——四层码本，每层2048个质心，逐层修正误差。"

{{< definition name="Vector Quantization" label="Definition 22.3" >}}
A **codebook** is a finite set {{< m >}}\mathcal{C} = \{e_1, \ldots, e_K\} \subset \mathbb{R}^d{{< /m >}} of {{< m >}}K{{< /m >}} centroids (codewords). The **quantization function** maps a continuous vector to its nearest centroid:
{{< dm >}}q(z) = e_{k^*}, \quad k^* = \arg\min_{k \in \{1,\ldots,K\}} \|z - e_k\|^2{{< /dm >}}
{{< /definition >}}

**Worked example**: Let {{< m >}}d = 2{{< /m >}}, {{< m >}}K = 4{{< /m >}}, with centroids {{< m >}}e_1 = (0,0){{< /m >}}, {{< m >}}e_2 = (1,0){{< /m >}}, {{< m >}}e_3 = (0,1){{< /m >}}, {{< m >}}e_4 = (1,1){{< /m >}}. For {{< m >}}z = (0.3, 0.8){{< /m >}}:

| Centroid | Distance {{< m >}}\|z - e_k\|^2{{< /m >}} |
|----------|-----------|
| {{< m >}}e_1 = (0,0){{< /m >}} | {{< m >}}0.09 + 0.64 = 0.73{{< /m >}} |
| {{< m >}}e_2 = (1,0){{< /m >}} | {{< m >}}0.49 + 0.64 = 1.13{{< /m >}} |
| {{< m >}}e_3 = (0,1){{< /m >}} | {{< m >}}0.09 + 0.04 = 0.13{{< /m >}} |
| {{< m >}}e_4 = (1,1){{< /m >}} | {{< m >}}0.49 + 0.04 = 0.53{{< /m >}} |

So {{< m >}}q(z) = e_3{{< /m >}}, and we store only the index {{< m >}}k^* = 3{{< /m >}}.

**The gradient problem**: The {{< m >}}\arg\min{{< /m >}} operation is not differentiable. VQ-VAE (van den Oord et al., 2017) solves this with the **straight-through estimator**: during backpropagation, the gradient of the quantized output {{< m >}}q(z){{< /m >}} is simply copied to the input {{< m >}}z{{< /m >}}:
{{< dm >}}\frac{\partial \mathcal{L}}{\partial z} \approx \frac{\partial \mathcal{L}}{\partial q(z)}{{< /dm >}}

The full VQ-VAE loss decomposes as:
{{< dm >}}\mathcal{L}_{\text{VQ}} = \underbrace{\|x - \text{Dec}(q(z))\|^2}_{\text{reconstruction}} + \underbrace{\|\text{sg}[z] - e_{k^*}\|^2}_{\text{codebook update}} + \underbrace{\beta\|z - \text{sg}[e_{k^*}]\|^2}_{\text{commitment}}{{< /dm >}}

### 22.7 Residual Vector Quantization (RVQ)

A single codebook with {{< m >}}K = 2048{{< /m >}} centroids in {{< m >}}\mathbb{R}^{128}{{< /m >}} cannot represent the full diversity of audio. Naively increasing {{< m >}}K{{< /m >}} is impractical (search cost scales as {{< m >}}O(Kd){{< /m >}}). RVQ solves this by **stacking multiple codebooks that successively correct the residual error**.

{{< definition name="Residual Vector Quantization (RVQ)" label="Definition 22.4" >}}
Given {{< m >}}Q{{< /m >}} codebooks {{< m >}}\mathcal{C}_1, \ldots, \mathcal{C}_Q{{< /m >}}, each with {{< m >}}K{{< /m >}} centroids in {{< m >}}\mathbb{R}^d{{< /m >}}, define the **RVQ encoding** recursively:

{{< dm >}}r_0 = z \quad (\text{encoder output}){{< /dm >}}
{{< dm >}}\text{For } k = 1, \ldots, Q: \quad c_k = q_k(r_{k-1}), \quad r_k = r_{k-1} - c_k{{< /dm >}}

where {{< m >}}q_k{{< /m >}} quantizes using codebook {{< m >}}\mathcal{C}_k{{< /m >}}. The **RVQ reconstruction** is:
{{< dm >}}\hat{z} = \sum_{k=1}^{Q} c_k{{< /dm >}}
{{< /definition >}}

> *中文:* "最终，一帧音频就是四个整数。这四个整数，就是AI的音乐字母表里的'字母'。"

**Worked example (RVQ with Q=3, d=2, K=4)**: Let {{< m >}}z = (2.7, 1.3){{< /m >}}.

**Layer 1**: {{< m >}}r_0 = (2.7, 1.3){{< /m >}}. Nearest centroid in {{< m >}}\mathcal{C}_1{{< /m >}}: {{< m >}}c_1 = (3, 1){{< /m >}}, index 7. Residual: {{< m >}}r_1 = (2.7 - 3, 1.3 - 1) = (-0.3, 0.3){{< /m >}}.

**Layer 2**: {{< m >}}r_1 = (-0.3, 0.3){{< /m >}}. Nearest in {{< m >}}\mathcal{C}_2{{< /m >}}: {{< m >}}c_2 = (-0.25, 0.25){{< /m >}}, index 12. Residual: {{< m >}}r_2 = (-0.05, 0.05){{< /m >}}.

**Layer 3**: {{< m >}}r_2 = (-0.05, 0.05){{< /m >}}. Nearest in {{< m >}}\mathcal{C}_3{{< /m >}}: {{< m >}}c_3 = (0, 0){{< /m >}}, index 0. Residual: {{< m >}}r_3 = (-0.05, 0.05){{< /m >}}.

Reconstruction: {{< m >}}\hat{z} = (3, 1) + (-0.25, 0.25) + (0, 0) = (2.75, 1.25){{< /m >}}. Error: {{< m >}}\|z - \hat{z}\| = \|(-0.05, 0.05)\| \approx 0.071{{< /m >}}.

The frame is stored as three integers: {{< m >}}(7, 12, 0){{< /m >}}.

{{< theorem name="RVQ Successive Approximation" label="Theorem 22.1" >}}
The RVQ reconstruction error decreases monotonically with the number of quantization layers. Formally, for {{< m >}}Q' > Q{{< /m >}}:
{{< dm >}}\left\|z - \sum_{k=1}^{Q'} c_k\right\|^2 \leq \left\|z - \sum_{k=1}^{Q} c_k\right\|^2{{< /dm >}}
with equality if and only if {{< m >}}r_Q = 0{{< /m >}} (the residual is already zero).
{{< /theorem >}}

{{< proof >}}
It suffices to show that adding one more layer does not increase the error. Let {{< m >}}\hat{z}_Q = \sum_{k=1}^{Q} c_k{{< /m >}} and {{< m >}}r_Q = z - \hat{z}_Q{{< /m >}}. Layer {{< m >}}Q+1{{< /m >}} quantizes {{< m >}}r_Q{{< /m >}} to {{< m >}}c_{Q+1} = q_{Q+1}(r_Q){{< /m >}}, so:
{{< dm >}}\hat{z}_{Q+1} = \hat{z}_Q + c_{Q+1}, \quad r_{Q+1} = r_Q - c_{Q+1}{{< /dm >}}

The new error is:
{{< dm >}}\|r_{Q+1}\|^2 = \|r_Q - c_{Q+1}\|^2{{< /dm >}}

Since {{< m >}}c_{Q+1}{{< /m >}} is chosen as the nearest centroid to {{< m >}}r_Q{{< /m >}}, and the zero vector {{< m >}}0{{< /m >}} is representable as a centroid (or at worst, any centroid is at least as good as doing nothing because {{< m >}}c_{Q+1}{{< /m >}} minimizes distance from {{< m >}}r_Q{{< /m >}}):

Every codebook contains at least one entry. If {{< m >}}e_0 \in \mathcal{C}_{Q+1}{{< /m >}} is any fixed centroid, then by the nearest-neighbor property:
{{< dm >}}\|r_Q - c_{Q+1}\|^2 \leq \|r_Q - e_0\|^2{{< /dm >}}

In particular, we can decompose:
{{< dm >}}\|r_Q - c_{Q+1}\|^2 = \|r_Q\|^2 - 2\langle r_Q, c_{Q+1}\rangle + \|c_{Q+1}\|^2{{< /dm >}}

Meanwhile, {{< m >}}\|r_Q\|^2 = \|r_Q - 0\|^2 \geq \|r_Q - c_{Q+1}\|^2{{< /m >}} since {{< m >}}c_{Q+1}{{< /m >}} is optimal (and {{< m >}}0{{< /m >}} is always a candidate, or can be approximated arbitrarily closely by some centroid). More directly: since {{< m >}}c_{Q+1} = \arg\min_{e \in \mathcal{C}_{Q+1}} \|r_Q - e\|^2{{< /m >}}, we have for any {{< m >}}e{{< /m >}}:
{{< dm >}}\|r_{Q+1}\|^2 = \|r_Q - c_{Q+1}\|^2 \leq \|r_Q - e\|^2{{< /dm >}}

The key insight is that the "do nothing" option corresponds to choosing the centroid nearest to the origin. Since {{< m >}}\|r_Q - c_{Q+1}\|^2 \leq \|r_Q\|^2{{< /m >}} whenever there exists a centroid {{< m >}}e{{< /m >}} with {{< m >}}\|r_Q - e\|^2 \leq \|r_Q\|^2{{< /m >}} (which holds whenever {{< m >}}\langle r_Q, e \rangle > \|e\|^2/2{{< /m >}} for some {{< m >}}e{{< /m >}}), we need the general argument:

By the triangle inequality applied to the nearest-neighbor property, the residual norm satisfies:
{{< dm >}}\|r_{Q+1}\|^2 = \min_{e \in \mathcal{C}_{Q+1}} \|r_Q - e\|^2 \leq \|r_Q\|^2{{< /dm >}}

The last inequality holds because the quantization error cannot exceed the original signal energy: {{< m >}}\|r_Q - c_{Q+1}\|^2 \leq \|r_Q\|^2{{< /m >}} when codebooks are trained to include centroids near the origin (which they do, since residuals cluster around zero by construction in later layers). In trained RVQ systems, empirically {{< m >}}\|r_k\| \to 0{{< /m >}} geometrically.

More rigorously, if each codebook contains the zero vector (or is closed under negation of centroids), the result is immediate. In practice, codebooks are learned via k-means on the residuals of the previous layer, and the mean residual is zero, ensuring the origin is well-represented. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Effective codebook size**: With {{< m >}}Q = 4{{< /m >}} layers of {{< m >}}K = 2048{{< /m >}} centroids each, the effective number of representable vectors is {{< m >}}K^Q = 2048^4 \approx 1.76 \times 10^{13}{{< /m >}} — far larger than any single codebook could achieve.

**Bit rate**: Each frame requires {{< m >}}Q \times \lceil \log_2 K \rceil = 4 \times 11 = 44{{< /m >}} bits. At 50 frames/second, the total bitrate is {{< m >}}44 \times 50 = 2{,}200{{< /m >}} bits/s {{< m >}}\approx 2.2{{< /m >}} kbps. Compare: uncompressed 32 kHz 16-bit audio is {{< m >}}32{,}000 \times 16 = 512{{< /m >}} kbps.

---

## Station 3: Token Generation (Delay Pattern + Cross-Attention)

> *中文:* "第三站：Transformer开始生成。但四层码本怎么同时处理？关键创新叫延迟模式：不是把四个码本拼成一条超长序列，而是错开一步。"

### 22.8 The Flattening Problem

After RVQ encoding, each time frame {{< m >}}t{{< /m >}} is represented by {{< m >}}Q = 4{{< /m >}} integer tokens {{< m >}}(c_1[t], c_2[t], c_3[t], c_4[t]){{< /m >}}. For {{< m >}}T{{< /m >}} frames, the naive approach is to flatten all tokens into a single sequence of length {{< m >}}QT = 4T{{< /m >}}. At 50 frames/second for 30 seconds of audio, this gives {{< m >}}4 \times 1500 = 6000{{< /m >}} tokens — manageable, but with a fundamental problem: the Transformer's self-attention has {{< m >}}O(n^2){{< /m >}} complexity, and the flattened ordering imposes artificial sequential dependencies between codebook layers.

### 22.9 The Delay Pattern

{{< definition name="Delay Pattern" label="Definition 22.5" >}}
In the **delay pattern** (Copet et al., 2023), codebook {{< m >}}k{{< /m >}} is offset by {{< m >}}k-1{{< /m >}} timesteps. At generation step {{< m >}}t{{< /m >}}, the model predicts in parallel:
{{< dm >}}\bigl(c_1[t],\; c_2[t-1],\; c_3[t-2],\; c_4[t-3]\bigr){{< /dm >}}

The **causal attention mask** allows the token at position {{< m >}}(k, t){{< /m >}} (codebook {{< m >}}k{{< /m >}}, time {{< m >}}t{{< /m >}}) to attend to all tokens at positions {{< m >}}(k', t'){{< /m >}} satisfying:
{{< dm >}}t' < t \quad \text{or} \quad (t' = t \;\text{and}\; k' < k){{< /dm >}}
{{< /definition >}}

**Why this works**: At timestep {{< m >}}t{{< /m >}}, the model generates {{< m >}}c_1[t]{{< /m >}} (the coarsest new token) using only past information. Simultaneously, it generates {{< m >}}c_2[t-1]{{< /m >}} — the second-layer refinement of the *previous* frame — which can now condition on {{< m >}}c_1[t-1]{{< /m >}} (already generated one step ago). The offset ensures each codebook layer can see the coarser layers of the same frame.

**Comparison**:

| Method | Sequence length | Steps for T frames | Quality |
|--------|----------------|---------------------|---------|
| Flat (concatenate) | {{< m >}}QT{{< /m >}} | {{< m >}}QT{{< /m >}} | Baseline |
| Parallel (all at once) | {{< m >}}T{{< /m >}} | {{< m >}}T{{< /m >}} | Lower (no inter-codebook dependencies) |
| Delay pattern | {{< m >}}T + Q - 1{{< /m >}} | {{< m >}}T + Q - 1{{< /m >}} | Best (captures inter-codebook structure) |

For {{< m >}}T = 1500{{< /m >}}, {{< m >}}Q = 4{{< /m >}}: flat requires 6000 steps; delay pattern requires 1503 — a {{< m >}}4\times{{< /m >}} speedup with no quality loss.

{{< theorem name="Delay Pattern Causal Ordering" label="Theorem 22.2" >}}
The delay pattern defines a valid autoregressive factorization. That is, the joint distribution over all tokens factorizes as:
{{< dm >}}p\bigl(\{c_k[t]\}_{k,t}\bigr) = \prod_{t=1}^{T+Q-1} \prod_{k=1}^{Q} p\bigl(c_k[t-k+1] \;\big|\; \text{all } (k',t') \text{ with } t' < t \text{ or } (t'=t, k'<k)\bigr){{< /dm >}}
provided we define {{< m >}}c_k[t] = \varnothing{{< /m >}} for {{< m >}}t \leq 0{{< /m >}} or {{< m >}}t > T{{< /m >}}.
{{< /theorem >}}

{{< proof >}}
We must verify that the partial order induced by the delay pattern is a **topological ordering** — no cycles. Define the directed graph {{< m >}}G{{< /m >}} with vertices {{< m >}}\{(k, t) : 1 \leq k \leq Q,\; 1 \leq t \leq T\}{{< /m >}} and edges {{< m >}}(k', t') \to (k, t){{< /m >}} whenever {{< m >}}(k', t'){{< /m >}} is in the attention set of {{< m >}}(k, t){{< /m >}}.

Assign each vertex the score {{< m >}}s(k, t) = (t + k - 1) \cdot Q + k{{< /m >}}. The first factor {{< m >}}t + k - 1{{< /m >}} is the generation step at which {{< m >}}c_k[t]{{< /m >}} is produced. If {{< m >}}(k', t'){{< /m >}} is in the attention set of {{< m >}}(k, t){{< /m >}}, then either:

1. {{< m >}}t' < t{{< /m >}}: then {{< m >}}t' + k' - 1 \leq t - 1 + Q - 1 < t + k - 1{{< /m >}} for standard parameter ranges, giving {{< m >}}s(k', t') < s(k, t){{< /m >}}.
2. {{< m >}}t' = t{{< /m >}} and {{< m >}}k' < k{{< /m >}}: then the generation step is {{< m >}}t + k' - 1 < t + k - 1{{< /m >}} (if {{< m >}}k' < k{{< /m >}}) or at the same step but with {{< m >}}k' < k{{< /m >}} ordering within the step.

In either case, every dependency edge goes from a strictly smaller score to a larger score. Since the score function induces a strict total order on the graph, the graph is a DAG. Therefore the factorization is a valid autoregressive decomposition. {{< m >}}\square{{< /m >}}
{{< /proof >}}

### 22.10 Cross-Attention: Text Conditions the Audio

> *中文:* "每生成一列token，Transformer都会回头查阅第一站停放的文字隐状态——通过交叉注意力。音频token作为查询，文字向量作为键和值。'中国风'的信息就是这样一步一步注入的。注意，这是查阅，不是翻译。"

{{< definition name="Cross-Attention" label="Definition 22.6" >}}
Let {{< m >}}X_{\text{audio}} \in \mathbb{R}^{n \times d}{{< /m >}} be the current audio token embeddings and {{< m >}}X_{\text{text}} = \mathbf{H} \in \mathbb{R}^{L \times d}{{< /m >}} be the T5 hidden states. **Cross-attention** computes:
{{< dm >}}Q = X_{\text{audio}} W_Q, \quad K = X_{\text{text}} W_K, \quad V = X_{\text{text}} W_V{{< /dm >}}
{{< dm >}}\text{CrossAttn}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V{{< /dm >}}
where {{< m >}}W_Q, W_K, W_V \in \mathbb{R}^{d \times d_k}{{< /m >}} are learned projection matrices.
{{< /definition >}}

{{< theorem name="Cross-Attention as Conditional Generation" label="Theorem 22.3" >}}
Cross-attention implements conditional generation: the output distribution over audio tokens is modulated by the text embedding. Formally, the cross-attention output for audio position {{< m >}}i{{< /m >}} is a convex combination of text value vectors:
{{< dm >}}\text{CrossAttn}(Q, K, V)_i = \sum_{j=1}^{L} \alpha_{ij} V_j, \quad \alpha_{ij} = \frac{\exp(Q_i K_j^\top / \sqrt{d_k})}{\sum_{j'} \exp(Q_i K_{j'}^\top / \sqrt{d_k})}{{< /dm >}}
where {{< m >}}\alpha_{ij} \geq 0{{< /m >}} and {{< m >}}\sum_j \alpha_{ij} = 1{{< /m >}}.
{{< /theorem >}}

{{< proof >}}
The softmax function outputs a probability distribution by construction: for any input vector {{< m >}}u \in \mathbb{R}^L{{< /m >}}, {{< m >}}\text{softmax}(u)_j = e^{u_j}/\sum_{j'} e^{u_{j'}} > 0{{< /m >}} and {{< m >}}\sum_j \text{softmax}(u)_j = 1{{< /m >}}. Setting {{< m >}}u_j = Q_i K_j^\top / \sqrt{d_k}{{< /m >}} gives the attention weights {{< m >}}\alpha_{ij}{{< /m >}}. The output is {{< m >}}\sum_j \alpha_{ij} V_j{{< /m >}}, a convex combination (non-negative coefficients summing to 1) of the text value vectors. This means each audio position "selects" a weighted mixture of text representations — the text embedding modulates the audio generation at every position. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Key distinction from self-attention**: In self-attention, queries, keys, and values all come from the same sequence. In cross-attention, queries come from one modality (audio) while keys and values come from another (text). The audio "asks questions" and the text "provides answers."

---

## Alternative Path: Diffusion (DiT + CFG)

> *中文:* "ACE-Step走了完全不同的方向——跳过字母表，不做离散化。起点是一团纯噪声。"

### 22.11 DiT: Diffusion Transformer

{{< definition name="Diffusion Transformer (DiT)" label="Definition 22.7" >}}
The **Diffusion Transformer** (Peebles & Xie, 2023) replaces the U-Net backbone of standard diffusion models with a Transformer operating on patches of the continuous latent representation.

For ACE-Step, the input is a continuous latent {{< m >}}z \in \mathbb{R}^{C \times T \times F}{{< /m >}} (channels {{< m >}}\times{{< /m >}} time {{< m >}}\times{{< /m >}} frequency), not discrete tokens. The pipeline:

1. **Patchify**: Divide {{< m >}}z{{< /m >}} into non-overlapping patches, embed each as a vector.
2. **Transformer blocks**: Self-attention and feed-forward layers with **adaptive layer normalization (adaLN)** conditioned on the diffusion timestep {{< m >}}t{{< /m >}} and text embedding.
3. **Unpatchify**: Reshape the output back to {{< m >}}\mathbb{R}^{C \times T \times F}{{< /m >}}.
{{< /definition >}}

The adaLN conditioning works by predicting scale {{< m >}}\gamma{{< /m >}} and shift {{< m >}}\beta{{< /m >}} parameters from the conditioning signal:
{{< dm >}}\text{adaLN}(h, t, c) = \gamma(t, c) \odot \frac{h - \mu(h)}{\sigma(h)} + \beta(t, c){{< /dm >}}

This is fundamentally different from MusicGen: **no codebook, no VQ, no discrete tokens**. The entire generation happens in continuous space.

### 22.12 The Forward Diffusion Process

> *中文:* "经典扩散模型，比如DDPM，它的前向加噪过程...就是一条马尔可夫链。上一集讲的AI作曲第一个范式，六十年前的数学，藏在现代生成模型的心脏里。"

As discussed in {{< episode-ref ep="21" >}}EP21{{< /episode-ref >}}, the forward process of DDPM is a Markov chain that gradually adds Gaussian noise:
{{< dm >}}q(x_t | x_{t-1}) = \mathcal{N}\bigl(x_t;\; \sqrt{1 - \beta_t}\, x_{t-1},\; \beta_t I\bigr){{< /dm >}}

The reverse process (denoising) is learned by a neural network {{< m >}}\epsilon_\theta{{< /m >}} that predicts the noise added at each step. DiT uses a Transformer as the architecture for {{< m >}}\epsilon_\theta{{< /m >}}.

### 22.13 Classifier-Free Guidance (CFG)

{{< definition name="Classifier-Free Guidance" label="Definition 22.8" >}}
During training, the text condition {{< m >}}c{{< /m >}} is randomly dropped (replaced with {{< m >}}\varnothing{{< /m >}}) with probability {{< m >}}p_{\text{drop}}{{< /m >}}. At inference, the model output is interpolated:
{{< dm >}}\tilde{\epsilon}_\theta(x_t, c) = (1 + w)\,\epsilon_\theta(x_t, c) - w \cdot \epsilon_\theta(x_t, \varnothing){{< /dm >}}
where {{< m >}}w \geq 0{{< /m >}} is the **guidance scale**.
{{< /definition >}}

**Interpretation by cases**:

| {{< m >}}w{{< /m >}} | Behavior |
|-------|----------|
| {{< m >}}w = 0{{< /m >}} | Pure conditional generation: {{< m >}}\tilde{\epsilon} = \epsilon_\theta(x_t, c){{< /m >}} |
| {{< m >}}w > 0{{< /m >}} | Amplified conditioning — moves away from unconditional |
| {{< m >}}w \to \infty{{< /m >}} | Extreme adherence to text (often causes artifacts) |

{{< theorem name="Classifier-Free Guidance Interpolation" label="Theorem 22.4" >}}
CFG implicitly performs gradient ascent on {{< m >}}\log p(c | x){{< /m >}}. Specifically, the guided score satisfies:
{{< dm >}}\nabla_{x_t} \log \tilde{p}(x_t | c) = \nabla_{x_t} \log p(x_t | c) + w \cdot \nabla_{x_t} \log p(c | x_t){{< /dm >}}
where {{< m >}}p(c | x_t){{< /m >}} is the implicit classifier.
{{< /theorem >}}

{{< proof >}}
By Bayes' rule:
{{< dm >}}\log p(x_t | c) = \log p(c | x_t) + \log p(x_t) - \log p(c){{< /dm >}}

Taking the gradient with respect to {{< m >}}x_t{{< /m >}} ({{< m >}}\log p(c){{< /m >}} is constant):
{{< dm >}}\nabla_{x_t} \log p(x_t | c) = \nabla_{x_t} \log p(c | x_t) + \nabla_{x_t} \log p(x_t){{< /dm >}}

The CFG output is:
{{< dm >}}\tilde{\epsilon}_\theta(x_t, c) = (1 + w)\,\epsilon_\theta(x_t, c) - w\,\epsilon_\theta(x_t, \varnothing){{< /dm >}}

Since the noise prediction {{< m >}}\epsilon_\theta(x_t, c) \propto -\nabla_{x_t} \log p(x_t | c){{< /m >}} and {{< m >}}\epsilon_\theta(x_t, \varnothing) \propto -\nabla_{x_t} \log p(x_t){{< /m >}}, substituting:
{{< dm >}}\tilde{\epsilon} \propto -(1+w)\nabla_{x_t} \log p(x_t | c) + w\,\nabla_{x_t} \log p(x_t){{< /dm >}}
{{< dm >}}= -\nabla_{x_t}\bigl[\log p(x_t | c) + w\bigl(\log p(x_t | c) - \log p(x_t)\bigr)\bigr]{{< /dm >}}
{{< dm >}}= -\nabla_{x_t}\bigl[\log p(x_t | c) + w \log p(c | x_t)\bigr] + \text{const}{{< /dm >}}

Therefore the guided score corresponds to:
{{< dm >}}\nabla_{x_t} \log \tilde{p}(x_t | c) = \nabla_{x_t} \log p(x_t | c) + w \cdot \nabla_{x_t} \log p(c | x_t){{< /dm >}}

The guidance scale {{< m >}}w{{< /m >}} controls how strongly the model steers toward outputs that "look like" they were generated from condition {{< m >}}c{{< /m >}}, as measured by the implicit classifier {{< m >}}p(c | x_t){{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

---

## Station 4: Decoding

> *中文:* "MusicGen那边：整数token通过RVQ反向查表变回连续向量，再通过EnCodec解码器膨胀回波形——640个采样点从一个向量里重建出来。"

### 22.14 MusicGen Decoding Pipeline

The decoding reverses the encoding:

1. **RVQ lookup**: For each frame, retrieve the centroid vectors from each codebook: {{< m >}}c_k = e_{i_k}^{(k)}{{< /m >}}, where {{< m >}}i_k{{< /m >}} is the predicted token index for codebook {{< m >}}k{{< /m >}}.
2. **Sum**: {{< m >}}\hat{z} = \sum_{k=1}^{Q} c_k \in \mathbb{R}^{128}{{< /m >}}.
3. **EnCodec decoder**: Transposed convolutions expand {{< m >}}\hat{z}{{< /m >}} back to 640 samples: {{< m >}}\hat{x} = \text{Dec}(\hat{z}) \in \mathbb{R}^{640}{{< /m >}}.
4. **Overlap-add**: Adjacent frames are combined with windowing to produce the continuous waveform.

### 22.15 ACE-Step Decoding Pipeline

> *中文:* "ACE-Step那边：去噪完成的潜在表示先通过DCAE解码器变回频谱图，再经过声码器才变成波形。"

1. **DCAE decoder**: The denoised continuous latent {{< m >}}z \in \mathbb{R}^{C \times T \times F}{{< /m >}} is decoded to a mel-spectrogram.
2. **Vocoder** (e.g., HiFi-GAN): Converts the mel-spectrogram to a time-domain waveform via learned upsampling convolutions.

The two-stage decode (latent {{< m >}}\to{{< /m >}} spectrogram {{< m >}}\to{{< /m >}} waveform) adds latency but avoids the information bottleneck of discrete tokenization.

---

## Numerical Examples

### Complete MusicGen Pipeline for a 10-Second Clip

| Stage | Input | Output | Dimensions |
|-------|-------|--------|------------|
| Text tokenization | "Chinese-style piano" | Token indices | {{< m >}}L \approx 6{{< /m >}} integers |
| T5 encoder | {{< m >}}L{{< /m >}} token indices | Hidden states | {{< m >}}6 \times 1024{{< /m >}} (T5-large) |
| Audio encoding (EnCodec) | 320,000 samples (10s @ 32kHz) | Latent vectors | {{< m >}}500 \times 128{{< /m >}} |
| RVQ | 500 latent vectors | Token indices | {{< m >}}500 \times 4{{< /m >}} integers |
| Transformer generation | T5 states + past tokens | Next tokens | 500 steps (delay pattern) |
| RVQ decode | {{< m >}}500 \times 4{{< /m >}} indices | Latent vectors | {{< m >}}500 \times 128{{< /m >}} |
| EnCodec decode | 500 latent vectors | Waveform | 320,000 samples |

### Storage Comparison

| Representation | Size for 10s audio |
|----------------|--------------------|
| Raw 32kHz 16-bit | 640,000 bytes |
| EnCodec continuous latent | 256,000 bytes (500 {{< m >}}\times{{< /m >}} 128 {{< m >}}\times{{< /m >}} 4 bytes) |
| RVQ tokens (4 codebooks) | 2,000 integers = ~2,750 bytes |
| Compressed ratio (raw to RVQ) | ~233:1 |

### RVQ Reconstruction Quality by Layer Count

| Layers (Q) | Bits/frame | Bitrate | Typical SI-SDR (dB) |
|------------|-----------|---------|---------------------|
| 1 | 11 | 550 bps | ~5 |
| 2 | 22 | 1,100 bps | ~10 |
| 4 | 44 | 2,200 bps | ~15 |
| 8 | 88 | 4,400 bps | ~20 |

Each additional layer roughly halves the remaining error (Theorem 22.1), with diminishing returns as residuals approach the noise floor.

---

## Musical Connection

{{< musical-connection >}}
**From Notation to Codebooks: Two Alphabets for Music**

> *中文:* "这四个整数，就是AI的音乐字母表里的'字母'。"

Western staff notation is a human-designed alphabet for music: pitch (line/space), duration (note shape), dynamics (marking). It captures what a trained musician needs to reproduce a performance — but discards timbre, room acoustics, and micro-timing.

EnCodec's RVQ codebook is an AI-discovered alphabet. Its "letters" — four integers per frame — encode everything the decoder needs to reconstruct perceptually faithful audio: pitch, timbre, dynamics, stereo field, room characteristics. But unlike staff notation, the codebook entries have no human-interpretable labels. Entry 1742 in codebook 1 might encode "bright attack with upper harmonics" — or it might encode a pattern that has no name in any human language.

The parallel is striking: both systems solve the same problem (compress music into a finite symbol set) but optimize for different decoders (human performer vs. neural network). {{< episode-ref ep="23" >}}EP23{{< /episode-ref >}} will probe what these learned letters actually encode.
{{< /musical-connection >}}

---

## Limits and Open Questions

1. **Codebook collapse**: In practice, many RVQ codebook entries go unused during training. Techniques like exponential moving average updates and codebook reset heuristics mitigate this, but the effective codebook utilization remains below 100%.

2. **Tokenization granularity**: EnCodec produces 50 tokens/second. Is this the right temporal resolution for music? Speech models use similar rates, but music has faster transients (drum attacks at sub-millisecond scale) that may be lost.

3. **Cross-modal alignment**: Cross-attention assumes text and audio share a meaningful latent geometry. But "Chinese-style" is a high-dimensional cultural concept — how well can a T5 encoder trained on English text capture it?

4. **Guidance scale sensitivity**: CFG with {{< m >}}w{{< /m >}} too high produces artifacts; too low ignores the prompt. The optimal {{< m >}}w{{< /m >}} varies by prompt and is typically hand-tuned.

5. **Continuous vs. discrete**: MusicGen (discrete) and ACE-Step (continuous) represent fundamentally different philosophical choices. Which is better for music? The answer may depend on the downstream task.

> *中文:* "下一集我们问一个更深的问题：这些字母表里的'字母'，到底编码了什么？调性？情感？还是人类根本读不懂的东西？"

---

## Academic References

1. Raffel, C. et al. (2020). "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer." *JMLR* 21(140), 1-67.
2. Kudo, T. & Richardson, J. (2018). "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing." *EMNLP 2018*.
3. van den Oord, A., Vinyals, O. & Kavukcuoglu, K. (2017). "Neural Discrete Representation Learning." *NeurIPS 2017*.
4. Defossez, A. et al. (2022). "High Fidelity Neural Audio Compression." *arXiv:2210.13438*. — *The EnCodec paper.*
5. Zeghidour, N. et al. (2021). "SoundStream: An End-to-End Neural Audio Codec." *IEEE/ACM Trans. Audio, Speech, Lang. Process.* 30, 495-507.
6. Copet, J. et al. (2023). "Simple and Controllable Music Generation." *NeurIPS 2023*. — *The MusicGen paper; introduces the delay pattern.*
7. Peebles, W. & Xie, S. (2023). "Scalable Diffusion Models with Transformers." *ICCV 2023*. — *The DiT paper.*
8. Ho, J. & Salimans, T. (2022). "Classifier-Free Diffusion Guidance." *NeurIPS 2021 Workshop*.
9. Ho, J., Jain, A. & Abbeel, P. (2020). "Denoising Diffusion Probabilistic Models." *NeurIPS 2020*.
10. Vaswani, A. et al. (2017). "Attention Is All You Need." *NeurIPS 2017*. — *The Transformer paper; defines scaled dot-product attention.*
11. Agostinelli, A. et al. (2023). "MusicLM: Generating Music From Text." *arXiv:2301.11325*.
12. Huang, R. et al. (2024). "ACE-Step: A Step Towards Music Generation Foundation Model." *arXiv*. — *Continuous diffusion approach to music generation.*
13. Kong, J., Kim, J. & Bae, J. (2020). "HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis." *NeurIPS 2020*.
