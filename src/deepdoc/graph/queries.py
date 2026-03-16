"""Predefined graph queries for documentation generation.

Each query corresponds to a documentation section and returns
structured data that the generator renders into markdown.
"""

from dataclasses import dataclass


@dataclass
class QueryResult:
    """Result from a graph query with evidence."""

    section: str
    facts: list[str]
    raw_results: list[dict] | None = None


async def query_all_facts(graphiti) -> list[str]:
    """Get all facts (edges) from the graph."""
    results = await graphiti.search(
        "list all modules, controllers, services, routes, and relationships",
    )
    return [r.fact for r in results]


async def query_routing_structure(graphiti) -> QueryResult:
    """Query which modules are registered in which routes."""
    results = await graphiti.search(
        "RouterModule registers modules as child routes"
    )
    facts = [r.fact for r in results]

    # Also search for modules that are NOT in the router
    import_results = await graphiti.search(
        "module imports another module"
    )
    import_facts = [r.fact for r in import_results]

    return QueryResult(
        section="routing",
        facts=facts + import_facts,
    )


async def query_database_connections(graphiti) -> QueryResult:
    """Query database connections and their entities."""
    results = await graphiti.search(
        "TypeOrmModule database connection name entities"
    )
    return QueryResult(
        section="database",
        facts=[r.fact for r in results],
    )


async def query_controllers_and_routes(graphiti) -> QueryResult:
    """Query all controllers and their HTTP endpoints."""
    results = await graphiti.search(
        "controller defines route endpoint HTTP GET POST"
    )
    return QueryResult(
        section="controllers",
        facts=[r.fact for r in results],
    )


async def query_guards_and_auth(graphiti) -> QueryResult:
    """Query authentication guards and permission checks."""
    queries = [
        "guard authentication JWT permission authorization",
        "JwtAuthGuard Bearer token validate",
        "cookie httpOnly access_token refresh_token",
        "API key x-api-key header",
    ]
    all_facts = []
    seen = set()
    for q in queries:
        results = await graphiti.search(q)
        for r in results:
            if r.fact not in seen:
                seen.add(r.fact)
                all_facts.append(r.fact)
    return QueryResult(
        section="auth",
        facts=all_facts,
    )


async def query_business_rules(graphiti) -> QueryResult:
    """Query business rules and validation conditions."""
    queries = [
        "NotAbleExtendPartnerTicketException thrown validation condition",
        "PartnerTicket extension status USING subDays",
        "exception thrown if condition not met",
        "business rule validation assert check",
    ]
    all_facts = []
    seen = set()
    for q in queries:
        results = await graphiti.search(q)
        for r in results:
            if r.fact not in seen:
                seen.add(r.fact)
                all_facts.append(r.fact)
    return QueryResult(
        section="business_rules",
        facts=all_facts,
    )


async def query_dependencies(graphiti) -> QueryResult:
    """Query external packages and internal module dependencies."""
    results = await graphiti.search(
        "package dependency import external library"
    )
    return QueryResult(
        section="dependencies",
        facts=[r.fact for r in results],
    )


async def query_queues_and_jobs(graphiti) -> QueryResult:
    """Query Bull queues and background job processing."""
    results = await graphiti.search(
        "Bull queue job processing background"
    )
    return QueryResult(
        section="queues",
        facts=[r.fact for r in results],
    )


async def query_configuration(graphiti) -> QueryResult:
    """Query configuration, environment variables, and constants."""
    results = await graphiti.search(
        "configuration environment variable constant port timeout limit"
    )
    return QueryResult(
        section="configuration",
        facts=[r.fact for r in results],
    )


async def run_all_queries(graphiti) -> dict[str, QueryResult]:
    """Run all documentation queries and return results by section."""
    queries = {
        "routing": query_routing_structure,
        "database": query_database_connections,
        "controllers": query_controllers_and_routes,
        "auth": query_guards_and_auth,
        "business_rules": query_business_rules,
        "dependencies": query_dependencies,
        "queues": query_queues_and_jobs,
        "configuration": query_configuration,
    }

    results = {}
    for name, query_fn in queries.items():
        try:
            results[name] = await query_fn(graphiti)
        except Exception as e:
            results[name] = QueryResult(section=name, facts=[f"Query error: {e}"])

    return results
