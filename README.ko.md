<div align="center">

# deepdoc

[English](README.md) | [한국어](README.ko.md)

**코드 지식 그래프 → 정확한 문서 생성**

소스코드를 빠짐없이 읽고, 엔티티와 관계를 지식 그래프에 저장한 뒤,
그래프 쿼리로 문서를 생성합니다 — LLM 추론이 아닌 조회.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

</div>

---

## 문제

LLM 기반 문서화 도구는 파일을 **선택적으로** 읽고 관계를 **추론**합니다. 이로 인해 체계적이고 발견하기 어려운 오류가 발생합니다:

| 오류 패턴 | 예시 | 원인 |
|-----------|------|------|
| **파일 수 ≠ 등록 수** | 라우터에 11개만 등록됐는데 "컨트롤러 18개" | 파일 존재와 런타임 등록을 동일시 |
| **디렉토리 ≠ 활성 모듈** | 3개만 import됐는데 "ext 모듈 5개" | 디렉토리 존재 ≠ 모듈 연결 |
| **요약 시 탈락** | 5개 검증 조건 중 3개만 기술 | LLM이 "비슷해 보이는" 조건을 병합 |
| **인접 코드 착각** | `subDays(12)`인데 "12영업일" | 옆의 `subBusinessDaysWithHolidays`에 영향 |
| **스펙을 사실로** | 미구현 기능을 구현된 것으로 기술 | 메모리/기획 문서가 컨텍스트에 유입 |

이것들은 랜덤한 실수가 아니라, 코드에 대한 LLM 추론의 **구조적 실패 패턴**입니다. LLM이 자신이 틀렸는지 모르기 때문에 프롬프트 엔지니어링으로는 안정적으로 방지할 수 없습니다.

## 해결

deepdoc은 근본적으로 다른 접근을 취합니다:

```
                          ┌─────────────────────────────┐
   소스코드                │   지식 그래프 (Kuzu)         │         문서
                          │                             │
   *.module.ts    ──scan──▶  Module ──registers_in──▶ Route    ──generate──▶  overview.md
   *.controller.ts         Controller ──defines──▶ Endpoint                  architecture.md
   *.spec.ts               Spec ──validates_with──▶ Condition                policies.md
   *.service.ts            Service ──injects──▶ Repository                   features.md
                          │                             │
                          └─────────────────────────────┘
```

1. **전수 스캔** — 모든 소스 파일을 빠짐없이 읽습니다
2. **구조화된 추출** — 엔티티와 관계를 그래프 노드와 엣지로 저장합니다
3. **추론 대신 조회** — 그래프 쿼리로 문서를 생성합니다
4. **"파일 존재" ≠ "등록됨"** — 이 둘은 그래프에서 별개의 조회 가능한 관계입니다

## 아키텍처

```
deepdoc/
├── scanner/                    # 1단계: 코드 → 그래프
│   ├── file_classifier.py      # 파일 분류, 스캔 순서 결정
│   ├── episode_builder.py      # 파일 → Graphiti 에피소드 변환
│   └── frameworks/
│       └── nestjs.py           # NestJS 특화 추출 힌트
│
├── graph/                      # 지식 그래프
│   ├── client.py               # Graphiti + Kuzu 초기화
│   ├── queries.py              # 문서 섹션별 사전 정의 쿼리
│   ├── local_embedder.py       # 로컬 코드 임베딩 (API 키 불필요)
│   └── kuzu_patch.py           # Kuzu 드라이버 FTS 인덱스 패치
│
├── schema/                     # 그래프 온톨로지
│   ├── entities.py             # 18종 노드 타입 (Module, Controller, Guard, ...)
│   └── edges.py                # 20종 엣지 타입 (imports, registers, validates, ...)
│
├── generator/                  # 2단계: 그래프 → 문서
│   ├── generator.py            # 그래프 쿼리 → 마크다운 렌더링
│   └── updoc_compat.py         # 프론트매터, 마커 블록
│
└── verifier/                   # 3단계: 검증
    └── verifier.py             # evidence 인용을 그래프와 대조
```

### 스캔 파이프라인

파일을 타입별로 분류한 뒤 **의존성 순서**로 스캔합니다 (리프 먼저, 루트 마지막):

```
config → entity → dto → spec → repository → service → guard → controller → module → app.module → main.ts
```

모듈 파일 처리 시점에 모든 의존성이 이미 그래프에 존재하므로, 관계 추출 정확도가 올라갑니다.

### 모듈 Enrichment

`*.module.ts` 파일을 처리할 때, import된 모듈의 요약을 에피소드에 첨부합니다. 이를 통해 LLM이 다음을 구분할 수 있습니다:

