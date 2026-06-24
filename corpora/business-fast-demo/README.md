# business-fast-demo

Минимальный бизнес-кейс для быстрого и стабильного демо.

## Что внутри

- 5 файлов для базового построения wiki:
  - `raw/00_case_brief.md`
  - `raw/01_customer_complaint_email.md`
  - `raw/02_billing_team_notes.md`
  - `raw/data/03_invoice_events.csv`
  - `raw/data/04_ticket_history.csv`
- 1 дополнительный файл для второго шага демо:
  - `raw/05_additional_followup_signal.md`

## Режим демо

1. Базовое построение (без дополнительного файла):
   - `uv run python -u run_demo.py business-fast-demo --build-only`
2. Затем отдельно можно показать incremental ingest:
   - добавить `raw/05_additional_followup_signal.md` вручную через отдельный шаг/промпт.
