# Threshold-Guided Optimization for Visual Generative Models

# Anonymous Authors1

# Abstract

Aligning large visual generative models with human feedback is often performed through pairwise preference optimization. While such approaches are conceptually simple, they fundamentally rely on annotated pairs, limiting scalability in settings where feedback is collected as independent scalar ratings. In this work, we revisit the KL-regularized alignment objective and show that the optimal policy implicitly compares each sample’s reward to an instance-specific baseline that is generally intractable. We propose a thresholdguided alignment framework that replaces this oracle baseline with a data-driven global threshold estimated from empirical score statistics. This formulation turns alignment into a binary decision task on unpaired data, enabling effective optimization directly from scalar feedback. We also incorporate a confidence weighting term to emphasize samples whose scores deviate strongly from the threshold, improving sample efficiency. Experiments across both diffusion and masked generative paradigms, spanning three test sets and five reward models, show that our method consistently improves preference alignment over previous methods. These results position our thresholdguided framework as a simple yet principled alternative for aligning visual generative models without paired comparisons.

![](images/6a22bd08736d6fdfdc2fe5b0014fcaea4cd666ba7a3845fe0f238b0eaf71cb36.jpg)  
Figure 1. The overview of the threshold-guided optimization framework for visual generative models. Scalar feedback is converted into pseudo-positive/pseudo-negative labels via a datadriven threshold, with confidence weighting based on the distance to the threshold.

complex human values can be incorporated through learned rewards. However, the operational complexity and instability of RL-style optimization (Rafailov et al., 2023) have motivated a shift towards simpler, more stable policy-fitting methods. Direct Preference Optimization (DPO) reframes alignment as a classification problem over pairs of preferred $\left( y _ { w } \right)$ and rejected $( y _ { l } )$ responses. Building on closed-form solutions of KL-regularized reinforcement learning objectives (Peters & Schaal, 2007; Peng et al., 2019; Go et al., 2023), DPO sidesteps explicit reward modeling and RL rollouts: the intractable partition function $Z ( x )$ cancels when taking differences between two responses (Rafailov et al., 2023), yielding an objective equivalent to fitting a reparameterized Bradley-Terry model (Bradley & Terry, 1952).

# 1. Introduction

Aligning large generative models with human feedback is a central challenge during the post-training stage. Reinforcement Learning from Human Feedback (RLHF) (Christiano et al., 2017; Achiam et al., 2023; Ouyang et al., 2022; Stiennon et al., 2020) formulates this problem as the optimization of a KL-regularized policy objective, demonstrating that

A central limitation of DPO (Rafailov et al., 2023) and its successors (Meng et al., 2024; Ethayarajh et al., 2024; Liu et al., 2024) is their fundamental reliance on paired preference data. In many practical settings, especially for visual generative models, feedback is more naturally collected as unpaired samples with scalar scores: for instance, 1–5 star ratings from users or continuous outputs from a reward model. While such data can in principle be converted into pairs (e.g., by comparing scores within a batch), this conversion is ad hoc, discards information about the absolute scale of scores, and can amplify noise when scores cluster tightly. This creates a gap between the pairwise assumptions baked into DPO-style objectives and the scalar nature of many real-world feedback signals.

In this work, we propose a threshold-guided optimization framework that operates directly on unpaired scalar feedback, as illustrated in Figure 1. The key idea is to convert absolute scores into preference-style supervision through a thresholding mechanism: Samples whose scores exceed a data-driven threshold are treated as “pseudo-positive”, while those below the threshold are treated as “pseudonegative”. This yields a binary decision signal on unpaired data, enabling a DPO-like classification loss without explicitly constructing pairs. We further introduce a confidenceweighting mechanism that scales each sample’s contribution by its deviation from the threshold, allowing the model to learn more from high-confidence examples while still using the full dataset.

Our framework is grounded in a theoretical analysis of the KL-regularized alignment objective (Eq. 1). We show that for any individual sample, whether to increase or decrease its probability relative to a reference model, the optimal policy update is governed by an elegant but intractable decision rule: the sample’s reward must be compared against an instance-dependent oracle baseline $\tau ^ { * } ( x ) = \beta \log Z ( x )$ This perspective makes explicit the core obstacle that has constrained both RLHF and policy-fitting methods: the intractability of the baseline $\tau ^ { * } ( x )$ for each input $x$ . Our threshold-guided framework introduces a tractable proxy for this ideal rule by replacing the oracle baseline with a global threshold $\tau$ estimated from empirical score statistics. This reformulation turns preference alignment into a binary classification problem on unpaired data, and the resulting estimator enjoys desirable consistency and calibration properties. The confidence weighting further refines this proxy by leveraging the full magnitude of the scalar scores.

We validate the proposed framework under two dominant paradigms in vision-centric generative modeling: diffusionbased models (Ho et al., 2020) trained with mean squared error (MSE) objectives, and MaskGIT-style masked token models (Chang et al., 2022) trained with cross-entropy. Our empirical evaluation covers multiple popular foundation models (Stable Diffusion v1.5 (Rombach et al., 2022), Meissonic (Bai et al., 2024), FLUX (Black-ForestLabs, 2024), and Wan 1.3B (Wan et al., 2025)) and five widely used reward models (HPSv2.1 (Wu et al., 2023), PickScore (Kirstain et al., 2023), ImageReward (Xu et al., 2023), CLIP Score (Radford et al., 2021), and LAION Aesthetic Score (Schuhmann et al., 2022)). Across these settings, threshold-guided optimization consistently improves preference alignment over previous optimization methods. Together, these findings position our framework as a simple yet principled approach to preference alignment for visual generative models without relying on paired comparisons.

In summary, our contributions are as follows:

• We introduce a threshold-guided alignment framework for visual generative models that operates directly on unpaired scalar feedback, addressing a key limitation of existing pairwise preference optimization methods.

• We provide a principled derivation of this framework as a tractable approximation to the KL-optimal decision rule, revealing how a data-driven threshold and confidence weighting arise naturally from the underlying objective.

• We demonstrate through comprehensive experiments on diffusion and masked generative paradigms that threshold-guided optimization achieves consistent preference alignment gains over previous optimization methods across multiple reward models.

# 2. Related Work

Generative Models. Generative modeling has witnessed a rapid evolution, from Generative Adversarial Networks (GANs) (Goodfellow et al., 2020) and Variational Autoencoders (VAEs) (Kingma et al., 2013), to the current dominance of diffusion models (Sohl-Dickstein et al., 2015; Ho et al., 2020; Podell et al., 2023; Betker et al., 2023; Black-Forest-Labs, 2024) and masked generative transformers (Chang et al., 2022). Denoising diffusion probabilistic models (DDPMs) have established a new state-of-the-art in high-fidelity image synthesis by iteratively reversing a noiseinjection process. Their remarkable generative quality and training stability have made them the de-facto architecture for large-scale text-to-image systems. A key breakthrough enabling granular control over the generation process was classifier-free guidance (Ho & Salimans, 2022), which allows a trade-off between sample fidelity and diversity without an external classifier. While classifier-free guidance provides a powerful mechanism for conditioning on explicit text prompts, it does not inherently address alignment with more abstract or ineffable human preferences, such as aesthetic appeal, compositional coherence, or stylistic nuance. This limitation necessitates a more direct approach to learn from human or model-based feedback.

Preference Optimization for Language Models. The challenge of aligning powerful base models with human intent was first studied systematically in large language models (LLMs). Reinforcement Learning from Human Feedback (RLHF) (Christiano et al., 2017) formulates alignment as optimizing a KL-regularized policy objective using a learned reward model. The standard RLHF pipeline (Ouyang et al., 2022; Achiam et al., 2023) consists of supervised fine-tuning (SFT), reward model training on human preference labels, and reinforcement learning (typically PPO (Schulman et al., 2017)) to maximize the learned reward under a KL constraint to a reference policy. Despite its empirical success, RLHF is complex and brittle in practice, requiring multiple models and inheriting the optimization instability of deep RL.

These difficulties have motivated a family of policy fitting methods that optimize directly on preference data. Direct Preference Optimization (DPO) (Rafailov et al., 2023) casts alignment as binary classification over pairs of preferred and rejected responses. By exploiting a closed-form solution to the KL-regularized objective, DPO directly relates this classification loss to the optimal policy, bypassing explicit reward modeling and RL rollouts. Subsequent work has generalized the basic formulation along several axes, including improvements to variance and regularization (Meng et al., 2024; Liu et al., 2025c) and kernel- or transportation-based objectives (Ethayarajh et al., 2024).

More recently, several works have sought to relax the reliance on strictly paired preferences and to exploit more general feedback structures. From a probabilistic inference viewpoint, Abdolmaleki et al. (2024) propose a framework that can learn from unpaired positive and negative examples, derived via an expectation–maximization procedure and regularized by a KL constraint to a reference policy. In parallel, Matrenok et al. (2025) introduces Quantile Reward Policy Optimization (QRPO), which fits policies directly to scalar rewards by transforming them into quantiles. This transformation makes the induced reward distribution uniform and renders the partition function analytically tractable, leading to a simple regression-style objective while still operating within the KL-regularized policy optimization framework.

