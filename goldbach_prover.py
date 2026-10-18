"""
Goldbach Conjecture Prover / Verifier

Goldbach's Conjecture: Every even integer greater than 2 can be expressed
as the sum of two primes.

Goldbach's Weak Conjecture: Every odd integer greater than 5 can be expressed
as the sum of three primes. (Proven by Helfgott, 2013)

This module provides:
1. Fast verification up to large bounds
2. Prime generation with sieves
3. Goldbach partition counting
4. Statistical analysis
5. Related conjectures (weak, ternary, etc.)
6. Hardy-Littlewood asymptotic formula verification
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
# Prime Generation and Testing
# ============================================================

@lru_cache(maxsize=10000)
def is_prime(n: int) -> bool:
    """Miller-Rabin primality test (deterministic for n < 2^64)"""
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small_primes:
        if n % p == 0:
            return n == p
    
    # Miller-Rabin deterministic bases for n < 2^64
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Bases sufficient for n < 2^64
    for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022]:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """Generate all primes up to limit using optimized sieve"""
    if limit < 2:
        return []
    
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0:2] = b'\x00\x00'
    
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i:limit+1:i] = b'\x00' * ((limit - i*i) // i + 1)
    
    return [i for i, is_p in enumerate(sieve) if is_p]


def segmented_sieve(limit: int, segment_size: int = 1_000_000) -> List[int]:
    """Memory-efficient segmented sieve for large limits"""
    if limit < 2:
        return []
    
    # Initial primes up to sqrt(limit)
    sqrt_limit = int(math.sqrt(limit)) + 1
    base_primes = sieve_of_eratosthenes(sqrt_limit)
    all_primes = base_primes.copy()
    
    # Process segments
    for low in range(sqrt_limit + 1, limit + 1, segment_size):
        high = min(low + segment_size - 1, limit)
        sieve = bytearray(b'\x01') * (high - low + 1)
        
        for p in base_primes:
            start = max(p * p, ((low + p - 1) // p) * p)
            sieve[start - low:high - low + 1:p] = b'\x00' * ((high - start) // p + 1)
        
        all_primes.extend([low + i for i, is_p in enumerate(sieve) if is_p])
    
    return all_primes


class PrimeGenerator:
    """Efficient prime generation with caching"""
    
    def __init__(self):
        self._primes: List[int] = []
        self._sieve_limit = 0
        self._is_prime_cache: Dict[int, bool] = {}
    
    def generate_up_to(self, limit: int) -> List[int]:
        """Generate primes up to limit, extending cache if needed"""
        if limit <= self._sieve_limit:
            return [p for p in self._primes if p <= limit]
        
        # Use segmented sieve for large limits
        if limit > 10_000_000:
            self._primes = segmented_sieve(limit)
        else:
            self._primes = sieve_of_eratosthenes(limit)
        self._sieve_limit = limit
        return self._primes
    
    def get_primes_in_range(self, start: int, end: int) -> List[int]:
        """Get primes in [start, end]"""
        if end <= self._sieve_limit:
            return [p for p in self._primes if start <= p <= end]
        return [p for p in self.generate_up_to(end) if p >= start]
    
    def is_prime(self, n: int) -> bool:
        """Check primality using cached sieve or Miller-Rabin"""
        if n <= self._sieve_limit:
            return n in self._prime_set
        if n in self._is_prime_cache:
            return self._is_prime_cache[n]
        result = is_prime(n)
        self._is_prime_cache[n] = result
        return result
    
    @property
    def _prime_set(self) -> Set[int]:
        return set(self._primes)


# ============================================================
# Goldbach Partition Finding
# ============================================================

def goldbach_partitions(n: int, primes: List[int] = None, prime_set: Set[int] = None) -> List[Tuple[int, int]]:
    """Find all Goldbach partitions of even n: n = p + q"""
    if n % 2 != 0 or n <= 2:
        return []
    
    if primes is None:
        primes = sieve_of_eratosthenes(n)
    if prime_set is None:
        prime_set = set(primes)
    
    partitions = []
    for p in primes:
        if p > n // 2:
            break
        q = n - p
        if q in prime_set:
            partitions.append((p, q))
    return partitions


def goldbach_partition_count(n: int, primes: List[int] = None, prime_set: Set[int] = None) -> int:
    """Count Goldbach partitions (faster than listing all)"""
    if n % 2 != 0 or n <= 2:
        return 0
    
    if primes is None:
        primes = sieve_of_eratosthenes(n)
    if prime_set is None:
        prime_set = set(primes)
    
    count = 0
    for p in primes:
        if p > n // 2:
            break
        if n - p in prime_set:
            count += 1
    return count


def minimal_goldbach_partition(n: int, primes: List[int] = None, prime_set: Set[int] = None) -> Optional[Tuple[int, int]]:
    """Find the Goldbach partition with minimal difference (p, q closest together)"""
    if n % 2 != 0 or n <= 2:
        return None
    
    if primes is None:
        primes = sieve_of_eratosthenes(n)
    if prime_set is None:
        prime_set = set(primes)
    
    # Search from n/2 downwards
    for p in reversed(primes):
        if p > n // 2:
            continue
        q = n - p
        if q in prime_set:
            return (p, q)
    return None


# ============================================================
# Goldbach Verification
# ============================================================

class GoldbachVerifier:
    """Verify Goldbach conjecture up to a limit"""
    
    def __init__(self):
        self.prime_gen = PrimeGenerator()
        self.stats = {
            'verified': 0,
            'failed': 0,
            'counterexamples': [],
            'min_partitions': float('inf'),
            'max_partitions': 0,
        }
    
    def verify_single(self, n: int) -> Tuple[bool, Dict]:
        """Verify Goldbach for a single even number"""
        if n % 2 != 0 or n <= 2:
            return True, {'skipped': True, 'reason': 'not even > 2'}
        
        primes = self.prime_gen.generate_up_to(n)
        prime_set = set(primes)
        
        partitions = goldbach_partitions(n, primes, prime_set)
        count = len(partitions)
        
        self.stats['verified'] += 1
        self.stats['min_partitions'] = min(self.stats['min_partitions'], count)
        self.stats['max_partitions'] = max(self.stats['max_partitions'], count)
        
        if count == 0:
            self.stats['failed'] += 1
            self.stats['counterexamples'].append(n)
            return False, {'partitions': 0}
        
        return True, {
            'partitions': count,
            'minimal': minimal_goldbach_partition(n, primes, prime_set)
        }
    
    def verify_range(self, start: int, end: int, progress_interval: int = 100000) -> Dict:
        """Verify Goldbach for all even numbers in range"""
        # Ensure we have primes up to end
        self.prime_gen.generate_up_to(end)
        
        results = {
            'verified': 0,
            'failed': 0,
            'counterexamples': [],
            'partition_counts': {}
        }
        
        # Start from first even >= start
        if start % 2 != 0:
            start += 1
        
        for n in range(start, end + 1, 2):
            ok, info = self.verify_single(n)
            if ok:
                results['verified'] += 1
                results['partition_counts'][n] = info['partitions']
            else:
                results['failed'] += 1
                results['counterexamples'].append(n)
            
            if n % progress_interval == 0:
                print(f"  Verified up to {n}...")
        
        return results
    
    def verify_up_to(self, limit: int) -> Dict:
        """Verify Goldbach for all even numbers up to limit"""
        print(f"Verifying Goldbach conjecture up to {limit:,}...")
        start_time = time.time()
        
        results = self.verify_range(4, limit)
        
        elapsed = time.time() - start_time
        results['elapsed_seconds'] = elapsed
        
        print(f"\nCompleted in {elapsed:.1f}s")
        print(f"Verified: {results['verified']:,} even numbers")
        print(f"Failed: {results['failed']:,}")
        print(f"Min partitions for any n: {self.stats['min_partitions']}")
        print(f"Max partitions for any n: {self.stats['max_partitions']}")
        
        return results


# ============================================================
# Hardy-Littlewood Asymptotic Formula
# ============================================================

def singular_series(n: int, primes: List[int] = None) -> float:
    """
    Compute the singular series (Goldbach's comet constant) for even n:
    S(n) = 2 * C_2 * prod_{p|n, p>2} (p-1)/(p-2)
    where C_2 = 0.66016... is the twin prime constant
    """
    if n % 2 != 0:
        return 0.0
    
    C2 = 0.660161815846869573927812110014  # Twin prime constant
    result = 2 * C2
    
    # Product over odd prime divisors of n
    temp = n
    p = 3
    while p * p <= temp:
        if temp % p == 0:
            result *= (p - 1) / (p - 2)
            while temp % p == 0:
                temp //= p
        p += 2
    if temp > 2:
        result *= (temp - 1) / (temp - 2)
    
    return result


def hardy_littlewood_estimate(n: int) -> float:
    """Hardy-Littlewood asymptotic for number of Goldbach partitions"""
    if n % 2 != 0 or n <= 2:
        return 0.0
    S = singular_series(n)
    return S * n / (math.log(n) ** 2)


def verify_hardy_littlewood(limit: int, step: int = 1000) -> Dict:
    """Compare actual partition counts with Hardy-Littlewood estimates"""
    primes = sieve_of_eratosthenes(limit)
    prime_set = set(primes)
    
    comparisons = []
    for n in range(4, limit + 1, step):
        if n % 2 == 0:
            actual = goldbach_partition_count(n, primes, prime_set)
            estimate = hardy_littlewood_estimate(n)
            ratio = actual / estimate if estimate > 0 else 0
            comparisons.append((n, actual, estimate, ratio))
    
    return {
        'comparisons': comparisons,
        'avg_ratio': sum(c[3] for c in comparisons) / len(comparisons) if comparisons else 0,
    }


# ============================================================
# Weak Goldbach (Ternary) - Proven by Helfgott 2013
# ============================================================

def weak_goldbach_partitions(n: int, primes: List[int] = None) -> List[Tuple[int, int, int]]:
    """Find all partitions of odd n as sum of three primes (n > 5)"""
    if n % 2 == 0 or n <= 5:
        return []
    
    if primes is None:
        primes = sieve_of_eratosthenes(n)
    prime_set = set(primes)
    
    partitions = []
    for i, p1 in enumerate(primes):
        if p1 > n - 4:  # need at least 2+2 for remaining
            break
        for p2 in primes[i:]:
            if p1 + p2 > n - 2:
                break
            p3 = n - p1 - p2
            if p3 >= p2 and p3 in prime_set:
                partitions.append((p1, p2, p3))
    return partitions


def verify_weak_goldbach(limit: int) -> Dict:
    """Verify weak Goldbach (proven, but good to check computationally)"""
    primes = sieve_of_eratosthenes(limit)
    prime_set = set(primes)
    
    results = {'verified': 0, 'failed': 0, 'counterexamples': []}
    
    for n in range(7, limit + 1, 2):
        found = False
        for p1 in primes:
            if p1 > n - 4:
                break
            for p2 in primes:
                if p1 + p2 > n - 2:
                    break
                p3 = n - p1 - p2
                if p3 in prime_set:
                    found = True
                    break
            if found:
                break
        
        if found:
            results['verified'] += 1
        else:
            results['failed'] += 1
            results['counterexamples'].append(n)
    
    return results


# ============================================================
# Related Conjectures
# ============================================================

def chen_theorem_check(limit: int) -> Dict:
    """
    Chen's Theorem (1973): Every sufficiently large even number is the sum
    of a prime and a product of at most two primes (semiprime).
    """
    primes = sieve_of_eratosthenes(limit)
    prime_set = set(primes)
    
    # Generate semiprimes (products of two primes)
    semiprimes = set()
    for i, p1 in enumerate(primes):
        for p2 in primes[i:]:
            prod = p1 * p2
            if prod > limit:
                break
            semiprimes.add(prod)
    
    results = {'verified': 0, 'failed': 0, 'counterexamples': []}
    
    for n in range(4, limit + 1, 2):
        found = False
        for p in primes:
            if p > n:
                break
            if (n - p) in prime_set or (n - p) in semiprimes:
                found = True
                break
        
        if found:
            results['verified'] += 1
        else:
            results['failed'] += 1
            results['counterexamples'].append(n)
    
    return results


def levy_conjecture_check(limit: int) -> Dict:
    """
    Levy's Conjecture: Every odd number >= 7 can be written as p + 2q
    where p, q are primes. (Equivalent to Goldbach)
    """
    primes = sieve_of_eratosthenes(limit)
    prime_set = set(primes)
    
    results = {'verified': 0, 'failed': 0, 'counterexamples': []}
    
    for n in range(7, limit + 1, 2):
        found = False
        for q in primes:
            if 2 * q > n - 2:
                break
            p = n - 2 * q
            if p in prime_set:
                found = True
                break
        
        if found:
            results['verified'] += 1
        else:
            results['failed'] += 1
            results['counterexamples'].append(n)
    
    return results


# ============================================================
# Statistical Analysis
# ============================================================

@dataclass
class GoldbachStats:
    n: int
    partition_count: int
    hl_estimate: float
    ratio: float
    minimal_partition: Tuple[int, int]


def analyze_goldbach_statistics(limit: int, step: int = 100) -> List[GoldbachStats]:
    """Statistical analysis of Goldbach partitions"""
    primes = sieve_of_eratosthenes(limit)
    prime_set = set(primes)
    
    stats = []
    for n in range(4, limit + 1, step):
        if n % 2 == 0:
            count = goldbach_partition_count(n, primes, prime_set)
            estimate = hardy_littlewood_estimate(n)
            minimal = minimal_goldbach_partition(n, primes, prime_set)
            stats.append(GoldbachStats(
                n=n,
                partition_count=count,
                hl_estimate=estimate,
                ratio=count / estimate if estimate > 0 else 0,
                minimal_partition=minimal
            ))
    return stats


# ============================================================
# Parallel Verification
# ============================================================

def _verify_goldbach_chunk(args: Tuple[int, int, List[int]]) -> Dict:
    """Worker for parallel Goldbach verification"""
    start, end, primes = args
    prime_set = set(primes)
    
    failed = []
    for n in range(start, end + 1, 2):
        found = False
        for p in primes:
            if p > n // 2:
                break
            if n - p in prime_set:
                found = True
                break
        if not found:
            failed.append(n)
    
    return {
        'start': start,
        'end': end,
        'verified': (end - start) // 2 + 1 - len(failed),
        'failed': len(failed),
        'counterexamples': failed
    }


def parallel_goldbach_verify(limit: int, num_workers: int = None) -> Dict:
    """Parallel Goldbach verification"""
    if num_workers is None:
        num_workers = mp.cpu_count()
    
    primes = sieve_of_eratosthenes(limit)
    chunk_size = max(10000, limit // (num_workers * 4))
    # Ensure even boundaries
    chunk_size = (chunk_size // 2) * 2
    
    chunks = []
    for start in range(4, limit + 1, chunk_size):
        end = min(start + chunk_size - 1, limit)
        if end % 2 != 0:
            end -= 1
        chunks.append((start, end, primes))
    
    print(f"Parallel Goldbach: {limit:,} limit, {num_workers} workers, {len(chunks)} chunks")
    start_time = time.time()
    
    results = {'verified': 0, 'failed': 0, 'counterexamples': []}
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(_verify_goldbach_chunk, chunk) for chunk in chunks]
        for future in as_completed(futures):
            chunk_result = future.result()
            results['verified'] += chunk_result['verified']
            results['failed'] += chunk_result['failed']
            results['counterexamples'].extend(chunk_result['counterexamples'])
    
    elapsed = time.time() - start_time
    results['elapsed_seconds'] = elapsed
    print(f"Completed in {elapsed:.1f}s")
    return results


# ============================================================
# Known Results
# ============================================================

def get_goldbach_known_results() -> Dict:
    """Summary of known Goldbach results"""
    return {
        'strong_conjecture_status': "OPEN - Verified up to 4×10^18 (Oliveira e Silva et al., 2014)",
        'weak_conjecture_status': "PROVEN - Helfgott (2013), all odd n > 5 are sum of 3 primes",
        'chen_theorem': "PROVEN - Every large even n = p + P_2 (prime + semiprime)",
        'verified_up_to': 4_000_000_000_000_000_000,  # 4e18
        'hardy_littlewood_constant': 0.660161815846869573927812110014,
        'asymptotic_formula': "G(n) ~ S(n) * n / log(n)^2 where S(n) is singular series",
        'min_partitions_observed': 1,  # For n=4,6,8,10,12
        'max_partitions_growth': "~ n / log(n)^2",
    }


# ============================================================
# Main CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Goldbach Conjecture Verifier")
    parser.add_argument('--verify-up-to', type=int, default=1_000_000,
                        help='Verify Goldbach up to this limit')
    parser.add_argument('--parallel', action='store_true',
                        help='Use parallel verification')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of parallel workers')
    parser.add_argument('--weak', type=int, metavar='LIMIT',
                        help='Verify weak Goldbach (ternary) up to limit')
    parser.add_argument('--chen', type=int, metavar='LIMIT',
                        help='Verify Chen\'s theorem up to limit')
    parser.add_argument('--levy', type=int, metavar='LIMIT',
                        help='Verify Levy\'s conjecture up to limit')
    parser.add_argument('--hl', type=int, metavar='LIMIT',
                        help='Compare with Hardy-Littlewood estimate up to limit')
    parser.add_argument('--stats', type=int, nargs=2, metavar=('START', 'END'),
                        help='Detailed statistics for range')
    parser.add_argument('--partitions', type=int, metavar='N',
                        help='Show all Goldbach partitions for N')
    parser.add_argument('--known', action='store_true',
                        help='Show known results summary')
    
    args = parser.parse_args()
    
    if args.known:
        known = get_goldbach_known_results()
        print(json.dumps(known, indent=2))
        return
    
    if args.partitions:
        n = args.partitions
        if n % 2 == 0 and n > 2:
            primes = sieve_of_eratosthenes(n)
            parts = goldbach_partitions(n, primes, set(primes))
            print(f"Goldbach partitions of {n}:")
            for p, q in parts:
                print(f"  {n} = {p} + {q}")
            print(f"Total: {len(parts)} partitions")
            print(f"HL estimate: {hardy_littlewood_estimate(n):.2f}")
        else:
            print("Please provide an even number > 2")
        return
    
    if args.hl:
        results = verify_hardy_littlewood(args.hl)
        print("Hardy-Littlewood comparison:")
        for n, actual, estimate, ratio in results['comparisons'][-20:]:
            print(f"  n={n:6d}: actual={actual:4d}, estimate={estimate:8.2f}, ratio={ratio:.4f}")
        print(f"\nAverage ratio: {results['avg_ratio']:.4f}")
        return
    
    if args.weak:
        results = verify_weak_goldbach(args.weak)
        print(f"Weak Goldbach up to {args.weak}:")
        print(f"  Verified: {results['verified']}")
        print(f"  Failed: {results['failed']}")
        if results['counterexamples']:
            print(f"  Counterexamples: {results['counterexamples'][:10]}")
        return
    
    if args.chen:
        results = chen_theorem_check(args.chen)
        print(f"Chen's Theorem up to {args.chen}:")
        print(f"  Verified: {results['verified']}")
        print(f"  Failed: {results['failed']}")
        if results['counterexamples']:
            print(f"  Counterexamples: {results['counterexamples'][:10]}")
        return
    
    if args.levy:
        results = levy_conjecture_check(args.levy)
        print(f"Levy's Conjecture up to {args.levy}:")
        print(f"  Verified: {results['verified']}")
        print(f"  Failed: {results['failed']}")
        if results['counterexamples']:
            print(f"  Counterexamples: {results['counterexamples'][:10]}")
        return
    
    if args.stats:
        start, end = args.stats
        stats = analyze_goldbach_statistics(end, step=max(1, (end-start)//100))
        for s in stats:
            if s.n >= start:
                print(f"n={s.n:6d}: parts={s.partition_count:4d}, HL={s.hl_estimate:8.2f}, "
                      f"ratio={s.ratio:.4f}, min=({s.minimal_partition[0]},{s.minimal_partition[1]})")
        return
    
    # Default: verify strong Goldbach
    if args.parallel:
        results = parallel_goldbach_verify(args.verify_up_to, args.workers)
    else:
        verifier = GoldbachVerifier()
        results = verifier.verify_up_to(args.verify_up_to)
    
    if results['counterexamples']:
        print(f"\n*** COUNTEREXAMPLES FOUND: {results['counterexamples'][:10]} ***")
    else:
        print(f"\nNo counterexamples found up to {args.verify_up_to:,}")


if __name__ == "__main__":
    main()