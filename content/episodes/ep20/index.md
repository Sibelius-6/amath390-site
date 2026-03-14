---
title: "EP20: Character Interaction Networks in Opera"
subtitle: "度/介数中心性, 社区检测, 割顶"
episode: 20
date: 2026-02-27
duration: "7:33"
domains:
  - "Graph Theory"
key_theorems:
  - "Cut Vertex Disconnection"
  - "Betweenness-Centrality Bridge Detection"
  - "Modularity Maximization"
callbacks: [3, 16, 17]
forward_refs: []
weight: 20
draft: false
---

## Overview

> *中文:* "瓦格纳的《指环》四联剧，三十四个角色。谁最重要？直觉会说沃坦，因为他认识最多人。但如果看图论，答案未必是王，而可能是桥。"

When Wagner's *Ring* cycle is encoded as a graph --- 34 characters as vertices, direct interactions as edges --- the question "who is the most important character?" becomes a question about **centrality measures** on finite graphs. Degree centrality identifies the most visible node (Wotan), but betweenness centrality identifies the most structurally indispensable one (Loge), and cut-vertex analysis reveals whose removal shatters the network entirely. These are distinct mathematical concepts with distinct dramaturgical consequences.

This episode develops the graph-theoretic toolkit for character interaction networks: degree and betweenness centrality (Definitions 20.1--20.2), cut vertices and bridges (Definitions 20.3--20.4), network density (Definition 20.5), modularity and community detection (Definition 20.6), and dynamic networks under node deletion (Definition 20.8). We prove the DFS characterization of cut vertices (Theorem 20.1), state Menger's theorem on vertex connectivity (Theorem 20.2), and show that modularity maximization is NP-hard (Theorem 20.3). The running example is Wagner's *Ring*, with comparisons to *Carmen* and *Le nozze di Figaro*.

> *中文:* "今天我们把角色变成节点，把互动变成边，看一张网络图怎样泄露戏剧的命运。"

---

## Prerequisites

- {{< episode-ref ep="3" >}}Cut Vertices and Graph Connectivity (EP03){{< /episode-ref >}} --- cut vertex definition and basic connectivity
- {{< episode-ref ep="16" >}}Rossini Syntax Trees (EP16){{< /episode-ref >}} --- graph-theoretic encoding of musical structure
- {{< episode-ref ep="17" >}}Wagner Leitmotif Networks (EP17){{< /episode-ref >}} --- transformation networks on motifs

---

## Section 1: Building the Character Network

> *中文:* "先别背人名。只记两条规则：角色是节点，直接互动是边。"

We model a dramatic work as an undirected simple graph.

**Construction rule**: Given an opera (or play, film, novel), form {{< m >}}G = (V, E){{< /m >}} where each character is a vertex {{< m >}}v \in V{{< /m >}}, and an edge {{< m >}}\{u,v\} \in E{{< /m >}} exists whenever characters {{< m >}}u{{< /m >}} and {{< m >}}v{{< /m >}} interact directly (share a scene, address each other, or are co-present in a dramatic exchange). The graph is unweighted and undirected unless otherwise stated.

**Running example**: Wagner's *Ring* cycle. {{< m >}}|V| = 34{{< /m >}} characters, approximately {{< m >}}|E| = 72{{< /m >}} interaction edges (exact count depends on encoding conventions; we follow Moretti 2011).

> *中文:* "整张图...不只是角色越来越多，而是拓扑越来越清楚：先分块，再连桥；先是几个局部世界，后是一个脆弱的整体。"

**Graph assembly over the four operas**: The *Ring* network does not appear all at once. In *Das Rheingold*, the gods' cluster and the Nibelung cluster form separately, connected only through Loge. In *Die Walkure*, the Volsung family introduces a new cluster bridged to the gods through Wotan. By *Siegfried*, the hero Siegfried creates a new path from the Nibelungs (through Mime) to the gods (through Brunnhilde). In *Gotterdammerung*, the Gibichung court adds yet another cluster. The network grows by **accretion of communities linked by bridges** --- a topological signature of epic narrative.

---

## Section 2: Centrality Measures

### 2.1 Degree Centrality

{{< definition name="Degree Centrality" label="Definition 20.1" >}}
Let {{< m >}}G = (V, E){{< /m >}} be a simple graph with {{< m >}}|V| = n{{< /m >}}. The **degree** of vertex {{< m >}}v{{< /m >}} is {{< m >}}\deg(v) = |\{u \in V : \{u,v\} \in E\}|{{< /m >}}. The **degree centrality** of {{< m >}}v{{< /m >}} is the normalized quantity
{{< dm >}}C_D(v) = \frac{\deg(v)}{n - 1}{{< /dm >}}
so that {{< m >}}0 \le C_D(v) \le 1{{< /m >}}.
{{< /definition >}}

> *中文:* "先看最直觉的指标：度中心性。数邻居。沃坦最高。"

**Worked example (Ring cycle)**: Wotan interacts with approximately 16 of the 33 other characters. Thus {{< m >}}C_D(\text{Wotan}) \approx 16/33 \approx 0.48{{< /m >}}. By contrast, the Woodbird interacts with only 2 characters, giving {{< m >}}C_D(\text{Woodbird}) \approx 2/33 \approx 0.06{{< /m >}}.

**Degree distribution**: The sequence {{< m >}}(d_1, d_2, \ldots, d_n){{< /m >}} sorted in non-increasing order is called the **degree sequence** of {{< m >}}G{{< /m >}}. Character networks of epic works tend to have heavy-tailed degree distributions: a few characters interact with many others, while most are peripheral. The *Ring* cycle's degree distribution is approximately power-law, consistent with other literary networks (Stiller, Nettle & Dunbar 2003).

**Handshake lemma check**: The sum of all degrees equals {{< m >}}2|E|{{< /m >}}. For the *Ring*, {{< m >}}\sum_{v \in V} \deg(v) = 2 \cdot 72 = 144{{< /m >}}, giving an average degree of {{< m >}}\bar{d} = 144/34 \approx 4.2{{< /m >}}. Each character interacts with about 4 others on average, but the distribution is highly skewed: Wotan has degree ~16 while many minor characters (Norns, Rhine maidens individually) have degree 2 or 3.

### 2.2 Betweenness Centrality

