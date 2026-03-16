<div align="center">

[English](README.md) | [한국어](README.ko.md)

# deepdoc

**Code knowledge graph → accurate documentation.**

Exhaustively reads source code, builds a knowledge graph of entities and relationships,
then generates documentation from graph queries — not LLM inference.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

</div>

---

## Problem

LLM-based documentation tools read files **selectively** and **infer** relationships. This leads to systematic, hard-to-detect errors:

| Error Pattern | Example | Root Cause |
|---------------|---------|------------|
| **File count ≠ registration count** | "18 controllers" when only 11 are registered in the router | Glob counts files, LLM equates existence with registration |
| **Directory ≠ active module** | "5 ext modules" when only 3 are imported | Directory exists ≠ module is wired |
| **Summarization loss** | Reports 3 of 5 validation conditions | LLM drops "similar-looking" conditions |
| **Proximity bias** | "12 business days" when code says `subDays(12)` (calendar days) | Adjacent function `subBusinessDaysWithHolidays` causes confusion |
| **Spec-as-fact** | Documents planned features as implemented | Memory/spec documents leak into context |

These are not random mistakes — they are **structural failure modes** of LLM inference on code. No amount of prompt engineering reliably prevents them because the LLM doesn't know it's wrong.

## Solution

deepdoc takes a fundamentally different approach:

```
                          ┌─────────────────────────────┐
   Source Code            │   Knowledge Graph (Kuzu)    │         Documentation
                          │                             │
   *.module.ts    ──scan──▶  Module ──registers_in──▶ Route    ──generate──▶  overview.md
   *.controller.ts         Controller ──defines──▶ Endpoint                  architecture.md
   *.spec.ts               Spec ──validates_with──▶ Condition                policies.md
   *.service.ts            Service ──injects──▶ Repository                   features.md
                          │                             │
                          └─────────────────────────────┘
```

1. **Exhaustive scan** — reads every source file, not a selective sample
2. **Structured extraction** — entities and relationships stored as graph nodes and edges
3. **Query, don't infer** — documentation generated from graph queries, not LLM reasoning
4. **"File exists" ≠ "is registered"** — these are distinct, queryable relationships in the graph

## Architecture

```
deepdoc/
├── scanner/                    # Phase 1: Code → Graph
│   ├── file_classifier.py      # Classify files by type, determine scan order
│   ├── episode_builder.py      # Convert files to Graphiti episodes
│   └── frameworks/
│       └── nestjs.py           # NestJS-specific extraction hints
│
├── graph/                      # Knowledge Graph
│   ├── client.py               # Graphiti + Kuzu initialization
│   ├── queries.py              # Predefined queries per doc section
│   ├── local_embedder.py       # Local code embeddings (no API key)
│   └── kuzu_patch.py           # FTS index fix for Kuzu driver
│
├── schema/                     # Graph Ontology
│   ├── entities.py             # 18 node types (Module, Controller, Guard, ...)
│   └── edges.py                # 20 edge types (imports, registers, validates, ...)
│
├── generator/                  # Phase 2: Graph → Docs
│   ├── generator.py            # Query graph, render markdown
│   └── updoc_compat.py         # Frontmatter, marker blocks
│
└── verifier/                   # Phase 3: Verify
    └── verifier.py             # Check evidence citations against graph
```

### Scan Pipeline

Files are classified by type and scanned in **dependency order** (leaves first, root last):

```
config → entity → dto → spec → repository → service → guard → controller → module → app.module → main.ts
```

This ensures that when a module file is processed, all its dependencies already exist in the graph, improving relationship extraction accuracy.

### Module Enrichment

For `*.module.ts` files, deepdoc attaches summaries of imported modules to the episode. This gives the LLM enough context to distinguish:

- `@Module({ imports: [AuthModule] })` → **imports** relationship
- `RouterModule.register([{ children: [AuthModule] }])` → **registers_in_router** relationship

Without enrichment, the LLM can't tell these apart from the module file alone.

### Extraction Instructions

Each file type gets framework-specific instructions that tell the LLM **what to extract and how to distinguish relationships**:

| File Type | Key Instructions |
|-----------|-----------------|
| Module | Distinguish `imports` vs `RouterModule.register` children — these are separate relationships |
| Controller | Extract route prefix, HTTP methods, guards, permission decorators |
| Spec | List ALL validation conditions in code order — never summarize or merge |
| Service | Extract DI, transactions, queue operations |

### Graph Schema

**Nodes (18 types):**
Module, Controller, Service, Repository, Guard, Entity, DTO, Spec, Config, RoutePrefix, Queue, DatabaseConnection, ExternalPackage, Function, Middleware, Interceptor, Filter, Pipe, Decorator

**Edges (20 types):**
imports_module, registers_in_router, exports_module, provides, injects, uses_guard, connects_to_db, registers_entity, defines_route, calls, validates_with, queues_job, handles_job, ...

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key (for LLM entity extraction via `gpt-4o-mini`)

```bash
# Embeddings run locally — no additional API key needed
```

### Install

```bash
git clone https://github.com/JangDongHa/deepdoc.git
cd deepdoc
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Configure

```yaml
# deepdoc.yaml
version: "0.1.0"

project:
  name: my-api
  path: /path/to/my-api
  language: typescript
  framework: nestjs

graph:
  path: .deepdoc/graph

llm:
  provider: openai
  model: gpt-4o-mini
  embedding_provider: local
  embedding_model: jinaai/jina-embeddings-v2-base-code

scan:
  include:
    - "src/**/*.ts"
  exclude:
    - "**/*.e2e.spec.ts"
    - "**/node_modules/**"
    - "**/dist/**"

output:
  path: ./docs
  format: updoc
  language: ko
```

### Run

```bash
export OPENAI_API_KEY="sk-..."

