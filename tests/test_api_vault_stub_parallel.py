"""Tests for parallel (threaded) execution of connect() and gather().

Verifies that using workers > 1 produces identical results to the
default sequential path, and that edge cases around the workers param
behave correctly.
"""

from pathlib import Path

import pytest

from obsidiantools.api import Vault

# NOTE: run the tests from the project dir.
WKD = Path().cwd()
VAULT_STUB = WKD / "tests/vault-stub"
WORKERS = 4


# --- fixtures: sequential (reference) ---


@pytest.fixture
def vault_sequential():
    """Vault connected and gathered sequentially (the reference)."""
    return Vault(VAULT_STUB).connect().gather()


# --- fixtures: parallel ---


@pytest.fixture
def vault_parallel():
    """Vault connected and gathered with threads."""
    return Vault(VAULT_STUB).connect(workers=WORKERS).gather(workers=WORKERS)


# --- connect(): parallel vs sequential equivalence ---


class TestConnectParallel:
    """Verify that connect(workers=N) produces the same indexes as
    the sequential default."""

    def test_graph_nodes_match(self, vault_sequential, vault_parallel):
        assert set(vault_sequential.graph.nodes) == set(vault_parallel.graph.nodes)

    def test_graph_edges_match(self, vault_sequential, vault_parallel):
        assert set(vault_sequential.graph.edges) == set(vault_parallel.graph.edges)

    def test_wikilinks_index_match(self, vault_sequential, vault_parallel):
        assert vault_sequential.wikilinks_index == vault_parallel.wikilinks_index

    def test_unique_wikilinks_index_match(self, vault_sequential, vault_parallel):
        assert (
            vault_sequential.unique_wikilinks_index
            == vault_parallel.unique_wikilinks_index
        )

    def test_md_links_index_match(self, vault_sequential, vault_parallel):
        assert vault_sequential.md_links_index == vault_parallel.md_links_index

    def test_embedded_files_index_match(self, vault_sequential, vault_parallel):
        assert (
            vault_sequential.embedded_files_index
            == vault_parallel.embedded_files_index
        )

    def test_tags_index_match(self, vault_sequential, vault_parallel):
        assert vault_sequential.tags_index == vault_parallel.tags_index

    def test_math_index_match(self, vault_sequential, vault_parallel):
        assert vault_sequential.math_index == vault_parallel.math_index

    def test_front_matter_index_match(self, vault_sequential, vault_parallel):
        assert (
            vault_sequential.front_matter_index == vault_parallel.front_matter_index
        )

    def test_backlinks_index_match(self, vault_sequential, vault_parallel):
        # backlinks_index values are lists; order may differ with threading
        # so we compare as sets
        seq_backlinks = {
            k: set(v) for k, v in vault_sequential.backlinks_index.items()
        }
        par_backlinks = {
            k: set(v) for k, v in vault_parallel.backlinks_index.items()
        }
        assert seq_backlinks == par_backlinks

    def test_nonexistent_notes_match(self, vault_sequential, vault_parallel):
        assert set(vault_sequential.nonexistent_notes) == set(
            vault_parallel.nonexistent_notes
        )

    def test_isolated_notes_match(self, vault_sequential, vault_parallel):
        assert set(vault_sequential.isolated_notes) == set(
            vault_parallel.isolated_notes
        )

    def test_is_connected_flag(self, vault_parallel):
        assert vault_parallel.is_connected


# --- gather(): parallel vs sequential equivalence ---


class TestGatherParallel:
    """Verify that gather(workers=N) produces the same text indexes as
    the sequential default."""

    def test_source_text_index_match(self, vault_sequential, vault_parallel):
        assert vault_sequential.source_text_index == vault_parallel.source_text_index

    def test_readable_text_index_match(self, vault_sequential, vault_parallel):
        assert (
            vault_sequential.readable_text_index
            == vault_parallel.readable_text_index
        )

    def test_is_gathered_flag(self, vault_parallel):
        assert vault_parallel.is_gathered

    def test_all_files_in_source_text_index(self, vault_parallel):
        assert set(vault_parallel.md_file_index.keys()) == set(
            vault_parallel.source_text_index.keys()
        )

    def test_all_files_in_readable_text_index(self, vault_parallel):
        assert set(vault_parallel.md_file_index.keys()) == set(
            vault_parallel.readable_text_index.keys()
        )


