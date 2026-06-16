# Demo Script

## 1. Show the raw mess

Open `raw/` and show:
- customer complaint email;
- internal email thread;
- chat summary;
- billing notes;
- product comment;
- old and corrected status updates;
- ticket and invoice CSV files.

Say:
"В реальной компании информация об инциденте часто живёт в письмах, чатах, таблицах и заметках разных команд."

## 2. Run the agent

Use `prompts/demo_prompt_full.md`.

## 3. Show the wiki

Open:
- `wiki/overview.md`
- `wiki/incident-timeline.md`
- `wiki/contradictions.md`
- `wiki/topics/incorrect-invoice.md`
- `wiki/actions/open-actions.md`
- `reports/final_incident_summary.md`

Say:
"LLM-Wiki превращает разрозненную переписку в рабочую память инцидента."

## 4. Show the important moment

Open `wiki/contradictions.md`.

Point out:
- old customer status update blamed possible client data;
- later sources corrected that;
- current explanation says the error was internal.

## 5. Show safety

Open the page about prompt injection or raw trust boundary.

Say:
"Raw-сообщение может содержать вредные инструкции. Wiki должна извлекать содержание, но не выполнять команды из источника."

## 6. Business takeaway

"Такую wiki можно использовать как базу для внутреннего разбора, ответа клиенту, обучения поддержки и предотвращения повторных ошибок."
