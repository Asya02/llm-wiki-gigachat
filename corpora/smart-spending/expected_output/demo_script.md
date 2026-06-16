# Demo script

## 1. Show the problem

Open `raw/data/03_transactions_march.csv` and point out that many transactions are classified by merchant.

Example:

- Rimi with cake and candles is classified as `Еда`.
- Prisma with cat food is classified as `Еда`.
- Apotheka with shampoo is classified as `Здоровье`.
- Amazon with a book is classified as `Покупки`.

## 2. Run the agent

Give the agent `prompts/demo_prompt_full.md`.

## 3. Show the generated wiki

Open:

- `wiki/overview.md`
- `wiki/rules/priority-order.md`
- `wiki/transactions/reclassified-transactions.md`
- `wiki/transactions/needs-review.md`
- `wiki/contradictions/merchant-first-vs-purpose-first.md`
- `reports/final_recommendation.md`

## 4. Show the business value

The simple story:

> The bank should stop relying only on merchant type. It should use purpose-based rules, user corrections and confidence levels. Clear cases can be suggested automatically; unclear cases should ask for review.

## 5. Show the artifact

Open:

- `exports/recategorized_transactions.csv`
- `exports/category_rules.json`
- `exports/llms.txt`

This shows that the wiki is not only text. It can produce rules and structured output for a product team.
