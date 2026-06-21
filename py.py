import itertools
import multiprocessing
import sys
import time

# Character pool including lowercase, uppercase, digits, and special characters
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$_- "


def init_worker(shared_value):
    """Initialize shared counter memory for each CPU process."""
    global counter
    counter = shared_value


def core_worker(length, core_id, step, target_indices, chars_len):
    """Execute combinatorial search using indexed matrix representation."""
    global counter
    local_count = 0
    local_c_lock = counter.get_lock

    # Calculate total combinations for the current length
    total_combos = chars_len**length

    # Each worker handles its own interleaved subset of index space
    for combo_idx in range(core_id, total_combos, step):
        local_count += 1

        # Reconstruct character indices from sequence number
        temp = combo_idx
        is_match = True

        # Validate sequence matching in reverse order for performance optimization
        for i in range(length - 1, -1, -1):
            char_idx = temp % chars_len
            if char_idx != target_indices[i]:
                is_match = False
                break
            temp //= chars_len

        # Buffering: Flush metrics to shared memory less frequently
        if local_count >= 2500000:
            with local_c_lock():
                counter.value += local_count
            local_count = 0

        if is_match:
            with local_c_lock():
                counter.value += local_count
            return True
    return False


if __name__ == "__main__":
    multiprocessing.freeze_support()

    print("=" * 60)
    print(" MULTIPROCESSING PERFORMANCE BENCHMARK & SEARCH TOOL")
    print("=" * 60)

    target_password = input("Enter target string to benchmark: ").strip()
    if not target_password:
        print("Error: Input cannot be empty.")
        exit()

    if any(c not in CHARS for c in target_password):
        print("Error: Input contains characters not present in CHARS dictionary.")
        exit()

    num_cores = multiprocessing.cpu_count()
    print(f"Detected CPU cores: {num_cores}. Allocating resources...")
    print("-" * 60)
    time.sleep(0.5)

    # Convert target string to numerical indices for performance scaling
    char_to_idx = {c: i for i, c in enumerate(CHARS)}
    target_indices = [char_to_idx[c] for c in target_password]
    chars_len = len(CHARS)

    shared_counter = multiprocessing.Value("q", 0)
    start_time = time.time()
    total_tested_all_lengths = 0
    found = False
    target_len = len(target_password)

    length = target_len
    current_length_combos = chars_len**length
    
    # Initialize the process pool
    pool = multiprocessing.Pool(
        processes=num_cores,
        initializer=init_worker,
        initargs=(shared_counter,),
    )
    results = []

    for i in range(num_cores):
        r = pool.apply_async(
            core_worker, args=(length, i, num_cores, target_indices, chars_len)
        )
        results.append(r)

    pool.close()

    # Main monitoring loop
    while True:
        ready_cores = sum(1 for r in results if r.ready())
        current_checked = shared_counter.value
        elapsed = time.time() - start_time
        if elapsed < 0.001:
            elapsed = 0.001

        speed = current_checked / elapsed

        # Display progress telemetry
        sys.stdout.write(
            f"\rLength: {length} | Checked: {current_checked:,} / {current_length_combos:,} | "
            f"Speed: {speed / 1_000_000:.2f} Mln/sec"
        )
        sys.stdout.flush()

        if any(r.ready() and r.get() for r in results):
            found = True
            break

        if ready_cores == num_cores:
            break

        time.sleep(0.05)

    pool.terminate()
    pool.join()

    end_time = time.time()
    total_time = end_time - start_time

    if found:
        print("\n" + "=" * 60)
        print(" TASK COMPLETED SUCCESSFULLY")
        print(f" Target String Recovered: {target_password}")
        print(f" Execution Time: {total_time:.4f} sec.")
        print(f" Peak Processing Speed: {current_checked / total_time / 1_000_000:.2f} Mln/sec")
        print("=" * 60)
    else:
        print("\nProcess finished. Target string was not recovered.")
