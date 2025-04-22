.....coming soon!

## Agents
- FetchAgent → pulls new issues, uses function calling
- ClassifyAgent→ reads issues, runs RAG, emits (issue, tags)
- EvaluatorAgent -> evaluates the label to see if it's okay using a different model
- LabelAgent → reads (issue, tags) and calls GitHub