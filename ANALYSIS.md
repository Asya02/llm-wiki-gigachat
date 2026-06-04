# Анализ GigaChat-3-Ultra в задаче LLM Wiki

Тестирование проводилось через deepagents v0.6.7 + deepagents-gigachat v0.0.2.
Модель: **GigaChat-3-Ultra** через `gigachat.sberdevices.ru/v1`.
Задача: Karpathy LLM Wiki — инджест 4 источников, 3 запроса, 1 линт.

---

## Сильные стороны

### 1. Качественная компиляция wiki-статей

GigaChat хорошо синтезирует исходный материал в структурированные wiki-страницы. Статья по BERT — лучший пример: модель добавила таблицу с вариантами модели, чего не было в явном виде в инструкции, но что логично для wiki-формата:

```markdown
## Model Variants
| Variant | Layers | Hidden Size | Attention Heads | Parameters |
|---|---|---|---|---|
| BERT-Base | 12 | 768 | 12 | 110M |
| BERT-Large | 24 | 1024 | 16 | 340M |
```

Статья по FlashAttention также хорошо реструктурирована — модель выделила "Memory Bottleneck", "Tiling and Kernel Fusion", "FlashAttention-2" и "Impact on LLM Training" как отдельные секции.

### 2. Корректные ответы на запросы

Запрос "Compare BERT and GPT" дал хорошую сравнительную таблицу:

```
| Aspect | BERT | GPT |
|---|---|---|
| Architecture | Bidirectional Transformer encoder | Autoregressive Transformer decoder |
| Training Objective | MLM | CLM |
| Use Cases | Classification, QA, NER | Text generation, dialogue, code |
```

Ответ на запрос про FlashAttention также был точным и структурированным, с корректными техническими деталями (O(N^2) -> O(N), тайлинг, kernel fusion).

### 3. Корректное создание директорий

Модель правильно разнесла источники по topic-директориям:
- `raw/nlp/` — Transformer, BERT, GPT
- `raw/attention/` — FlashAttention

Это соответствует SKILL.md: "Create a new subdirectory only for genuinely distinct topics."

### 4. Использование `think` tool

При линтинге модель использовала `think` tool для структурированного рассуждения:

```
[think] Index consistency: wiki/index.md lists flash-attention.md,
gpt-generative-pre-training-of-language-models.md, bert.md, and
transformer.md. All these files exist...
```

Это хороший паттерн — middleware из deepagents-gigachat работает как задумано.

---

## Ошибки и слабые стороны

### ОШИБКА 1: Несогласованный формат raw-файлов (критическая)

SKILL.md задаёт шаблон `references/raw-template.md`:

```markdown
# {Title}

> Source: {URL or origin description}
> Collected: {YYYY-MM-DD}
> Published: {YYYY-MM-DD or Unknown}
```

Модель использовала **три разных формата** для четырёх raw-файлов:

**Файл 1** (`raw/nlp/attention-is-all-you-need.md`) — ближе к шаблону, но `>` blockquote:
```markdown
# Attention Is All You Need

> Source: Attention Is All You Need
> Collected: 2025-11-02
> Published: 2017-06-12
```

**Файл 2** (`raw/nlp/2024-06-10-bert-pretraining-deep-bidirectional-transformers.md`) — совершенно другой формат, без `#` заголовка для метаданных и без `>`:
```markdown
Source URL: Unknown
Collected Date: 2024-06-10
Published Date: Unknown
```

**Файл 4** (`raw/attention/flash-attention-2022.md`) — третий вариант:
```markdown
Source URL: Unknown
Collected: 2025-11-03
Published: 2022
```

**Файл 3** (`raw/nlp/gpt-generative-pre-training-of-language-models.md`) — вообще **без метаданных**, начинается прямо с контента.

Вывод: модель не способна стабильно следовать шаблону между отдельными сессиями. Каждый инджест — это новый `agent.invoke()`, и модель "забывает" формат, который использовала в предыдущем вызове.

