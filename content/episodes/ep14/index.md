---
title: "EP14: Tonnetz Hodge Duality"
subtitle: "Simplicial Complexes, Hodge Star, and the Decomposition of Harmony"
episode: 14
date: 2026-02-27
duration: "16:27"
domains:
  - "Topology"
  - "Linear Algebra"
  - "Harmonic Analysis"
key_theorems:
  - "Discrete Hodge Theorem (ker L_k ≅ H^k)"
  - "Hodge Decomposition (exact ⊕ coexact ⊕ harmonic)"
  - "Poincaré Duality (cell count bijection)"
  - "Boundary-squared = 0"
callbacks: [1, 2, 4]
forward_refs: [23]
weight: 14
draft: false
---

## Overview

The Tonnetz — Euler's 1739 interval lattice, rediscovered by neo-Riemannian theorists — is not merely a picture of chord relationships. It is a **simplicial complex triangulating a torus**, and every chord progression on it is a cochain that decomposes, uniquely and orthogonally, into three mathematically distinct components.

This episode applies **discrete Hodge theory** (Eckmann 1944; Lim 2020) to the Tonnetz. The central result:

> *Any 1-cochain on the Tonnetz torus decomposes as:*
> {{< dm >}}\omega = \omega_{\text{exact}} \;+\; \omega_{\text{coexact}} \;+\; \omega_{\text{harmonic}}{{< /dm >}}
> *where the three summands are pairwise orthogonal and uniquely determined.*

The three components correspond — as testable hypotheses — to functional cadences, chromatic PLR cycles, and remote modulations along the torus topology.

---

## Prerequisites

- {{< episode-ref ep="1" >}}Chord Space as Torus (EP01){{< /episode-ref >}} — Tonnetz and PLR transformations
- {{< episode-ref ep="2" >}}Wave equation and Fourier series (EP02){{< /episode-ref >}} — analogy with heat diffusion on manifolds
- {{< episode-ref ep="4" >}}All-Interval Rows and ℤ₁₂ (EP04){{< /episode-ref >}} — cyclic group structure underlying pitch classes

---

## Preamble: What Is a "Hole"? Building Homology from Scratch

*Who this is for*: You have watched the video and understand the setup (boundary matrices, chain groups, Betti numbers), but the definition {{< m >}}H_k = \ker(\partial_k)/\operatorname{im}(\partial_{k+1}){{< /m >}} feels like a formula dropped from the sky. This preamble builds it from a single question: *what actually is a hole?*

### P.1 — The Naive Question

A doughnut has one hole. A pretzel has two. A solid ball has none.

First attempt: *"a hole is a region with nothing in it."* That doesn't work — the inside of a sphere is also "nothing," but a sphere doesn't have the same kind of hole as a torus.

Second attempt: *"a hole is something you can stick a finger through."* That's dimension-specific and requires 3D embedding.

The algebraic topology approach sidesteps all of this. Instead of defining what a hole *is*, we define what a hole *does*: **it obstructs you from filling in a closed curve.**

### P.2 — The Loop Test

Draw a closed loop on a surface. Try to "fill it in" — can you find a 2-dimensional patch whose boundary is exactly that loop?

On the **sphere**: every closed loop bounds a disk — no obstruction.

On the **torus**: the loop going *through* the hole cannot bound any patch. The hole *is* that obstruction.

**The algebraic challenge**: detect this without geometry or deformation. The answer is the boundary operator {{< m >}}\partial{{< /m >}}.

![Loop test: which loops can be filled in?](img/LoopTestScene_ManimCE_v0.19.1.png)

![Loops that cannot shrink to a point on the torus](img/LoopShrinkGif.gif)

### P.3 — Chains: The Algebraic Skeleton

Replace the geometric surface with an oriented combinatorial skeleton. Work with **formal linear combinations** over {{< m >}}\mathbb{R}{{< /m >}}:

- A **0-chain**: {{< m >}}3A - 2B + C{{< /m >}} — weighted vertices.
- A **1-chain**: {{< m >}}[A,B] + 2[B,C] - [A,C]{{< /m >}} — weighted oriented edges.
- A **2-chain**: {{< m >}}[A,B,C] - [D,E,F]{{< /m >}} — weighted oriented triangles.

Orientation: {{< m >}}[B,A] = -[A,B]{{< /m >}}. These form real vector spaces {{< m >}}C_0, C_1, C_2, \ldots{{< /m >}}

### P.4 — The Boundary Operator ∂

{{< m >}}\partial_k{{< /m >}} takes a {{< m >}}k{{< /m >}}-chain and returns its {{< m >}}(k-1){{< /m >}}-dimensional boundary:

{{< dm >}}\partial_0(A) = 0, \qquad \partial_1([A,B]) = B - A{{< /dm >}}

{{< dm >}}\partial_2([A,B,C]) = [B,C] - [A,C] + [A,B]{{< /dm >}}

Sign rule: delete each vertex in turn, alternating signs — the result is the counterclockwise perimeter.

![Boundary operator: triangle → its three edges](img/BoundaryScene_ManimCE_v0.19.1.png)

### P.5 — ∂² = 0: The Fundamental Identity

{{< theorem name="Boundary of a Boundary Vanishes" label="Theorem P.1" >}}
For any simplicial complex, {{< m >}}\partial_k \circ \partial_{k+1} = 0{{< /m >}}.
{{< /theorem >}}

{{< proof >}}
Compute {{< m >}}\partial_1(\partial_2([A,B,C])){{< /m >}}:
{{< dm >}}\partial_1\bigl([B,C] - [A,C] + [A,B]\bigr) = (C-B) - (C-A) + (B-A) = 0 \;\checkmark{{< /dm >}}

In general, applying {{< m >}}\partial_{k-1}{{< /m >}} to {{< m >}}\partial_k[v_0,\ldots,v_k] = \sum_i (-1)^i [v_0,\ldots,\hat{v}_i,\ldots,v_k]{{< /m >}} and collecting terms by pairs {{< m >}}(i,j){{< /m >}} with {{< m >}}i < j{{< /m >}} shows every pair cancels with opposite sign. {{< m >}}\square{{< /m >}}
{{< /proof >}}

*Geometric meaning*: The boundary of a solid region is a closed surface — which has no boundary itself. Algebraic signs enforce this cancellation. **This one identity is what makes all of homology work.**

