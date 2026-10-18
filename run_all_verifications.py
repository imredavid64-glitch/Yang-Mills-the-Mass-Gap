#!/usr/bin/env python3
"""
Comprehensive Test Runner for:
1. Yang-Mills Mass Gap Proof (Phase 1 - Strong Coupling)
2. Collatz Conjecture Verification
3. Goldbach Conjecture Verification

Runs all verifications and produces a summary report.
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def run_yang_mills_verification():
    """Run Yang-Mills Phase 1 verification"""
    print("=" * 70)
    print("YANG-MILLS MASS GAP - PHASE 1 VERIFICATION")
    print("=" * 70)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, "scripts/verify_phase1.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return {
        'name': 'Yang-Mills Mass Gap (Phase 1)',
        'success': result.returncode == 0,
        'elapsed': elapsed,
        'output': result.stdout
    }


def run_collatz_verification(limit=1000000):
    """Run Collatz verification"""
    print("=" * 70)
    print(f"COLLATZ CONJECTURE VERIFICATION (up to {limit:,})")
    print("=" * 70)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, "collatz_prover.py", "--verify-up-to", str(limit)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return {
        'name': f'Collatz Conjecture (up to {limit:,})',
        'success': result.returncode == 0 and "No counterexamples found" in result.stdout,
        'elapsed': elapsed,
        'output': result.stdout
    }


def run_goldbach_verification(limit=100000):
    """Run Goldbach verification"""
    print("=" * 70)
    print(f"GOLDBACH CONJECTURE VERIFICATION (up to {limit:,})")
    print("=" * 70)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, "goldbach_prover.py", "--verify-up-to", str(limit)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return {
        'name': f'Goldbach Conjecture (up to {limit:,})',
        'success': result.returncode == 0 and "No counterexamples found" in result.stdout,
        'elapsed': elapsed,
        'output': result.stdout
    }


def run_collatz_records(limit=1000000):
    """Run Collatz record analysis"""
    print("=" * 70)
    print(f"COLLATZ RECORD ANALYSIS (up to {limit:,})")
    print("=" * 70)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, "collatz_prover.py", "--records", str(limit)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start
    
    print(result.stdout)
    return {
        'name': 'Collatz Records',
        'success': result.returncode == 0,
        'elapsed': elapsed,
        'output': result.stdout
    }


def run_goldbach_analysis(limit=50000):
    """Run Goldbach Hardy-Littlewood analysis"""
    print("=" * 70)
    print(f"GOLDBACH HARDY-LITTLEWOOD ANALYSIS (up to {limit:,})")
    print("=" * 70)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, "goldbach_prover.py", "--hl", str(limit)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start
    
    print(result.stdout)
    return {
        'name': 'Goldbach Hardy-Littlewood',
        'success': result.returncode == 0,
        'elapsed': elapsed,
        'output': result.stdout
    }


def main():
    print("COMPREHENSIVE MATHEMATICAL VERIFICATION SUITE")
    print("=" * 70)
    print()
    
    results = []
    
    # 1. Yang-Mills Mass Gap (Phase 1 - already proven at beta=0)
    results.append(run_yang_mills_verification())
    
    # 2. Collatz Conjecture
    results.append(run_collatz_verification(500000))
    results.append(run_collatz_records(500000))
    
    # 3. Goldbach Conjecture
    results.append(run_goldbach_verification(100000))
    results.append(run_goldbach_analysis(50000))
    
    # Summary
    print("=" * 70)
    print("COMPREHENSIVE VERIFICATION SUMMARY")
    print("=" * 70)
    
    total_time = sum(r['elapsed'] for r in results)
    
    for r in results:
        status = "[PASS]" if r['success'] else "[FAIL]"
        print(f"{status} | {r['name']:<40} | {r['elapsed']:.1f}s")
    
    print("-" * 70)
    print(f"Total time: {total_time:.1f}s")
    print(f"Tests passed: {sum(1 for r in results if r['success'])}/{len(results)}")
    
    # Save detailed results
    with open(PROJECT_ROOT / "verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to verification_results.json")
    
    return all(r['success'] for r in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)