### ОШИБКА 2: Несогласованный формат wiki-статей (критическая)

SKILL.md задаёт шаблон `references/article-template.md`:

```markdown
# {Title}

> Sources: {Author1, YYYY-MM-DD; Author2, YYYY-MM-DD}
> Raw: [{source1}](../../raw/{topic1}/{filename1}.md)
```

Реальные результаты:

**transformer.md** — использует `>` blockquote для Sources/Raw (правильно):
```markdown
> Sources: Vaswani et al., 2017
> Raw: [Attention Is All You Need](../../raw/nlp/attention-is-all-you-need.md)
```

**bert.md** — использует `##` заголовки вместо `>` blockquote, и "Raw Materials" вместо "Raw":
```markdown
## Sources
- Devlin, J., Chang, M.-W., Lee, K., Toutanova, K. (2018)...

## Raw Materials
[Source Document](../../raw/nlp/2024-06-10-bert-...)
```

**gpt-generative-pre-training-of-language-models.md** — **вообще нет секций Sources и Raw**. Весь текст — просто копия исходного материала без метаданных.

**flash-attention.md** — использует `###` заголовки (третий уровень):
```markdown
### Sources
Dao et al.; 2022; "FlashAttention:..."

### Raw
[flash-attention-2022.md](../../raw/attention/flash-attention-2022.md)
```

Четыре файла — четыре разных формата метаданных.

### ОШИБКА 3: Несогласованный формат index.md (серьёзная)

`references/index-template.md` задаёт табличный формат:

```markdown
| Article | Summary | Updated |
|---------|---------|---------|
| [{Title}]({path}) | {summary} | {YYYY-MM-DD} |
```

Фактический index.md использует списки вместо таблиц, причём каждая запись имеет свой формат:

```markdown
## attention
- [FlashAttention](attention/flash-attention.md) • Exact attention with...

## NLP
- [GPT: ...](wiki/nlp/gpt-generative-pre-training-of-language-models.md)
- [BERT: ...](nlp/bert.md) | Updated: 2024-06-10
- [Transformer Architecture](nlp/transformer.md) | The Transformer...
```

Проблемы:
- Список вместо таблицы (не соответствует шаблону)
- У FlashAttention разделитель `•`, у BERT — `|`, у Transformer — `|` с полным текстом вместо краткого summary
- У GPT вообще нет summary и даты

### ОШИБКА 4: Несогласованные пути в index.md (серьёзная)

Внутри `wiki/index.md` используются три разные схемы путей:

```
[FlashAttention](attention/flash-attention.md)              ← относительный (правильно)
[GPT: ...](wiki/nlp/gpt-generative-pre-training-of-...)     ← от корня проекта (НЕПРАВИЛЬНО)
[BERT: ...](nlp/bert.md)                                    ← относительный (правильно)
[Transformer Architecture](nlp/transformer.md)              ← относительный (правильно)
```

Ссылка на GPT содержит `wiki/nlp/...` — это путь от корня проекта, а не от `wiki/`. В Obsidian эта ссылка будет сломана, потому что файл `wiki/wiki/nlp/gpt-...` не существует.

SKILL.md явно говорит: "Inside wiki/ files, all markdown links use paths relative to the current file." Модель нарушила это правило для одного из четырёх файлов.

### ОШИБКА 5: Неверные даты в log.md (средняя)

```markdown
## 2024-06-10 ingest | BERT...
## 2025-11-02 ingest | Transformer Architecture
## [2024-10-31] ingest | GPT...
## 2025-11-03 ingest | FlashAttention
```

Все четыре инджеста произошли в один день (2026-06-03), но модель записала:
- `2024-06-10` для BERT (откуда взялась эта дата?)
- `2025-11-02` для Transformer
- `2024-10-31` для GPT (и ещё в квадратных скобках `[2024-10-31]`, хотя остальные без скобок)
- `2025-11-03` для FlashAttention