# Step 1: Build knowledge graph
deepdoc scan

# Step 2: Generate documentation
deepdoc generate

# Optional: Query the graph
deepdoc query "which modules are registered in the /partner router?"

# Optional: Verify existing docs
deepdoc verify docs/wiki/my-api/policies.md
```

## Commands

### `deepdoc scan`

Exhaustively scans the project and builds the knowledge graph.

```bash
deepdoc scan                          # Use deepdoc.yaml in current directory
deepdoc scan --config path/to.yaml    # Specify config file
deepdoc scan --project /other/path    # Override project path
```

**What happens:**
1. Discovers all files matching `scan.include` patterns
2. Classifies each file by type (module, controller, spec, etc.)
3. Sorts by dependency order (leaves → root)
4. Builds Graphiti episodes with framework-specific extraction instructions
5. Ingests episodes into Kuzu graph database

**Output:** `.deepdoc/graph` — embedded Kuzu database file

### `deepdoc generate`

Generates documentation from the knowledge graph.

```bash
deepdoc generate                      # Use deepdoc.yaml
deepdoc generate --output ./my-docs   # Override output directory
```

**Output (9 files, updoc-compatible):**
```
docs/
├── index.md
├── projects/{name}/
│   ├── overview.md          # Routing, DB, queues — with synced_from/synced_at
│   ├── architecture.md      # Module structure, controllers, endpoints
│   ├── configuration.md     # Env vars, constants, secrets
│   └── dependencies.md      # Packages, versions
└── wiki/{name}/
    ├── index.md             # Service overview
    ├── features.md          # Capabilities, background jobs
    ├── access.md            # Auth guards, API keys, endpoints
    └── policies.md          # Business rules, validation conditions
```

All content inside `<!-- updoc:begin -->` / `<!-- updoc:end -->` markers. User content outside markers is preserved on re-generation.

### `deepdoc query`

Natural language search over the knowledge graph.

```bash
deepdoc query "which guards protect settlement endpoints?"
deepdoc query "what exceptions does PartnerTicketSpec throw?"
deepdoc query "show all database connections"
```

### `deepdoc verify`

Verify evidence citations in existing documentation against the graph.

```bash
deepdoc verify docs/wiki/my-api/policies.md
```

Parses `<!-- evidence: file:function snippet -->` comments and checks each against the graph.

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Graph Engine** | [Graphiti](https://github.com/getzep/graphiti) | Temporal knowledge graph with LLM-based entity extraction |
| **Graph DB** | [Kuzu](https://kuzudb.com) (embedded) | No server needed, pip-installable, fast local queries |
| **LLM** | OpenAI gpt-4o-mini | Entity/relationship extraction from code (configurable) |
| **Embeddings** | [jina-embeddings-v2-base-code](https://huggingface.co/jinaai/jina-embeddings-v2-base-code) via [FastEmbed](https://github.com/qdrant/fastembed) | Local execution, code-optimized, no API key |
| **CLI** | [Click](https://click.palletsprojects.com) + [Rich](https://rich.readthedocs.io) | Clean interface with progress display |
| **Output** | [updoc](https://github.com/hungryoon/updoc)-compatible markdown | Frontmatter, marker blocks, evidence citations |

## Verified Results

Tested on a real-world NestJS project (modu-api-partner, 200+ files):

| Metric | LLM-only (updoc) | deepdoc |
|--------|-------------------|---------|
| ext routing modules | 5 (wrong — counted directories) | **3 (correct — counted registrations)** |
| Ticket extension conditions | 3/5 (dropped 2) | **5/5 (all extracted)** |
| `subDays` vs `subBusinessDays` | Confused (called it "12 business days") | **Separate facts in graph** |
| Unimplemented spec features | Included (from memory/specs) | **Excluded (code-only source)** |
| `/partner` route modules | 18 (counted controller files) | **10/11 (counted router registrations)** |

## Known Limitations

- **Scan speed**: ~30 seconds per file (4-10 LLM calls per episode via Graphiti). A 200-file project takes ~30 minutes. Future: replace structural extraction with AST parsing, use LLM only for semantic understanding.
- **Large files**: Files over 20KB (e.g., `app.module.ts` at 24KB) may have extraction gaps. The LLM can miss items in long lists. Future: episode chunking.
- **NestJS only**: Currently targets NestJS/TypeScript projects. The `scanner/frameworks/` directory is designed for extension (Spring, FastAPI, etc.) but only `nestjs.py` is implemented.
- **Kuzu FTS bug**: graphiti-core's Kuzu driver doesn't create FTS indexes. deepdoc includes a monkey-patch (`kuzu_patch.py`) that adds them.

## Roadmap

- [ ] **AST-based structural extraction** — Replace LLM calls for imports/modules/routing with TypeScript AST parsing. Keep LLM only for business rules.
- [ ] **Incremental scan** — Only re-scan changed files since last commit.
- [ ] **Prose generation layer** — Current output is fact-list format. Add LLM pass to generate readable prose from graph facts.
- [ ] **Framework plugins** — Spring Boot, FastAPI, Express support.
- [ ] **Interactive review** — Present key facts for user confirmation before generating docs.

## Origin Story

deepdoc was born from a documentation accuracy experiment. We used [updoc](https://github.com/hungryoon/updoc) to document a NestJS project, then systematically verified the output against source code. Four categories of errors emerged — all caused by LLM inference over selectively-read files. Prompt engineering (Source Fencing, Evidence Citation, Exhaustive Enumeration) fixed some but not all. The remaining errors required a structural solution: read everything, store relationships explicitly, query instead of infer.

The full analysis is documented in:
- `review.md` — Error patterns with code evidence
- `improvement.md` — Prompt-level mitigations and their limits

## License

Apache-2.0