Our work is conceptually related to these methods. We revisit the KL-regularized alignment objective and seek a tractable surrogate that can be optimized from scalar feedback. However, instead of quantile transformations or EMbased inference, we focus on a threshold-guided formulation that converts scores into binary decisions via a data-driven baseline, together with a confidence-weighted loss.

Preference Optimization for Vision Models. Following the success of preference optimization in LLMs, similar ideas have been adapted to vision and, in particular, diffusion models (Lee et al., 2023; Yang et al., 2024b; Deng et al., 2024; Yang et al., 2024a; Li et al., 2024; Ren et al., 2025; Yang et al., 2025; Zhang et al., 2024). Early work largely mirrored the RLHF pipeline, first training an explicit reward or aesthetic model from human judgments (Schuhmann et al., 2022) and then fine-tuning the diffusion process with RL, as in DDPO (Black et al., 2023). While effective, these methods inherit the complexity and instability of RL-based training.

Inspired by DPO, a line of work has proposed direct preference optimization for diffusion (Wallace et al., 2024), adapting the DPO loss to the diffusion setting to improve aesthetics and prompt faithfulness without explicit RL. Related approaches such as generalized reinforcement policy optimization (GRPO) (Xue et al., 2025; Liu et al., 2025a) further explore KL-regularized updates for generative models. However, most of these methods fundamentally rely on pairwise preference data, or on pairs synthesized from scalar scores, and therefore do not fully exploit the information contained in absolute ratings. In practice, feedback for visual generation is often available as unpaired scalar scores: either from human raters or from learned reward models.

In contrast, we focus on threshold-guided optimization for visual generative models under scalar feedback. We revisit the same KL-regularized objective underlying RLHF and DPO and derive a tractable surrogate based on comparing scores to a data-driven threshold. This yields a classificationstyle loss that can be optimized directly on unpaired, scored data, providing a complementary path to preference alignment that does not require explicit preference pairs or RLstyle training.

# 3. Method

We begin by revisiting the KL-regularized objective that underlies modern preference-based alignment methods and highlight the role of an instance-dependent oracle baseline. We then show how pairwise policy fitting methods such as DPO exploit this structure to avoid the intractable partition function, and why this breaks down in the unpaired, scalarfeedback setting. Finally, we derive a threshold-guided surrogate objective that enables direct optimization from unpaired scores and instantiate it for visual generative models.

# 3.1. Preliminaries: KL-Regularized RL and Policy Fitting

Many alignment methods seek a policy $\pi _ { \theta }$ that maximizes expected reward while remaining close to a reference policy $\pi _ { \mathrm { r e f } }$ (Ziebart et al., 2010; Jaques et al., 2019). This is captured by the KL-regularized objective

$$
\begin{array} { r } { \operatorname* { m a x } _ { \pi _ { \theta } } \mathbb { E } _ { x \sim \mathcal { D } , y \sim \pi _ { \theta } ( \cdot | x ) } \big [ \mathcal { R } ( x , y ) \big ] - \beta \mathbb { D } _ { \mathrm { K L } } ( \pi _ { \theta } ( \cdot | x ) | | \pi _ { \mathrm { r e f } } ( \cdot | x ) ) } \end{array}
$$

where $\mathcal { R } ( x , y )$ is a reward function and $\beta$ controls the strength of regularization.

This objective admits a closed-form optimal policy

$$
\pi ^ { * } ( y | x ) = \frac { 1 } { Z ( x ) } \pi _ { \mathrm { r e f } } ( y | x ) \exp \left( \frac { 1 } { \beta } \mathcal { R } ( x , y ) \right) ,
$$

where $\begin{array} { r } { Z ( x ) = \sum _ { y } \pi _ { \mathrm { r e f } } ( y | x ) \exp ( \mathcal { R } ( x , y ) / \beta ) } \end{array}$ is a per-input partition function. Directly optimizing through Eq. (2) is intractable because $Z ( x )$ requires summing over all possible outputs $y$ , an infinite space in realistic language and vision models.

Taking logarithms and rearranging yields

$$
\mathcal { R } ( x , y ) = \beta \log \frac { \pi ^ { * } ( y | x ) } { \pi _ { \mathrm { r e f } } ( y | x ) } + \beta \log Z ( x ) .
$$

The log-ratio $\log { \frac { \pi ^ { * } ( y | x ) } { \pi _ { \mathrm { r e f } } ( y | x ) } }$ is thus determined by the reward shifted by an oracle baseline $\tau ^ { * } ( x ) = \beta \log Z ( x )$ :

$$
\log \frac { \pi ^ { * } ( y | x ) } { \pi _ { \mathrm { r e f } } ( y | x ) } > 0 \iff \mathcal { R } ( x , y ) > \tau ^ { * } ( x ) .
$$

In words, the KL-optimal decision rule increases the probability of a sample if and only if its reward exceeds an instance-dependent baseline $\tau ^ { * } ( x )$ , which is itself intractable because it depends on $Z ( x )$ .

Pairwise policy fitting. DPO (Rafailov et al., 2023) and related methods circumvent the need to compute $\tau ^ { * } ( x )$ by working with pairwise preferences. Under the Bradley-Terry model (Bradley & Terry, 1952), the probability that $y _ { w }$ is preferred to $y _ { l }$ given $x$ is

$$
p ( y _ { w } \succ y _ { l } \mid x ) = \sigma \big ( \mathcal { R } ( x , y _ { w } ) - \mathcal { R } ( x , y _ { l } ) \big ) ,
$$

where $\sigma ( \cdot )$ is the logistic function. Substituting Eq. (3) into Eq. (5) gives

$$
\mathcal { R } ( x , y _ { w } ) - \mathcal { R } ( x , y _ { l } ) = \beta \log \frac { \pi _ { \theta } ( y _ { w } | x ) } { \pi _ { \mathrm { r e f } } ( y _ { w } | x ) } - \beta \log \frac { \pi _ { \theta } ( y _ { l } | x ) } { \pi _ { \mathrm { r e f } } ( y _ { l } | x ) } ,
$$

in which the oracle baseline $\tau ^ { * } ( x )$ cancels out. This leads to the DPO loss

$$
\begin{array} { r l r } & { } & { \mathcal { L } _ { \mathrm { D P O } } ( \pi _ { \theta } ; \pi _ { \mathrm { r e f } } ) = - \mathbb { E } _ { ( x , y _ { w } , y _ { l } ) \sim \mathcal { D } } \Big [ \log \sigma \Big ( \beta \log \frac { \pi _ { \theta } \left( y _ { w } | x \right) } { \pi _ { \mathrm { r e f } } \left( y _ { w } | x \right) } } \\ & { } & { ~ - \beta \log \frac { \pi _ { \theta } \left( y _ { l } | x \right) } { \pi _ { \mathrm { r e f } } \left( y _ { l } | x \right) } \Big ) \Big ] , ~ ( 7 ) } \end{array}
$$

which optimizes a classification-style objective without ever computing $Z ( x )$ .

Crucially, this derivation relies on access to paired samples $( y _ { w } , y _ { l } )$ for the same prompt $x$ . When supervision is provided instead as unpaired scalar scores $s$ for individual samples, the pairwise cancellation in Eq. (6) is no longer available. In this setting, we must confront the oracle baseline $\tau ^ { * } ( x )$ more directly.

# 3.2. Threshold-Guided Optimization from Scalar Feedback

We consider the common situation where supervision is available as unpaired scalar feedback:

$$
\mathcal { D } = \{ ( x _ { i } , y _ { i } , s _ { i } ) \} _ { i = 1 } ^ { n } ,
$$

where $s _ { i } \in \mathbb { R }$ is a score from a human annotator or a reward model. We treat $s$ as a noisy but informative proxy for the latent reward $\mathcal { R } ( x , y )$ in Eq. (1). Our goal is to design a tractable surrogate objective that (approximately) follows the KL-optimal decision rule in Eq. (4) without computing $\tau ^ { * } ( x )$ or constructing explicit preference pairs.

3.2.1. IDEAL KL-OPTIMAL DECISION RULE

Rewriting Eq. (4) in terms of the policy ratio gives

$$
\pi ^ { * } ( y | x ) \left\{ \begin{array} { l l } { > \pi _ { \mathrm { r e f } } ( y | x ) , } & { \mathrm { i f } \ \mathcal { R } ( x , y ) > \tau ^ { * } ( x ) , } \\ { < \pi _ { \mathrm { r e f } } ( y | x ) , } & { \mathrm { i f } \ \mathcal { R } ( x , y ) < \tau ^ { * } ( x ) . } \end{array} \right.
$$

As shown in Appendix A, the policy ratio $\pi ^ { * } ( y | x ) / \pi _ { \mathrm { r e f } } ( y | x )$ is strictly increasing in $\mathcal { R } ( x , y )$ , so Eq. (8) indeed defines an optimal classification rule. The difficulty is that the decision boundary $\tau ^ { * } ( x ) = \beta \log Z ( x )$ is input-dependent and intractable.

# 3.2.2. DATA-DRIVEN THRESHOLDING AND PSEUDO-PREFERENCES

We approximate the ideal rule in Eq. (8) using two standard modeling assumptions: First, the observed score $s$ is a monotone transform of the latent reward $\mathcal { R } ( x , y )$ , so comparing rewards can be approximated by comparing scores. Second, the oracle baseline $\tau ^ { * } ( x )$ can be replaced by a data-driven threshold $\tau$ estimated from the empirical score distribution.

Concretely, given scores $\left\{ s _ { i } \right\}$ , we set

$$
\tau = \mathrm { P e r c e n t i l e } ( \{ s _ { i } \} , p ) ,
$$

with $p$ typically chosen as the median $\scriptstyle ( p = 5 0 )$ ). We then define a pseudo-preference label

