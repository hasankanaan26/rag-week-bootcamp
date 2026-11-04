# Demo Question Bank

Organized by expected behavior. Use these during live demos.

## High Confidence (should work well)

| Question | Expected Source | Notes |
|----------|----------------|-------|
| "How many vacation days do I get?" | leave-policy.md | Classic RAG demo |
| "What is our Git branching strategy?" | coding-standards.md | |
| "Can I expense a standing desk?" | expense-policy.md | |
| "What are the core working hours?" | remote-work.md | |
| "What is our parental leave policy?" | leave-policy.md | |
| "How do I submit a leave request?" | leave-policy.md | |
| "What is our code review policy?" | coding-standards.md | |
| "What tools do we use for CI/CD?" | tech-stack.md | |

## Medium Confidence (vague or broad)

| Question | Notes |
|----------|-------|
| "What about time off?" | Vague — retrieves leave policy but with weaker match |
| "Tell me about the rules" | Too broad — matches many documents poorly |
| "What should new employees know?" | Broad — could match onboarding, FAQ, policies |

## No Result (out of domain)

| Question | Notes |
|----------|-------|
| "Tell me about quantum physics" | Nothing in the knowledge base |
| "What is the capital of France?" | General knowledge, not in docs |
| "How do I cook pasta?" | Completely unrelated |

## Failure Modes (tricky questions)

| Question | Failure Type | Why It Fails |
|----------|-------------|--------------|
| "Is the leave policy generous?" | Subjective | RAG retrieves facts but can't make value judgments |
| "What changed in the latest policy update?" | Temporal | Docs don't track change history |
| "Compare our benefits to Google's" | Cross-domain | RAG only knows Acme Corp data |
| "What is the maximum expense for a team dinner per person?" | Conflicting data | expense-policy.md says $50, the 2024 update says $75 |

## Semantic Search Demos (for /search and /embed)

### Synonym matching
Search for "vacation days", then "annual leave" — same chunks, different words.

### Embedding distance exploration
```json
{"texts": ["vacation days", "annual leave", "time off"]}
```
All three should be close (low distance).

```json
{"texts": ["vacation days", "annual leave", "Python programming"]}
```
First pair close, other pairs far apart.

### Question-answer matching
```json
{"texts": ["How many vacation days?", "Employees receive 20 days of annual leave"]}
```
Should be fairly close — this is why RAG works.
