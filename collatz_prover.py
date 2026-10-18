"""
Collatz Conjecture Prover / Verifier

The Collatz conjecture (3n+1 problem): For any positive integer n,
- if n is even: n → n/2
- if n is odd: n → 3n + 1
Eventually reaches 1.

This module provides:
1. Fast verification up to large bounds using memoization
2. Cycle detection (searching for counterexamples)
3. Heuristic analysis and statistics
4. Parallel verification
5. Mathematical analysis tools (stopping time, total stopping time, etc.)
"""

import math
import sys
import time
from functools import lru_cache
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Iterator
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from pathlib import Path
import json

# ============================================================
# Core Collatz Functions
# ============================================================

@lru_cache(maxsize=None)
def collatz_step(n: int) -> int:
    """Single Collatz step: n -> n/2 if even, 3n+1 if odd"""
    if n % 2 == 0:
        return n // 2
    return 3 * n + 1


@lru_cache(maxsize=None)
def collatz_sequence(n: int, max_steps: int = 10000) -> List[int]:
    """Generate Collatz sequence until 1 or max_steps reached"""
    seq = [n]
    while n != 1 and len(seq) < max_steps:
        n = collatz_step(n)
        seq.append(n)
    return seq


@lru_cache(maxsize=None)
def total_stopping_time(n: int) -> int:
    """Number of steps to reach 1 (total stopping time)"""
    steps = 0
    while n != 1:
        n = collatz_step(n)
        steps += 1
        if steps > 100000:  # Safety limit
            return -1
    return steps


@lru_cache(maxsize=None)
def stopping_time(n: int) -> int:
    """Steps to reach a value < n (stopping time)"""
    original = n
    steps = 0
    while n >= original:
        n = collatz_step(n)
        steps += 1
        if steps > 100000:
            return -1
    return steps


@lru_cache(maxsize=None)
def max_value_in_trajectory(n: int) -> int:
    """Maximum value reached in Collatz trajectory"""
    max_val = n
    while n != 1:
        n = collatz_step(n)
        if n > max_val:
            max_val = n
    return max_val


# ============================================================
# Verification with Memoization
# ============================================================