$$
l = \mathbb { H } [ s \geq \tau ] ,
$$

so that samples with $s \geq \tau$ are treated as “pseudo-positive” (desirable) and those with $s < \tau$ as “pseudo-negative” (undesirable). This yields the following surrogate decision rule:

$$
( x , y , s ) \mapsto \left\{ \begin{array} { l l } { \pi _ { \theta } ( y | x ) \gtrsim \pi _ { \mathrm { r e f } } ( y | x ) , } & { \mathrm { i f } s \geq \tau , } \\ { \pi _ { \theta } ( y | x ) \lesssim \pi _ { \mathrm { r e f } } ( y | x ) , } & { \mathrm { i f } s < \tau , } \end{array} \right.
$$

which mimics the sign of the the KL-optimal update using a single global threshold. In practice, $\tau$ can be estimated once per epoch or from a proxy dataset generated by the reference policy (Sec. 3.5).

# 3.3. Threshold-Guided Objective

To turn the surrogate rule in Eq. (9) into a learning objective, we define an implicit policy score

$$
\hat { s } _ { \theta , \mathrm { r e f } } ( x , y ) = \beta \log \frac { \pi _ { \theta } ( y | x ) } { \pi _ { \mathrm { r e f } } ( y | x ) } ,
$$

which corresponds to the log-ratio in Eq. (3). We then train a classifier that predicts whether a sample should be above or below the threshold:

$$
\begin{array} { r l } & { \mathcal { L } _ { \mathrm { T G } } ( \pi _ { \theta } ) = - \mathbb { E } _ { ( x , y , s ) \sim \mathcal { D } } \Big [ w ( s , \tau ) \big ( l \log \sigma ( \hat { s } _ { \theta , \mathrm { r e f } } ) } \\ & { \qquad + ( 1 - l ) \log ( 1 - \sigma ( \hat { s } _ { \theta , \mathrm { r e f } } ) ) \big ) \Big ] , } \end{array}
$$

where $\sigma ( \cdot )$ is the logistic function, $l = \mathcal { H } [ s \geq \tau ]$ , and $w ( s , \tau )$ is a confidence weight.

Confidence weighting. Scores far from the threshold provide less ambiguous supervision than scores near $\tau$ . We encode this intuition by setting

$$
w ( s , \tau ) = 1 + c | s - \tau | ,
$$

with a hyperparameter $c \geq 0$ controlling the strength of reweighting. This places more emphasis on high-confidence samples while still using the full dataset.

Minimizing $\mathcal { L } _ { \mathrm { T G } }$ guides $\pi _ { \theta }$ to assign larger log-probability ratios to pseudo-positive samples than to pseudo-negative ones, thereby implementing a threshold-guided approximation to the KL-optimal rule in Eq. (4).

# 3.4. Theoretical Properties

Although the surrogate objective in Eq. (10) is motivated by tractability, it is important to understand its statistical behavior. Our analysis (Appendix B) studies the estimator that minimizes the population version of $\mathcal { L } _ { \mathrm { T G } }$ and then relates the empirical minimizer to this population optimum.

Theorem 3.1 (Informal guarantees). Let $\theta ^ { \star }$ denote the population minimizer of $\mathcal { L } _ { \mathrm { T G } }$ under mild regularity conditions, and let $\hat { \theta } _ { n }$ be the empirical minimizer on n i.i.d. samples. Then:

1. Consistency. $\hat { \theta } _ { n } \ \to \ \theta ^ { \star }$ as $n  \infty$ ; in particular, the empirical estimator converges to the population optimum of the surrogate objective.

2. Asymptotic bias. The estimation error admits an expansion of order $O ( 1 / n )$ whose leading term depends on the curvature, variance, and skewness of $\mathcal { L } _ { \mathrm { T G } }$ (see Appendix $B$ ).

3. Calibration. The classifier induced by the threshold $\tau$ approximates the KL-optimal decision rule $\mathcal { k } [ \mathcal { R } ( x , y ) > \tau ^ { * } ( x ) ]$ up to a quantifiable estimation error that vanishes as the score distribution is estimated more accurately.

These results show that the threshold-guided surrogate is statistically well-behaved: the empirical minimizer is consistent for the population optimum, and the deviation from the ideal KL rule is controlled by the quality of the score and threshold estimates. We emphasize that the guarantees are stated with respect to the surrogate objective in Eq. (10), which is designed to approximate the original KL-regularized problem while remaining tractable.

# 3.5. Implementation for Visual Generative Models

3.5.1. LOG-LIKELIHOOD APPROXIMATION

The implicit policy score ${ \hat { s } } _ { \theta , { \mathrm { r e f } } }$ in Eq. (10) depends on loglikelihoods $\log \pi _ { \theta } ( y | x )$ and $\log \pi _ { \mathrm { r e f } } ( y | x )$ , whose computation is model-dependent.

Diffusion models (continuous outputs). For diffusionbased generative models, exact likelihoods are generally intractable. Following prior work on diffusion preference optimization (Lee et al., 2023; Wallace et al., 2024), we approximate the likelihood under a Gaussian observation model. If ${ \hat { y } } _ { \boldsymbol { \theta } } ( { \boldsymbol { x } } )$ is the denoised prediction, we write

$$
\begin{array} { l } { p ( y | x ) = \mathcal { N } \big ( \hat { y } _ { \theta } ( x ) , \sigma ^ { 2 } I \big ) } \\ { \displaystyle \Rightarrow \log p ( y | x ) = - \frac { 1 } { 2 \sigma ^ { 2 } } \big \| y - \hat { y } _ { \theta } ( x ) \big \| ^ { 2 } + \mathrm { c o n s t . } } \end{array}
$$

and thus use a scaled negative MSE as a surrogate:

$$
\log \pi _ { \boldsymbol { \theta } } ( y \vert x ) \approx - \frac { 1 } { T } \operatorname { M S E } \big ( y , \hat { y } _ { \boldsymbol { \theta } } ( x ) \big ) ,
$$

with a temperature hyperparameter $T$ controlling the scale.

MaskGIT (discrete outputs). For MaskGIT (Chang et al., 2022)-style (masked generative transformers) models, an image $y$ is encoded as tokens $( t _ { 1 } , \dots , t _ { N } )$ via a VQGAN (Esser et al., 2021). The model predicts masked tokens given visible context and condition $x$ , so the log-likelihood is directly available as

$$
\log \pi _ { \theta } ( y | x ) = { \frac { 1 } { | M | } } \sum _ { i \in M } \log p _ { \theta } ( t _ { i } \mid y _ { \setminus M } , x ) ,
$$

where $M$ is the set of masked positions and $y _ { \backslash M }$ denotes unmasked tokens.

# 3.5.2. TRAINING PROCEDURE

In our experiments, we adopt an offline training setup, where a fixed dataset $\{ ( x _ { i } , y _ { i } ) \}$ is first generated and scored. Reward scores $s _ { i } = r ( x _ { i } , y _ { i } )$ are precomputed, and a global threshold $\tau$ is estimated from their empirical distribution (or from a proxy set generated by $\pi _ { \mathrm { r e f . } }$ ). During training, each mini-batch receives pseudo-labels $l$ and confidence weights $w ( s , \tau )$ , and the model parameters are updated by minimizing $\mathcal { L } _ { \mathrm { T G } }$ . Algorithm 1 summarizes the threshold-guided optimization procedure.

# Algorithm 1 Offline Threshold-Guided Optimization from Scalar Feedback

Require: Initial policy $\pi \theta$ , reward model $r ( \cdot )$ , dataset $\mathcal { D } =$   
$\{ ( x _ { i } , y _ { i } ) \}$ , batch size $B$ , percentile $p$ , scale $c$ , temperature $\beta$   
Ensure: Updated policy $\pi \theta$   
1: $\pi _ { \mathrm { r e f } }  \pi _ { \theta }$   
2: Compute $s _ { i } \gets r ( x _ { i } , y _ { i } )$ for all $( x _ { i } , y _ { i } ) \in \mathcal { D }$   
3: $\tau \gets \mathrm { P e r c e n t i l e } ( \{ s _ { i } \} , p )$   
4: for each epoch do   
5: for each minibatch $\{ ( x _ { j } , y _ { j } , s _ { j } ) \} _ { j = 1 } ^ { B } \sim \mathcal { D }$ do   
6: 7: for $\begin{array} { r l } & { \mathbf { o r } j = 1 , \ldots , B \mathbf { d o } } \\ & { \ l _ { j }  \mathcal { Y } [ s _ { j } \geq \tau ] } \\ & { \ w _ { j }  1 + c \cdot | s _ { j } - \tau | } \\ & { \ \hat { r } _ { j }  \beta \big ( \log \pi _ { \theta } ( y _ { j } | x _ { j } ) - \log \pi _ { \mathrm { r e f } } ( y _ { j } | x _ { j } ) \big ) } \\ & { \ell _ { j }  - w _ { j } \Big ( l _ { j } \log \sigma ( \hat { r } _ { j } ) + ( 1 - l _ { j } ) \log ( 1 - \sigma ( \hat { r } _ { j } ) ) \Big ) } \end{array}$   
8:   
9:   
10:   
11: end for   
12: $\begin{array} { r } { \mathcal { L }  \frac { 1 } { B } \sum _ { j = 1 } ^ { B } \ell _ { j } } \end{array}$   
13: Update $\pi \theta$ by a gradient step on $\nabla _ { \boldsymbol { \theta } } \mathcal { L }$   
14: end for   
15: (Optional) $\pi _ { \mathrm { r e f } }  \pi _ { \theta }$   
16: end for

In large-scale settings where pre-scored datasets may come from a distribution different from the current policy, we estimate $\tau$ using smaller proxy sets generated by the reference policy and scored by the reward model, and then reuse the resulting threshold on the large dataset. As the proxy sets grow, the estimation error in $\tau$ shrinks, and our theoretical analysis (Theorem 3.1) shows that the induced bias in the surrogate objective decays at rate $O ( 1 / n )$ .

# 4. Experiments

We evaluate Threshold-Guided Optimization (TGO) for visual generation alignment under two training settings: (i) a true scalar-feedback setting where each prompt is associated with a single scalar score (our 10k-prompt collection), and (ii) a pairwise-to-scalar setting derived from Pick-a-Pic v2, used only for controlled comparison with prior preferencealignment methods that are commonly benchmarked on this dataset. Across both settings, we report results on standard prompt test sets and multiple reward models to reduce sensitivity to any single scorer.

# 4.1. Experimental Setup

Training data. (1) Scalar-feedback prompts (10k). We collect and filter 10,000 high-quality text prompts from the Internet (Details of prompt statistics and overlap checks with test sets are provided in App. C). For each foundation model, we sample images conditioned on these prompts and obtain scalar feedback via reward models. We use a percentile-based threshold to convert scalar scores into pseudo-preferred vs. pseudo-rejected labels. (2) Pick-aPic v2 (pairwise-to-scalar). Pick-a-Pic v2 contains human pairwise preferences. To follow the common evaluation protocol in diffusion alignment and to enable fair comparison with baselines, we convert the pairwise annotations into per-image scalar scores by aggregating win counts across comparisons1, then apply the same percentile thresholding to obtain pseudo-preferred and pseudo-rejected subsets. We use this setting only for comparison with methods whose official benchmarks are reported on Pick-a-Pic v2 (Sec. 4.3).

Models and training. We fine-tune three text-to-image foundation models: Stable Diffusion (Rombach et al., 2022), Meissonic (Bai et al., 2024), and FLUX (Black-Forest-Labs, 2024). Unless otherwise stated, TGO uses $\beta = 1$ , diffusion log-likelihood temperature $T = 0 . 0 0 1$ , and confidence scaling $c = 5$ . For the scalar-feedback (10k) setting, we train TGO and SFT with identical optimization hyperparameters (batch size 128, 78 update steps, learning rate 1e−5). For Pick-a-Pic v2 comparisons, we follow the published or official training protocol of each baseline.

Baselines. We compare against: (i) the original pretrained model, (ii) SFT (training on pseudo-preferred samples only), (iii) CSFT (Wu et al., 2023), and preference-alignment baselines including AlignProp (Prabhudesai et al., 2023), Diffusion-DPO (Wallace et al., 2024), Diffusion-KTO (Li et al., 2024), and DSPO (Zhu et al., 2025).

Evaluation protocol. We evaluate on three standard prompt test sets: Pick-a-Pic (424 prompts) (Kirstain et al., 2023), PartiPrompts (1,632 prompts) (Yu et al., 2022), and HPSv2 (3,200 prompts) (Wu et al., 2023). We report scores from multiple widely used reward models (HPSv2.1 (Wu et al., 2023), PickScore (Kirstain et al., 2023), CLIP (Radford et al., 2021), ImageReward (Xu et al., 2023) and Laion Aesthetic Score (Schuhmann et al., 2022)) to reduce dependence on any single scorer.

# 4.2. Main Results on 10k Scalar-Feedback Prompts

Quantitative results. We first study the true scalarfeedback setting using our 10k-prompt collection (App. C). Table 2 reports mean and median scores on HPS Prompts under four reward models. Compared to the original model and SFT, TGO yields consistent improvements across foundation models, with gains reflected not only in mean scores but also in medians, indicating a broad distributional shift rather than improvements driven by a small subset of prompts.

Distributional analysis. To further quantify how TGO changes model behavior beyond averages, Fig. 3 visualizes full score distributions on SD v1.4 across reward metrics. This view complements table summaries and makes it explicit whether improvements correspond to a global right-shift or only to tail effects.

Table 1. Mean reward-model scores of different post-training methods applied to SD v1.5 on three text-to-image benchmarks. Higher is better. The best result in each column is in bold, and the second best is underlined.   
![](images/4294e1f5bdcfdb06319e7f67811fc149a6d0d23a438841d54d23a4a1f310ebf2.jpg)

Table 2. Quantitative comparison of text-to-image generation across original, supervised fine-tuned (SFT), and threshold-guided optimization (TGO) methods. Higher is better. Evaluation is conducted on HPS Prompts using four different reward models.   
![](images/904c4965ec7242c9b55de069f0e4b8b38b76ad3c05539f538ffebac62e95598c.jpg)

# 4.3. Comparison on Pick-a-Pic v2

While Pick-a-Pic v2 provides pairwise human preferences, most diffusion alignment baselines report results on this dataset. To compare against these methods under their standard setting, we follow prior work2 and convert Pick-a-Pic v2 into per-image scalar scores via aggregated win counts, then threshold at percentile $p \ = \ 0 . 5$ to obtain pseudopreferred and pseudo-rejected subsets. This yields 237,530 pseudo-preferred and 690,538 pseudo-rejected samples for training.

Results. Table 1 summarizes win-rate comparisons on SD v1.5 across three test sets. TGO achieves strong performance relative to both supervised baselines and prior preference-alignment methods. Additional results on Meissonic and FLUX, as well as extended evaluations, are provided in App. E.

# 4.4. Qualitative Results

Fig. 2 provides side-by-side comparisons on SD v1.5. Across prompts sampled from HPSv2, Pick-a-Pic, and PartiPrompts, TGO better preserves prompt-relevant attributes and reduces obvious artifacts compared with SFT/CSFT and several preference-based baselines. Additional qualitative examples are deferred to Appendix F.

![](images/1a748e6582587f513aad9bcb6bd55fdf9a0b05ce78bf4669f3b5fc2ba6957d7c.jpg)  
Figure 2. Qualitative comparison on Stable Diffusion v1.5. Each column corresponds to one finetuning method (from left to right: TGO (ours), DSPO, Diffusion-KTO, Diffusion-DPO, AlignProp, CSFT, SFT, and the original SD v1.5). Each row shows images generated from the same text prompt (listed on the left), sampled from the HPS v2, Pick-a-Pic, and PartiPrompts test sets.

![](images/592ab65a88ab0bc713a7e00a152353d84ea76a8f2e5c82f54f43f45ec7860fe3.jpg)  
Figure 3. Score distributions by model and reward metric for SD1.4.

# 4.5. Text-to-Video Generalization

We further test TGO on text-to-video generation by finetuning Wan 1.3B (Wan et al., 2025) on a 15,218-prompt subset of VidProM (Wang & Yang, 2024). App. D reports VideoAlign metrics using VideoReward (Liu et al., 2025b). These results provide evidence that TGO generalizes well

from image to video.

# 4.6. Ablations

We ablate key hyperparameters in the threshold-guided loss, including the diffusion temperature $T$ , confidence scaling $c$ preference strength $\beta$ . All ablations are conducted on SD v1.5 trained on Pick-a-Pic v2; full tables are provided in App. G.

# 5. Conclusion

In this work, we introduced a threshold-guided optimization framework for aligning visual generative models directly from scalar feedback, without requiring explicitly paired preferences. By revisiting the KL-regularized objective, we interpret alignment as comparing each sample’s reward to an intractable instance-specific baseline, and replace this oracle with a global, data-driven threshold combined with a confidence-weighted surrogate loss. Experiments across diffusion and masked generative models, multiple datasets, and diverse reward models show consistent improvements over supervised fine-tuning and recent preference-based baselines. Our work indicates that scalar scores are sufficient to recover much of the benefit of pairwise preference optimization in practical visual generation settings.

# Impact Statement

This paper studies preference optimization for visual generative models using scalar feedback via a threshold-guided objective. The primary intended impact is to reduce the dependence on explicitly paired comparisons, which can be costly to collect and difficult to scale, thereby making alignment pipelines for image/video generation more accessible and efficient.

# References

Abdolmaleki, A., Piot, B., Shahriari, B., Springenberg, J. T., Hertweck, T., Joshi, R., Oh, J., Bloesch, M., Lampe, T., Heess, N., et al. Preference optimization as probabilistic inference. arXiv e-prints, pp. arXiv–2410, 2024.   
Achiam, J., Adler, S., Agarwal, S., Ahmad, L., Akkaya, I., Aleman, F. L., Almeida, D., Altenschmidt, J., Altman, S., Anadkat, S., et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.   
Bai, J., Ye, T., Chow, W., Song, E., Li, X., Dong, Z., Zhu, L., and Yan, S. Meissonic: Revitalizing masked generative transformers for efficient high-resolution text-to-image synthesis. arXiv preprint arXiv:2410.08261, 2024.   
Betker, J., Goh, G., Jing, L., Brooks, T., Wang, J., Li, L., Ouyang, L., Zhuang, J., Lee, J., Guo, Y., et al. Improving image generation with better captions. Computer Science. https://cdn. openai. com/papers/dall-e-3. pdf, 2(3): 8, 2023.   
Black, K., Janner, M., Du, Y., Kostrikov, I., and Levine, S. Training diffusion models with reinforcement learning. arXiv preprint arXiv:2305.13301, 2023.   
Black-Forest-Labs. Flux. https://github.com/ black-forest-labs/flux, 2024.   
Bradley, R. A. and Terry, M. E. Rank analysis of incomplete block designs: I. the method of paired comparisons. Biometrika, 39(3/4):324–345, 1952.   
Chang, H., Zhang, H., Jiang, L., Liu, C., and Freeman, W. T. Maskgit: Masked generative image transformer. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 11315–11325, 2022.   
Christiano, P. F., Leike, J., Brown, T., Martic, M., Legg, S., and Amodei, D. Deep reinforcement learning from human preferences. Advances in neural information processing systems, 30, 2017.   
Deng, F., Wang, Q., Wei, W., Hou, T., and Grundmann, M. Prdp: Proximal reward difference prediction for largescale reward finetuning of diffusion models. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 7423–7433, 2024.   
Esser, P., Rombach, R., and Ommer, B. Taming transformers for high-resolution image synthesis. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 12873–12883, 2021.   
Ethayarajh, K., Xu, W., Muennighoff, N., Jurafsky, D., and Kiela, D. Kto: Model alignment as prospect theoretic optimization. arXiv preprint arXiv:2402.01306, 2024.   
Go, D., Korbak, T., Kruszewski, G., Rozen, J., Ryu, N., and Dymetman, M. Aligning language models with preferences through f-divergence minimization. arXiv preprint arXiv:2302.08215, 2023.   
Goodfellow, I., Pouget-Abadie, J., Mirza, M., Xu, B., Warde-Farley, D., Ozair, S., Courville, A., and Bengio, Y. Generative adversarial networks. Communications of the ACM, 63(11):139–144, 2020.   
Ho, J. and Salimans, T. Classifier-free diffusion guidance. arXiv preprint arXiv:2207.12598, 2022.   
Ho, J., Jain, A., and Abbeel, P. Denoising diffusion probabilistic models. Advances in neural information processing systems, 33:6840–6851, 2020.   
Jaques, N., Ghandeharioun, A., Shen, J. H., Ferguson, C., Lapedriza, A., Jones, N., Gu, S., and Picard, R. Way off-policy batch deep reinforcement learning of implicit human preferences in dialog. arXiv preprint arXiv:1907.00456, 2019.   
Kingma, D. P., Welling, M., et al. Auto-encoding variational bayes, 2013.   
Kirstain, Y., Polyak, A., Singer, U., Matiana, S., Penna, J., and Levy, O. Pick-a-pic: An open dataset of user preferences for text-to-image generation. Advances in neural information processing systems, 36:36652–36663, 2023.   
Lee, K., Liu, H., Ryu, M., Watkins, O., Du, Y., Boutilier, C., Abbeel, P., Ghavamzadeh, M., and Gu, S. S. Aligning textto-image models using human feedback. arXiv preprint arXiv:2302.12192, 2023.   
Li, S., Kallidromitis, K., Gokul, A., Kato, Y., and Kozuka, K. Aligning diffusion models by optimizing human utility. Advances in Neural Information Processing Systems, 37: 24897–24925, 2024.   
Liu, J., Liu, G., Liang, J., Li, Y., Liu, J., Wang, X., Wan, P., Zhang, D., and Ouyang, W. Flow-grpo: Training flow matching models via online rl. arXiv preprint arXiv:2505.05470, 2025a.   
Liu, J., Liu, G., Liang, J., Yuan, Z., Liu, X., Zheng, M., Wu, X., Wang, Q., Qin, W., Xia, M., et al. Improving

video generation with human feedback. arXiv preprint arXiv:2501.13918, 2025b.

Liu, T., Qin, Z., Wu, J., Shen, J., Khalman, M., Joshi, R., Zhao, Y., Saleh, M., Baumgartner, S., Liu, J., et al. Lipo: Listwise preference optimization through learningto-rank. arXiv preprint arXiv:2402.01878, 2024.

Liu, T., Qin, Z., Wu, J., Shen, J., Khalman, M., Joshi, R., Zhao, Y., Saleh, M., Baumgartner, S., Liu, J., et al. Lipo: Listwise preference optimization through learningto-rank. In Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), pp. 2404–2420, 2025c.