- `@Module({ imports: [AuthModule] })` → **imports** 관계
- `RouterModule.register([{ children: [AuthModule] }])` → **registers_in_router** 관계

Enrichment 없이는 모듈 파일만으로는 이 둘을 구분할 수 없습니다.

### 추출 지시 (Extraction Instructions)

각 파일 타입에 프레임워크 특화 지시를 부여하여 **무엇을 추출하고 어떻게 관계를 구분할지** 안내합니다:

| 파일 타입 | 핵심 지시 |
|-----------|----------|
| Module | `imports`와 `RouterModule.register` children을 구분 — 별개의 관계 |
| Controller | 라우트 접두사, HTTP 메서드, 가드, 퍼미션 데코레이터 추출 |
| Spec | 모든 검증 조건을 코드 순서대로 전수 나열 — 요약/병합 금지 |
| Service | DI, 트랜잭션, 큐 작업 추출 |

### 그래프 스키마

**노드 (18종):**
Module, Controller, Service, Repository, Guard, Entity, DTO, Spec, Config, RoutePrefix, Queue, DatabaseConnection, ExternalPackage, Function, Middleware, Interceptor, Filter, Pipe, Decorator

**엣지 (20종):**
imports_module, registers_in_router, exports_module, provides, injects, uses_guard, connects_to_db, registers_entity, defines_route, calls, validates_with, queues_job, handles_job, ...

## 빠른 시작

### 사전 요구사항

- Python 3.10+
- OpenAI API 키 (`gpt-4o-mini`로 엔티티/관계 추출)

```bash
# 임베딩은 로컬 실행 — 추가 API 키 불필요
```

### 설치

```bash
git clone https://github.com/JangDongHa/deepdoc.git
cd deepdoc
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 설정

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

### 실행

```bash
export OPENAI_API_KEY="sk-..."

# 1단계: 지식 그래프 구축
deepdoc scan

# 2단계: 문서 생성
deepdoc generate

# 선택: 그래프에 질문
deepdoc query "어떤 모듈이 /partner 라우터에 등록됐어?"

# 선택: 기존 문서 검증
deepdoc verify docs/wiki/my-api/policies.md
```

## 명령어

### `deepdoc scan`

프로젝트를 전수 스캔하고 지식 그래프를 구축합니다.

```bash
deepdoc scan                          # 현재 디렉토리의 deepdoc.yaml 사용
deepdoc scan --config path/to.yaml    # 설정 파일 지정
deepdoc scan --project /other/path    # 프로젝트 경로 오버라이드
```

**동작 순서:**
1. `scan.include` 패턴에 매칭되는 파일 탐색
2. 파일별 타입 분류 (module, controller, spec 등)
3. 의존성 순서로 정렬 (리프 → 루트)
4. 프레임워크 특화 추출 지시와 함께 Graphiti 에피소드 생성
5. Kuzu 그래프 데이터베이스에 적재

**출력:** `.deepdoc/graph` — Kuzu 임베디드 데이터베이스

### `deepdoc generate`

지식 그래프에서 문서를 생성합니다.

```bash
deepdoc generate                      # deepdoc.yaml 사용
deepdoc generate --output ./my-docs   # 출력 경로 오버라이드
```

**출력 (9개 파일, updoc 호환):**
```
docs/
├── index.md
├── projects/{name}/
│   ├── overview.md          # 라우팅, DB, 큐 — synced_from/synced_at 포함
│   ├── architecture.md      # 모듈 구조, 컨트롤러, 엔드포인트
│   ├── configuration.md     # 환경 변수, 상수, 시크릿
│   └── dependencies.md      # 패키지, 버전
└── wiki/{name}/
    ├── index.md             # 서비스 개요
    ├── features.md          # 기능, 백그라운드 작업
    ├── access.md            # 인증 가드, API 키, 엔드포인트
    └── policies.md          # 비즈니스 규칙, 검증 조건