![Boundary-squared = 0: opposite boundary edges cancel](img/BoundarySquaredScene_ManimCE_v0.19.1.png)

### P.6 — Cycles, Boundaries, and the Definition of a Hole

{{< definition name="Cycles and Boundaries" label="Definition P.1" >}}
A **{{< m >}}k{{< /m >}}-cycle** is a {{< m >}}k{{< /m >}}-chain with zero boundary: {{< m >}}Z_k = \ker(\partial_k){{< /m >}}.

A **{{< m >}}k{{< /m >}}-boundary** is a {{< m >}}k{{< /m >}}-chain in {{< m >}}\operatorname{im}(\partial_{k+1}){{< /m >}}.

Since {{< m >}}\partial^2 = 0{{< /m >}}: every boundary is automatically a cycle:
{{< dm >}}B_k \;\subseteq\; Z_k \;\subseteq\; C_k{{< /dm >}}
{{< /definition >}}

| Chain | Cycle? | Boundary? |
|-------|--------|-----------|
| Open path {{< m >}}[A,B]{{< /m >}} | No | — |
| Triangle perimeter {{< m >}}\partial_2[A,B,C]{{< /m >}} | Yes | Yes |
| Loop through torus hole | Yes | **No** |

![Cycles vs boundaries: which loops can be filled?](img/CycleScene_ManimCE_v0.19.1.png)

> **A {{< m >}}k{{< /m >}}-dimensional hole is a {{< m >}}k{{< /m >}}-cycle that is NOT the boundary of any {{< m >}}(k+1){{< /m >}}-chain.**

![Holes as obstructions to filling: the algebraic picture](img/HoleScene_ManimCE_v0.19.1.png)

Two cycles are **homologous** if they differ by a boundary: {{< m >}}c_1 \sim c_2 \iff c_1 - c_2 \in B_k{{< /m >}}.

![Venn diagram: {{< m >}}B_k \subseteq Z_k \subseteq C_k{{< /m >}}](img/VennScene_ManimCE_v0.19.1.png)

{{< definition name="Homology Groups and Betti Numbers" label="Definition P.2" >}}
{{< dm >}}H_k = Z_k / B_k = \ker(\partial_k) \,/\, \operatorname{im}(\partial_{k+1}){{< /dm >}}

The **{{< m >}}k{{< /m >}}-th Betti number** {{< m >}}\beta_k = \dim(H_k){{< /m >}} counts independent {{< m >}}k{{< /m >}}-dimensional holes.
{{< /definition >}}

### P.7 — Connecting to the Tonnetz Numbers

The video computes {{< m >}}\dim(\ker \partial_1) = 25{{< /m >}} and {{< m >}}\operatorname{rank}(\partial_2) = 23{{< /m >}}. Therefore:
{{< dm >}}\beta_1 = 25 - 23 = 2{{< /dm >}}

Of 25 closed loops, 23 can be filled by triangles (fake holes). The remaining **2 equivalence classes** are genuine: one along the circle of fifths, one along the major third cycle. These two holes are why the harmonic component of the Hodge decomposition is non-trivial.

*Water-flow analogy*: Boundaries {{< m >}}B_k{{< /m >}} are currents driven by a potential — remove the pump and they stop. Non-boundary cycles are currents with no source, no sink, no pump — they persist because the topology allows it. {{< m >}}H_k = Z_k/B_k{{< /m >}} is the space of "eternal currents."

![Quotient construction: {{< m >}}H_k = Z_k / B_k{{< /m >}}, homologous cycles identified](img/QuotientScene_ManimCE_v0.19.1.png)

![Two homologous cycles on the torus: same hole, different paths](img/ExamplesABScene_ManimCE_v0.19.1.png)

---

## The Tonnetz as a Simplicial Complex

{{< definition name="Tonnetz Simplicial Complex" label="Definition 0.1" >}}
The **Tonnetz** is a simplicial complex {{< m >}}K{{< /m >}} triangulating the torus {{< m >}}T^2 = S^1 \times S^1{{< /m >}}:

| Dimension | Cells | Count | Musical meaning |
|-----------|-------|-------|-----------------|
| 0 (vertices) | Pitch classes {{< m >}}\{C, C\sharp, \ldots, B\}{{< /m >}} | 12 | Individual notes |
| 1 (edges) | Minor 3rd + Major 3rd + Perfect 5th | 36 | Consonant intervals |
| 2 (faces) | Major triads + Minor triads | 24 | Triads |

Euler characteristic: {{< m >}}\chi(K) = 12 - 36 + 24 = 0{{< /m >}}. Since {{< m >}}\chi = 2 - 2g{{< /m >}} for orientable closed surfaces, {{< m >}}g = 1{{< /m >}} — confirming the torus.
{{< /definition >}}

{{< musical-connection >}}
*中文:* "Tonnetz 的顶点是十二个音高类，边是音程，三角形是三和弦。整个结构是一个三角剖分的环面。"

The 36 edges are exactly the consonant intervals of Western voice leading: perfect fifths (3:2), major thirds (5:4), minor thirds (6:5). Going up 12 perfect fifths returns to the starting pitch class mod 12; going up 4 major thirds does the same ({{< m >}}4 \times 3 = 12{{< /m >}} semitones). Both directions "close up," forcing the torus topology.
{{< /musical-connection >}}

**Betti numbers** (from {{< m >}}\operatorname{rank}(\partial_1) = 11{{< /m >}}, {{< m >}}\operatorname{rank}(\partial_2) = 23{{< /m >}}):

| {{< m >}}\beta_k{{< /m >}} | Value | Meaning |
|-----------|-------|---------|
| {{< m >}}\beta_0 = 12 - 11{{< /m >}} | 1 | Connected: all pitch classes in one piece |
| {{< m >}}\beta_1 = 25 - 23{{< /m >}} | 2 | Two non-contractible loops: circle of fifths + major third cycle |
| {{< m >}}\beta_2 = 24 - 23{{< /m >}} | 1 | One enclosed cavity (the torus encloses a void) |

> *中文:* "Betti 数 1, 2, 1 是环面 {{< m >}}T^2{{< /m >}} 的拓扑签名。"

![The Tonnetz torus: two non-contractible loops, Betti numbers (1,2,1)](img/TorusScene_ManimCE_v0.19.1.png)