Matrenok, S., Moalla, S., and Gulcehre, C. Quantile reward policy optimization: Alignment with pointwise regression and exact partition functions. arXiv preprint arXiv:2507.08068, 2025.

Meng, Y., Xia, M., and Chen, D. Simpo: Simple preference optimization with a reference-free reward. Advances in Neural Information Processing Systems, 37:124198– 124235, 2024.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., et al. Training language models to follow instructions with human feedback. Advances in neural information processing systems, 35:27730–27744, 2022.

Peng, X. B., Kumar, A., Zhang, G., and Levine, S. Advantage-weighted regression: Simple and scalable off-policy reinforcement learning. arXiv preprint arXiv:1910.00177, 2019.

Peters, J. and Schaal, S. Reinforcement learning by rewardweighted regression for operational space control. In Proceedings of the 24th international conference on Machine learning, pp. 745–750, 2007.

Podell, D., English, Z., Lacey, K., Blattmann, A., Dockhorn, T., Muller, J., Penna, J., and Rombach, R. Sdxl: Im- ¨ proving latent diffusion models for high-resolution image synthesis. arXiv preprint arXiv:2307.01952, 2023.

Prabhudesai, M., Goyal, A., Pathak, D., and Fragkiadaki, K. Aligning text-to-image diffusion models with reward backpropagation. 2023.

Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pp. 8748–8763. PmLR, 2021.

