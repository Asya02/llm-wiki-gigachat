# GPT: Generative Pre-Training of Language Models

The GPT (Generative Pre-trained Transformer) family, developed by OpenAI starting in 2018, uses the Transformer decoder architecture for autoregressive language modeling. Unlike BERT's bidirectional approach, GPT models predict the next token given all previous tokens.

## GPT-1 (2018)

The original GPT demonstrated that generative pre-training on a large corpus followed by discriminative fine-tuning could achieve strong performance on various NLP tasks. It used a 12-layer Transformer decoder with 117M parameters, trained on the BooksCorpus dataset.

## GPT-2 (2019)

GPT-2 scaled up to 1.5B parameters and showed that language models can perform tasks **zero-shot** — without any fine-tuning or task-specific training data. The key insight was that a sufficiently large language model trained on diverse internet text learns to perform many tasks implicitly. OpenAI initially withheld the full model due to concerns about misuse.

## GPT-3 (2020)

GPT-3 dramatically scaled to 175B parameters and demonstrated **few-shot learning**: by providing just a few examples in the prompt (in-context learning), the model could perform new tasks without updating its weights. This established the "prompt engineering" paradigm.

## Scaling laws

The GPT series empirically confirmed **scaling laws**: model performance improves predictably as a power law with increases in model size, dataset size, and compute. This observation drove the subsequent race toward ever-larger models and eventually led to GPT-4 and beyond.

## Comparison with BERT

While BERT uses bidirectional attention and excels at understanding tasks (classification, NER), GPT uses causal (left-to-right) attention and excels at generation tasks (text completion, dialogue, code). Modern LLMs have largely converged on the GPT-style decoder-only architecture for its superior scalability and generality.
