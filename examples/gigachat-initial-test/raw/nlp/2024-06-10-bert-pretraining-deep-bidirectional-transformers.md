Source URL: Unknown
Collected Date: 2024-06-10
Published Date: Unknown

# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

BERT (Bidirectional Encoder Representations from Transformers), introduced by Devlin et al. at Google in 2018, is a language representation model based on the Transformer encoder. Unlike previous models that read text left-to-right or right-to-left, BERT reads the entire sequence at once, making it **deeply bidirectional**.

## Pre-training objectives

BERT is pre-trained on two unsupervised tasks:

1. **Masked Language Modeling (MLM)**: 15% of input tokens are randomly masked, and the model must predict them. This forces bidirectional context learning — the model must use both left and right context to predict a masked word.

2. **Next Sentence Prediction (NSP)**: The model receives pairs of sentences and must predict whether the second sentence follows the first in the original text. This helps the model understand sentence-level relationships.

## Architecture

BERT uses only the encoder part of the Transformer architecture. Two model sizes were released:
- **BERT-Base**: 12 layers, 768 hidden size, 12 attention heads, 110M parameters
- **BERT-Large**: 24 layers, 1024 hidden size, 16 attention heads, 340M parameters

## Fine-tuning

BERT introduced the paradigm of **pre-train then fine-tune**: a single pre-trained model can be fine-tuned with just one additional output layer for a wide range of downstream tasks — question answering, sentiment analysis, named entity recognition, etc. This approach achieved state-of-the-art results on 11 NLP benchmarks upon release.

## Impact

BERT demonstrated that deep bidirectional pre-training produces representations that transfer well across tasks. It sparked a wave of similar models: RoBERTa (optimized training), ALBERT (parameter reduction), DistilBERT (distillation), and domain-specific variants like BioBERT and SciBERT.