Rafailov, R., Sharma, A., Mitchell, E., Manning, C. D., Ermon, S., and Finn, C. Direct preference optimization: Your language model is secretly a reward model. Advances in neural information processing systems, 36: 53728–53741, 2023.

Ren, J., Zhang, Y., Liu, D., Zhang, X., and Tian, Q. Refining alignment framework for diffusion models with intermediate-step preference ranking. arXiv preprint arXiv:2502.01667, 2025.

Rombach, R., Blattmann, A., Lorenz, D., Esser, P., and Ommer, B. High-resolution image synthesis with latent diffusion models. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 10684–10695, 2022.

Schuhmann, C., Beaumont, R., Vencu, R., Gordon, C., Wightman, R., Cherti, M., Coombes, T., Katta, A., Mullis, C., Wortsman, M., et al. Laion-5b: An open large-scale dataset for training next generation image-text models. Advances in neural information processing systems, 35: 25278–25294, 2022.

Schulman, J., Wolski, F., Dhariwal, P., Radford, A., and Klimov, O. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347, 2017.

Sohl-Dickstein, J., Weiss, E., Maheswaranathan, N., and Ganguli, S. Deep unsupervised learning using nonequilibrium thermodynamics. In International conference on machine learning, pp. 2256–2265. pmlr, 2015.

Stiennon, N., Ouyang, L., Wu, J., Ziegler, D., Lowe, R., Voss, C., Radford, A., Amodei, D., and Christiano, P. F. Learning to summarize with human feedback. Advances in neural information processing systems, 33:3008–3021, 2020.

Wallace, B., Dang, M., Rafailov, R., Zhou, L., Lou, A., Purushwalkam, S., Ermon, S., Xiong, C., Joty, S., and Naik, N. Diffusion model alignment using direct preference optimization. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 8228–8238, 2024.

Wan, T., Wang, A., Ai, B., Wen, B., Mao, C., Xie, C.-W., Chen, D., Yu, F., Zhao, H., Yang, J., et al. Wan: Open and advanced large-scale video generative models. arXiv preprint arXiv:2503.20314, 2025.

Wang, W. and Yang, Y. Vidprom: A million-scale real prompt-gallery dataset for text-to-video diffusion models. Advances in Neural Information Processing Systems, 37: 65618–65642, 2024.

