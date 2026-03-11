#!/usr/bin/env python3
"""Quick test to verify parallel tests work."""
import time
from pathlib import Path
from obsidiantools.api import Vault

WKD = Path().cwd()
VAULT_STUB = WKD / "tests/vault-stub"

print("Testing sequential connection...")
start = time.time()
v_seq = Vault(VAULT_STUB).connect()
seq_connect_time = time.time() - start
print(f"  Sequential connect: {seq_connect_time:.3f}s")
print(f"  Graph nodes: {len(v_seq.graph.nodes)}")
print(f"  Graph edges: {len(v_seq.graph.edges)}")

start = time.time()
v_seq = v_seq.gather()
seq_gather_time = time.time() - start
print(f"  Sequential gather: {seq_gather_time:.3f}s")
print(f"  Source text files: {len(v_seq.source_text_index)}")

print("\nTesting parallel connection with 4 workers...")
start = time.time()
v_par = Vault(VAULT_STUB).connect(workers=4)
par_connect_time = time.time() - start
print(f"  Parallel connect: {par_connect_time:.3f}s")
print(f"  Graph nodes: {len(v_par.graph.nodes)}")
print(f"  Graph edges: {len(v_par.graph.edges)}")

start = time.time()
v_par = v_par.gather(workers=4)
par_gather_time = time.time() - start
print(f"  Parallel gather: {par_gather_time:.3f}s")
print(f"  Source text files: {len(v_par.source_text_index)}")

print("\nVerifying equivalence...")
print(f"  Graph nodes match: {set(v_seq.graph.nodes) == set(v_par.graph.nodes)}")
print(f"  Graph edges match: {set(v_seq.graph.edges) == set(v_par.graph.edges)}")
print(f"  Wikilinks match: {v_seq.wikilinks_index == v_par.wikilinks_index}")
print(f"  Source text match: {v_seq.source_text_index == v_par.source_text_index}")

print("\nTiming comparison:")
print(f"  Connect speedup: {seq_connect_time / par_connect_time:.2f}x")
print(f"  Gather speedup: {seq_gather_time / par_gather_time:.2f}x")