class CollatzVerifier:
    """
    Fast Collatz verification using memoization and known results.
    Can verify up to very large bounds efficiently.
    """
    
    def __init__(self, cache_size: int = 10_000_000):
        self.cache: Dict[int, bool] = {1: True}
        self.verified_up_to = 0
        self.stats = {
            'total_verified': 0,
            'max_trajectory_value': 0,
            'max_stopping_time': 0,
            'max_total_stopping_time': 0,
        }
    
    def verify_single(self, n: int) -> Tuple[bool, Dict]:
        """Verify a single number, returning (reaches_1, info_dict)"""
        if n in self.cache:
            return self.cache[n], {'cached': True}
        
        original = n
        trajectory = []
        visited = set()
        max_val = n
        steps = 0
        
        while n != 1:
            if n in self.cache:
                # We hit a known value - propagate result
                result = self.cache[n]
                for v in reversed(trajectory):
                    self.cache[v] = result
                return result, {
                    'steps': steps,
                    'max_value': max_val,
                    'cached_at': n,
                    'trajectory_length': len(trajectory)
                }
            
            if n in visited:
                # Cycle detected (counterexample!)
                for v in trajectory:
                    self.cache[v] = False
                return False, {
                    'cycle_detected': True,
                    'cycle_start': n,
                    'trajectory': trajectory
                }
            
            visited.add(n)
            trajectory.append(n)
            max_val = max(max_val, n)
            n = collatz_step(n)
            steps += 1
            
            if steps > 100000:
                # Safety - shouldn't happen for verified ranges
                raise RuntimeError(f"Exceeded max steps for n={original}")
        
        # Reached 1 - propagate success
        for v in reversed(trajectory):
            self.cache[v] = True
        
        self.stats['total_verified'] += 1
        self.stats['max_trajectory_value'] = max(self.stats['max_trajectory_value'], max_val)
        self.stats['max_stopping_time'] = max(self.stats['max_stopping_time'], stopping_time(original))
        self.stats['max_total_stopping_time'] = max(self.stats['max_total_stopping_time'], total_stopping_time(original))
        
        return True, {
            'steps': steps,
            'max_value': max_val,
            'trajectory_length': len(trajectory)
        }
    
    def verify_range(self, start: int, end: int, progress_interval: int = 1_000_000) -> Dict:
        """Verify all numbers in [start, end]"""
        results = {
            'verified': 0,
            'failed': 0,
            'counterexamples': [],
            'stats': {}
        }
        
        for n in range(start, end + 1):
            if n % 2 == 0:
                # Even numbers reduce immediately - skip if n/2 already verified
                if (n // 2) in self.cache:
                    self.cache[n] = True
                    results['verified'] += 1
                    continue
            
            ok, info = self.verify_single(n)
            if ok:
                results['verified'] += 1
            else:
                results['failed'] += 1
                results['counterexamples'].append((n, info))
            
            if n % progress_interval == 0:
                print(f"  Verified up to {n}...")
        
        self.verified_up_to = max(self.verified_up_to, end)
        results['stats'] = self.stats.copy()
        return results
    
    def verify_up_to(self, limit: int, chunk_size: int = 1_000_000) -> Dict:
        """Verify all numbers up to limit in chunks"""
        print(f"Verifying Collatz conjecture up to {limit:,}...")
        start_time = time.time()
        
        # Known result: verified up to 2^68 ≈ 2.95e20
        # We'll verify what we can computationally
        
        total_results = {'verified': 0, 'failed': 0, 'counterexamples': [], 'chunks': []}
        
        for chunk_start in range(1, limit + 1, chunk_size):
            chunk_end = min(chunk_start + chunk_size - 1, limit)
            print(f"Chunk [{chunk_start:,} .. {chunk_end:,}]")
            chunk_results = self.verify_range(chunk_start, chunk_end)
            total_results['verified'] += chunk_results['verified']
            total_results['failed'] += chunk_results['failed']
            total_results['counterexamples'].extend(chunk_results['counterexamples'])
            total_results['chunks'].append(chunk_results)
        
        elapsed = time.time() - start_time
        total_results['elapsed_seconds'] = elapsed
        total_results['numbers_per_second'] = total_results['verified'] / elapsed if elapsed > 0 else 0
        
        print(f"\nCompleted in {elapsed:.1f}s")
        print(f"Verified: {total_results['verified']:,}")
        print(f"Failed: {total_results['failed']:,}")
        print(f"Rate: {total_results['numbers_per_second']:,.0f} numbers/sec")
        
        return total_results


# ============================================================
# Parallel Verification
# ============================================================

def _verify_chunk(args: Tuple[int, int]) -> Dict:
    """Worker function for parallel verification"""
    start, end = args
    local_cache = {1: True}
    
    def verify(n: int) -> bool:
        if n in local_cache:
            return local_cache[n]
        original = n
        trajectory = []
        while n != 1:
            if n in local_cache:
                result = local_cache[n]
                for v in reversed(trajectory):
                    local_cache[v] = result
                return result
            trajectory.append(n)
            n = n // 2 if n % 2 == 0 else 3 * n + 1
        for v in reversed(trajectory):
            local_cache[v] = True
        return True
    
    failed = []
    for n in range(start, end + 1):
        if not verify(n):
            failed.append(n)
    
    return {
        'start': start,
        'end': end,
        'verified': end - start + 1 - len(failed),
        'failed': len(failed),
        'counterexamples': failed
    }


def parallel_verify(limit: int, num_workers: int = None) -> Dict:
    """Parallel verification using multiple processes"""
    if num_workers is None:
        num_workers = mp.cpu_count()
    
    chunk_size = max(10000, limit // (num_workers * 10))
    chunks = []
    for start in range(1, limit + 1, chunk_size):
        end = min(start + chunk_size - 1, limit)
        chunks.append((start, end))
    
    print(f"Parallel verification: {limit:,} numbers, {num_workers} workers, {len(chunks)} chunks")
    start_time = time.time()
    
    results = {'verified': 0, 'failed': 0, 'counterexamples': []}
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(_verify_chunk, chunk) for chunk in chunks]
        for future in as_completed(futures):
            chunk_result = future.result()
            results['verified'] += chunk_result['verified']
            results['failed'] += chunk_result['failed']
            results['counterexamples'].extend(chunk_result['counterexamples'])
    
    elapsed = time.time() - start_time
    results['elapsed_seconds'] = elapsed
    print(f"Parallel verification completed in {elapsed:.1f}s")
    return results


# ============================================================
# Mathematical Analysis
# ============================================================

@dataclass
class CollatzStats:
    """Statistics for a range of Collatz trajectories"""
    n: int
    stopping_time: int
    total_stopping_time: int
    max_value: int
    max_value_ratio: float  # max_value / n
    trajectory: List[int]


def analyze_range(start: int, end: int) -> List[CollatzStats]:
    """Detailed analysis of Collatz trajectories in range"""
    stats = []
    for n in range(start, end + 1):
        traj = collatz_sequence(n)
        st = stopping_time(n)
        tst = total_stopping_time(n)
        max_val = max(traj)
        stats.append(CollatzStats(
            n=n,
            stopping_time=st,
            total_stopping_time=tst,
            max_value=max_val,
            max_value_ratio=max_val / n,
            trajectory=traj
        ))
    return stats


def find_records(limit: int) -> Dict[str, List[Tuple[int, int]]]:
    """Find record holders for various metrics"""
    records = {
        'max_total_stopping_time': [],
        'max_stopping_time': [],
        'max_peak_value': [],
        'max_peak_ratio': [],
    }
    
    best_tst = 0
    best_st = 0
    best_peak = 0
    best_ratio = 0.0
    
    for n in range(1, limit + 1):
        tst = total_stopping_time(n)
        if tst > best_tst:
            best_tst = tst
            records['max_total_stopping_time'].append((n, tst))
        
        st = stopping_time(n)
        if st > best_st:
            best_st = st
            records['max_stopping_time'].append((n, st))
        
        peak = max_value_in_trajectory(n)
        if peak > best_peak:
            best_peak = peak
            records['max_peak_value'].append((n, peak))
        
        ratio = peak / n
        if ratio > best_ratio:
            best_ratio = ratio
            records['max_peak_ratio'].append((n, ratio))
    
    return records


# ============================================================
# Heuristic / Probabilistic Analysis
# ============================================================

def collatz_heuristic_analysis(n: int) -> Dict:
    """
    Probabilistic analysis of Collatz trajectory.
    On average, odd steps multiply by ~3/2, even steps divide by 2.
    Expected growth factor per step: (3/2)^(1/2) * (1/2)^(1/2) = sqrt(3/4) < 1.
    """
    trajectory = collatz_sequence(n)
    odd_steps = sum(1 for x in trajectory[:-1] if x % 2 == 1)
    even_steps = len(trajectory) - 1 - odd_steps
    
    # Expected log change per step
    # odd: log(3n+1) - log(n) ≈ log(3) + log(1 + 1/(3n)) ≈ log(3)
    # even: log(n/2) - log(n) = -log(2)
    
    return {
        'total_steps': len(trajectory) - 1,
        'odd_steps': odd_steps,
        'even_steps': even_steps,
        'odd_even_ratio': odd_steps / even_steps if even_steps > 0 else float('inf'),
        'log_start': math.log(n),
        'log_end': 0.0,  # log(1)
        'expected_drift': odd_steps * math.log(3) - even_steps * math.log(2),
        'max_value': max(trajectory),
        'max_value_log': math.log(max(trajectory)),
    }


def search_cycles(limit: int, max_steps: int = 10000) -> List[Tuple[int, List[int]]]:
    """Search for cycles other than 1-4-2-1"""
    # Known: only cycles are 1-4-2-1, and possibly negative ones
    # We search positive integers
    
    visited_global = set()
    cycles = []
    
    for start in range(1, limit + 1):
        if start in visited_global:
            continue
        
        n = start
        trajectory = []
        local_visited = {}
        step = 0
        
        while n not in local_visited and n not in visited_global and step < max_steps:
            local_visited[n] = step
            trajectory.append(n)
            n = collatz_step(n)
            step += 1
        
        if n in local_visited:
            # Found a cycle
            cycle_start_idx = local_visited[n]
            cycle = trajectory[cycle_start_idx:]
            if cycle != [1, 4, 2]:  # Skip the known trivial cycle
                cycles.append((start, cycle))
        
        visited_global.update(trajectory)
    
    return cycles


# ============================================================
# Known Results and Constants
# ============================================================

# As of 2024, Collatz has been verified up to 2^68 ≈ 2.95 × 10^20
# by David Bařina (2020) and others using distributed computing.

KNOWN_VERIFICATION_LIMIT = 2**68  # ~2.95e20

# Record holders (as of known computations)
RECORD_HOLDERS = {
    'max_total_stopping_time_under_100M': (63728127, 949),
    'max_stopping_time_under_100M': (63728127, 949),
    # Many more records exist...
}


def get_known_results() -> Dict:
    """Return summary of known Collatz results"""
    return {
        'verified_up_to': KNOWN_VERIFICATION_LIMIT,
        'verified_up_to_scientific': f"{KNOWN_VERIFICATION_LIMIT:.2e}",
        'conjecture_status': "OPEN - No counterexample found, no proof exists",
        'known_cycles_positive': [[1, 4, 2]],  # Only known positive cycle
        'known_cycles_negative': [[-1], [-5, -14, -7, -20, -10], [-17, -50, -25, -74, -37, -110, -55, -164, -82, -41, -122, -61, -182, -91, -272, -136, -68, -34]],
        'heuristic_argument': "Expected log decrease per step: 0.5*log(3/4) < 0, so trajectories should decrease on average",
    }


# ============================================================
# Main CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Collatz Conjecture Verifier")
    parser.add_argument('--verify-up-to', type=int, default=1_000_000,
                        help='Verify all numbers up to this limit')
    parser.add_argument('--parallel', action='store_true',
                        help='Use parallel verification')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of parallel workers')
    parser.add_argument('--analyze', type=int, nargs=2, metavar=('START', 'END'),
                        help='Analyze range in detail')
    parser.add_argument('--records', type=int, metavar='LIMIT',
                        help='Find record holders up to limit')
    parser.add_argument('--search-cycles', type=int, metavar='LIMIT',
                        help='Search for non-trivial cycles up to limit')
    parser.add_argument('--heuristic', type=int, metavar='N',
                        help='Heuristic analysis for single number')
    parser.add_argument('--known', action='store_true',
                        help='Show known results summary')
    
    args = parser.parse_args()
    
    if args.known:
        known = get_known_results()
        print(json.dumps(known, indent=2))
        return
    
    if args.heuristic:
        n = args.heuristic
        analysis = collatz_heuristic_analysis(n)
        print(f"Heuristic analysis for n = {n}:")
        for k, v in analysis.items():
            print(f"  {k}: {v}")
        return
    
    if args.records:
        records = find_records(args.records)
        for metric, holders in records.items():
            print(f"\n{metric}:")
            for n, val in holders[-10:]:  # Last 10 records
                print(f"  n={n:,}: {val}")
        return
    
    if args.search_cycles:
        cycles = search_cycles(args.search_cycles)
        if cycles:
            print(f"Found {len(cycles)} non-trivial cycles:")
            for start, cycle in cycles:
                print(f"  Start {start}: {cycle}")
        else:
            print(f"No non-trivial cycles found up to {args.search_cycles}")
        return
    
    if args.analyze:
        start, end = args.analyze
        stats = analyze_range(start, end)
        for s in stats:
            print(f"n={s.n}: TST={s.total_stopping_time}, ST={s.stopping_time}, "
                  f"max={s.max_value:,} (ratio={s.max_value_ratio:.2f})")
        return
    
    # Default: verify
    verifier = CollatzVerifier()
    if args.parallel:
        results = parallel_verify(args.verify_up_to, args.workers)
    else:
        results = verifier.verify_up_to(args.verify_up_to)
    
    if results['counterexamples']:
        print(f"\n*** COUNTEREXAMPLES FOUND: {results['counterexamples']} ***")
    else:
        print(f"\nNo counterexamples found up to {args.verify_up_to:,}")


if __name__ == "__main__":
    main()