SKILL.md: "Today's date for log entries, Collected dates, and Archived dates." Модель проигнорировала правило и использовала выдуманные или перепутанные даты.

### ОШИБКА 6: Статья GPT — копия вместо компиляции (средняя)

`wiki/nlp/gpt-generative-pre-training-of-language-models.md` — это побайтовая копия исходного текста. Модель не добавила:
- Metadata header (Sources, Raw)
- Overview section
- See Also

SKILL.md: "Synthesize a coherent structure from the source material. Do not copy source text verbatim." Это правило было нарушено.

### ОШИБКА 7: Нет cascade updates и cross-references (средняя)

При инджесте BERT (2-й источник), который прямо упоминает Transformer, модель должна была обновить статью `transformer.md`, добавив cross-reference. SKILL.md:

> "After the primary article, check for ripple effects:
> 1. Scan articles in the same topic directory for content affected..."

Ни одна статья не содержит секции "See Also". Линт правильно это заметил, но сам не исправил (отнёс к heuristic checks).

### ОШИБКА 8: write_file vs edit_file (незначительная, но систематическая)

Модель систематически пытается использовать `write_file` для файлов, которые уже существуют, получает ошибку, затем переключается на `read_file` + `edit_file`:

```
[write_file] Cannot write to wiki/index.md because it already exists.
[read_file] ...
[edit_file] Successfully replaced...
```

Это происходит при каждом инджесте для `index.md` и `log.md`. Модель не запоминает между шагами, что эти файлы были созданы при инициализации. Deepagents-gigachat profile содержит инструкцию "use edit_file for small changes", но модель всё равно пытается write_file сначала.

### ОШИБКА 9: Фантомный путь при Query (незначительная)

При первом Query модель пыталась прочитать несуществующий файл:

```
[read_file] Error: File 'wiki/machine-learning/transformer-architecture.md' not found
```

Директории `machine-learning/` не существует — модель выдумала путь вместо того, чтобы сначала проверить `index.md`. Затем модель восстановилась, прочитала индекс и нашла правильный файл.

---

## Сводная таблица

| # | Проблема | Серьёзность | Причина |
|---|---------|-------------|---------|
| 1 | Разный формат raw-файлов | Критическая | Не следует шаблону стабильно |
| 2 | Разный формат wiki-статей | Критическая | Не следует шаблону стабильно |
| 3 | Формат index.md не соответствует шаблону | Серьёзная | Использует списки вместо таблиц |
| 4 | Сломанные пути в index.md | Серьёзная | Смешивает относительные и абсолютные пути |
| 5 | Неверные даты в log.md | Средняя | Не знает текущую дату, выдумывает |
| 6 | GPT-статья — копия вместо компиляции | Средняя | Пропускает обработку |
| 7 | Нет cascade updates | Средняя | Не выполняет post-ingest проверки |
| 8 | write_file → ошибка → edit_file | Незначительная | Не учится на ошибках внутри сессии |
| 9 | Фантомный путь при Query | Незначительная | Галлюцинация пути |

---

## Общие выводы

**GigaChat-3-Ultra справляется с базовой механикой**: создаёт файлы, правильно выбирает topic-директории, компилирует содержательные статьи, отвечает на вопросы с пониманием предметной области. Сравнительная таблица BERT vs GPT и объяснение FlashAttention были качественными.

**Главная слабость — нестабильность следования шаблонам и конвенциям** между независимыми вызовами. Каждый `agent.invoke()` — это новая сессия, и модель каждый раз интерпретирует SKILL.md по-своему. Это проявляется в:
- Разных форматах метаданных
- Непоследовательных стилях ссылок
- Выдуманных датах
- Пропуске обязательных шагов (cascade updates)

**Для production-использования** необходимо либо (a) более жёсткие промпты с конкретными примерами в самом SKILL.md, либо (b) пост-процессинг + lint с auto-fix, либо (c) persistent multi-turn сессия вместо независимых invocations.
