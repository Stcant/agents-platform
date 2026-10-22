# Performance reference

## Before optimizing

- Is there an observable requirement or a measurement that shows a problem? Name it.
- What is the actual input size and growth? Small, bounded work does not need optimization.

## Where the cost usually is

- Query count per request: is this an N+1? Are all rows loaded when only an aggregate is needed?
- Unbounded work: full scans, unbounded lists, loading whole files or tables into memory.
- Repeated work in loops: parsing, I/O, or identical computation.
- I/O latency: sequential calls that could be combined or parallelized, with a bound.
- Memory growth: accumulating results, caches without eviction, per-request allocations that outlive the request.

## Caching

- Add a cache only with a measured benefit, an explicit key, an invalidation rule, and a bound.
- State which behavior becomes stale and for how long.

## Verification

Measure before and after with the same command and input. Report the numbers and their conditions, not an impression.
