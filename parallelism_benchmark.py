#!/usr/bin/env python3
"""Quick test to verify parallel tests work."""
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from obsidiantools.api import Vault

load_dotenv()

VAULT_DIR = Path(os.environ["VAULT_DIR"])
N_WORKERS = 8


def main():
    print("Testing sequential connection...")
    start = time.time()
    v_seq = Vault(VAULT_DIR).connect()
    seq_connect_time = time.time() - start
    print(f"  Sequential connect: {seq_connect_time:.3f}s")
    print(f"  Graph nodes: {len(v_seq.graph.nodes)}")
    print(f"  Graph edges: {len(v_seq.graph.edges)}")

    start = time.time()
    v_seq = v_seq.gather()
    seq_gather_time = time.time() - start
    print(f"  Sequential gather: {seq_gather_time:.3f}s")
    print(f"  Source text files: {len(v_seq.source_text_index)}")

    print(f"\nTesting parallel connection with {N_WORKERS} workers...")
    start = time.time()
    v_par = Vault(VAULT_DIR, workers=N_WORKERS).connect()
    par_connect_time = time.time() - start
    print(f"  Parallel connect: {par_connect_time:.3f}s")
    print(f"  Graph nodes: {len(v_par.graph.nodes)}")
    print(f"  Graph edges: {len(v_par.graph.edges)}")

    start = time.time()
    v_par = v_par.gather()
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


if __name__ == "__main__":
    main()