{{< definition name="Betweenness Centrality" label="Definition 20.2" >}}
Let {{< m >}}\sigma_{st}{{< /m >}} denote the number of shortest paths from {{< m >}}s{{< /m >}} to {{< m >}}t{{< /m >}} in {{< m >}}G{{< /m >}}, and let {{< m >}}\sigma_{st}(v){{< /m >}} denote the number of those shortest paths passing through {{< m >}}v{{< /m >}} (where {{< m >}}v \neq s, t{{< /m >}}). The **betweenness centrality** of {{< m >}}v{{< /m >}} is
{{< dm >}}C_B(v) = \sum_{\substack{s,t \in V \\ s \neq v \neq t}} \frac{\sigma_{st}(v)}{\sigma_{st}}{{< /dm >}}
The **normalized** betweenness centrality divides by {{< m >}}\binom{n-1}{2} = \frac{(n-1)(n-2)}{2}{{< /m >}}, the maximum possible value.
{{< /definition >}}

**Worked example (Ring cycle)**: Consider three vertices: Wotan (W), Loge (L), and Alberich (A). Suppose the shortest path from Fasolt to Mime is Fasolt--Loge--Alberich--Mime (length 3), and this is the unique shortest path. Then {{< m >}}\sigma_{\text{Fasolt},\text{Mime}}(L) = 1{{< /m >}} and {{< m >}}\sigma_{\text{Fasolt},\text{Mime}} = 1{{< /m >}}, contributing {{< m >}}1/1 = 1{{< /m >}} to {{< m >}}C_B(L){{< /m >}}.

In the *Ring* network, Loge's betweenness centrality exceeds Wotan's despite Loge's lower degree. Loge sits on most shortest paths between the gods' cluster and the Nibelung cluster. Wotan has many neighbors but those neighbors also connect to each other, so shortest paths can bypass Wotan.

> *中文:* "但'最显眼'不等于'最不可替代'。介数中心性问的是另一件事：网络里有多少最短路径必须经过你。"

**Algorithmic note**: Brandes (2001) computes betweenness centrality for all vertices in {{< m >}}O(nm){{< /m >}} time for unweighted graphs, using BFS from each vertex.

**Comparing the two centralities**: For a star graph {{< m >}}K_{1,n-1}{{< /m >}} (one center connected to {{< m >}}n-1{{< /m >}} leaves), the center has {{< m >}}C_D = 1{{< /m >}} and {{< m >}}C_B = \binom{n-1}{2}{{< /m >}} (unnormalized) --- both maximal. But in a graph with two dense clusters connected by a single bridge vertex {{< m >}}b{{< /m >}} of degree 2, {{< m >}}C_D(b){{< /m >}} is small while {{< m >}}C_B(b){{< /m >}} is large. The *Ring* network exemplifies this second pattern: Loge's degree is low but his betweenness is high.

> *中文:* "哪些边只是热闹，哪些连接一断，整部戏就塌了？"

---

## Section 3: Cut Vertices and Bridges

### 3.1 Cut Vertices (Articulation Points)

{{< definition name="Cut Vertex" label="Definition 20.3" >}}
A vertex {{< m >}}v{{< /m >}} in a connected graph {{< m >}}G = (V, E){{< /m >}} is a **cut vertex** (or **articulation point**) if the subgraph {{< m >}}G - v{{< /m >}} (obtained by deleting {{< m >}}v{{< /m >}} and all its incident edges) is disconnected.
{{< /definition >}}

> *中文:* "第三集讲过，割点是删掉之后图就断裂的节点。把这个定义搬进歌剧里，意思立刻变得很残酷：有些角色一退场，整个世界就散了。"

**Worked example**: In the *Ring* network, Loge is a cut vertex. Removing Loge disconnects the Nibelung realm (Alberich, Mime) from the gods' realm (Wotan, Fricka, Freia, etc.) because Loge is the only character who interacts with both clusters directly. As recalled from {{< episode-ref ep="3" >}}EP03{{< /episode-ref >}}, this is exactly the formal definition: {{< m >}}G - \text{Loge}{{< /m >}} has more connected components than {{< m >}}G{{< /m >}}.

{{< theorem name="DFS Characterization of Cut Vertices" label="Theorem 20.1" >}}
Let {{< m >}}G{{< /m >}} be a connected undirected graph and let {{< m >}}T{{< /m >}} be a DFS tree of {{< m >}}G{{< /m >}} rooted at {{< m >}}r{{< /m >}}. A vertex {{< m >}}v{{< /m >}} is a cut vertex of {{< m >}}G{{< /m >}} if and only if one of the following holds:

1. {{< m >}}v = r{{< /m >}} and {{< m >}}v{{< /m >}} has at least two children in {{< m >}}T{{< /m >}}.
2. {{< m >}}v \neq r{{< /m >}} and {{< m >}}v{{< /m >}} has a child {{< m >}}u{{< /m >}} in {{< m >}}T{{< /m >}} such that no vertex in the subtree rooted at {{< m >}}u{{< /m >}} has a back edge to a proper ancestor of {{< m >}}v{{< /m >}}.

Equivalently, defining {{< m >}}\mathrm{disc}(v){{< /m >}} as the discovery time and
{{< dm >}}\mathrm{low}(u) = \min\bigl(\mathrm{disc}(u),\;\min_{(w,x) \text{ back edge from subtree}(u)} \mathrm{disc}(x)\bigr){{< /dm >}}
the condition for case 2 becomes: {{< m >}}\mathrm{low}(u) \ge \mathrm{disc}(v){{< /m >}} for some child {{< m >}}u{{< /m >}} of {{< m >}}v{{< /m >}}.
{{< /theorem >}}

