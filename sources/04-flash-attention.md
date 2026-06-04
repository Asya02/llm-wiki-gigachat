# FlashAttention: Fast and Memory-Efficient Exact Attention

FlashAttention, introduced by Dao et al. in 2022, is an IO-aware exact attention algorithm that reduces memory usage from O(N^2) to O(N) and achieves 2-4x wall-clock speedup over standard attention implementations, where N is the sequence length.

## The memory bottleneck

Standard attention computes the full N x N attention matrix, stores it in GPU high-bandwidth memory (HBM), and then multiplies by the value matrix. For long sequences, this is both memory-intensive and slow because HBM reads/writes dominate the computation time — not the actual floating point operations.

## Tiling and kernel fusion

FlashAttention's key insight is **tiling**: instead of materializing the full attention matrix, it computes attention in blocks, keeping intermediate results in fast SRAM (on-chip memory) and only writing the final output to HBM. This requires a careful recomputation strategy during the backward pass (recomputing attention scores from Q, K, V blocks rather than storing them).

The entire forward pass — matrix multiply, softmax, dropout, matrix multiply — is fused into a single GPU kernel, eliminating redundant HBM reads/writes.

## FlashAttention-2 (2023)

FlashAttention-2 improved upon the original with better work partitioning across GPU thread blocks and warps, achieving approximately 2x additional speedup. It reaches 50-73% of theoretical maximum FLOPS on A100 GPUs.

## Impact on LLM training

FlashAttention has become the de facto standard for attention computation in modern LLM training and inference. It enables training with much longer context windows (e.g., 100K+ tokens) that would be infeasible with standard attention due to memory constraints. Models like Llama 2, Mistral, and GPT-4 are trained using FlashAttention or similar IO-aware techniques.
