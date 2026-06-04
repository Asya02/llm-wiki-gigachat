# FlashAttention

**FlashAttention**, introduced by Dao et al. in 2022, is an IO-aware exact attention algorithm that reduces memory usage from O(N²) to O(N) and achieves 2–4× wall-clock speedup over standard attention implementations, where N is the sequence length.

## The Memory Bottleneck

Standard attention computes the full N × N attention matrix, stores it in GPU high-bandwidth memory (HBM), then multiplies by the value matrix. For long sequences, this is both memory-intensive and slow because HBM reads/writes dominate computation time — not the actual floating-point operations.

## Tiling and Kernel Fusion

FlashAttention's key insight is **tiling**: instead of materializing the full attention matrix, it computes attention in blocks, keeping intermediate results in fast SRAM (on-chip memory) and only writing the final output to HBM. This requires a careful recomputation strategy during backward pass (recomputing Q, K, V blocks rather than storing them).

The entire forward pass—matrix multiply, softmax, dropout, matrix multiply—is fused into a single GPU kernel, eliminating redundant HBM transfers.

## FlashAttention-2 (2023)

FlashAttention-2 improved work partitioning across thread blocks and warps for ~2x additional speedup, reaching 50–73% of theoretical max FLOPS on A100 GPUs.

## Impact on LLM Training

FlashAttention has become the de facto standard for modern LLM training/inference, enabling much longer context windows (e.g., 100K+ tokens). Models like Llama 2, Mistral, and GPT-4 use FlashAttention or similar IO-aware techniques.

### Sources
Dao et al.; 2022; "FlashAttention: Fast and Memory-Efficient Exact Attention"

### Raw
[flash-attention-2022.md](../../raw/attention/flash-attention-2022.md)