# Expected wiki shape

A strong demo result should look roughly like this:

```text
wiki/
  index.md
  log.md
  overview.md

  concepts/
    merchant-based-categorization.md
    purpose-based-categorization.md
    personal-spending-rules.md
    confidence-and-review.md
    privacy-boundary.md

  categories/
    home-food.md
    workday-meals.md
    social-events.md
    home-and-household.md
    pet-care.md
    personal-care.md
    health.md
    transport.md
    learning.md
    gifts.md
    subscriptions.md
    other.md

  merchants/
    supermarkets.md
    cafes-and-delivery.md
    pharmacies.md
    marketplaces.md
    transport-services.md

  rules/
    priority-order.md
    supermarket-rules.md
    pharmacy-rules.md
    marketplace-rules.md
    workday-meal-rules.md
    review-rules.md

  transactions/
    reclassified-transactions.md
    needs-review.md
    unchanged-transactions.md

  contradictions/
    merchant-first-vs-purpose-first.md

  risks/
    privacy-leakage.md
    over-personalization.md
    wrong-confident-classification.md
    prompt-injection-in-raw-source.md

  answers/
    improved-categorization-recommendation.md

  claims/
    claims.jsonl

reports/
  final_recommendation.md

exports/
  recategorized_transactions.csv
  category_rules.json
  llms.txt
```