{{< proof >}}
**(Case 1: {{< m >}}v = r{{< /m >}}).** If the root has children {{< m >}}u_1, u_2, \ldots, u_k{{< /m >}} in the DFS tree with {{< m >}}k \ge 2{{< /m >}}, then the subtrees rooted at {{< m >}}u_1, \ldots, u_k{{< /m >}} are pairwise disconnected in {{< m >}}G - r{{< /m >}}. To see this, note that in a DFS tree every non-tree edge is a back edge (connecting a descendant to an ancestor). No non-tree edge can connect a vertex in {{< m >}}\mathrm{subtree}(u_i){{< /m >}} to a vertex in {{< m >}}\mathrm{subtree}(u_j){{< /m >}} for {{< m >}}i \neq j{{< /m >}}, because such an edge would be a cross edge, which cannot exist in an undirected DFS tree. Therefore {{< m >}}G - r{{< /m >}} has at least {{< m >}}k \ge 2{{< /m >}} components, so {{< m >}}r{{< /m >}} is a cut vertex. Conversely, if {{< m >}}r{{< /m >}} has exactly one child in {{< m >}}T{{< /m >}}, then all other vertices are in the subtree of that child and remain connected in {{< m >}}G - r{{< /m >}}.

**(Case 2: {{< m >}}v \neq r{{< /m >}}, forward direction.)** Suppose {{< m >}}v{{< /m >}} has a child {{< m >}}u{{< /m >}} in {{< m >}}T{{< /m >}} such that {{< m >}}\mathrm{low}(u) \ge \mathrm{disc}(v){{< /m >}}. This means no vertex in {{< m >}}\mathrm{subtree}(u){{< /m >}} has a back edge reaching above {{< m >}}v{{< /m >}} (or to {{< m >}}v{{< /m >}}'s ancestors). In {{< m >}}G - v{{< /m >}}, every path from {{< m >}}\mathrm{subtree}(u){{< /m >}} to the parent of {{< m >}}v{{< /m >}} must use either a tree edge through {{< m >}}v{{< /m >}} (deleted) or a back edge above {{< m >}}v{{< /m >}} (none exists by hypothesis). So {{< m >}}\mathrm{subtree}(u){{< /m >}} is disconnected from the rest of {{< m >}}G - v{{< /m >}}, and {{< m >}}v{{< /m >}} is a cut vertex.

**(Case 2: {{< m >}}v \neq r{{< /m >}}, reverse direction.)** Suppose for every child {{< m >}}u{{< /m >}} of {{< m >}}v{{< /m >}}, {{< m >}}\mathrm{low}(u) < \mathrm{disc}(v){{< /m >}}. Then every subtree below {{< m >}}v{{< /m >}} has a back edge reaching a proper ancestor of {{< m >}}v{{< /m >}}. Removing {{< m >}}v{{< /m >}}, every vertex in {{< m >}}\mathrm{subtree}(u){{< /m >}} can reach an ancestor of {{< m >}}v{{< /m >}} via that back edge. The parent-side of {{< m >}}v{{< /m >}} remains connected (it is a subtree of {{< m >}}T - v{{< /m >}} containing {{< m >}}r{{< /m >}}). Hence {{< m >}}G - v{{< /m >}} remains connected and {{< m >}}v{{< /m >}} is not a cut vertex. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Complexity**: The algorithm runs in {{< m >}}O(n + m){{< /m >}} time via a single DFS pass, computing {{< m >}}\mathrm{disc}{{< /m >}} and {{< m >}}\mathrm{low}{{< /m >}} values. This is due to Tarjan (1972), who also used the same DFS framework for strongly connected components and biconnected components.

**Worked example (DFS on a 5-vertex path)**: Consider the path graph {{< m >}}P_5 = a - b - c - d - e{{< /m >}}. DFS from {{< m >}}a{{< /m >}} produces the tree {{< m >}}a \to b \to c \to d \to e{{< /m >}} with no back edges. For every internal vertex {{< m >}}v{{< /m >}} (i.e., {{< m >}}b, c, d{{< /m >}}), the child subtree has {{< m >}}\mathrm{low} = \mathrm{disc}(\text{child}) \ge \mathrm{disc}(v){{< /m >}}, so every internal vertex is a cut vertex. This matches intuition: removing any internal vertex from a path disconnects it.

### 3.2 Bridges

{{< definition name="Bridge" label="Definition 20.4" >}}
An edge {{< m >}}e = \{u, v\} \in E{{< /m >}} of a connected graph {{< m >}}G{{< /m >}} is a **bridge** if {{< m >}}G - e{{< /m >}} (the graph with edge {{< m >}}e{{< /m >}} removed but both endpoints retained) is disconnected.
{{< /definition >}}

**Worked example**: The edge {{< m >}}\{\text{Loge}, \text{Alberich}\}{{< /m >}} in the *Ring* is a bridge if it is the sole edge connecting the gods' cluster to the Nibelung cluster. Removing this edge (i.e., if Loge and Alberich never interacted) would split the network.

{{< proposition label="Prop 20.1" name="Bridge--Cut-Vertex Relation" >}}
If {{< m >}}e = \{u, v\}{{< /m >}} is a bridge and {{< m >}}\deg(u) \ge 2{{< /m >}}, then {{< m >}}u{{< /m >}} is a cut vertex. Conversely, if {{< m >}}v{{< /m >}} is a cut vertex connected to a component of {{< m >}}G - v{{< /m >}} by a single edge, then that edge is a bridge.
{{< /proposition >}}

{{< proof >}}
Suppose {{< m >}}e = \{u,v\}{{< /m >}} is a bridge and {{< m >}}\deg(u) \ge 2{{< /m >}}. Then {{< m >}}G - e{{< /m >}} has two components; call the one containing {{< m >}}u{{< /m >}} as {{< m >}}C_u{{< /m >}} and the one containing {{< m >}}v{{< /m >}} as {{< m >}}C_v{{< /m >}}. Since {{< m >}}\deg(u) \ge 2{{< /m >}}, vertex {{< m >}}u{{< /m >}} has at least one neighbor {{< m >}}w \neq v{{< /m >}} in {{< m >}}C_u{{< /m >}}. In {{< m >}}G - u{{< /m >}}, vertex {{< m >}}v{{< /m >}} is separated from {{< m >}}w{{< /m >}}: any path from {{< m >}}w{{< /m >}} to {{< m >}}v{{< /m >}} in {{< m >}}G{{< /m >}} must either pass through {{< m >}}u{{< /m >}} (deleted) or through the bridge {{< m >}}e{{< /m >}} (which requires reaching {{< m >}}u{{< /m >}} first). So {{< m >}}G - u{{< /m >}} is disconnected and {{< m >}}u{{< /m >}} is a cut vertex.

For the converse, if {{< m >}}v{{< /m >}} is a cut vertex and some component {{< m >}}C{{< /m >}} of {{< m >}}G - v{{< /m >}} is attached to {{< m >}}v{{< /m >}} by the single edge {{< m >}}e = \{v, w\}{{< /m >}} where {{< m >}}w \in C{{< /m >}}, then removing {{< m >}}e{{< /m >}} disconnects {{< m >}}C{{< /m >}} from the rest of {{< m >}}G{{< /m >}}, so {{< m >}}e{{< /m >}} is a bridge. {{< m >}}\square{{< /m >}}
{{< /proof >}}

> *中文:* "洛格连接着众神阵营和侏儒阵营。删掉他，网络直接断开。这就是第三集的割点。"

---

## Section 4: Network Density and Connectivity

{{< definition name="Network Density" label="Definition 20.5" >}}
The **density** of a simple undirected graph {{< m >}}G = (V, E){{< /m >}} with {{< m >}}|V| = n{{< /m >}} and {{< m >}}|E| = m{{< /m >}} is
{{< dm >}}D(G) = \frac{2m}{n(n-1)}{{< /dm >}}
so that {{< m >}}0 \le D(G) \le 1{{< /m >}}. A graph with {{< m >}}D{{< /m >}} close to 1 is **dense**; with {{< m >}}D{{< /m >}} close to 0 is **sparse**.
{{< /definition >}}

**Worked example**: For *Carmen* with approximately {{< m >}}n = 12{{< /m >}} characters and {{< m >}}m = 40{{< /m >}} edges: {{< m >}}D = 2 \cdot 40 / (12 \cdot 11) \approx 0.61{{< /m >}}. For the *Ring* with {{< m >}}n = 34{{< /m >}} and {{< m >}}m = 72{{< /m >}}: {{< m >}}D = 2 \cdot 72 / (34 \cdot 33) \approx 0.13{{< /m >}}. For *Le nozze di Figaro* with approximately {{< m >}}n = 11{{< /m >}} and {{< m >}}m = 24{{< /m >}}: {{< m >}}D = 2 \cdot 24 / (11 \cdot 10) \approx 0.44{{< /m >}}.

*Carmen* is a high-density network; the *Ring* is sparse; *Figaro* sits in between.

> *中文:* "《卡门》。高密度网络...冲突无处可逃...天然朝悲剧收缩。"

In a dense network, almost every pair of characters can interact directly, leaving no room for avoidance or ignorance. Conflict is inescapable. In a sparse network, characters inhabit separate worlds that may never collide --- until a bridge character carries information (or betrayal) across the divide.

> *中文:* "密度高，倾向悲剧；模块化强，倾向史诗；跨阵营边占主导，倾向喜剧。"

{{< definition name="Vertex Connectivity" label="Definition 20.6" >}}
The **vertex connectivity** {{< m >}}\kappa(G){{< /m >}} of a connected graph {{< m >}}G{{< /m >}} is the minimum number of vertices whose removal disconnects {{< m >}}G{{< /m >}} (or reduces it to a single vertex). A graph is **{{< m >}}k{{< /m >}}-connected** if {{< m >}}\kappa(G) \ge k{{< /m >}}.
{{< /definition >}}

**Worked example**: If the *Ring* network has a single cut vertex (Loge), then {{< m >}}\kappa(G_{\text{Ring}}) = 1{{< /m >}}. The *Carmen* network, being denser with many redundant paths, likely has {{< m >}}\kappa(G_{\text{Carmen}}) \ge 3{{< /m >}}.

{{< theorem name="Menger's Theorem" label="Theorem 20.2" >}}
Let {{< m >}}G = (V, E){{< /m >}} be a graph and let {{< m >}}s, t \in V{{< /m >}} be non-adjacent vertices. The maximum number of internally vertex-disjoint {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} paths equals the minimum number of vertices in an {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} separating set (a set {{< m >}}S \subseteq V \setminus \{s,t\}{{< /m >}} whose removal disconnects {{< m >}}s{{< /m >}} from {{< m >}}t{{< /m >}}).
{{< /theorem >}}

{{< proof >}}
We prove both directions.

**Direction 1 (max {{< m >}}\le{{< /m >}} min):** If {{< m >}}S{{< /m >}} is an {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} separating set of size {{< m >}}k{{< /m >}}, then every {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} path must pass through at least one vertex of {{< m >}}S{{< /m >}}. Since internally vertex-disjoint paths share no internal vertices, at most {{< m >}}k{{< /m >}} such paths can exist.

**Direction 2 (max {{< m >}}\ge{{< /m >}} min) by induction on {{< m >}}|E|{{< /m >}}:** The base case ({{< m >}}s, t{{< /m >}} with no path) gives both sides equal to 0. For the inductive step, let the minimum {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} separator have size {{< m >}}k{{< /m >}}.

Pick any edge {{< m >}}e = \{u, w\}{{< /m >}} on some {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} path. Consider two auxiliary graphs:

- {{< m >}}G_1 = G / e{{< /m >}} (contract {{< m >}}e{{< /m >}}, merging {{< m >}}u, w{{< /m >}} into a single vertex {{< m >}}uw{{< /m >}}). Any {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} separator in {{< m >}}G_1{{< /m >}} yields one in {{< m >}}G{{< /m >}} of equal or smaller size, so the min separator in {{< m >}}G_1{{< /m >}} has size {{< m >}}\le k{{< /m >}}. Since {{< m >}}|E(G_1)| < |E(G)|{{< /m >}}, by induction {{< m >}}G_1{{< /m >}} has {{< m >}}k{{< /m >}} vertex-disjoint {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} paths.
- {{< m >}}G_2 = G - e{{< /m >}}. Similarly, apply induction.

By a careful case analysis on whether the minimum separator in {{< m >}}G_1{{< /m >}} or {{< m >}}G_2{{< /m >}} has size exactly {{< m >}}k{{< /m >}} or {{< m >}}k-1{{< /m >}}, one reconstructs {{< m >}}k{{< /m >}} vertex-disjoint paths in {{< m >}}G{{< /m >}} from the paths in {{< m >}}G_1{{< /m >}} and {{< m >}}G_2{{< /m >}}. The full combinatorial argument (due to Menger 1927, with a streamlined proof by Dirac 1966) proceeds by splitting the minimum separator and patching paths; we refer to Diestel (2017, Theorem 3.3.1) for the complete details.

As a corollary, {{< m >}}\kappa(G) = \min_{s \neq t} \{\text{min } s\text{-}t \text{ separator size}\}{{< /m >}} equals the maximum number of vertex-disjoint paths between the worst-case pair. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Dramatic interpretation**: Menger's theorem tells us that {{< m >}}\kappa(G_{\text{Ring}}) = 1{{< /m >}} means there exist two characters whose only communication channel passes through a single intermediary. If that intermediary exits the drama, those two worlds can no longer interact.

**Worked example**: Between Fricka (in the gods' cluster) and Mime (in the Nibelung cluster), suppose there are exactly 2 internally vertex-disjoint paths: Fricka--Wotan--Loge--Alberich--Mime and Fricka--Brunnhilde--Siegfried--Mime. By Menger's theorem, any separating set for Fricka and Mime must contain at least 2 vertices. Indeed, removing both Loge and Siegfried disconnects Fricka from Mime. But for the pair (Freia, Mime), there may be only one path through Loge, so a single vertex cut suffices.

---

## Section 5: Community Detection and Modularity

> *中文:* "社区检测...让模块度尽量高。于是《指环》自然裂成几个说明性团块：众神、侏儒、英雄。"

{{< definition name="Modularity" label="Definition 20.7" >}}
Let {{< m >}}G = (V, E){{< /m >}} with {{< m >}}|E| = m{{< /m >}}, adjacency matrix {{< m >}}A{{< /m >}}, and let {{< m >}}c : V \to \{1, \ldots, r\}{{< /m >}} be a partition of vertices into {{< m >}}r{{< /m >}} communities. The **modularity** of this partition is
{{< dm >}}Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j){{< /dm >}}
where {{< m >}}k_i = \deg(i){{< /m >}}, {{< m >}}\delta(c_i, c_j) = 1{{< /m >}} if {{< m >}}c_i = c_j{{< /m >}} (same community) and 0 otherwise.

The term {{< m >}}k_i k_j / (2m){{< /m >}} is the **null model**: the expected number of edges between {{< m >}}i{{< /m >}} and {{< m >}}j{{< /m >}} in a random graph preserving the degree sequence (the configuration model). Modularity measures the fraction of edges within communities minus the expected fraction under the null model.
{{< /definition >}}

**Interpretation of the null model**: If edges were randomly distributed while preserving each vertex's degree, the probability that {{< m >}}i{{< /m >}} and {{< m >}}j{{< /m >}} are connected is approximately {{< m >}}k_i k_j / (2m){{< /m >}}. High modularity ({{< m >}}Q > 0{{< /m >}}) means the actual graph has more within-community edges than this random baseline. Values of {{< m >}}Q \ge 0.3{{< /m >}} are typically considered indicative of significant community structure (Newman & Girvan 2004).

**Worked example**: In the *Ring*, suppose we partition into three communities: Gods ({{< m >}}C_1{{< /m >}}: Wotan, Fricka, Freia, Donner, Froh, Erda, Loge, Brunnhilde), Nibelungs ({{< m >}}C_2{{< /m >}}: Alberich, Mime, Hagen), and Heroes ({{< m >}}C_3{{< /m >}}: Siegmund, Sieglinde, Siegfried, Gutrune, Gunther). Consider two vertices Wotan ({{< m >}}k_W = 16{{< /m >}}) and Fricka ({{< m >}}k_F = 6{{< /m >}}) in the same community, with {{< m >}}m = 72{{< /m >}}. Their contribution to {{< m >}}Q{{< /m >}} is {{< m >}}\frac{1}{144}[A_{WF} - \frac{16 \cdot 6}{144}]{{< /m >}}. Since {{< m >}}A_{WF} = 1{{< /m >}} and {{< m >}}\frac{96}{144} \approx 0.67{{< /m >}}, this pair contributes {{< m >}}\frac{1}{144}(1 - 0.67) \approx 0.0023{{< /m >}} to {{< m >}}Q{{< /m >}}. Summing over all same-community pairs yields the total modularity.

{{< theorem name="NP-hardness of Modularity Maximization" label="Theorem 20.3" >}}
*(Brandes et al. 2008)* Finding the partition {{< m >}}c : V \to \{1, \ldots, r\}{{< /m >}} that maximizes the modularity {{< m >}}Q{{< /m >}} is NP-hard.
{{< /theorem >}}

{{< proof >}}
*(Sketch.)* Brandes et al. (2008) reduce 3-PARTITION to modularity maximization. Given an instance of 3-PARTITION with integers {{< m >}}a_1, \ldots, a_{3s}{{< /m >}} summing to {{< m >}}sB{{< /m >}}, they construct a graph {{< m >}}G{{< /m >}} such that {{< m >}}Q{{< /m >}} achieves a specific target value if and only if the integers can be partitioned into {{< m >}}s{{< /m >}} triples each summing to {{< m >}}B{{< /m >}}. The construction encodes each integer {{< m >}}a_i{{< /m >}} as a clique of size proportional to {{< m >}}a_i{{< /m >}}, connected by carefully chosen inter-clique edges. The modularity function {{< m >}}Q{{< /m >}} then decomposes into per-community terms whose sum is maximized precisely when the 3-PARTITION condition is satisfied. Since 3-PARTITION is strongly NP-complete, modularity maximization is NP-hard. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**The Louvain algorithm** (Blondel et al. 2008) is the standard heuristic for approximate modularity maximization:

1. **Local moves**: Start with each vertex in its own community. For each vertex {{< m >}}v{{< /m >}}, compute the modularity gain from moving {{< m >}}v{{< /m >}} to each neighbor's community. Move {{< m >}}v{{< /m >}} to the community yielding the largest positive gain. Repeat until no move increases {{< m >}}Q{{< /m >}}.
2. **Aggregation**: Contract each community into a single super-node, preserving edge weights. Return to step 1 on the coarsened graph.
3. **Iterate** until convergence.

The Louvain algorithm runs in {{< m >}}O(n \log n){{< /m >}} time in practice and typically finds partitions close to the global maximum.

**Community structure of the Ring**: Applying Louvain to the *Ring* network yields communities closely matching the dramatic factions:

| Community | Characters | Internal edges | Cross-community edges |
|-----------|-----------|----------------|----------------------|
| Gods | Wotan, Fricka, Freia, Donner, Froh, Erda | Dense (most pairs interact) | Loge bridges to Nibelungs |
| Nibelungs | Alberich, Mime, Hagen | Moderate | Loge, Siegfried bridge outward |
| Volsungs/Heroes | Siegmund, Sieglinde, Siegfried, Brunnhilde | Moderate | Brunnhilde bridges to Gods |
| Gibichungs | Gunther, Gutrune | Sparse | Hagen, Siegfried bridge inward |

> *中文:* "洛格把众神接到侏儒，布伦希尔德横跨众神与英雄，齐格琳德则把家族秘密拖过边界。桥一出现，命运就出现了。"

The characters with edges crossing community boundaries --- Loge, Brunnhilde, Sieglinde, Siegfried --- are precisely those whose dramatic arcs drive the plot forward. In graph-theoretic terms, they are the **inter-community bridge vertices**. Their structural role (high betweenness, potential cut-vertex status) mirrors their narrative role (carrying information, loyalty, or betrayal across factional lines).

---

## Section 6: Dynamic Networks

{{< definition name="Temporal Graph" label="Definition 20.8" >}}
A **temporal graph** (or dynamic network) is a sequence of graphs {{< m >}}G(t) = (V(t), E(t)){{< /m >}} indexed by time {{< m >}}t \in \{1, 2, \ldots, T\}{{< /m >}}. Node deletion at time {{< m >}}t_0{{< /m >}} means {{< m >}}V(t_0) = V(t_0 - 1) \setminus \{v\}{{< /m >}} and {{< m >}}E(t_0) = E(t_0 - 1) \setminus \{e : v \in e\}{{< /m >}}.

Centrality measures become functions of time: {{< m >}}C_B(v; t){{< /m >}} is the betweenness centrality of vertex {{< m >}}v{{< /m >}} in {{< m >}}G(t){{< /m >}}.
{{< /definition >}}

> *中文:* "《诸神的黄昏》...齐格弗里德被杀，节点直接删除...布伦希尔德的介数中心性暴涨...最后一座桥。"

**Worked example (Gotterdammerung)**: Consider three snapshots:
- {{< m >}}G(1){{< /m >}}: Full network before any deaths. Brunnhilde has moderate betweenness.
- {{< m >}}G(2){{< /m >}}: Siegfried is killed --- remove vertex Siegfried. Brunnhilde, who previously shared Siegfried's bridging role, now becomes the sole connection between the heroes' remnant and the gods. Her betweenness centrality increases sharply.
- {{< m >}}G(3){{< /m >}}: Brunnhilde's self-immolation --- remove Brunnhilde. The network shatters. If Brunnhilde was the last cut vertex, {{< m >}}G(3){{< /m >}} has multiple disconnected components. The drama ends in fragmentation.

{{< proposition label="Prop 20.2" name="Betweenness Monotonicity Under Deletion" >}}
Let {{< m >}}v{{< /m >}} be a non-cut vertex deleted from {{< m >}}G{{< /m >}} to form {{< m >}}G' = G - v{{< /m >}}. If {{< m >}}w{{< /m >}} lies on shortest paths that previously went through {{< m >}}v{{< /m >}}, then {{< m >}}C_B(w; G'){{< /m >}} may increase or decrease relative to {{< m >}}C_B(w; G){{< /m >}} --- there is no general monotonicity. However, if {{< m >}}v{{< /m >}} is a cut vertex and {{< m >}}w{{< /m >}} is the unique alternative bridge between the resulting components, then {{< m >}}C_B(w; G') > C_B(w; G){{< /m >}}.
{{< /proposition >}}

{{< proof >}}
When {{< m >}}v{{< /m >}} is deleted, shortest paths that used {{< m >}}v{{< /m >}} must reroute. If {{< m >}}w{{< /m >}} is the unique alternative bridge, then all {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} pairs that were separated by {{< m >}}v{{< /m >}}'s removal but remain connected via {{< m >}}w{{< /m >}} now have all their shortest paths passing through {{< m >}}w{{< /m >}}. The numerator {{< m >}}\sigma_{st}(w){{< /m >}} increases for these pairs while {{< m >}}\sigma_{st}{{< /m >}} may also change, but the net effect is an increase because the number of {{< m >}}(s,t){{< /m >}} pairs routed exclusively through {{< m >}}w{{< /m >}} grows. In the *Ring* example, Brunnhilde absorbs all inter-component shortest paths after Siegfried's removal. {{< m >}}\square{{< /m >}}
{{< /proof >}}

**Evolution table for Gotterdammerung** (simplified):

| Time | Event | {{< m >}}|V|{{< /m >}} | {{< m >}}|E|{{< /m >}} | Cut vertices | {{< m >}}\kappa(G){{< /m >}} |
|------|-------|---------|---------|-------------|------------|
| {{< m >}}t_1{{< /m >}} | Full cast assembled | 10 | 14 | L | 1 |
| {{< m >}}t_2{{< /m >}} | Siegfried killed | 9 | 10 | B, L | 1 |
| {{< m >}}t_3{{< /m >}} | Brunnhilde's immolation | 8 | 7 | L | 1 |
| {{< m >}}t_4{{< /m >}} | Hagen drowns | 7 | 5 | L | 1 |

The progressive deletion of high-betweenness vertices causes the network to fragment. Each deletion removes edges and potentially creates new cut vertices, accelerating the collapse.

> *中文:* "悲剧，就是割点被删除的那一刻。"

---

## Section 7: Numerical Example --- The Ring Cycle Network

We compute key quantities for a simplified *Ring* network with {{< m >}}n = 10{{< /m >}} representative characters and {{< m >}}m = 14{{< /m >}} edges.

**Vertices**: W (Wotan), F (Fricka), B (Brunnhilde), L (Loge), A (Alberich), M (Mime), S (Siegfried), Sg (Siegmund), Sl (Sieglinde), H (Hagen).

**Edges**: W--F, W--B, W--L, W--Sg, W--Sl, W--S (via Erda's prophecy chain), F--B, L--A, A--M, M--S, S--B, Sg--Sl, S--H, B--H.

**Density**:
{{< dm >}}D = \frac{2 \cdot 14}{10 \cdot 9} = \frac{28}{90} \approx 0.31{{< /dm >}}

**Degree centrality**: {{< m >}}C_D(W) = 6/9 \approx 0.67{{< /m >}}, {{< m >}}C_D(L) = 2/9 \approx 0.22{{< /m >}}, {{< m >}}C_D(S) = 4/9 \approx 0.44{{< /m >}}, {{< m >}}C_D(B) = 4/9 \approx 0.44{{< /m >}}.

**Betweenness centrality of Loge**: Loge's only neighbors are Wotan and Alberich. Every shortest path from the gods' side ({W, F, B, Sg, Sl}) to the Nibelung side ({A, M}) that does not pass through S--M must pass through L. For example, {{< m >}}\sigma_{F,M} = 1{{< /m >}} (F--W--L--A--M), and {{< m >}}\sigma_{F,M}(L) = 1{{< /m >}}. Summing over all such pairs, {{< m >}}C_B(L) \ge 10{{< /m >}} (unnormalized), despite L having only degree 2.

> *中文:* "沃坦的重要性，是覆盖面；洛格的重要性，是通行权。"

**Cut vertex check**: Is Loge a cut vertex? In the DFS tree rooted at W, Loge's only child is Alberich. The subtree of Alberich contains {A, M}. The only back edge from this subtree goes to... Loge has {{< m >}}\mathrm{disc}(L) = 3{{< /m >}} (say), and the subtree of A has no back edge to any vertex with discovery time {{< m >}}< 3{{< /m >}}. So {{< m >}}\mathrm{low}(A) \ge 3 = \mathrm{disc}(L){{< /m >}}, confirming Loge is a cut vertex by Theorem 20.1.

However, the edge S--M provides an alternative path from the gods to the Nibelungs (via Siegfried). So in the full 10-vertex graph, Loge may not be a cut vertex if S--M exists. This illustrates the sensitivity of the cut-vertex property to the encoding. In the original Moretti encoding of the full *Ring*, Loge is indeed a cut vertex because certain interactions are indirect.

**Bridge detection**: The edge L--A is a bridge if there is no alternative path from L to A avoiding that edge. In our simplified graph, L's only neighbors are W and A, and A's only neighbors are L and M. The only L--A path not using the direct edge would require L--W--...--M--A, which requires the path W--S--M--A (length 4 via Siegfried). If this path exists, L--A is not a bridge. The existence of even one alternative path --- however long --- prevents an edge from being a bridge. This subtlety distinguishes the bridge concept from informal notions of "important connection."

**Full betweenness calculation for L**: We enumerate all {{< m >}}(s,t){{< /m >}} pairs with {{< m >}}s \neq L \neq t{{< /m >}} where L lies on a shortest path. The pairs where L is on the unique shortest path include: (W, A) via W--L--A (length 2, while alternative W--S--M--A has length 3, so the shortest goes through L); (F, A) via F--W--L--A (length 3); (B, A) via B--W--L--A (length 3) or B--S--M--A (length 3, bypassing L). When there are multiple shortest paths of equal length, {{< m >}}\sigma_{st}(L)/\sigma_{st}{{< /m >}} may be a fraction.

**Modularity**: Partition into {{< m >}}C_1 = \{W, F, B, Sg, Sl\}{{< /m >}} (gods/Volsungs), {{< m >}}C_2 = \{A, M, H\}{{< /m >}} (antagonists), {{< m >}}C_3 = \{S, L\}{{< /m >}} (intermediaries). The within-community edges are: {{< m >}}C_1{{< /m >}}: W--F, W--B, W--Sg, W--Sl, F--B, Sg--Sl (6 edges); {{< m >}}C_2{{< /m >}}: A--M (1 edge); {{< m >}}C_3{{< /m >}}: none. Total within-community: 7. Under the null model, the expected within-community edges for {{< m >}}C_1{{< /m >}} with degrees summing to {{< m >}}\sum k_i = 22{{< /m >}} would be approximately {{< m >}}\frac{22^2}{4 \cdot 14} \approx 8.6{{< /m >}}. The modularity {{< m >}}Q{{< /m >}} accumulates these differences across all communities.

---

## Musical Connection

{{< musical-connection >}}
> *中文:* "《卡门》。高密度网络...冲突无处可逃...天然朝悲剧收缩。《指环》。不是密室，而是大陆。社区很多，模块度很高...桥一断，世界分裂。这就是史诗的拓扑。"

Three operas illustrate three graph-theoretic regimes:

| Opera | Density {{< m >}}D{{< /m >}} | Modularity {{< m >}}Q{{< /m >}} | Cut vertices | Dramatic mode |
|-------|---------|------------|-------------|---------------|
| *Carmen* | High (~0.6) | Low (~0.1) | Few/none | Tragedy: dense conflict, no escape |
| *Ring* cycle | Low (~0.13) | High (~0.5) | Several (Loge, Brunnhilde) | Epic: modular worlds, fragile bridges |
| *Le nozze di Figaro* | Medium (~0.4) | Low (~0.15) | None | Comedy: cross-community edges dominate |

The narration's taxonomy --- "density tends toward tragedy; modularity toward epic; cross-faction edges toward comedy" --- corresponds to these three graph invariants. This is not deterministic but suggests a structural vocabulary for dramatic topology.

> *中文:* "《费加罗的婚礼》...跨界不是灾难源，而是笑料源。喜剧。"

In *Le nozze di Figaro*, the cross-community edges (servant--master, lover--rival) are not fragile bridges but robust, redundant connections. Removing any single character does not disconnect the network. Comedy thrives on the *inability* to separate: characters who should not interact are forced together, and the resulting entanglements produce humor rather than tragedy. The graph-theoretic signature is low modularity (communities bleed into each other) and high connectivity ({{< m >}}\kappa(G) \ge 2{{< /m >}}).

As noted in {{< episode-ref ep="16" >}}EP16{{< /episode-ref >}}, Rossini's structures are syntax trees; in {{< episode-ref ep="17" >}}EP17{{< /episode-ref >}}, Wagner's leitmotifs form transformation networks. Today's character networks add a third layer. The narration's concluding observation is apt:

> *中文:* "歌剧不是一个故事，而是一个多层图。"

Each layer --- syntactic (tree), motivic (transformation network), social (interaction graph), strategic ({{< episode-ref ep="18" >}}game-theoretic, EP18{{< /episode-ref >}}) --- captures a different aspect of the same dramatic object. A complete mathematical model of opera would be a **multiplex graph**: the same vertex set {{< m >}}V{{< /m >}} (characters) with multiple edge sets {{< m >}}E_1, E_2, \ldots{{< /m >}} (one per layer), and inter-layer dependencies encoding how a character's structural role in one layer constrains their role in another.

> *中文:* "第十六集，罗西尼是一棵语法树...第十七集，瓦格纳的动机是变换网络...今天，角色是社会网络...第十八集我们又在每条边上叠了一层策略，那就是博弈。"
{{< /musical-connection >}}

---

## Limits and Open Questions

1. **Encoding ambiguity**: The character network depends heavily on what counts as an "interaction." Co-presence on stage, direct address, singing simultaneously, and narrative reference all give different graphs with potentially different cut vertices and community structures.

2. **Weighted networks**: The unweighted model treats a single exchange and a 30-minute duet identically. Weighted edges (by scene duration, number of lines, or emotional intensity) would refine all centrality measures but introduce additional modeling choices.

3. **Directed networks**: Many dramatic interactions are asymmetric (one character commands, another obeys). Directed betweenness centrality and directed modularity are defined but computationally harder and less studied in the literary-network literature.

4. **Resolution limit of modularity**: Fortunato and Barthelemy (2007) showed that modularity maximization has a resolution limit: communities smaller than {{< m >}}\sqrt{2m}{{< /m >}} edges may be invisible. For the *Ring* with {{< m >}}m = 72{{< /m >}}, the resolution limit is approximately {{< m >}}\sqrt{144} = 12{{< /m >}} edges, meaning small sub-communities (e.g., the Norns trio) may be absorbed into larger clusters.

5. **Temporal resolution**: Our dynamic model (Definition 20.8) uses discrete snapshots. Continuous-time models (e.g., interval graphs where edges have active time intervals) would better capture the flow of dramatic time.

6. **Cross-work comparison**: Can density and modularity predict genre (tragedy/comedy/epic) across a large corpus? Moretti (2011) suggests yes for Shakespeare; systematic testing on opera libretti remains open.

7. **Spectral gap and robustness**: The algebraic connectivity {{< m >}}\lambda_2(L){{< /m >}} (second-smallest eigenvalue of the graph Laplacian) measures how well-connected a graph is. For the *Ring*, {{< m >}}\lambda_2{{< /m >}} is small (near a cut vertex, connectivity is fragile); for *Carmen*, {{< m >}}\lambda_2{{< /m >}} is larger. A systematic study relating {{< m >}}\lambda_2{{< /m >}} to dramatic pacing and tension remains open.

8. **Multilayer network formalization**: Combining character interactions, leitmotif transformations, and game-theoretic strategies into a single multiplex framework (Kivela et al. 2014) would allow centrality measures that account for cross-layer influence --- e.g., a character who is peripheral in the social layer but central in the motivic layer.

9. **Algorithmic drama analysis**: Can an algorithm, given only the character interaction graph (no libretto, no music), predict which character dies? A cut vertex whose deletion maximizes the increase in the number of connected components is a candidate. Testing this "topological death prediction" across a corpus of tragedies is an open computational question.

---

## Summary of Notation

| Symbol | Meaning |
|--------|---------|
| {{< m >}}G = (V, E){{< /m >}} | Undirected simple graph |
| {{< m >}}n = |V|{{< /m >}}, {{< m >}}m = |E|{{< /m >}} | Vertex and edge counts |
| {{< m >}}\deg(v){{< /m >}} | Degree of vertex {{< m >}}v{{< /m >}} |
| {{< m >}}C_D(v){{< /m >}} | Degree centrality |
| {{< m >}}C_B(v){{< /m >}} | Betweenness centrality |
| {{< m >}}\sigma_{st}{{< /m >}} | Number of shortest {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} paths |
| {{< m >}}\sigma_{st}(v){{< /m >}} | Number of shortest {{< m >}}s{{< /m >}}--{{< m >}}t{{< /m >}} paths through {{< m >}}v{{< /m >}} |
| {{< m >}}D(G){{< /m >}} | Network density |
| {{< m >}}\kappa(G){{< /m >}} | Vertex connectivity |
| {{< m >}}Q{{< /m >}} | Modularity |
| {{< m >}}A_{ij}{{< /m >}} | Adjacency matrix entry |
| {{< m >}}k_i{{< /m >}} | Degree of vertex {{< m >}}i{{< /m >}} |
| {{< m >}}G(t){{< /m >}} | Temporal graph at time {{< m >}}t{{< /m >}} |

---

## Academic References

1. Moretti, F. (2011). "Network Theory, Plot Analysis." *New Left Review* 68, 80--102.
2. Freeman, L. C. (1977). "A Set of Measures of Centrality Based on Betweenness." *Sociometry* 40(1), 35--41.
3. Brandes, U. (2001). "A Faster Algorithm for Betweenness Centrality." *Journal of Mathematical Sociology* 25(2), 163--177.
4. Newman, M. E. J. & Girvan, M. (2004). "Finding and Evaluating Community Structure in Networks." *Physical Review E* 69(2), 026113.
5. Blondel, V. D., Guillaume, J.-L., Lambiotte, R. & Lefebvre, E. (2008). "Fast Unfolding of Communities in Large Networks." *Journal of Statistical Mechanics*, P10008.
6. Brandes, U., Delling, D., Gaertler, M., Gorke, R., Hoefer, M., Nikoloski, Z. & Wagner, D. (2008). "On Modularity Clustering." *IEEE Transactions on Knowledge and Data Engineering* 20(2), 172--188.
7. Fortunato, S. & Barthelemy, M. (2007). "Resolution Limit in Community Detection." *Proceedings of the National Academy of Sciences* 104(1), 36--41.
8. Menger, K. (1927). "Zur allgemeinen Kurventheorie." *Fundamenta Mathematicae* 10, 96--115.
9. Diestel, R. (2017). *Graph Theory*, 5th ed. Springer GTM 173.
10. Stiller, J., Nettle, D. & Dunbar, R. I. M. (2003). "The Small World of Shakespeare's Plays." *Human Nature* 14(4), 397--408.