**The dual complex {{< m >}}K^*{{< /m >}} (chicken-wire torus)**: Reversing the roles of vertices and faces — each triangle of {{< m >}}K{{< /m >}} becomes a vertex, each shared edge becomes an edge, each vertex becomes a hexagonal face — gives the **Poincaré dual** {{< m >}}K^*{{< /m >}}:

| In {{< m >}}K{{< /m >}} | In {{< m >}}K^*{{< /m >}} |
|--------|---------|
| 12 vertices (pitch classes) | 12 hexagonal faces |
| 36 edges (intervals) | 36 edges (PLR voice leadings) |
| 24 triangular faces (triads) | 24 vertices (triads) |

{{< m >}}\chi(K^*) = 0{{< /m >}} — still a torus. This is the **chicken-wire torus** of Douthett & Steinbach (1998), where P, L, R transformations correspond to edges of {{< m >}}K^*{{< /m >}}.

{{< definition name="k-Cochain" label="Definition 0.2" >}}
A **{{< m >}}k{{< /m >}}-cochain** {{< m >}}\phi \in C^k(K){{< /m >}} is a real-valued function on oriented {{< m >}}k{{< /m >}}-simplices, satisfying {{< m >}}\phi(-\sigma) = -\phi(\sigma){{< /m >}}.

- **0-cochain** {{< m >}}f \in C^0{{< /m >}}: a "tonal weight" on pitch classes. Example: {{< m >}}f(C) = 1{{< /m >}}, {{< m >}}f(G) = 0.8{{< /m >}}, …
- **1-cochain** {{< m >}}\omega \in C^1{{< /m >}}: a signed flow on directed intervals. Example: {{< m >}}\omega([C,G]) = +7{{< /m >}} (up a fifth), {{< m >}}\omega([G,C]) = -7{{< /m >}}.
- **2-cochain** {{< m >}}g \in C^2{{< /m >}}: a signed weight on oriented triads.

The **coboundary** {{< m >}}\delta_k = \partial_{k+1}^T : C^k \to C^{k+1}{{< /m >}} satisfies {{< m >}}\delta_k \circ \delta_{k-1} = 0{{< /m >}} — the cochain analogue of {{< m >}}\partial^2 = 0{{< /m >}}.
{{< /definition >}}

![A 1-form (cochain) assigns signed values to oriented edges of the Tonnetz](img/OneFormScene_ManimCE_v0.19.1.png)

---

## Section 1: The Hodge Star Operator ★

> *中文:* "离散 Hodge 星算子，记作 ★，是连接原始复形 {{< m >}}K{{< /m >}} 和对偶复形 {{< m >}}K^*{{< /m >}} 的代数算子。"

{{< definition name="Discrete Hodge Star" label="Definition 1.1" >}}
Let {{< m >}}K{{< /m >}} triangulate an orientable closed {{< m >}}n{{< /m >}}-manifold with dual {{< m >}}K^*{{< /m >}}. The **discrete Hodge star** is the linear map
{{< dm >}}\star_k : C^k(K) \to C^{n-k}(K^*){{< /dm >}}
sending each basis {{< m >}}k{{< /m >}}-cochain (dual to {{< m >}}\sigma \in K{{< /m >}}) to the basis {{< m >}}(n-k){{< /m >}}-cochain (dual to {{< m >}}\sigma^* \in K^*{{< /m >}}).
{{< /definition >}}

For the Tonnetz torus ({{< m >}}n = 2{{< /m >}}):

| Map | Dimensions | Musical translation |
|-----|------------|---------------------|
| {{< m >}}\star_0 : C^0(K) \to C^2(K^*){{< /m >}} | {{< m >}}12 \to 12{{< /m >}} | Pitch-class weights → hexagonal face weights |
| {{< m >}}\star_1 : C^1(K) \to C^1(K^*){{< /m >}} | {{< m >}}36 \to 36{{< /m >}} | Interval flows ↔ PLR voice-leading flows |
| {{< m >}}\star_2 : C^2(K) \to C^0(K^*){{< /m >}} | {{< m >}}24 \to 24{{< /m >}} | Triad weights → dual vertex weights |

> *中文:* "★ 把 1-上链映射到 1-上链。边上的流映射到对偶边上的流。36 对 36，一维在二维流形上是自对偶的。"

**Worked examples**:

- **{{< m >}}\star_0{{< /m >}}**: {{< m >}}f \in C^0{{< /m >}} with {{< m >}}f(C)=1{{< /m >}}, all others $0$ → {{< m >}}\star_0 f{{< /m >}} assigns $1$ to the hexagonal face of {{< m >}}K^*{{< /m >}} surrounding {{< m >}}C{{< /m >}}, bounded by the six triads containing {{< m >}}C{{< /m >}}. Translates "note C" into "hexagonal region of triadic space centered on C."
- **{{< m >}}\star_1{{< /m >}} (self-dual)**: Flow {{< m >}}+1{{< /m >}} on edge {{< m >}}[C,E]{{< /m >}} (major third) → the dual edge connects the two triads sharing {{< m >}}C{{< /m >}} and {{< m >}}E{{< /m >}}: C major and A minor. Translates "interval flow" into "PLR voice-leading motion between the two triads sharing that interval."

{{< theorem name="Poincaré Duality — Cell Count" label="Theorem 1.1" >}}
For an orientable closed {{< m >}}n{{< /m >}}-manifold, the number of {{< m >}}k{{< /m >}}-cells in {{< m >}}K{{< /m >}} equals the number of {{< m >}}(n-k){{< /m >}}-cells in {{< m >}}K^*{{< /m >}}. Consequently {{< m >}}\star_k{{< /m >}} is a square matrix.
{{< /theorem >}}

