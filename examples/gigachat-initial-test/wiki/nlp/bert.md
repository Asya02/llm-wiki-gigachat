# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

BERT (Bidirectional Encoder Representations from Transformers) is a language representation model based on the Transformer encoder. It reads entire sequences at once, enabling deep bidirectionality.

## Overview
- Introduced by Devlin et al., Google, 2018
- Core idea: deeply bidirectional representations via masked prediction and sentence relationships
- Paradigm shift: pre-train then fine-tune for downstream NLP tasks

## Key Concepts
- **Masked Language Modeling**: Predict randomly masked tokens using both left and right context
- **Next Sentence Prediction**: Determine if two sentences are consecutive in original text
- **Architecture**: Only uses Transformer encoder; no decoder

## Model Variants
| Variant | Layers | Hidden Size | Attention Heads | Parameters |
|---|---|---|---|---|
| BERT-Base | 12 | 768 | 12 | 110M |
| BERT-Large | 24 | 1024 | 16 | 340M |

## Impact & Extensions
- Achieved state-of-the-art results across 11 NLP benchmarks upon release
- Inspired RoBERTa (optimized training), ALBERT (parameter reduction), DistilBERT (distillation)
- Domain-specific variants include BioBERT and SciBERT

## Sources
- Devlin, J., Chang, M.-W., Lee, K., Toutanova, K. (2018). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding* [ACL]

## Raw Materials
[Source Document](../../raw/nlp/2024-06-10-bert-pretraining-deep-bidirectional-transformers.md)