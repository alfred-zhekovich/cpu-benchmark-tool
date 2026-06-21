# Multiprocessing Performance Benchmark & Search Tool

A high-performance, multi-core benchmarking utility written in Python. It evaluates CPU processing power by performing a matrix-based combinatorial search across an indexed character space.

## Features
- **True Multiprocessing:** Automatically detects and scales workload across all available CPU cores using Python's `multiprocessing` module.
- **Index-Based Optimization:** Eliminates runtime string concatenation bottlenecks by managing candidate sequences as numerical index arrays.
- **Thread-Safe Buffering:** Utilizes atomic shared memory locks with metrics buffering to maximize raw computing throughput.
- **Telemetry Feedback:** Provides live console updates including calculation speed (Million operations/sec) and total execution time.

## Dictionary Space
The utility evaluates combinations against a pool of characters including lowercase, uppercase, digits, and special symbols.

## Requirements
- Python 3.10 or higher
- No external dependencies (uses standard library modules only)

## Usage
Run the script via your terminal or command prompt:
```bash
python py.py
```

## Disclaimer
This project is developed strictly for educational purposes, hardware performance evaluation, and computational benchmarking.