{{< proof >}}
The construction of {{< m >}}K^*{{< /m >}} gives a bijection {{< m >}}\sigma \mapsto \sigma^*{{< /m >}} between {{< m >}}k{{< /m >}}-simplices of {{< m >}}K{{< /m >}} and {{< m >}}(n-k){{< /m >}}-cells of {{< m >}}K^*{{< /m >}}. Therefore {{< m >}}\dim C^k(K) = \dim C^{n-k}(K^*){{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

> *中文:* "Poincaré 对偶保证原始 {{< m >}}k{{< /m >}}-胞腔数等于对偶 {{< m >}}n-k{{< /m >}} 胞腔数，所以 ★ 总是方阵。"

**Self-duality at the middle dimension**: When {{< m >}}k = n/2{{< /m >}}, {{< m >}}\star_k{{< /m >}} maps a space to itself. For the Tonnetz torus ({{< m >}}n=2{{< /m >}}, {{< m >}}k=1{{< /m >}}): 1-cochains are self-dual. Same phenomenon: the electromagnetic field tensor {{< m >}}F{{< /m >}} is a 2-form on Minkowski spacetime ({{< m >}}n=4{{< /m >}}, {{< m >}}k=2{{< /m >}}), and Maxwell's equations are {{< m >}}dF = 0{{< /m >}}, {{< m >}}d{\star}F = J{{< /m >}}.

> *中文:* "其实 Maxwell 方程组可以写成两行：{{< m >}}dF = 0{{< /m >}}，{{< m >}}d\star F = J{{< /m >}}。整个电磁学就是外微分 {{< m >}}d{{< /m >}} 和 Hodge 星的组合。"

---

## Section 2: Inner Product and Adjoint Operators

{{< definition name="Standard Inner Product on Cochain Spaces" label="Definition 2.1" >}}
Equip {{< m >}}C^k{{< /m >}} with the inner product declaring all basis {{< m >}}k{{< /m >}}-simplices orthonormal:
{{< dm >}}\langle e_i, e_j \rangle = \delta_{ij}{{< /dm >}}
{{< /definition >}}

> *中文:* "我们给链空间 {{< m >}}C_k{{< /m >}} 装一个标准内积，声明基底正交归一。"

The inner product identifies chains with cochains canonically, and gives us the **adjoint** of {{< m >}}\partial{{< /m >}} — the key ingredient for the Hodge Laplacian.

{{< definition name="Coboundary (Adjoint) Operator" label="Definition 2.2" >}}
The **coboundary** {{< m >}}\delta_k := \partial_{k+1}^T : C^k \to C^{k+1}{{< /m >}} is the transpose of the boundary operator. It runs in the opposite direction:
{{< dm >}}C_2 \xrightarrow{\partial_2} C_1 \xrightarrow{\partial_1} C_0 \qquad \text{(boundary, downward)}{{< /dm >}}
{{< dm >}}C^0 \xrightarrow{\delta_0 = \partial_1^T} C^1 \xrightarrow{\delta_1 = \partial_2^T} C^2 \qquad \text{(coboundary, upward)}{{< /dm >}}
The adjoint property: {{< m >}}\langle \partial_{k+1}\beta, \alpha \rangle = \langle \beta, \delta_k \alpha \rangle{{< /m >}}.
{{< /definition >}}

> *中文:* "伴随算子的方向和 {{< m >}}\partial{{< /m >}} 相反。{{< m >}}\partial{{< /m >}} 从高维到低维，它的转置从低维到高维。"

**Worked example ({{< m >}}\delta_0{{< /m >}} — discrete gradient)**: Let {{< m >}}f \in C^0{{< /m >}} have {{< m >}}f(C) = 1{{< /m >}}, {{< m >}}f = 0{{< /m >}} elsewhere. Then {{< m >}}(\delta_0 f)([C,E]) = f(E) - f(C) = -1{{< /m >}} and {{< m >}}(\delta_0 f)([G,C]) = f(C) - f(G) = +1{{< /m >}}. So {{< m >}}\delta_0 f{{< /m >}} assigns {{< m >}}-1{{< /m >}} to every edge *leaving* {{< m >}}C{{< /m >}} and {{< m >}}+1{{< /m >}} to every edge *arriving* at {{< m >}}C{{< /m >}} — a discrete gradient converging toward the high-potential note.

{{< proposition label="Prop 2.1" name="Coboundary Squared = 0" >}}
{{< m >}}\delta_k \circ \delta_{k-1} = 0{{< /m >}}.
{{< /proposition >}}

{{< proof >}}
{{< m >}}\delta_k \circ \delta_{k-1} = \partial_{k+1}^T \circ \partial_k^T = (\partial_k \circ \partial_{k+1})^T = 0^T = 0{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

---

## Section 3: The Hodge Laplacian

> *中文:* "{{< m >}}L_k{{< /m >}} 的两个矩阵项分别检测两类'非调和'分量。{{< m >}}\partial_k^T \partial_k{{< /m >}} 检测非零梯度，{{< m >}}\partial_{k+1} \partial_{k+1}^T{{< /m >}} 检测非零旋度。"

{{< definition name="Hodge Laplacian" label="Definition 3.1" >}}
The **{{< m >}}k{{< /m >}}-th Hodge Laplacian** is the self-adjoint operator {{< m >}}L_k : C^k \to C^k{{< /m >}}:
{{< dm >}}L_k = \partial_k^T \partial_k + \partial_{k+1} \partial_{k+1}^T{{< /dm >}}

- {{< m >}}\partial_k^T \partial_k{{< /m >}} (down-up): penalizes non-zero divergence (sources/sinks at vertices).
- {{< m >}}\partial_{k+1} \partial_{k+1}^T{{< /m >}} (up-down): penalizes non-zero curl (circulation around faces).

{{< m >}}L_1 \omega = 0{{< /m >}} means the 1-cochain {{< m >}}\omega{{< /m >}} has *neither* sources/sinks *nor* local whirlpools.
{{< /definition >}}

**Heat diffusion analogy**: Imagine edge flows as temperatures on a donut-shaped pipe network. {{< m >}}L_1 \omega{{< /m >}} measures how far {{< m >}}\omega{{< /m >}} is from thermal equilibrium. The equilibrium states — where no gradient wants to push heat downhill and no eddy stirs heat in circles — are the **harmonic forms**.

{{< proposition label="Prop 3.1" name="Hodge Laplacian is PSD" >}}
{{< m >}}L_k{{< /m >}} is symmetric and positive semi-definite: {{< m >}}\langle L_k \omega, \omega \rangle = \|\partial_k \omega\|^2 + \|\partial_{k+1}^T \omega\|^2 \geq 0{{< /m >}}.
{{< /proposition >}}

{{< proof >}}
{{< m >}}\langle L_k \omega, \omega \rangle = \langle \partial_k^T \partial_k \omega, \omega \rangle + \langle \partial_{k+1} \partial_{k+1}^T \omega, \omega \rangle = \|\partial_k \omega\|^2 + \|\partial_{k+1}^T \omega\|^2 \geq 0{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

{{< theorem name="Discrete Hodge Theorem" label="Theorem 3.1" >}}
For any finite simplicial complex {{< m >}}K{{< /m >}} with the standard inner product:
{{< dm >}}\ker(L_k) \cong H^k(K;\mathbb{R}), \qquad \dim(\ker L_k) = \beta_k{{< /dm >}}
Elements of {{< m >}}\ker(L_k){{< /m >}} are called **harmonic forms** (调和形式).
{{< /theorem >}}

{{< proof >}}
Since {{< m >}}L_k{{< /m >}} is PSD:
{{< dm >}}\omega \in \ker(L_k) \iff \langle L_k \omega, \omega \rangle = 0 \iff \|\partial_k \omega\|^2 + \|\partial_{k+1}^T \omega\|^2 = 0{{< /dm >}}
{{< dm >}}\iff \partial_k \omega = 0 \;\;\text{AND}\;\; \partial_{k+1}^T \omega = 0{{< /dm >}}

So {{< m >}}\ker(L_k) = \ker(\partial_k) \cap \ker(\partial_{k+1}^T){{< /m >}} — the set of {{< m >}}k{{< /m >}}-cycles that are orthogonal to all boundaries.

Since {{< m >}}Z^k = B^k \oplus (Z^k \cap (B^k)^\perp){{< /m >}} (orthogonal decomposition), we have {{< m >}}H^k = Z^k/B^k \cong Z^k \cap (B^k)^\perp = \ker(L_k){{< /m >}}. Therefore {{< m >}}\dim \ker(L_k) = \beta_k{{< /m >}}. {{< m >}}\square{{< /m >}}
{{< /proof >}}

> *中文:* "Hodge 定理说，{{< m >}}L_k{{< /m >}} 的 kernel 同构于第 {{< m >}}k{{< /m >}} 个上同调群。kernel 里的元素叫调和形式。"

**Concrete numbers for the Tonnetz**:

| Laplacian | Size | {{< m >}}\ker{{< /m >}} dimension | Musical interpretation |
|-----------|------|-----------------|------------------------|
| {{< m >}}L_0{{< /m >}} | {{< m >}}12\times 12{{< /m >}} | {{< m >}}\beta_0 = 1{{< /m >}} | One constant harmonic function (connected) |
| {{< m >}}L_1{{< /m >}} | {{< m >}}36\times 36{{< /m >}} | {{< m >}}\beta_1 = 2{{< /m >}} | Two independent harmonic interval flows |
| {{< m >}}L_2{{< /m >}} | {{< m >}}24\times 24{{< /m >}} | {{< m >}}\beta_2 = 1{{< /m >}} | One harmonic 2-cochain (volume form) |

The two harmonic 1-cochains in {{< m >}}\ker(L_1){{< /m >}} correspond to:
1. The **circle of fifths direction**: C→G→D→A→E→B→F♯→C♯→A♭→E♭→B♭→F→C
2. The **major third direction**: C→E→G♯→C

These are the only non-zero flows on the torus that are simultaneously divergence-free and curl-free. A sphere ({{< m >}}\beta_1 = 0{{< /m >}}) would have no such flows; a double torus ({{< m >}}\beta_1 = 4{{< /m >}}) would have four.

> *中文:* "对 Tonnetz 上的 1-上链来说，调和空间的维度等于 {{< m >}}\beta_1 = 2{{< /m >}}，对应五度圈方向和大三度方向的两个独立全局循环。"

---

## Section 4: The Hodge Decomposition Theorem

> *中文:* "任意 {{< m >}}k{{< /m >}} 维上链都可以唯一正交分解为三个分量。"

{{< theorem name="Discrete Hodge Decomposition" label="Theorem 4.1" >}}
For any finite simplicial complex {{< m >}}K{{< /m >}} with standard inner product, the cochain space {{< m >}}C^k{{< /m >}} admits an **orthogonal direct sum decomposition**:
{{< dm >}}C^k = \operatorname{im}(\partial_k^T) \;\oplus\; \operatorname{im}(\partial_{k+1}) \;\oplus\; \ker(L_k){{< /dm >}}

Every {{< m >}}\omega \in C^k{{< /m >}} has a **unique** decomposition:
{{< dm >}}\omega = \underbrace{\omega_{\text{exact}}}_{\in\,\operatorname{im}(\partial_k^T)} \;+\; \underbrace{\omega_{\text{coexact}}}_{\in\,\operatorname{im}(\partial_{k+1})} \;+\; \underbrace{\omega_{\text{harmonic}}}_{\in\,\ker(L_k)}{{< /dm >}}

Moreover: {{< m >}}\|\omega\|^2 = \|\omega_\text{exact}\|^2 + \|\omega_\text{coexact}\|^2 + \|\omega_\text{harmonic}\|^2{{< /m >}} (Pythagorean theorem for orthogonal components).
{{< /theorem >}}

{{< proof >}}
**Step 1: Pairwise orthogonality.**

**(a) {{< m >}}\operatorname{im}(\partial_k^T) \perp \operatorname{im}(\partial_{k+1}){{< /m >}}**: For {{< m >}}u = \partial_k^T \alpha{{< /m >}} and {{< m >}}v = \partial_{k+1}\beta{{< /m >}}:
{{< dm >}}\langle u, v \rangle = \langle \partial_k^T \alpha, \partial_{k+1}\beta \rangle = \langle \alpha, \partial_k \partial_{k+1}\beta \rangle = \langle \alpha, 0 \rangle = 0 \;\checkmark{{< /dm >}}

**(b) {{< m >}}\operatorname{im}(\partial_k^T) \perp \ker(L_k){{< /m >}}**: For {{< m >}}u = \partial_k^T \alpha{{< /m >}} and {{< m >}}\omega \in \ker(L_k){{< /m >}} (which gives {{< m >}}\partial_k \omega = 0{{< /m >}}):
{{< dm >}}\langle u, \omega \rangle = \langle \partial_k^T \alpha, \omega \rangle = \langle \alpha, \partial_k \omega \rangle = 0 \;\checkmark{{< /dm >}}

**(c) {{< m >}}\operatorname{im}(\partial_{k+1}) \perp \ker(L_k){{< /m >}}**: For {{< m >}}v = \partial_{k+1}\beta{{< /m >}} and {{< m >}}\omega \in \ker(L_k){{< /m >}} (which gives {{< m >}}\partial_{k+1}^T \omega = 0{{< /m >}}):
{{< dm >}}\langle v, \omega \rangle = \langle \partial_{k+1}\beta, \omega \rangle = \langle \beta, \partial_{k+1}^T \omega \rangle = 0 \;\checkmark{{< /dm >}}

**Step 2: The three subspaces span {{< m >}}C^k{{< /m >}}.**

We show {{< m >}}\dim(\operatorname{im}(\partial_k^T)) + \dim(\operatorname{im}(\partial_{k+1})) + \dim(\ker(L_k)) = \dim(C^k){{< /m >}}.

Since {{< m >}}\partial_{k+1}^T \partial_k^T = (\partial_k \partial_{k+1})^T = 0{{< /m >}}, the cross-term in {{< m >}}L_k{{< /m >}} vanishes when {{< m >}}L_k{{< /m >}} acts on {{< m >}}\operatorname{im}(\partial_k^T){{< /m >}}: for {{< m >}}u = \partial_k^T \alpha{{< /m >}}, {{< m >}}L_k u = \partial_k^T \partial_k \partial_k^T \alpha{{< /m >}}. One verifies {{< m >}}L_k{{< /m >}} acts injectively (and thus surjectively) on each of {{< m >}}\operatorname{im}(\partial_k^T){{< /m >}} and {{< m >}}\operatorname{im}(\partial_{k+1}){{< /m >}} separately. Therefore {{< m >}}\operatorname{im}(L_k) = \operatorname{im}(\partial_k^T) \oplus \operatorname{im}(\partial_{k+1}){{< /m >}}, and by rank-nullity:
{{< dm >}}\dim(\operatorname{im}(\partial_k^T)) + \dim(\operatorname{im}(\partial_{k+1})) + \dim(\ker(L_k)) = \dim(\operatorname{im}(L_k)) + \dim(\ker(L_k)) = \dim(C^k) \;\square{{< /dm >}}
{{< /proof >}}

> *中文:* "这不是近似，是精确的数学定理。"

**Dimension count for {{< m >}}k=1{{< /m >}} on the Tonnetz**:

| Component | Subspace | Dimension |
|-----------|----------|-----------|
| Exact {{< m >}}\omega_\text{exact} = \partial_1^T f{{< /m >}} | {{< m >}}\operatorname{im}(\partial_1^T){{< /m >}} | {{< m >}}11 = \operatorname{rank}(\partial_1){{< /m >}} |
| Coexact {{< m >}}\omega_\text{coexact} = \partial_2 g{{< /m >}} | {{< m >}}\operatorname{im}(\partial_2){{< /m >}} | {{< m >}}23 = \operatorname{rank}(\partial_2){{< /m >}} |
| Harmonic | {{< m >}}\ker(L_1){{< /m >}} | {{< m >}}2 = \beta_1{{< /m >}} |
| **Total** | {{< m >}}C^1{{< /m >}} | **36** ✓ |

**Meaning of each component**:

| Component | Formula | Vector calculus analogy | Characterization |
|-----------|---------|------------------------|-----------------|
| **Exact** | {{< m >}}\partial_1^T f{{< /m >}} | Gradient {{< m >}}\nabla f{{< /m >}} | Acyclic; flow on {{< m >}}[u,v]{{< /m >}} is {{< m >}}f(v)-f(u){{< /m >}} |
| **Coexact** | {{< m >}}\partial_2 g{{< /m >}} | Curl {{< m >}}\nabla \times \mathbf{A}{{< /m >}} | Circulates locally around triangular faces |
| **Harmonic** | {{< m >}}L_1 \omega = 0{{< /m >}} | Harmonic function | Divergence-free AND curl-free simultaneously |

> *中文:* "Exact 分量——梯度。Coexact 分量——旋度。Harmonic 分量——沿着环面的拓扑洞做全局循环。"

**Water-on-a-donut analogy**:

| Type | Water analogy | Musical analogy |
|------|--------------|-----------------|
| **Exact** | Flows **downhill** from peak to valley | V→I cadence; directed tension-resolution |
| **Coexact** | **Whirlpools** spinning in tight circles | PLR cycles, chromatic voice leading |
| **Harmonic** | A **river circling the donut** — no hill drives it, no eddy spins it | Tonal center migrating along circle of fifths |

The decomposition is **orthogonal** — the three types never interfere.

**Computing the decomposition** (for implementation): The orthogonal projections use Moore–Penrose pseudoinverses:
{{< dm >}}\omega_\text{exact} = \partial_1^T(\partial_1 \partial_1^T)^\dagger \partial_1 \omega, \quad \omega_\text{coexact} = \partial_2(\partial_2^T \partial_2)^\dagger \partial_2^T \omega, \quad \omega_\text{harmonic} = \omega - \omega_\text{exact} - \omega_\text{coexact}{{< /dm >}}

---

## Section 5: Three Musical Hypotheses

> *中文:* "Hodge 分解是定理。接下来我们提出三个可检验的音乐假设。"

**Encoding a chord progression**: Assign weights to Tonnetz edges traversed (e.g., proportional to interval activation duration). Apply the decomposition. The energy ratios {{< m >}}E_\text{exact}/\|w\|^2{{< /m >}}, {{< m >}}E_\text{coexact}/\|w\|^2{{< /m >}}, {{< m >}}E_\text{harmonic}/\|w\|^2{{< /m >}} give the harmonic profile.

{{< conjecture name="H1: Exact Energy ≈ Cadential Harmony" >}}
A passage with high {{< m >}}E_\text{exact}/\|w\|^2{{< /m >}} tends to exhibit strong cadences and functional harmony.

**Reasoning**: {{< m >}}\omega_\text{exact} = \partial_1^T f{{< /m >}} means flow on edge {{< m >}}[u,v]{{< /m >}} equals {{< m >}}f(v) - f(u){{< /m >}}: the progression flows from high-potential to low-potential pitch classes. Dominant (high potential) → tonic (low potential) is exactly this gradient structure. The exact component is automatically acyclic — consistent with goal-directed harmonic motion.

**Example**: Final bars of Bach chorale BWV 269. The cadence ii⁶–V–V⁷–I is almost pure gradient flow: {{< m >}}f(D) > f(G) > f(C){{< /m >}}, monotonically descending to the tonic.

**Falsification**: Find high {{< m >}}E_\text{exact}{{< /m >}} with no cadential structure.
{{< /conjecture >}}

{{< conjecture name="H2: Coexact Energy ≈ Chromatic Cycles (PLR)" >}}
A passage with high {{< m >}}E_\text{coexact}/\|w\|^2{{< /m >}} tends to exhibit PLR-type short cycles and chromatic voice leading.

**Reasoning**: {{< m >}}\omega_\text{coexact} = \partial_2 g{{< /m >}} is a sum of triangle boundaries — local circulation around triads. Neo-Riemannian P, L, R transformations create short cycles wrapping around adjacent triangles (each step moves one voice by a semitone or whole tone).

**Example**: Opening of Brahms Intermezzo Op. 119 No. 1 — chains of third-related triads (B min → D maj → F♯ min → A maj → …), each a P or R step, locally circular with no global modulation. The hexatonic cycle (C maj → C min → A♭ maj → A♭ min → E maj → E min → C maj) lies entirely in {{< m >}}\operatorname{im}(\partial_2){{< /m >}}.

**Falsification**: Find high {{< m >}}E_\text{coexact}{{< /m >}} with no chromatic activity.
{{< /conjecture >}}

{{< conjecture name="H3: Harmonic Energy ≈ Remote Modulation" >}}
A passage with high {{< m >}}E_\text{harmonic}/\|w\|^2{{< /m >}} corresponds to modulation along the torus topology — the tonal center migrates globally.

**Reasoning**: {{< m >}}\omega_\text{harmonic} \in \ker(L_1){{< /m >}} means simultaneously divergence-free ({{< m >}}\partial_1 \omega = 0{{< /m >}}) and curl-free ({{< m >}}\partial_2^T \omega = 0{{< /m >}}). The only non-zero flows on a torus satisfying both are those along the two non-contractible loops: circle of fifths or major third axis. The tonal center itself migrates — no local potential drop or eddy explains it; the flow is topological.

**Examples**:
- Development of Schubert's String Quintet D. 956, mvt. 2: E maj → F min → chain of major-third related keys — traverses the major-third non-contractible loop.
- Development of Beethoven's "Waldstein" Sonata Op. 53: C → E → A♭ → C, a complete circle of major thirds — one generator of {{< m >}}H_1{{< /m >}}.

**Falsification**: Find high {{< m >}}E_\text{harmonic}{{< /m >}} with only nearby key relations.
{{< /conjecture >}}

**Caveats**:

> *中文:* "三个分量是结构性分解，不是价值判断。Exact 不等于'好'，harmonic 不等于'高级'。"

1. **No value judgment**: "Exact" does not mean better; "harmonic" does not mean more sophisticated.
2. **Model sensitivity**: Results depend on which Tonnetz variant is used, how durations are weighted, and how musical passages are segmented.
3. **Validation required**: Statistical testing on corpora (Bach chorales, common-practice sonatas, jazz standards) against baseline tonal-distance features is needed before these hypotheses can be accepted.

> *中文:* "验证需要在真实音乐语料库上做统计检验。"

---

## Section 6: Langlands Duality and the Tonnetz

> *中文:* "数学中的 Langlands 对偶，交换根与余根，恰好对应音乐中的大小调对偶。这是一个严格的结构性对应，不是松散类比。"

The standard Tonnetz triangulates the torus {{< m >}}T^2 = \mathbb{R}^2 / \Lambda{{< /m >}}, where {{< m >}}\Lambda{{< /m >}} is the **{{< m >}}A_2{{< /m >}} root lattice** — the lattice generated by the simple roots of the Lie algebra {{< m >}}\mathfrak{sl}(3){{< /m >}}.

{{< definition name="Langlands Dual (Root System Level)" label="Definition 6.1" >}}
For a semisimple Lie algebra {{< m >}}\mathfrak{g}{{< /m >}} with root system {{< m >}}\Phi{{< /m >}}, the **coroot** of {{< m >}}\alpha \in \Phi{{< /m >}} is {{< m >}}\alpha^\vee = 2\alpha / \langle \alpha, \alpha \rangle{{< /m >}}. The **Langlands dual** {{< m >}}\mathfrak{g}^\vee{{< /m >}} is obtained by {{< m >}}\Phi \leftrightarrow \Phi^\vee{{< /m >}}.

For the {{< m >}}A_2{{< /m >}} root system (which is simply laced — all roots have the same length), roots and coroots differ only by uniform scaling, so {{< m >}}A_2{{< /m >}} is **self-dual**.
{{< /definition >}}

{{< theorem name="Langlands Duality = Major/Minor Duality" label="Theorem 6.1" >}}
*(Rietsch, 2024)* On the {{< m >}}A_2{{< /m >}} Tonnetz, the Langlands involution — interchange of roots and coroots — structurally corresponds to major/minor duality: every major triad maps to its parallel minor.
{{< /theorem >}}

{{< proof >}}
*(Sketch — see Rietsch 2024 §3.)* The two simple root directions in the {{< m >}}A_2{{< /m >}} lattice correspond to the major third axis ({{< m >}}+4{{< /m >}} semitones) and the minor third axis ({{< m >}}+3{{< /m >}} semitones) of the Tonnetz. Swapping roots with coroots exchanges these two axes. In the Tonnetz, edge {{< m >}}C \to E{{< /m >}} (major third, {{< m >}}+4{{< /m >}}) maps to {{< m >}}C \to E\flat{{< /m >}} (minor third, {{< m >}}+3{{< /m >}}), and edge {{< m >}}E \to G{{< /m >}} (minor third, {{< m >}}+3{{< /m >}}) maps to {{< m >}}E\flat \to G{{< /m >}} (major third, {{< m >}}+4{{< /m >}}). The triangle {{< m >}}\{C, E, G\}{{< /m >}} (C major) maps to {{< m >}}\{C, E\flat, G\}{{< /m >}} (C minor). This involution acts globally on the entire {{< m >}}A_2{{< /m >}} lattice simultaneously, yielding the parallel-minor operation across all 24 triads. {{< m >}}\square{{< /m >}}
{{< /proof >}}

{{< musical-connection >}}
**Euler 1739 → Rietsch 2024: A 285-year arc**

> *中文:* "Euler 在 1739 年画了一张音程网格。285 年后，我们才认出它里面藏着的代数拓扑结构。"

Euler drew his interval lattice as a tuning tool with no concept of simplicial homology, differential forms, or root systems. Yet the structure he wrote down is recognizable, 285 years later, as:

1. A simplicial triangulation of a torus with Betti numbers {{< m >}}(1,2,1){{< /m >}}
2. A space where the Hodge decomposition gives a tripartite analysis of harmony: gradients (cadences) + curls (PLR cycles) + topological flows (modulations)
3. A quotient of the {{< m >}}A_2{{< /m >}} root lattice — making its major/minor duality an instance of Langlands duality

The Hodge decomposition yields testable predictions: Bach chorales should have high {{< m >}}E_\text{exact}{{< /m >}} (strong cadences); Brahms intermezzos high {{< m >}}E_\text{coexact}{{< /m >}} (chromatic PLR); late Schubert high {{< m >}}E_\text{harmonic}{{< /m >}} (third-relation modulations). Whether these energy ratios outperform simpler tonal-distance metrics is an open empirical question — but the mathematical structure is exact.

**Additional results** (Rietsch 2024): A Tonnetz on a *sphere* encoding all major ninth chords; the transformation group of the seventh-chord Tonnetz is {{< m >}}S_5 \times \mathbb{Z}_{12}^4{{< /m >}}.

**Scope note**: The "Langlands duality" here operates at the level of root systems of {{< m >}}A_2{{< /m >}} — a very special case. It does not claim connections to the full Langlands program in number theory. The correspondence is precise but limited: a structural coincidence at the {{< m >}}A_2{{< /m >}} lattice level that turns out to have musical meaning.
{{< /musical-connection >}}

---

## Historical Timeline

| Year | Development | Key figure(s) |
|------|-------------|---------------|
| 1739 | Euler's interval lattice (*Tentamen novae theoriae musicae*) | Leonhard Euler |
| 1941 | Hodge theory on Riemannian manifolds | W.V.D. Hodge |
| 1944 | Discrete Hodge theory on simplicial complexes | Beno Eckmann |
| 1998 | Chicken-wire torus from parsimonious voice leading | Douthett & Steinbach |
| 2011 | HodgeRank: Hodge decomposition for statistical ranking | Jiang, Lim, Yao & Ye |
| 2013 | Tonnetz as simplicial complex; computational homology | Bigo & Andreatta |
| 2020 | Hodge Laplacians on Graphs (key reference, free PDF) | Lek-Heng Lim |
| 2020 | Generalized Tonnetze topology and homology | Jason Yust |
| 2024 | Langlands duality = major/minor duality on {{< m >}}A_2{{< /m >}} Tonnetz | Konstanze Rietsch |

---

## Extended Reading

{{< youtube id="5xLe77iTHuQ" start="14" title="What is algebraic topology?" caption="A visual introduction to algebraic topology: holes, loops, and how algebra captures what geometry cannot. The conceptual foundation for the homology groups H_k and Betti numbers used throughout EP14." >}}

{{< youtube id="MflpyJwhMhQ" title="Simplicial homology explained" caption="Simplicial complexes, boundary operators, and homology groups built from scratch — the mathematical machinery behind the Tonnetz Betti numbers β₀=1, β₁=2, β₂=1." >}}

{{< youtube id="IDcw33YRgpY" start="11" title="Visualizing the Hodge decomposition" caption="The Hodge decomposition on graphs: exact (gradient), coexact (curl), and harmonic components visualized as water flows. The EP14 musical interpretation (cadences/PLR cycles/modulations) maps directly onto these three flow types." >}}

{{< youtube id="2ptFnIj71SM" start="78" title="The derivative isn't what you think" caption="3Blue1Brown on exterior derivatives and differential forms — the continuous analogue of the coboundary operator δ used in EP14's discrete Hodge theory." >}}

{{< youtube id="IQqtsm-bBRU" start="279" title="The open hole problem" caption="An exploration of holes in topology — why the loop test (can you fill this closed curve?) is the right definition of a hole, connecting to the Tonnetz's two non-contractible loops." >}}

## Academic References

1. Euler, L. (1739). *Tentamen novae theoriae musicae*. St. Petersburg.
2. Hodge, W.V.D. (1941). *The Theory and Applications of Harmonic Integrals*. Cambridge University Press.
3. Eckmann, B. (1944). "Harmonische Funktionen und Randwertaufgaben in einem Komplex." *Commentarii Mathematici Helvetici* 17, 240–255.
4. Douthett, J. & Steinbach, P. (1998). "Parsimonious Graphs: A Study in Parsimony, Contextual Transformations, and Modes of Limited Transposition." *Journal of Music Theory* 42(2), 241–263.
5. Friedman, J. (1998). "Computing Betti Numbers via Combinatorial Laplacians." *Algorithmica* 21(4), 331–346.
6. Hatcher, A. (2002). *Algebraic Topology*. Cambridge University Press. Free PDF: https://pi.math.cornell.edu/~hatcher/AT/ATpage.html
7. Edelsbrunner, H. & Harer, J. (2010). *Computational Topology: An Introduction*. AMS.
8. Jiang, X., Lim, L.-H., Yao, Y. & Ye, Y. (2011). "Statistical Ranking and Combinatorial Hodge Theory." *Mathematical Programming* 127, 203–244.
9. Bigo, L. & Andreatta, M. (2013). "Computation and Visualization of Musical Structures in Chord-Based Simplicial Complexes." *MCM 2013*.
10. Frankel, T. (2012). *The Geometry of Physics*, 3rd ed. Cambridge University Press. Ch. 14.
11. Cannas, S. & Andreatta, M. (2018). "A Generalized Dual of the Tonnetz for Seventh Chords." *Bridges 2018*, 301–308.
12. Lim, L.-H. (2020). "Hodge Laplacians on Graphs." *SIAM Review* 62(3), 685–715. DOI: 10.1137/18M1223101. Free PDF: https://www.stat.uchicago.edu/~lekheng/work/hodge-graph.pdf — *Primary reference for all discrete Hodge theory in EP14.*
13. Yust, J. (2020). "Generalized Tonnetze and Zeitnetze, and the Topology of Music Concepts." *Journal of Mathematics and Music* 14(2), 170–203.
14. Humphreys, J. (1972). *Introduction to Lie Algebras and Representation Theory*. Springer GTM 9.
15. Rietsch, K. (2024). "Generalisations of Euler's Tonnetz on Triangulated Surfaces." *Journal of Mathematics and Music*. DOI: 10.1080/17459737.2024.2362132
