"""Graph queries for documentation generation.

Uses direct Kuzu queries to get ALL facts from the graph,
then categorizes them by documentation section.
No more semantic search dependency — works across all projects.
"""

import re
from dataclasses import dataclass, field

import kuzu

from deepdoc.graph.kuzu_patch import patch_kuzu_fts

patch_kuzu_fts()


@dataclass
class QueryResult:
    """Result from a graph query with evidence."""

    section: str
    facts: list[str] = field(default_factory=list)


# Keywords for categorizing facts into documentation sections
CATEGORY_PATTERNS: dict[str, list[str]] = {
    "routing": [
        r"route", r"router", r"prefix", r"endpoint",
        r"global.?prefix", r"@Controller", r"GET|POST|PUT|DELETE|PATCH",
        r"registers.*child", r"registers.*route",
    ],
    "database": [
        r"database", r"TypeOrm", r"connection", r"repository",
        r"entity", r"replication", r"master", r"slave",
    ],
    "auth": [
        r"guard", r"auth", r"jwt", r"token", r"login",
        r"permission", r"api.?key", r"cookie", r"Bearer",
        r"password", r"social.?login", r"guest.?login",
    ],
    "business_rules": [
        r"exception", r"thrown", r"throw", r"assert",
        r"valid", r"expired", r"condition", r"check",
        r"status", r"spec", r"rule", r"usable",
        r"if.*then", r"must", r"require",
    ],
    "queues": [
        r"queue", r"bull", r"job", r"process",
        r"background", r"async",
    ],
    "configuration": [
        r"config", r"port", r"timeout", r"limit",
        r"secret", r"env", r"constant", r"setting",
        r"url", r"prefix.*path",
    ],
    "modules": [
        r"module", r"import", r"export", r"provide",
        r"controller", r"service",
    ],
    "dependencies": [
        r"package", r"version", r"dependency", r"library",
        r"npm", r"install",
    ],
}


def _categorize_fact(fact: str) -> list[str]:
    """Categorize a fact into one or more documentation sections."""
    categories = []
    fact_lower = fact.lower()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, fact_lower):
                categories.append(category)
                break
    return categories if categories else ["other"]


def get_all_facts_from_graph(graph_path: str) -> list[tuple[str, str, str]]:
    """Get ALL facts (edges) from the Kuzu graph via direct query.

    Returns list of (source_name, fact, target_name) tuples.
    """
    from graphiti_core.driver.kuzu_driver import KuzuDriver

    driver = KuzuDriver(db=graph_path)
    conn = kuzu.Connection(driver.db)

    facts = []

    # Get all edges via RelatesToNode_ (Kuzu's edge representation)
    result = conn.execute(
        "MATCH (n:Entity)-[:RELATES_TO]->(r:RelatesToNode_)-[:RELATES_TO]->(m:Entity) "
        "RETURN n.name, r.fact, m.name"
    )
    while result.has_next():
        row = result.get_next()
        facts.append((row[0], row[1], row[2]))

    conn.close()
    return facts


def get_all_nodes_from_graph(graph_path: str) -> list[dict]:
    """Get ALL entity nodes from the graph."""
    from graphiti_core.driver.kuzu_driver import KuzuDriver

    driver = KuzuDriver(db=graph_path)
    conn = kuzu.Connection(driver.db)

    nodes = []
    result = conn.execute(
        "MATCH (n:Entity) RETURN n.name, n.summary, n.labels"
    )
    while result.has_next():
        row = result.get_next()
        nodes.append({
            "name": row[0],
            "summary": row[1] or "",
            "labels": row[2] or [],
        })

    conn.close()
    return nodes


def run_all_queries(graph_path: str) -> dict[str, QueryResult]:
    """Get all facts from graph and categorize into documentation sections.

    This replaces the old semantic-search approach.
    Works across ALL projects without project-specific keywords.
    """
    raw_facts = get_all_facts_from_graph(graph_path)

    # Deduplicate facts
    seen = set()
    unique_facts = []
    for source, fact, target in raw_facts:
        if fact not in seen:
            seen.add(fact)
            unique_facts.append(fact)

    # Categorize
    results: dict[str, QueryResult] = {}
    for section in CATEGORY_PATTERNS:
        results[section] = QueryResult(section=section)

    for fact in unique_facts:
        categories = _categorize_fact(fact)
        for cat in categories:
            if cat in results:
                results[cat].facts.append(fact)

    return results
