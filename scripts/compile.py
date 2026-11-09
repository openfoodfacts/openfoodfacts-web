#!/usr/bin/env python3
"""
Master compilation and validation orchestrator for Open Food Facts Web data.

Compiles per-entity YAML files into backward-compatible JSON datasets
and generates localized static HTML showcase/press review pages.

Usage:
    python3 scripts/compile.py              # Validate and compile everything
    python3 scripts/compile.py --check      # Dry-run validation only (CI friendly)
    python3 scripts/compile.py --reuses     # Compile reuses only
    python3 scripts/compile.py --press      # Compile press review only
    python3 scripts/compile.py --queries    # Compile useful queries only
"""

import argparse
import os
import sys
import time

# Ensure scripts directory is in path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from compile_reuses import compile_reuses, load_reuses
from compile_press_review import compile_press_review, load_press_items
from compile_faq import compile_faq
from compile_queries import compile_queries, load_queries
from compile_scan_parties import compile_scan_parties
from compile_campaign_pages import compile_campaign_pages
<<<<<<< Updated upstream
=======
from build_scientific_publications import compile_publications
from compile_releases import compile_releases
>>>>>>> Stashed changes

def main():
    parser = argparse.ArgumentParser(
        description="Compile YAML-based reuses, press review, FAQ, and scan parties datasets into JSON and HTML."
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Validate all YAML and Markdown entities against schema without writing output files."
    )
    parser.add_argument(
        "--reuses", action="store_true",
        help="Compile or validate only the reuses dataset."
    )
    parser.add_argument(
        "--press", action="store_true",
        help="Compile or validate only the press review dataset."
    )
    parser.add_argument(
        "--faq", action="store_true",
        help="Compile or validate only the FAQ dataset."
    )
    parser.add_argument(
        "--queries", action="store_true",
        help="Compile or validate only the useful queries dataset."
    )
    parser.add_argument(
        "--scan-parties", action="store_true",
        help="Compile or validate only the scan parties dataset."
    )
    parser.add_argument(
        "--campaigns", action="store_true",
        help="Compile historical campaigns and missions (Opération Sodas, What's in my yogurt, What's in my shampoo)."
    )
    parser.add_argument(
<<<<<<< Updated upstream
=======
        "--publications", action="store_true",
        help="Compile or validate only the scientific publications dataset."
    )
    parser.add_argument(
        "--releases", action="store_true",
        help="Compile or validate only the ecosystem releases and features dataset."
    )
    parser.add_argument(
>>>>>>> Stashed changes
        "--quiet", "-q", action="store_true",
        help="Suppress detailed logs and only display errors or final summary."
    )

    args = parser.parse_args()

    # Determine what to run
<<<<<<< Updated upstream
    run_all = not (args.reuses or args.press or args.faq or args.queries or args.scan_parties or args.campaigns)
=======
    run_all = not (args.reuses or args.press or args.faq or args.queries or args.scan_parties or args.campaigns or args.publications or args.releases)
>>>>>>> Stashed changes
    do_reuses = run_all or args.reuses
    do_press = run_all or args.press
    do_faq = run_all or args.faq
    do_queries = run_all or args.queries
    do_scan_parties = run_all or args.scan_parties
    do_campaigns = run_all or args.campaigns
<<<<<<< Updated upstream
=======
    do_publications = run_all or args.publications
    do_releases = run_all or args.releases
>>>>>>> Stashed changes
    verbose = not args.quiet

    start_time = time.time()

    print("=" * 60)
    print("🛠️  Open Food Facts Data Compilation Pipeline")
    print("=" * 60)
    if args.check:
        print("🔍 Mode: VALIDATION ONLY (--check)")
    else:
        print("🚀 Mode: VALIDATE & COMPILE (JSON + HTML)")
    print()

    all_ok = True

    # 1. Reuses Pipeline
    if do_reuses:
<<<<<<< Updated upstream
        print("📦 [1/5] Processing Reuses (data/reuses/)...")
=======
        print("📦 [1/8] Processing Reuses (data/reuses/)...")
>>>>>>> Stashed changes
        reuses_ok = compile_reuses(check_only=args.check, verbose=verbose)
        if not reuses_ok:
            all_ok = False
        print()

    # 2. Press Review Pipeline
    if do_press:
<<<<<<< Updated upstream
        print("📰 [2/5] Processing Press Review (data/press-review/)...")
=======
        print("📰 [2/8] Processing Press Review (data/press-review/)...")
>>>>>>> Stashed changes
        press_ok = compile_press_review(check_only=args.check, verbose=verbose)
        if not press_ok:
            all_ok = False
        print()

    # 3. FAQ Pipeline
    if do_faq:
<<<<<<< Updated upstream
        print("❓ [3/5] Processing FAQ (data/faq/)...")
=======
        print("❓ [3/8] Processing FAQ (data/faq/)...")
>>>>>>> Stashed changes
        faq_ok = compile_faq(check_only=args.check, verbose=verbose)
        if not faq_ok:
            all_ok = False
        print()

    # 4. Useful Queries Pipeline
    if do_queries:
<<<<<<< Updated upstream
        print("📊 [4/5] Processing Useful Queries (data/queries/)...")
=======
        print("📊 [4/8] Processing Useful Queries (data/queries/)...")
>>>>>>> Stashed changes
        queries_ok = compile_queries(check_only=args.check, verbose=verbose)
        if not queries_ok:
            all_ok = False
        print()

    # 5. Scan Parties Pipeline
    if do_scan_parties:
<<<<<<< Updated upstream
        print("🎉 [5/6] Processing Scan Parties (data/scan_parties/)...")
=======
        print("🎉 [5/8] Processing Scan Parties (data/scan_parties/)...")
>>>>>>> Stashed changes
        sp_ok = compile_scan_parties(check_only=args.check, verbose=verbose)
        if not sp_ok:
            all_ok = False
        print()

    # 6. Historical Campaigns & Missions Pipeline
    if do_campaigns and not args.check:
<<<<<<< Updated upstream
        print("🚀 [6/6] Processing Historical Campaigns & Missions (data/missions/)...")
=======
        print("🚀 [6/8] Processing Historical Campaigns & Missions (data/missions/)...")
>>>>>>> Stashed changes
        camp_ok = compile_campaign_pages(verbose=verbose)
        if not camp_ok:
            all_ok = False
        print()

<<<<<<< Updated upstream
=======
    # 7. Scientific Publications Pipeline
    if do_publications:
        print("🔬 [7/8] Processing Scientific Publications (data/scientific_publications/)...")
        pubs_ok = compile_publications(check_only=args.check, verbose=verbose)
        if not pubs_ok:
            all_ok = False
        print()

    # 8. Ecosystem Releases & Features Pipeline
    if do_releases:
        print("✨ [8/8] Processing Ecosystem Releases & Features (data/releases.json & data/release_highlights.yaml)...")
        rels_ok = compile_releases(check_only=args.check, verbose=verbose)
        if not rels_ok:
            all_ok = False
        print()

>>>>>>> Stashed changes
    elapsed = time.time() - start_time

    # Summary
    print("=" * 60)
    if all_ok:
        print(f"✨ SUCCESS: All requested datasets validated & compiled in {elapsed:.2f}s!")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"❌ FAILED: Validation or compilation errors encountered ({elapsed:.2f}s).")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