Wu, X., Hao, Y., Sun, K., Chen, Y., Zhu, F., Zhao, R., and Li, H. Human preference score v2: A solid benchmark for evaluating human preferences of text-to-image synthesis. arXiv preprint arXiv:2306.09341, 2023.   
Xu, J., Liu, X., Wu, Y., Tong, Y., Li, Q., Ding, M., Tang, J., and Dong, Y. Imagereward: Learning and evaluating human preferences for text-to-image generation. Advances in Neural Information Processing Systems, 36: 15903–15935, 2023.   
Xue, Z., Wu, J., Gao, Y., Kong, F., Zhu, L., Chen, M., Liu, Z., Liu, W., Guo, Q., Huang, W., et al. Dancegrpo: Unleashing grpo on visual generation. arXiv preprint arXiv:2505.07818, 2025.   
Yang, K., Tao, J., Lyu, J., Ge, C., Chen, J., Shen, W., Zhu, X., and Li, X. Using human feedback to fine-tune diffusion models without any reward model. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 8941–8951, 2024a.   
Yang, S., Chen, T., and Zhou, M. A dense reward view on aligning text-to-image diffusion with preference. arXiv preprint arXiv:2402.08265, 2024b.   
Yang, X., Tan, Z., and Li, H. Ipo: Iterative preference optimization for text-to-video generation. arXiv preprint arXiv:2502.02088, 2025.   
Yu, J., Xu, Y., Koh, J. Y., Luong, T., Baid, G., Wang, Z., Vasudevan, V., Ku, A., Yang, Y., Ayan, B. K., et al. Scaling autoregressive models for content-rich text-to-image generation. arXiv preprint arXiv:2206.10789, 2(3):5, 2022.   
Zhang, J., Wu, J., Chen, W., Ji, Y., Xiao, X., Huang, W., and Han, K. Onlinevpo: Align video diffusion model with online video-centric preference optimization. arXiv preprint arXiv:2412.15159, 2024.   
Zhu, H., Xiao, T., and Honavar, V. G. Dspo: Direct score preference optimization for diffusion model alignment. In The Thirteenth International Conference on Learning Representations, 2025.   
Ziebart, B. D., Bagnell, J. A., and Dey, A. K. Modeling interaction via the principle of maximum causal entropy, 2010.

# Main Content.

• Appendix A: Proof of Monotonicity for the Policy Ratio.   
• Appendix B: Formal Guarantees for Threshold-Guided Optimization.   
• Appendix C: Analysis of our $1 0 \mathrm { k }$ -prompt collection from Internet.   
• Appendix D: Text-to-Video Synthesis with Threshold-Guided Optimization.   
• Appendix E: Additional Quantitative Results on Text-to-Image Generation.   
• Appendix F: Additional Qualitative Results on Text-to-Image Generation.   
• Appendix G: Ablation Study.   
• Appendix H: Pseudocode of the Threshold-Guided Loss.

# A. Proof of Monotonicity for the Policy Ratio

Theorem A.1 (Monotonicity of the Policy Ratio). Let the optimal policy $\pi ^ { * } ( y | x )$ be defined by the KL-regularized objective:

$$
\pi ^ { * } ( y | x ) = \frac { 1 } { Z ( x ) } \pi _ { \mathrm { r e f } } ( y | x ) \exp \left( \frac { 1 } { \beta } r ( x , y ) \right) ,
$$

where the partition function $\begin{array} { r } { Z ( x ) = \sum _ { y ^ { \prime } \in \mathcal { V } } \pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) \exp \left( \frac { 1 } { \beta } r ( x , y ^ { \prime } ) \right) } \end{array}$ . Then, for any $y _ { k } \in \mathcal { V }$ such that $\pi _ { \mathrm { r e f } } ( y _ { k } | x ) > 0$ the ratio $\frac { \pi ^ { * } ( y _ { k } | x ) } { \pi _ { \mathrm { r e f } } \left( y _ { k } | x \right) }$ is a strictly increasing function of its reward $r ( x , y _ { k } )$ , provided there exists at least one alternative response $y ^ { \prime } \ne y _ { \boldsymbol { k } }$ with $\pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) > 0$ .

Proof. Fix $y _ { k } \in \mathcal { V }$ and define $r : = r ( x , y _ { k } )$ to simplify notation. We analyze the function:

$$
f ( r ) : = \frac { \pi ^ { * } ( y _ { k } | x ) } { \pi _ { \mathrm { r e f } } ( y _ { k } | x ) } = \frac { \exp { ( r / \beta ) } } { Z ( x ) } ,
$$

where the normalization constant $Z ( x )$ depends on $r$ , since $r ( x , y _ { k } )$ is one of the terms in its summation.

To determine if $f ( r )$ is strictly increasing, we compute its derivative with respect to $r$ using the quotient rule. Let $u ( r ) : = \exp ( r / \beta )$ and $v ( r ) : = Z ( x )$ . Then $\begin{array} { r } { \frac { d f } { d r } = \frac { u ^ { \prime } v - u v ^ { \prime } } { v ^ { 2 } } } \end{array}$ .

The derivatives of $u ( r )$ and $v ( r )$ are:

$$
\begin{array} { l } { { \displaystyle u ^ { \prime } ( r ) = \frac { 1 } { \beta } \exp ( r / \beta ) , } } \\ { { \displaystyle v ^ { \prime } ( r ) = \frac { d } { d r } \left[ \sum _ { y ^ { \prime } \in \mathcal { V } } \pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) \exp \bigl ( \frac { r ( x , y ^ { \prime } ) } { \beta } \bigr ) \right] = \pi _ { \mathrm { r e f } } ( y _ { k } | x ) \frac { 1 } { \beta } \exp ( r / \beta ) . } } \end{array}
$$

The derivative $v ^ { \prime } ( r )$ only contains the term corresponding to $y _ { k }$ because all other rewards $r ( x , y ^ { \prime } )$ for $y ^ { \prime } \ne y _ { \boldsymbol { k } }$ are treated as constants with respect to $r$ .

Substituting these into the quotient rule expression:

$$
\begin{array} { r l } & { \frac { d f } { d r } = \frac { \left( \frac { 1 } { \beta } e ^ { r / \beta } \right) Z ( x ) - e ^ { r / \beta } \left( \pi _ { \mathrm { r e f } } \left( y _ { k } | x \right) \frac { 1 } { \beta } e ^ { r / \beta } \right) } { Z ( x ) ^ { 2 } } } \\ & { \quad = \frac { e ^ { r / \beta } } { \beta Z ( x ) ^ { 2 } } \Big [ Z ( x ) - \pi _ { \mathrm { r e f } } \left( y _ { k } | x \right) e ^ { r / \beta } \Big ] . } \end{array}
$$

onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

The term in the brackets simplifies to:

$$
\begin{array} { l } { { Z ( x ) - \pi _ { \mathrm { r e f } } ( y _ { k } | x ) e ^ { r / \beta } = \Big ( \displaystyle \sum _ { y ^ { \prime } \in \mathcal { Y } } \pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) \exp \big ( \frac { r ( x , y ^ { \prime } ) } { \beta } \big ) \Big ) - \pi _ { \mathrm { r e f } } \big ( y _ { k } | x \big ) \exp \big ( \frac { r } { \beta } \big ) } } \\ { { \qquad = \displaystyle \sum _ { y ^ { \prime } \not = y _ { k } } \pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) \exp \big ( \frac { r ( x , y ^ { \prime } ) } { \beta } \big ) . } } \end{array}
$$

Since $\pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) \ge 0$ and $\exp ( \cdot ) > 0$ , each term in this sum is non-negative. By the theorem’s condition, there is at least one $y ^ { \prime } \ne y _ { \boldsymbol { k } }$ with $\pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) > 0$ , so this sum is strictly positive.

Therefore, the derivative in Eq. 15 is a product of strictly positive terms:

$$
\frac { d f } { d r } = \underbrace { \frac { \exp ( r / \beta ) } { \beta Z ( x ) ^ { 2 } } } _ { > 0 } \cdot \underbrace { \Bigg ( \sum _ { y ^ { \prime } \ne y _ { k } } \pi _ { \mathrm { r e f } } ( y ^ { \prime } | x ) \exp \bigl ( \frac { r ( x , y ^ { \prime } ) } { \beta } \bigr ) \Bigg ) } _ { > 0 } > 0 .
$$

Since the derivative is strictly positive, the function $f ( r )$ is strictly increasing in $r$ .

# B. Formal Guarantees for Threshold-Guided Optimization

This appendix collects the formal assumptions, theorems, and proofs for the guarantees of our threshold-guided objective $L _ { \mathrm { T G } }$ summarized in Theorem 3.1 in the main text. We view the minimizer of $L _ { \mathrm { T G } }$ as the threshold-guided estimator (TGO estimator).

# B.1. Assumptions

Assumption B.1 (Regularity Conditions for Threshold-Guided Optimization). Let $\ell ( \theta ; z )$ denote the per-sample thresholdguided loss (the contribution of a single sample $z$ to $L _ { \mathrm { T G } }$ ). Assume:

1. (Identifiability) The population loss $L ( \theta ) = \mathbb { E } _ { z } [ \ell ( \theta ; z ) ]$ has a unique minimizer $\theta ^ { * }$ in an open neighborhood $\mathcal { N }$ .

