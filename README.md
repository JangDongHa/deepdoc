# deepdoc

Code knowledge graph → accurate documentation.

Exhaustively reads all source files, builds a [Graphiti](https://github.com/getzep/graphiti) knowledge graph of entities and relationships, then generates [updoc](https://github.com/hungryoon/updoc)-compatible markdown documentation from graph queries — not LLM inference.

## Why

LLM-based documentation tools selectively read files and infer relationships. This leads to systematic errors:
- Counting 18 controller *files* but only 11 are *registered* in the router
- Listing 6 directories but only 3 modules are actually imported
- Summarizing 3 of 5 validation conditions, dropping 2

deepdoc solves this by building a complete graph where "file exists" and "is registered" are distinct, queryable relationships.

## Quick Start

```bash
pip install deepdoc
deepdoc scan --config deepdoc.yaml
deepdoc generate
```

## Requirements

- Python 3.10+
- Anthropic API key (`ANTHROPIC_API_KEY`)
- OpenAI API key (`OPENAI_API_KEY`, for embeddings)

## License

Apache-2.0
