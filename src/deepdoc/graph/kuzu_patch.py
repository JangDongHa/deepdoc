"""Monkey-patch for Kuzu driver FTS index bug in graphiti-core.

graphiti-core's Kuzu driver doesn't create FTS indexes in setup_schema(),
but search code tries to use QUERY_FTS_INDEX('Entity', 'node_name_and_summary').
This patch adds the missing FTS indexes after schema creation.
"""

import logging

logger = logging.getLogger(__name__)

FTS_INDEX_QUERIES = [
    "CALL CREATE_FTS_INDEX('Entity', 'node_name_and_summary', ['name', 'summary'])",
    "CALL CREATE_FTS_INDEX('RelatesToNode_', 'edge_name_and_fact', ['name', 'fact'])",
    "CALL CREATE_FTS_INDEX('Episodic', 'episode_content', ['content', 'name'])",
]


def patch_kuzu_fts():
    """Patch KuzuDriver.setup_schema to create FTS indexes."""
    from graphiti_core.driver.kuzu_driver import KuzuDriver
    import kuzu

    original_setup = KuzuDriver.setup_schema

    def patched_setup_schema(self):
        original_setup(self)

        conn = kuzu.Connection(self.db)
        for query in FTS_INDEX_QUERIES:
            try:
                conn.execute(query)
            except RuntimeError as e:
                if "already exists" in str(e).lower():
                    pass
                else:
                    logger.warning(f"FTS index creation warning: {e}")
        conn.close()
        logger.debug("Kuzu FTS indexes created successfully")

    KuzuDriver.setup_schema = patched_setup_schema
