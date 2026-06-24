# LLM Wiki Fast Business Demo

Один минимальный, быстрый и понятный демо-сценарий:

1. построить wiki-базу из 5 источников;
2. показать ответ на вопрос по базе;
3. добавить вручную 1 новый файл;
4. доинжестить только его;
5. снова задать вопрос и показать более релевантный ответ.

Проект намеренно упрощен под живую демонстрацию.

## Что в проекте осталось

Один корпус:

- `corpora/business-fast-demo`

Один раннер:

- `run_demo.py`

Ключевые служебные файлы:

- `skills/karpathy-llm-wiki/SKILL.md`
- `AGENTS.md`
- `tools/wiki_lint.py`

## Кейс (для рассказа на демо)

B2B-клиент получил неверный счет: в нем ошибочно выставили плату за модуль, который по допсоглашению должен быть бесплатным первые 3 месяца.

Цель:

- быстро собрать единую базу знаний по инциденту;
- получить понятный summary для бизнеса;
- показать, как новая информация сразу улучшает базу и ответы.

## Источники в корпусе

### Базовые (входят в initial build)

- `raw/00_case_brief.md`
- `raw/01_customer_complaint_email.md`
- `raw/02_billing_team_notes.md`
- `raw/data/03_invoice_events.csv`
- `raw/data/04_ticket_history.csv`

### Дополнительный (для шага "добавим новый файл")

- `raw/05_additional_followup_signal.md`

Важно: при `--build-only` раннер копирует в workspace только базовые 5 файлов из `sources` в `run_demo.py`.
Дополнительный файл не попадает в `outputs/.../raw` автоматически.

## Команды, которые тебе нужны

## 0) Подготовить чистую базу

```bash
rm -rf outputs/business-fast-demo
```

## 1) Построить базу (только базовые источники)

```bash
export PHOENIX_PROJECT_NAME="llm-wiki-demo-business-fast-demo"
uv run python -u run_demo.py business-fast-demo --build-only
```

Что получится:

- `outputs/business-fast-demo/raw/` — только 5 базовых источников
- `outputs/business-fast-demo/wiki/` — собранные статьи
- без финальных answer/report шагов
- при запущенном Arize Phoenix: traces сохраняются в проект `llm-wiki-demo-business-fast-demo`

## 2) На демо показать “база уже есть”

Открыть в Obsidian vault:

- `outputs/business-fast-demo`

Показать файлы:

- `outputs/business-fast-demo/raw/` (5 источников)
- `outputs/business-fast-demo/wiki/index.md`
- `outputs/business-fast-demo/wiki/cases/00_case_brief.md`
- `outputs/business-fast-demo/wiki/cases/ticket_history.md`

## 3) Получить первый ответ по текущей базе

```bash
uv run python -u run_demo.py business-fast-demo --answer-only
```

Показать:

- `outputs/business-fast-demo/wiki/incident-summary.md`
- `outputs/business-fast-demo/reports/final_incident_summary.md`

## 4) Ручками добавить новый файл в raw

Скопировать подготовленный дополнительный источник в workspace:

```bash
cp corpora/business-fast-demo/raw/05_additional_followup_signal.md \
  outputs/business-fast-demo/raw/05_additional_followup_signal.md
```

Показать, что новый файл появился:

- `outputs/business-fast-demo/raw/05_additional_followup_signal.md`

## 5) Доинжестить только этот новый файл (без полного прогона)

```bash
uv run python -u run_demo.py business-fast-demo --ingest-file raw/05_additional_followup_signal.md
```

Это точечный режим: обрабатывается только указанный raw-файл.

## 6) Снова получить ответ после дообогащения

```bash
uv run python -u run_demo.py business-fast-demo --answer-only
```

Сравнить “до/после”:

- `outputs/business-fast-demo/wiki/incident-summary.md`
- `outputs/business-fast-demo/reports/final_incident_summary.md`

Ожидание: ответ учитывает новый сигнал и обновленные действия/риски.

### Удобный one-command вариант для последнего шага

Чтобы не чистить `.progress` руками на демо, используй:

```bash
scripts/demo_last_step.sh --ingest-file raw/05_additional_followup_signal.md
```

Скрипт сам:

1) доинжестит только указанный файл,  
2) сбросит только `query:*` и `lint` в `.progress`,  
3) запустит `--answer-only`.

## Полный сценарий демо (короткий текст для проговаривания)

1. "У нас есть 5 исходников по инциденту, на них строится рабочая wiki-база."
2. "Сейчас покажу, как из базы автоматически получается бизнес-summary."
3. "Теперь вручную добавляю новый факт в raw."
4. "Доинжестим только этот файл, без полного пересчета."
5. "Снова задаем вопрос — ответ стал более полным за счет нового источника."

## Полезные проверки

Проверка структуры:

```bash
uv run python tools/wiki_lint.py --workspace outputs/business-fast-demo
```

Автофикс детерминированных проблем:

```bash
uv run python tools/wiki_lint.py --workspace outputs/business-fast-demo --fix
```

## Почему это работает стабильно

В раннере включено:

- жесткое ограничение путей (писать только в `wiki/`, `reports/`, `exports/`);
- авто-ремонт workspace, если модель пишет в неожиданные директории;
- прогресс-файл `.progress` без дублей;
- ретраи при временных сетевых ошибках.
