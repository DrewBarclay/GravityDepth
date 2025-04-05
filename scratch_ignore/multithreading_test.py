import threading
import time
import concurrent.futures
import numpy as np
from typing import List, Tuple
import math

def heavy_compute(n: int) -> float:
    """Pure Python CPU-intensive computation."""
    x = 0.0
    for i in range(n):
        x += math.sin(i) * math.cos(i)
    return x

def create_matrix(size: int) -> np.ndarray:
    """Create a random matrix of given size."""
    return np.random.rand(size, size)

def multiply_matrices(matrices: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    """Multiply two matrices and perform additional computations."""
    result = np.dot(matrices[0], matrices[1])
    # Add more CPU-intensive operations
    result = np.exp(result * 0.1)  # Element-wise operations
    result = np.sin(result)
    return result

def process_chunk(chunk: List[Tuple[np.ndarray, np.ndarray]]) -> List[np.ndarray]:
    """Process a chunk of matrix pairs with additional CPU work."""
    results = []
    for pair in chunk:
        # Do some pure Python computation first
        heavy_compute(100000)
        # Then do the matrix operations
        results.append(multiply_matrices(pair))
    return results

def main():
    # Print NumPy config
    print("NumPy configuration:")
    np.show_config()

    # Test parameters
    matrix_size = 1500  # Adjusted for balance
    num_pairs = 24     # Adjusted for more consistent load
    thread_counts = [1, 2, 4, 8, 16]  # Testing up to 16 threads
    num_runs = 3       # Number of runs for averaging

    # Create matrices
    print("\nCreating matrices...")
    matrices = [(create_matrix(matrix_size), create_matrix(matrix_size))
                for _ in range(num_pairs)]

    # Warmup run
    print("Performing warmup run...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        _ = list(executor.map(process_chunk, [matrices]))

    for num_threads in thread_counts:
        print(f"\nTesting with {num_threads} thread(s):")

        # Split work among threads
        chunk_size = max(1, len(matrices) // num_threads)
        chunks = [matrices[i:i + chunk_size] for i in range(0, len(matrices), chunk_size)]

        # Run multiple times and average
        total_time = 0
        for run in range(num_runs):
            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                results = list(executor.map(process_chunk, chunks))

            end_time = time.time()
            execution_time = end_time - start_time
            total_time += execution_time

            print(f"Run {run + 1}: {execution_time:.2f} seconds")

        avg_execution_time = total_time / num_runs
        print(f"Average execution time: {avg_execution_time:.2f} seconds")

        # Calculate speedup relative to single thread
        if num_threads == 1:
            baseline_time = avg_execution_time
        else:
            speedup = baseline_time / avg_execution_time
            print(f"Speedup: {speedup:.2f}x")
            print(f"Theoretical max speedup: {num_threads}x")
            print(f"Efficiency: {(speedup/num_threads)*100:.1f}%")

if __name__ == "__main__":
    main()