2. (Smoothness) $\ell ( \theta ; z )$ is three-times continuously differentiable in $\mathcal { N }$ almost surely. The population derivatives $\nabla ^ { k } L ( \theta )$ for $k = 1 , 2 , 3$ exist and are continuous at $\theta ^ { * }$ .

3. (Regularity) The Hessian $H = \nabla ^ { 2 } L ( \theta ^ { * } )$ is positive definite. The score $\nabla \ell ( \theta ^ { * } ; z )$ has finite second moments with covariance $S = \operatorname { C o v } ( \nabla \ell ( \theta ^ { * } ; z ) )$ . A Central Limit Theorem holds for $\sqrt { n } \nabla L _ { n } ( \theta ^ { * } )$ .

# B.2. Consistency of the Threshold-Guided Estimator

Corollary B.2 (Consistency of Threshold-Guided Optimization). Under Assumption B.1, the empirical TGO estimator

$$
\hat { \theta } _ { n } = \arg \operatorname* { m i n } _ { \theta } L _ { n } ( \theta ) , \quad L _ { n } ( \theta ) = \textstyle { \frac { 1 } { n } } \sum _ { i = 1 } ^ { n } \ell ( \theta ; z _ { i } )
$$

is consistent, i.e., $\hat { \theta } _ { n } \overset { p } {  } \theta ^ { * }$ as $n \to \infty$

Proof. By standard M-estimation theory, $L _ { n } ( \theta )$ converges uniformly to $L ( \theta )$ , and $L ( \theta )$ has a unique minimizer $\theta ^ { * }$ under Assumption B.1. The argmin consistency theorem therefore yields $\hat { \theta } _ { n } \overset { p } {  } \theta ^ { * }$ . □

# B.3. Asymptotic Bias of the Threshold-Guided Estimator

Theorem B.3 (Asymptotic Bias of Threshold-Guided Optimization). Under Assumption B.1, the expectation of $\hat { \theta } _ { n }$ admits the expansion

$$
\begin{array} { r } { \mathbb { E } [ \hat { \theta } _ { n } ] - \theta ^ { * } = \frac { 1 } { n } B _ { 1 } ( \theta ^ { * } ) + o ( 1 / n ) , } \end{array}
$$

onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

where the a-th coordinate of $B _ { 1 } ( \theta ^ { * } )$ is

$$
\begin{array} { r } { ( B _ { 1 } ( { \theta } ^ { \ast } ) ) _ { a } = - \frac 1 2 H _ { a b } ^ { - 1 } J _ { b c d } ( H ^ { - 1 } S H ^ { - 1 } ) _ { c d } , } \end{array}
$$

with $H = \nabla ^ { 2 } L ( \theta ^ { * } )$ , $S = \operatorname { C o v } ( \nabla \ell ( \theta ^ { * } ; z ) )$ , and $J _ { b c d } = \mathbb { E } [ \partial ^ { 3 } \ell ( \theta ^ { * } ; z ) / \partial \theta _ { b } \partial \theta _ { c } \partial \theta _ { d } ]$ .

Proof. Step 1: First-order condition and Taylor expansion. By optimality, $\nabla L _ { n } (  { \hat { \theta } } _ { n } ) = 0$ . Expanding around $\theta ^ { * }$ gives

$$
\begin{array} { r l } & { 0 = \nabla L _ { n } ( \theta ^ { * } ) + \nabla ^ { 2 } L _ { n } ( \theta ^ { * } ) ( \hat { { \theta } } _ { n } - \theta ^ { * } ) } \\ & { ~ + \frac { 1 } { 2 } \nabla ^ { 3 } L _ { n } ( \bar { \theta } ) [ \hat { { \theta } } _ { n } - { \theta } ^ { * } , \hat { { \theta } } _ { n } - { \theta } ^ { * } ] + r _ { n } , } \end{array}
$$

where $\bar { \theta }$ lies between $\hat { \theta } _ { n }$ and $\theta ^ { * }$ , and $r _ { n } = o _ { p } ( \lVert { \hat { \theta } } _ { n } - \theta ^ { * } \rVert ^ { 2 } ) = o _ { p } ( n ^ { - 1 } )$ .

Step 2: Isolate $\Delta = \hat { \theta } _ { n } - \theta ^ { * }$ . Rearranging Eq. 19 yields

$$
\begin{array} { r l } & { \Delta = - \big [ \nabla ^ { 2 } L _ { n } ( { \theta } ^ { * } ) \big ] ^ { - 1 } \nabla L _ { n } ( { \theta } ^ { * } ) } \\ & { \qquad - \frac { 1 } { 2 } \big [ \nabla ^ { 2 } L _ { n } ( { \theta } ^ { * } ) \big ] ^ { - 1 } \nabla ^ { 3 } L _ { n } ( \bar { \theta } ) [ \Delta , \Delta ] + o _ { p } ( n ^ { - 1 } ) . } \end{array}
$$

Step 3: Take expectations. Since $\mathbb { E } [ \nabla L _ { n } ( \theta ^ { * } ) ] = 0$ and $\nabla ^ { 2 } L _ { n } ( \theta ^ { * } ) \overset { p } { \to } H$ , we can replace the empirical Hessian and third derivatives by their population counterparts $H$ and $J$ up to $o ( n ^ { - 1 } )$ terms:

$$
\begin{array} { r } { \mathbb { E } [ \Delta ] = - \frac { 1 } { 2 } H ^ { - 1 } J \mathbb { E } [ \Delta \otimes \Delta ] + o ( n ^ { - 1 } ) . } \end{array}
$$

Step 4: Insert asymptotic covariance. From standard M-estimator theory,

$$
\mathbb { E } [ \Delta \otimes \Delta ] = \frac { 1 } { n } H ^ { - 1 } S H ^ { - 1 } + o ( n ^ { - 1 } ) .
$$

Substituting Eq. 22 into Eq. 21 gives

$$
\mathbb { E } [ \Delta ] = - \frac { 1 } { 2 n } H ^ { - 1 } J \big ( H ^ { - 1 } S H ^ { - 1 } \big ) + o \big ( n ^ { - 1 } ) ,
$$

which matches Eq. 18.

Remark. If $\ell ( \theta ; z )$ is the negative log-likelihood of a correctly specified model, then $S = H = I ( \theta ^ { * } )$ (the Fisher information), which further simplifies the bias term.

# B.4. Calibration of Threshold-Guided Pseudo-Labels

Proposition B.4 (Calibration of Threshold-Guided Pseudo-Labels). Let $\tau ^ { * } ( x ) = \beta \log Z ( x )$ denote the KL-optimal baseline. Suppose scores satisfy $s = g ( R ( x , y ) ) + \xi$ , where $g$ is strictly increasing and $\xi$ is sub-Gaussian. If $\tau$ is estimated as the empirical $p$ -quantile with error $\varepsilon _ { \tau } = O ( 1 / \sqrt { n } )$ , then

$$
\operatorname* { P r } [ l \neq l ^ { * } ] = O ( \varepsilon _ { \tau } + \| \xi \| _ { \psi _ { 2 } } ) ,
$$

where $l = \nV [ s \geq \tau ]$ and $l ^ { * } = \mathcal { H } [ R ( x , y ) \ge \tau ^ { * } ( x ) ]$ .

Proof. By Theorem A.1 in Appendix A, the KL-optimal rule is equivalent to thresholding $R ( x , y )$ against $\tau ^ { * } ( x )$ . Since $g$ is strictly monotone, comparing $s$ is equivalent to comparing $R$ up to the additive noise $\xi$ . The empirical quantile $\tau$ concentrates around the true quantile at rate $O ( 1 / \sqrt { n } )$ , and label flips occur only when either $\xi$ or $\varepsilon _ { \tau }$ is large enough to cross the decision boundary. This yields the stated bound. □

# C. Analysis of our 10k-prompt collection from Internet

We collect 10,000 high-quality prompts, termed MeiPrompts, for both supervised fine-tuning (SFT) and threshold-guided optimization (TGO). Figure 4 presents an analysis of the prompt set, including (a) the prompt length distribution, (b) the most frequent keywords, and (c) a CLIP-based t-SNE visualization comparing the semantic space of MeiPrompts (train set) and HPS Prompts (test set). The clear distributional divergence indicates no data leakage between the training and test sets.

![](images/456cb9deb547f9a4823479338a165ca0e50f2a041fb0b9bb774497b2967dba81.jpg)  
Figure 4. (a) Prompt length distribution, (b) word cloud, and (c) $\mathrm { C L I P + t { \cdot } S N E }$ semantic visualization of MeiPrompts and HPS Prompts.

Table 3. Text-to-video results on the VideoAlign benchmark with Wan 1.3B and VideoReward. TGO-LoRA improves the overall VideoReward score and most component metrics compared with SFT-LoRA and KTO-LoRA.   
![](images/20bd3bc4d5c08f66e9784e6874352b5be364a154efa48ab5391db0ded3c65937.jpg)

# D. Text-to-Video Synthesis with Threshold-Guided Optimization

