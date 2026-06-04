# Attention Is All You Need

> Source: Attention Is All You Need
> Collected: 2025-11-02
> Published: 2017-06-12

The Transformer architecture, introduced by Vaswani et al. in 2017, replaced recurrent layers entirely with self-attention mechanisms. The key innovation is the **scaled dot-product attention**: given queries Q, keys K, and values V, attention is computed as softmax(QK^T / sqrt(d_k)) * V, where d_k is the dimension of the keys.

**Multi-head attention** runs several attention functions in parallel, each with different learned linear projections. This allows the model to attend to information from different representation subspaces at different positions. The outputs are concatenated and projected to produce the final result.

The Transformer uses a stack of encoder and decoder layers. Each encoder layer has two sub-layers: multi-head self-attention and a position-wise feed-forward network. Each decoder layer adds a third sub-layer for cross-attention over the encoder output. Residual connections and layer normalization wrap each sub-layer.

Since attention has no inherent notion of order, the model adds **positional encodings** — sinusoidal functions of different frequencies — to the input embeddings, allowing the model to use sequence position information.

The Transformer achieved state-of-the-art results on English-to-German and English-to-French translation benchmarks while being significantly more parallelizable than recurrent models. Training time was reduced by an order of magnitude compared to previous architectures.

This architecture became the foundation for virtually all subsequent large language models, including BERT, GPT, T5, and their descendants. The self-attention mechanism's ability to capture long-range dependencies without the sequential bottleneck of RNNs proved transformative for NLP and beyond.