```

모든 콘텐츠는 `<!-- updoc:begin -->` / `<!-- updoc:end -->` 마커 안에 생성됩니다. 마커 밖의 사용자 콘텐츠는 재생성 시 보존됩니다.

### `deepdoc query`

지식 그래프를 자연어로 검색합니다.

```bash
deepdoc query "정산 엔드포인트를 어떤 가드가 보호해?"
deepdoc query "PartnerTicketSpec이 던지는 예외는?"
deepdoc query "데이터베이스 연결 목록"
```

### `deepdoc verify`

기존 문서의 evidence 인용을 그래프와 대조하여 검증합니다.

```bash
deepdoc verify docs/wiki/my-api/policies.md
```

`<!-- evidence: file:function snippet -->` 주석을 파싱하여 각각을 그래프에서 확인합니다.

## 기술 스택

| 구성요소 | 선택 | 이유 |
|----------|------|------|
| **그래프 엔진** | [Graphiti](https://github.com/getzep/graphiti) | LLM 기반 엔티티 추출이 가능한 시간적 지식 그래프 |
| **그래프 DB** | [Kuzu](https://kuzudb.com) (임베디드) | 서버 불필요, pip 설치 가능, 로컬 쿼리 빠름 |
| **LLM** | OpenAI gpt-4o-mini | 코드에서 엔티티/관계 추출 (변경 가능) |
| **임베딩** | [jina-embeddings-v2-base-code](https://huggingface.co/jinaai/jina-embeddings-v2-base-code) via [FastEmbed](https://github.com/qdrant/fastembed) | 로컬 실행, 코드 최적화, API 키 불필요 |
| **CLI** | [Click](https://click.palletsprojects.com) + [Rich](https://rich.readthedocs.io) | 진행 표시와 깔끔한 출력 |
| **출력** | [updoc](https://github.com/hungryoon/updoc) 호환 마크다운 | 프론트매터, 마커 블록, evidence 인용 |

## 검증 결과

실제 NestJS 프로젝트(modu-api-partner, 200+ 파일)로 테스트한 결과:

| 항목 | LLM 단독 (updoc) | deepdoc |
|------|-------------------|---------|
| ext 라우팅 모듈 | 5개 (오류 — 디렉토리 수 카운트) | **3개 (정확 — 등록 수 카운트)** |
| 주차권 연장 조건 | 3/5개 (2개 탈락) | **5/5개 (전부 추출)** |
| `subDays` vs `subBusinessDays` | 혼동 ("12영업일"로 기술) | **그래프에서 별도 fact** |
| 미구현 스펙 기능 | 포함 (메모리/스펙에서 유입) | **제외 (코드만 소스)** |
| `/partner` 라우트 모듈 | 18개 (컨트롤러 파일 수 카운트) | **10/11개 (라우터 등록 수 카운트)** |

## 알려진 제한사항

- **스캔 속도**: 파일당 ~30초 (Graphiti가 에피소드당 LLM을 4-10회 호출). 200파일 프로젝트는 ~30분. 향후: 구조적 추출을 AST 파싱으로 대체, LLM은 의미 이해에만 사용.
- **대용량 파일**: 20KB 이상 파일(예: 24KB `app.module.ts`)은 추출 누락 가능. LLM이 긴 목록에서 항목을 놓칠 수 있음. 향후: 에피소드 분할.
- **NestJS 한정**: 현재 NestJS/TypeScript 프로젝트만 지원. `scanner/frameworks/` 디렉토리가 확장 가능하게 설계되어 있지만(Spring, FastAPI 등) `nestjs.py`만 구현됨.
- **Kuzu FTS 버그**: graphiti-core의 Kuzu 드라이버가 FTS 인덱스를 생성하지 않음. deepdoc이 몽키패치(`kuzu_patch.py`)로 추가.

## 로드맵

- [ ] **AST 기반 구조 추출** — imports/modules/routing을 TypeScript AST 파서로 대체. LLM은 비즈니스 규칙에만 사용.
- [ ] **증분 스캔** — 마지막 커밋 이후 변경된 파일만 재스캔.
- [ ] **산문 생성 레이어** — 현재 fact 나열 형태. 그래프 fact에서 읽기 좋은 산문을 생성하는 LLM 패스 추가.
- [ ] **프레임워크 플러그인** — Spring Boot, FastAPI, Express 지원.
- [ ] **인터랙티브 검토** — 문서 생성 전 핵심 사실을 사용자에게 확인.

## 탄생 배경

deepdoc은 문서화 정확도 실험에서 탄생했습니다. [updoc](https://github.com/hungryoon/updoc)으로 NestJS 프로젝트를 문서화한 뒤, 생성된 결과를 소스코드와 체계적으로 검증했습니다. 4가지 오류 패턴이 발견되었고, 모두 선택적으로 읽은 파일에 대한 LLM 추론이 원인이었습니다.

프롬프트 엔지니어링(Source Fencing, Evidence Citation, Exhaustive Enumeration)으로 일부를 개선했지만 전부는 아니었습니다. 나머지 오류는 구조적 해결이 필요했습니다: 전부 읽고, 관계를 명시적으로 저장하고, 추론 대신 조회.

상세 분석:
- `review.md` — 코드 근거가 포함된 오류 패턴 분석
- `improvement.md` — 프롬프트 수준 개선안과 그 한계

## 라이선스

Apache-2.0
