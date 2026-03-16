"""Verify evidence citations in documentation against the knowledge graph."""

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from deepdoc.config import DeepDocConfig
from deepdoc.graph.client import create_graphiti_client, close_graphiti_client

console = Console()

EVIDENCE_PATTERN = re.compile(
    r"<!--\s*evidence:\s*(.+?)\s*-->"
)


@dataclass
class EvidenceCitation:
    """A parsed evidence citation from a markdown file."""

    raw: str
    file_ref: str
    detail: str
    line_number: int


@dataclass
class VerificationResult:
    """Result of verifying a single citation."""

    citation: EvidenceCitation
    status: str  # "confirmed", "unconfirmed", "contradicted"
    graph_facts: list[str]
    notes: str = ""


def parse_evidence_citations(doc_path: str) -> list[EvidenceCitation]:
    """Extract all evidence citations from a markdown document."""
    path = Path(doc_path)
    if not path.exists():
        return []

    citations = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for match in EVIDENCE_PATTERN.finditer(line):
            raw = match.group(1).strip()
            # Parse "file:function_or_line snippet"
            parts = raw.split(None, 1)
            file_ref = parts[0] if parts else raw
            detail = parts[1] if len(parts) > 1 else ""

            citations.append(
                EvidenceCitation(
                    raw=raw,
                    file_ref=file_ref,
                    detail=detail,
                    line_number=i,
                )
            )
    return citations


async def verify_document(config: DeepDocConfig, doc_path: str) -> list[VerificationResult]:
    """Verify all evidence citations in a document against the graph."""
    citations = parse_evidence_citations(doc_path)

    if not citations:
        console.print(f"[yellow]No evidence citations found in {doc_path}[/yellow]")
        return []

    console.print(f"Found [cyan]{len(citations)}[/cyan] evidence citations in {doc_path}")

    graphiti = await create_graphiti_client(config)
    results = []

    for citation in citations:
        # Search the graph for facts related to this citation
        search_query = f"{citation.file_ref} {citation.detail}"
        try:
            search_results = await graphiti.search(search_query)
            graph_facts = [r.fact for r in search_results]

            if graph_facts:
                status = "confirmed"
            else:
                status = "unconfirmed"

            results.append(
                VerificationResult(
                    citation=citation,
                    status=status,
                    graph_facts=graph_facts[:5],
                )
            )
        except Exception as e:
            results.append(
                VerificationResult(
                    citation=citation,
                    status="error",
                    graph_facts=[],
                    notes=str(e),
                )
            )

    await close_graphiti_client(graphiti)
    return results


def run_verify(config: DeepDocConfig, doc_path: str):
    """Run verification and print results."""
    results = asyncio.run(verify_document(config, doc_path))

    confirmed = sum(1 for r in results if r.status == "confirmed")
    unconfirmed = sum(1 for r in results if r.status == "unconfirmed")

    console.print(f"\n[bold]Verification Results[/bold]")
    console.print(f"  Confirmed: [green]{confirmed}[/green]")
    console.print(f"  Unconfirmed: [yellow]{unconfirmed}[/yellow]")

    for r in results:
        icon = "✅" if r.status == "confirmed" else "⚠️" if r.status == "unconfirmed" else "❌"
        console.print(f"\n  {icon} Line {r.citation.line_number}: {r.citation.raw}")
        if r.graph_facts:
            for fact in r.graph_facts[:3]:
                console.print(f"     → {fact}")
        elif r.status == "unconfirmed":
            console.print(f"     → No matching facts in graph")

    return results