# --- metadata equivalence ---


class TestMetadataParallel:
    """Verify that the note metadata DataFrame is identical regardless
    of sequential vs parallel processing."""

    def test_metadata_df_match(self, vault_sequential, vault_parallel):
        df_seq = vault_sequential.get_note_metadata()
        df_par = vault_parallel.get_note_metadata()
        # sort by index so order doesn't matter
        df_seq = df_seq.sort_index()
        df_par = df_par.sort_index()
        assert df_seq.equals(df_par)


# --- workers edge cases ---


class TestWorkersEdgeCases:
    """Verify that unusual values for workers behave correctly."""

    def test_workers_none_is_sequential(self, vault_sequential):
        """workers=None should behave identically to default."""
        v = Vault(VAULT_STUB).connect(workers=None).gather(workers=None)
        assert v.wikilinks_index == vault_sequential.wikilinks_index
        assert v.source_text_index == vault_sequential.source_text_index

    def test_workers_one_is_sequential(self, vault_sequential):
        """workers=1 should use the sequential path."""
        v = Vault(VAULT_STUB).connect(workers=1).gather(workers=1)
        assert v.wikilinks_index == vault_sequential.wikilinks_index
        assert v.source_text_index == vault_sequential.source_text_index

    def test_workers_zero_is_sequential(self, vault_sequential):
        """workers=0 (falsy) should fall back to sequential."""
        v = Vault(VAULT_STUB).connect(workers=0).gather(workers=0)
        assert v.wikilinks_index == vault_sequential.wikilinks_index
        assert v.source_text_index == vault_sequential.source_text_index

    def test_workers_large_number(self, vault_sequential):
        """workers much larger than file count should still work."""
        v = Vault(VAULT_STUB).connect(workers=100).gather(workers=100)
        assert v.wikilinks_index == vault_sequential.wikilinks_index
        assert v.source_text_index == vault_sequential.source_text_index


# --- connect with options + parallel ---


class TestConnectOptionsParallel:
    """Verify that connect() options interact correctly with workers."""

    def test_show_nested_tags_parallel(self):
        v_seq = Vault(VAULT_STUB).connect(show_nested_tags=True)
        v_par = Vault(VAULT_STUB).connect(show_nested_tags=True, workers=WORKERS)
        assert v_seq.tags_index == v_par.tags_index

    def test_attachments_true_parallel(self):
        v_seq = Vault(VAULT_STUB).connect(attachments=True)
        v_par = Vault(VAULT_STUB).connect(attachments=True, workers=WORKERS)
        assert v_seq.wikilinks_index == v_par.wikilinks_index
        assert set(v_seq.graph.nodes) == set(v_par.graph.nodes)
        assert set(v_seq.graph.edges) == set(v_par.graph.edges)


# --- idempotency: calling connect/gather twice ---


class TestIdempotencyParallel:
    """Calling connect() or gather() twice should not change results."""

    def test_double_connect_parallel(self):
        v = Vault(VAULT_STUB).connect(workers=WORKERS)
        nodes_before = set(v.graph.nodes)
        edges_before = set(v.graph.edges)
        v.connect(workers=WORKERS)  # second call should be a no-op
        assert set(v.graph.nodes) == nodes_before
        assert set(v.graph.edges) == edges_before

    def test_gather_after_parallel_connect(self):
        """gather() sequentially after parallel connect() should work."""
        v = Vault(VAULT_STUB).connect(workers=WORKERS).gather()
        assert v.is_gathered
        assert set(v.md_file_index.keys()) == set(v.source_text_index.keys())


# --- thread safety: run connect multiple times concurrently on
#     separate Vault instances to check for shared-state leaks ---


class TestThreadSafety:
    """Smoke test that multiple Vault instances processed in parallel
    don't interfere with each other."""

    def test_independent_vaults_parallel(self):
        """Create two independent vaults with parallel workers and
        verify they both produce correct, identical results."""
        v1 = Vault(VAULT_STUB).connect(workers=WORKERS).gather(workers=WORKERS)
        v2 = Vault(VAULT_STUB).connect(workers=WORKERS).gather(workers=WORKERS)

        assert v1.wikilinks_index == v2.wikilinks_index
        assert v1.source_text_index == v2.source_text_index
        assert set(v1.graph.nodes) == set(v2.graph.nodes)