We further evaluate TGO on text-to-video generation.Starting from VidProM, we construct a 15,218-prompt subset3 and split it into training and test sets with an 8:2 ratio. For all experiments, we randomly subsample the training split for computational efficiency.

As the backbone, we adopt Wan 1.3B (Wan et al., 2025) and use VideoReward (Liu et al., 2025b) as the reward model. Table 3 reports VideoAlign metrics for visual quality (VQ), motion quality (MQ), temporal alignment (TA), and the overall score. Compared with the supervised fine-tuning baseline (SFT-LoRA) and the preference-optimization baseline (KTOLoRA), TGO-LoRA improves the overall VideoReward score and yields better VQ and MQ while maintaining competitive temporal alignment, suggesting that the threshold-guided scheme naturally extends from images to video generation.

# E. Additional Quantitative Results on Text-to-Image Generation

We report additional quantitative comparisons for text-to-image generation across different foundation models. We apply our threshold-guided optimization to both Meissonic and Flux, and evaluate on three standard test sets: Pick-a-Pic, Parti Prompts, and HPSv2. As baselines, we include supervised fine-tuning (SFT), conditional supervised fine-tuning (CSFT), and the strongest preference-optimization method, Diffusion-KTO. Win-rate calculations follow Diffusion-KTO (Li et al., 2024).

Table 4 summarizes win rates of TGO over Meissonic on the three test sets.

Table 5 summarizes win rates of TGO over Flux on the three test sets.

We further conduct a GPT-based evaluation of threshold-guided optimization over Stable Diffusion v1.5. For each prompt in the Pick-a-Pic test set, we prepare one image generated by TGO and one image generated by a baseline model, and then randomly swap their order with $50 \%$ probability. We adopt GPT-5 as an automated judge with the following comparative instruction: “Given the text, which image better matches the description in terms of semantics and visual quality?” For each baseline, we report the fraction of prompts where GPT prefers TGO, as well as the tie rate, in Figure 5. GPT preferences are consistent with the reward-model–based metrics in Table 1 and consistently favor TGO over all baselines.

Table 4. Winrate results of threshold-guided optimization over Meissonic.   
![](images/67014e70167928ed9ff591184a7056d12ace15ff49b584eb24112763004a6822.jpg)

Table 5. Winrate results of threshold-guided optimization over Flux.   
![](images/cc30c6437d29f60c5e7b45dc7c32b3794a2109d23ea2830a760078d496ae7a0e.jpg)

# F. Additional Qualitative Results on Text-to-Image Generation

We also provide additional qualitative examples for text-to-image generation. Figures 6 and 7 show further side-by-side comparisons of images generated by SD v1.5 fine-tuned with different alignment methods.

Figures 8, 9, 10 and 11 show analogous side-by-side comparisons for Meissonic and Flux fine-tuned with different alignmen methods4.

Across all comparison figures, TGO consistently outperforms both supervised fine-tuning and prior preference-alignment baselines, producing images that better match the prompts in both semantics and visual quality.

![](images/c08d283eec1a28f37a81a88801a055f14421b9915f847c89bb87e7fd4639c4db.jpg)  
Figure 5. GPT-based evaluation of threshold-guided optimization over Stable Diffusion v1.5 on the Pick-a-Pic test set. For each baseline, we show a stacked horizontal bar indicating the fraction of prompts where GPT-5 prefers TGO, judges a tie, or prefers the baseline.

Table 6. Ablation of TGO hyperparameters on Stable Diffusion v1.5: win rate $( \% )$ of the baseline configuration $( \beta { = } 1 , c { = } 5 , T { = } 1 0 ^ { - 3 } )$ against other variants, evaluated with five reward models.   
![](images/310f37b875f1ecf6146c5b9c93af6749639d61272dc003b8a02a55b43a551364.jpg)

![](images/289677785fdd4cdb72437abe49ef5dbdde5367b96b60d1729c0b6ce7dd410eb1.jpg)  
Figure 6. More qualitative comparison on Stable Diffusion v1.5. Each column corresponds to one finetuning method (from left to right: TGO (ours), DSPO, Diffusion-KTO, Diffusion-DPO, AlignProp, CSFT, SFT, and the original SD v1.5). Each row shows images generated from the same text prompt (listed on the left), sampled from the HPS v2, Pick-a-Pic, and PartiPrompts test sets.   
onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

![](images/cbaf1e744005619dfead89c477de43e268cf77b5774d647c371831392a277938.jpg)  
Figure 7. More qualitative comparison on Stable Diffusion v1.5. Each column corresponds to one finetuning method (from left to right: TGO (ours), DSPO, Diffusion-KTO, Diffusion-DPO, AlignProp, CSFT, SFT, and the original SD v1.5). Each row shows images generated from the same text prompt (listed on the left), sampled from the HPS v2, Pick-a-Pic, and PartiPrompts test sets.   
onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

![](images/cc07a0ed5ce3e46e9991fd8bdc50c0bf84a7dc8487a2c7075e34959a69a40eaa.jpg)  
"A young girl with a red hat at night."   
"Pop figure of mom playing the piano with glasses and slightly curly brown hair."   
Figure 8. More qualitative comparison on Meissonic. Each column corresponds to one finetuning method (from left to right: TGO (ours), Diffusion-KTO, CSFT and SFT). Each row shows images generated from the same text prompt (listed on the left), sampled from the HPS v2, Pick-a-Pic, and PartiPrompts test sets.   
onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

"A photograph of the inside of a subway train. There are frogs sitting on the seats. One of them is reading a newspaper. The window shows the river in the background."

![](images/e5e4360a515b6aa6a5f1cce325e9230845be517a836a6b50ee5bf4d0e8514214.jpg)  
"A portrait of bamboo living pods shaped like a sea shell embedded on the side of a cliff."   
"The Oriental Pearl in oil painting"   
Figure 9. More qualitative comparison on Meissonic. Each column corresponds to one finetuning method (from left to right: TGO (ours), Diffusion-KTO, CSFT and SFT). Each row shows images generated from the same text prompt (listed on the left), sampled from the HPS v2, Pick-a-Pic, and PartiPrompts test sets.

onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

![](images/b4ee43160204073c67010a078b89d8bab403811f6fedec054442c9ccb3722336.jpg)  
"a little white car that has a dog in it"   
"A painting of a Japanese repair shop with celestial ornaments and HR Giger architecture."   
Figure 10. More qualitative comparison on Flux. Each column corresponds to one finetuning method (from left to right: TGO (ours), Diffusion-KTO, CSFT and SFT). Each row shows images generated from the same text prompt (listed on the left), sampled from the HPS v2, Pick-a-Pic, and PartiPrompts test sets.   
onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

![](images/517de8db544e82c4020dd56afabc867c6a32728b02c0c0b5e91e7c0c27618c6e.jpg)  
Figure 11. More qualitative comparison on Flux. Each column corresponds to one finetuning method (from left to right: TGO (ours), Diffusion-KTO, CSFT and SFT). Each row shows images generated from the same text prompt (listed on the left), sampled from the HPS v2, Pick-a-Pic, and PartiPrompts test sets.   
onfidential reviewer copy. This manuscript is under double-blind review by ICML 2026. Unauthorized sharing, redistribution, or disclosure is strictly prohibited.

# G. Ablation Study

In this section, we ablate the key hyperparameters of our threshold-guided loss: the temperature $T$ used in the diffusion log-likelihood approximation, the difference scaling factor $c$ , and the preference strength $\beta$ . All experiments are conducted on Stable Diffusion v1.5 with Pick-a-Pic v2. We present win rates of different combinations of key hyperparameters in Table 6. Overall, for SD v1.5 the best TGO hyperparameter setting is $\beta = 1$ , $c = 5$ , and $T = 0 . 0 0 1$ . Other foundation models may favor different settings, but this combination serves as a strong default in practice.

# H. Pseudocode of the Threshold-Guided Loss

We provide PyTorch-style pseudocode for the threshold-guided loss. The implementation closely follows the formulation in Section 3.5, using log-likelihood ratios between the current policy and the reference policy, reweighted by relative scores:

2771 import torch   
2782 import torch.nn.functional as F   
12804 def compute_tgo_loss(log_probs, ref_log_probs, relative_scores, beta, c): """Args: log_probs: log pi_theta(y|x), shape (B,) ref_log_probs: log pi_ref(y|x), shape (B,) relative_scores: r(y) - tau, shape (B,) beta: temperature for reward difference c: weight scaling for RM difference """ # Implicit reward difference induced by the policy ratio reward_diff $=$ beta $\star$ (log_probs - ref_log_probs) # (B,) # Preference direction and confidence weighting signs $=$ torch.sign(relative_scores) $\#$ (B,) weights $=$ 1 + c \* relative_scores.abs() # $( B ,$ ) # Binary logistic loss (use log1p for numerical stability) sig $=$ torch.sigmoid(reward_diff) pos_loss $=$ -weights $\star$ torch.log(sig $^ +$ 1e-12) neg_loss $=$ -weights $\star$ torch.log1p(-sig $^ +$ 1e-12) loss $=$ torch.where(signs $\scriptstyle > = 0$ , pos_loss, neg_loss) return loss.mean()