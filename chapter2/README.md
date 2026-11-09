# Chapter 2: Thread-Based Parallelism

A single script (`implementation.py`) that demonstrates the main tools of Python's `threading` module. Each concept is shown through a small everyday scenario instead of abstract counters, so the behaviour is easy to picture.

## What each demo shows

| # | Concept | Scenario | Idea |
|---|---------|----------|------|
| 1 | Defining & naming threads | Two baristas making drinks | `Thread(target=..., name=...)`, `current_thread()`, `join()` |
| 2 | Custom thread class | File downloader | Subclass `Thread`, override `run()`, store a result |
| 3 | Lock | Shared bank account | Prevent lost updates with `with lock:` |
| 4 | RLock | Inventory restock | The same thread may re-acquire the lock safely |
| 5 | Semaphore | Parking lot with 3 spaces | Limit how many threads use a resource at once |
| 6 | Barrier | Runners at a start line | All threads wait until everyone arrives |
| 7 | Event | Traffic light | One thread signals many waiting threads |
| 8 | Condition | Chef and waiter sharing a shelf | `wait()` / `notify_all()` on a shared state |
| 9 | Queue | Task dispatcher with workers | Thread-safe work distribution and stop signals |
| 10 | ThreadPoolExecutor | Loading pages concurrently | Reuse a fixed pool of threads |

## Requirements
Python 3.8 or newer. No external packages are needed.

## How to run
```bash
python implementation.py
```
Output order from concurrent threads can vary between runs; that is expected.

## Notes
- Threads share memory, so any shared data that is modified needs a lock or a thread-safe structure like `Queue`.
- Threads work well for waiting-heavy (I/O) tasks. For CPU-heavy work, see the process-based chapter.
