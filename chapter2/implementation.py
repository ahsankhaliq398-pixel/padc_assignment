"""
Chapter 2 - Thread-Based Parallelism
Each demo uses a small real-world scenario to show one threading concept.
"""
import threading
import time
import random
from queue import Queue
from concurrent.futures import ThreadPoolExecutor


# ------------------------------------------------------------
# 1. Defining and naming threads: a café with two baristas
# ------------------------------------------------------------
def make_coffee(drink):
    me = threading.current_thread()
    print(f"[{me.name}] started making a {drink}")
    time.sleep(0.5)
    print(f"[{me.name}] finished the {drink}")


def demo_naming():
    print("\n=== 1. Defining & Naming Threads ===")
    baristas = [
        threading.Thread(target=make_coffee, args=("latte",), name="Barista-Sara"),
        threading.Thread(target=make_coffee, args=("espresso",), name="Barista-Omar"),
    ]
    for b in baristas:
        b.start()
    for b in baristas:
        b.join()
    print(f"Threads still running: {threading.active_count()} (main only)")


# ------------------------------------------------------------
# 2. Custom thread class: a file downloader simulation
# ------------------------------------------------------------
class Downloader(threading.Thread):
    def __init__(self, filename, size_mb):
        super().__init__(name=f"DL-{filename}")
        self.filename = filename
        self.size_mb = size_mb
        self.result = None

    def run(self):
        print(f"Downloading {self.filename} ({self.size_mb} MB)...")
        time.sleep(self.size_mb * 0.1)
        self.result = f"{self.filename} done"


def demo_custom_thread():
    print("\n=== 2. Custom Thread Class ===")
    jobs = [Downloader("video.mp4", 8), Downloader("song.mp3", 3), Downloader("doc.pdf", 1)]
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
        print(f"Result from {j.name}: {j.result}")


# ------------------------------------------------------------
# 3. Lock: a shared bank account (race condition fixed)
# ------------------------------------------------------------
class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()

    def deposit(self, amount):
        with self.lock:
            current = self.balance
            time.sleep(0.01)  # widens the race window if the lock is removed
            self.balance = current + amount


def demo_lock():
    print("\n=== 3. Lock ===")
    account = BankAccount(100)
    threads = [threading.Thread(target=account.deposit, args=(10,)) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"Balance after 10 deposits of 10: {account.balance} (expected 200)")


# ------------------------------------------------------------
# 4. RLock: a method that calls another locked method
# ------------------------------------------------------------
class Inventory:
    def __init__(self):
        self.items = {}
        self.rlock = threading.RLock()

    def add(self, name, qty):
        with self.rlock:
            self.items[name] = self.items.get(name, 0) + qty

    def restock(self, mapping):
        with self.rlock:  # re-acquired inside add() by the same thread
            for name, qty in mapping.items():
                self.add(name, qty)


def demo_rlock():
    print("\n=== 4. RLock ===")
    inv = Inventory()
    inv.restock({"apples": 5, "pears": 3})
    print(f"Inventory: {inv.items}")
    print("A plain Lock here would have deadlocked; RLock lets the owner re-enter.")


# ------------------------------------------------------------
# 5. Semaphore: a parking lot with 3 spaces
# ------------------------------------------------------------
def park_car(car_id, spaces):
    print(f"Car {car_id} is waiting for a space")
    with spaces:
        print(f"Car {car_id} parked")
        time.sleep(0.6)
    print(f"Car {car_id} left")


def demo_semaphore():
    print("\n=== 5. Semaphore ===")
    spaces = threading.BoundedSemaphore(3)
    cars = [threading.Thread(target=park_car, args=(i, spaces)) for i in range(1, 6)]
    for c in cars:
        c.start()
    for c in cars:
        c.join()


# ------------------------------------------------------------
# 6. Barrier: runners wait at the start line
# ------------------------------------------------------------
def runner(name, start_line):
    time.sleep(random.uniform(0.1, 0.8))
    print(f"{name} is at the start line")
    start_line.wait()
    print(f"{name} is running!")


def demo_barrier():
    print("\n=== 6. Barrier ===")
    start_line = threading.Barrier(4)
    names = ["Ali", "Bina", "Chen", "Dara"]
    threads = [threading.Thread(target=runner, args=(n, start_line)) for n in names]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ------------------------------------------------------------
# 7. Event: a traffic light
# ------------------------------------------------------------
def pedestrian(name, green_light):
    green_light.wait()
    print(f"{name} crosses the road")


def demo_event():
    print("\n=== 7. Event ===")
    green_light = threading.Event()
    people = [threading.Thread(target=pedestrian, args=(f"Person-{i}", green_light)) for i in range(3)]
    for p in people:
        p.start()
    print("Light is red, everyone waits...")
    time.sleep(1)
    print("Light turns green!")
    green_light.set()
    for p in people:
        p.join()


# ------------------------------------------------------------
# 8. Condition: a restaurant pass with a limited shelf
# ------------------------------------------------------------
def chef(shelf, cond, capacity, plates):
    for i in range(plates):
        with cond:
            while len(shelf) >= capacity:
                cond.wait()
            shelf.append(f"plate-{i}")
            print(f"Chef placed plate-{i} (shelf: {len(shelf)})")
            cond.notify_all()
        time.sleep(0.1)


def waiter(shelf, cond, plates):
    served = 0
    while served < plates:
        with cond:
            while not shelf:
                cond.wait()
            item = shelf.pop(0)
            print(f"Waiter served {item}")
            served += 1
            cond.notify_all()
        time.sleep(0.3)


def demo_condition():
    print("\n=== 8. Condition ===")
    shelf, cond = [], threading.Condition()
    t1 = threading.Thread(target=chef, args=(shelf, cond, 2, 5))
    t2 = threading.Thread(target=waiter, args=(shelf, cond, 5))
    t1.start(); t2.start()
    t1.join(); t2.join()


# ------------------------------------------------------------
# 9. Queue: a task dispatcher with worker threads
# ------------------------------------------------------------
def queue_worker(tasks, results):
    while True:
        n = tasks.get()
        if n is None:
            tasks.task_done()
            break
        results.append((n, n ** 2))
        tasks.task_done()


def demo_queue():
    print("\n=== 9. Queue ===")
    tasks, results = Queue(), []
    workers = [threading.Thread(target=queue_worker, args=(tasks, results)) for _ in range(3)]
    for w in workers:
        w.start()
    for n in range(1, 9):
        tasks.put(n)
    for _ in workers:
        tasks.put(None)  # one stop signal per worker
    tasks.join()
    for w in workers:
        w.join()
    print(f"Squares computed: {sorted(results)}")


# ------------------------------------------------------------
# 10. ThreadPoolExecutor: fetching "pages" concurrently
# ------------------------------------------------------------
def fetch_page(page):
    time.sleep(0.3)
    return f"page-{page} loaded"


def demo_thread_pool():
    print("\n=== 10. ThreadPoolExecutor ===")
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch_page, range(1, 9)))
    print(results)
    print(f"8 pages in {time.time() - start:.1f}s (sequentially it would take ~2.4s)")


if __name__ == "__main__":
    print("##### CHAPTER 2: THREAD-BASED PARALLELISM #####")
    demo_naming()
    demo_custom_thread()
    demo_lock()
    demo_rlock()
    demo_semaphore()
    demo_barrier()
    demo_event()
    demo_condition()
    demo_queue()
    demo_thread_pool()
    print("\n##### ALL DEMOS COMPLETED #####")
