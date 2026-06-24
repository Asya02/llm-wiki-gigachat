# Demo Playbook: LLM Wiki Fast Business Demo

Этот документ — готовый сценарий живого показа.

Цель: за один проход показать:

1. как строится база знаний из нескольких raw-источников;
2. как база отвечает на бизнес-вопрос;
3. как добавление одного нового файла улучшает итоговый ответ без полного пересчета.

---

## 0) Подготовка перед встречей (1 раз)

Проверь, что ты в корне проекта:

```bash
pwd
```

Должно быть что-то вроде:

`.../llm-wiki-example`

---

## 1) Быстрый prep перед созвоном

### Команда

```bash
rm -rf outputs/business-fast-demo
export PHOENIX_PROJECT_NAME="llm-wiki-demo-business-fast-demo"
uv run python -u run_demo.py business-fast-demo --build-only
```

### Что сказать

"Сначала я строю базу знаний только из исходников. На этом шаге мы не генерируем финальные ответы, только собираем структурированный wiki-слой."

### Что проверить глазами

- В выводе терминала есть шаги `INGEST ...`
- В финале есть `FINAL STATE`
- В выводе есть строка `[phoenix] tracing enabled ...`

### Что проверить в Phoenix

- Открой проект `llm-wiki-demo-business-fast-demo`
- Убедись, что появились свежие traces/спаны после прогона `--build-only`

### Что открыть в проводнике/Obsidian

- `outputs/business-fast-demo/raw/`
- `outputs/business-fast-demo/wiki/index.md`
- `outputs/business-fast-demo/wiki/cases/00_case_brief.md`
- `outputs/business-fast-demo/wiki/cases/ticket_history.md`

---

## 2) Старт демо: вводная (30–40 секунд)

### Что сказать (готовый текст)

"Показываю короткий бизнес-кейс: крупному B2B-клиенту ошибочно выставили оплату за модуль, который по договору должен быть бесплатным.  
У нас есть несколько разрозненных источников — brief, письмо клиента, заметки биллинга и CSV по событиям.  
Задача: собрать единый слой знаний, получить понятный клиентский summary и показать, как система дообучается одним новым сигналом."

---

## 3) Показ базы (без ответов)

### Что открыть

1. `outputs/business-fast-demo/raw/`
2. `outputs/business-fast-demo/wiki/index.md`
3. `outputs/business-fast-demo/wiki/cases/00_case_brief.md`

### Что сказать

"Слева сырье (`raw`), справа уже собранная wiki-база.  
Важно, что raw не редактируется вручную агентом — он только синтезирует wiki-слой."

"В `index.md` видно, что база структурирована и статьи уже связаны по кейсу."

---

## 4) Первый вопрос к базе (до нового файла)

### Команда

```bash
uv run python -u run_demo.py business-fast-demo --answer-only
```

### Что сказать

"Теперь на уже собранной базе формируем ответ и клиентский summary."

### Что открыть после команды

- `outputs/business-fast-demo/wiki/incident-summary.md`
- `outputs/business-fast-demo/reports/final_incident_summary.md`

### На что смотреть / что подчеркнуть

- Есть структура: что случилось / причины / что исправили / что дальше
- Ответ опирается на wiki-материалы, а не на абстрактный шаблон

### Что сказать

"Это версия ответа на текущем наборе данных. Теперь добавим новый факт и посмотрим, как изменится результат."

---

## 5) Добавление нового файла вручную (инкремент)

### Команда (вставить новый файл в workspace raw)

```bash
cp corpora/business-fast-demo/raw/05_additional_followup_signal.md \
  outputs/business-fast-demo/raw/05_additional_followup_signal.md
```

### Что открыть

- `outputs/business-fast-demo/raw/05_additional_followup_signal.md`

### Что сказать

"Сейчас я вручную добавляю новый источник в raw.  
Это типичный production-сценарий: появился новый сигнал после первичного разбора."

---

## 6) Доинжест только нового файла + пересборка ответа

### Рекомендуемая команда (one-shot)

```bash
scripts/demo_last_step.sh --ingest-file raw/05_additional_followup_signal.md
```

Что делает скрипт:

1. доинжестит только этот файл;
2. сбрасывает только `query/lint` в `.progress`;
3. запускает `--answer-only`.

### Что сказать

"Я не пересобираю всё с нуля.  
Обрабатывается только новый файл, затем пересобирается ответный слой."

---

## 7) Показ "до/после"

### Что открыть

- `outputs/business-fast-demo/wiki/incident-summary.md`
- `outputs/business-fast-demo/reports/final_incident_summary.md`

### Что сказать

"Теперь в ответе учтен дополнительный сигнал из нового файла: обновились риски и действия.  
То есть база действительно инкрементально обогащается, а не просто генерирует статический шаблон."

---

## 8) Короткое завершение (20 секунд)

### Что сказать (готовый текст)

"Итог: у нас быстрый и прозрачный цикл.  
Сначала строим wiki-базу из первичных источников, затем получаем бизнес-ответы, затем добавляем новые факты и обновляем только нужную часть пайплайна.  
Это снижает стоимость повторных прогонов и делает демонстрацию/эксплуатацию предсказуемой."

---

## Команды-шпаргалка (все вместе)

```bash
# 1) clean + base build
rm -rf outputs/business-fast-demo
uv run python -u run_demo.py business-fast-demo --build-only

# 2) first answers
uv run python -u run_demo.py business-fast-demo --answer-only

# 3) add new raw file manually
cp corpora/business-fast-demo/raw/05_additional_followup_signal.md \
  outputs/business-fast-demo/raw/05_additional_followup_signal.md

# 4) ingest only new file + refresh answers
scripts/demo_last_step.sh --ingest-file raw/05_additional_followup_signal.md
```

---

## Если что-то пошло не так (быстрый recovery)

### Симптом: `--answer-only` пишет `SKIP (already done)`

Решение:

используй скрипт:

```bash
scripts/demo_last_step.sh
```

Он сам сбросит только query/lint метки.

### Симптом: хочется начать заново

```bash
rm -rf outputs/business-fast-demo
uv run python -u run_demo.py business-fast-demo --build-only
```

---

## Мини-чеклист ведущего (перед шарингом экрана)

- Открыт терминал в корне проекта
- Открыт `outputs/business-fast-demo` в файловом дереве/Obsidian
- Под рукой этот файл `DEMO_PLAYBOOK.md`
- Проверено, что команда `scripts/demo_last_step.sh --help` работает
