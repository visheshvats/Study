#!/usr/bin/env python3
"""
Quantization Fixtures — FP32 → INT8 Matrix Compression
=========================================================
Pure-Python implementation of weight quantization demonstrating:

  • Symmetric uniform quantization (FP32 → INT8)
  • Asymmetric quantization with zero-point offset
  • Per-tensor vs per-channel scaling strategies
  • Dequantization and accuracy measurement
  • Memory savings calculation

No external dependencies required (no NumPy).

Run:
    python quantization_fixtures.py
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple

random.seed(42)

# Type aliases
Matrix = List[List[float]]
IntMatrix = List[List[int]]


# ── Matrix Utilities ───────────────────────────────────────────────────────
def create_random_matrix(rows: int, cols: int, scale: float = 1.0) -> Matrix:
    """Generate a random float matrix simulating neural network weights."""
    return [[random.gauss(0, scale) for _ in range(cols)] for _ in range(rows)]


def matrix_abs_max(M: Matrix) -> float:
    """Find the absolute maximum value in a matrix."""
    return max(abs(x) for row in M for x in row)


def matrix_min_max(M: Matrix) -> Tuple[float, float]:
    """Find min and max values in a matrix."""
    flat = [x for row in M for x in row]
    return min(flat), max(flat)


def matrix_mse(A: Matrix, B: Matrix) -> float:
    """Mean squared error between two matrices."""
    total = 0.0
    count = 0
    for ra, rb in zip(A, B):
        for a, b in zip(ra, rb):
            total += (a - b) ** 2
            count += 1
    return total / count


def matrix_shape(M) -> Tuple[int, int]:
    return len(M), len(M[0])


# ── Symmetric Quantization (FP32 → INT8) ──────────────────────────────────
@dataclass
class QuantizedTensor:
    """A quantized representation of a float matrix."""
    int_data: IntMatrix
    scale: float           # Per-tensor scale factor
    zero_point: int        # Zero-point offset (0 for symmetric)
    bit_width: int         # 8 for INT8
    original_shape: Tuple[int, int]
    strategy: str          # "symmetric" or "asymmetric"


def symmetric_quantize(M: Matrix, bit_width: int = 8) -> QuantizedTensor:
    """
    Symmetric uniform quantization:

      scale = max(|W|) / (2^(b-1) - 1)
      W_int = round(W / scale)
      W_int = clamp(W_int, -2^(b-1), 2^(b-1) - 1)

    For INT8: range is [-128, 127], scale = max(|W|) / 127
    """
    max_abs = matrix_abs_max(M)
    qmax = (1 << (bit_width - 1)) - 1  # 127 for INT8
    qmin = -(1 << (bit_width - 1))     # -128 for INT8

    scale = max_abs / qmax if max_abs > 0 else 1.0

    int_data: IntMatrix = []
    for row in M:
        int_row = []
        for val in row:
            q = round(val / scale)
            q = max(qmin, min(qmax, q))  # Clamp
            int_row.append(q)
        int_data.append(int_row)

    return QuantizedTensor(
        int_data=int_data,
        scale=scale,
        zero_point=0,
        bit_width=bit_width,
        original_shape=matrix_shape(M),
        strategy="symmetric",
    )


def asymmetric_quantize(M: Matrix, bit_width: int = 8) -> QuantizedTensor:
    """
    Asymmetric quantization with zero-point offset:

      scale = (max(W) - min(W)) / (2^b - 1)
      zero_point = round(-min(W) / scale)
      W_int = round(W / scale) + zero_point
      W_int = clamp(W_int, 0, 2^b - 1)

    For UINT8: range is [0, 255]
    """
    w_min, w_max = matrix_min_max(M)
    qmax = (1 << bit_width) - 1  # 255 for 8-bit

    scale = (w_max - w_min) / qmax if (w_max - w_min) > 0 else 1.0
    zero_point = round(-w_min / scale)
    zero_point = max(0, min(qmax, zero_point))

    int_data: IntMatrix = []
    for row in M:
        int_row = []
        for val in row:
            q = round(val / scale) + zero_point
            q = max(0, min(qmax, q))
            int_row.append(q)
        int_data.append(int_row)

    return QuantizedTensor(
        int_data=int_data,
        scale=scale,
        zero_point=zero_point,
        bit_width=bit_width,
        original_shape=matrix_shape(M),
        strategy="asymmetric",
    )


def per_channel_quantize(M: Matrix, bit_width: int = 8) -> List[QuantizedTensor]:
    """
    Per-channel (per-row) quantization — each output channel gets its
    own scale factor, reducing quantization error for channels with
    different weight magnitude ranges.
    """
    results = []
    for row in M:
        row_matrix = [row]
        qt = symmetric_quantize(row_matrix, bit_width)
        results.append(qt)
    return results


# ── Dequantization ────────────────────────────────────────────────────────
def dequantize(qt: QuantizedTensor) -> Matrix:
    """
    Reconstruct float values from quantized representation:

      W_approx = scale × (W_int - zero_point)
    """
    result: Matrix = []
    for row in qt.int_data:
        float_row = [qt.scale * (q - qt.zero_point) for q in row]
        result.append(float_row)
    return result


# ── Analysis ──────────────────────────────────────────────────────────────
def memory_analysis(original: Matrix, bit_width: int = 8) -> dict:
    """Calculate memory savings from quantization."""
    rows, cols = matrix_shape(original)
    elements = rows * cols
    fp32_bytes = elements * 4       # 4 bytes per FP32
    int8_bytes = elements * 1       # 1 byte per INT8
    int4_bytes = elements * 0.5     # 0.5 bytes per INT4

    return {
        "elements": elements,
        "fp32_mb": fp32_bytes / (1024 * 1024),
        "int8_mb": int8_bytes / (1024 * 1024),
        "int4_mb": int4_bytes / (1024 * 1024),
        "int8_ratio": fp32_bytes / int8_bytes,
        "int4_ratio": fp32_bytes / int4_bytes,
    }


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("QUANTIZATION FIXTURES — FP32 → INT8 Matrix Compression")
    print("=" * 72)

    # Create a mock weight matrix (simulate a linear layer)
    rows, cols = 8, 8
    original = create_random_matrix(rows, cols, scale=2.0)

    print(f"\n  Weight Matrix: {rows}×{cols} (FP32)")
    print(f"  Value range: [{matrix_min_max(original)[0]:.4f}, {matrix_min_max(original)[1]:.4f}]")
    print(f"  Abs max: {matrix_abs_max(original):.4f}")

    # 1. Symmetric quantization
    print(f"\n{'─' * 60}")
    print("  1. SYMMETRIC QUANTIZATION (INT8, range [-128, 127])")
    print(f"{'─' * 60}")
    qt_sym = symmetric_quantize(original)
    deq_sym = dequantize(qt_sym)
    mse_sym = matrix_mse(original, deq_sym)
    print(f"  Scale factor: {qt_sym.scale:.6f}")
    print(f"  Zero point:   {qt_sym.zero_point}")
    print(f"  MSE error:    {mse_sym:.8f}")
    print(f"  RMSE:         {math.sqrt(mse_sym):.6f}")

    # Show sample values
    print(f"\n  Sample values (first row):")
    print(f"  {'Original':>10s}  {'Quantized':>10s}  {'Dequantized':>12s}  {'Error':>10s}")
    for i in range(min(cols, 8)):
        orig = original[0][i]
        qval = qt_sym.int_data[0][i]
        deq = deq_sym[0][i]
        err = abs(orig - deq)
        print(f"  {orig:>10.4f}  {qval:>10d}  {deq:>12.4f}  {err:>10.6f}")

    # 2. Asymmetric quantization
    print(f"\n{'─' * 60}")
    print("  2. ASYMMETRIC QUANTIZATION (UINT8, range [0, 255])")
    print(f"{'─' * 60}")
    qt_asym = asymmetric_quantize(original)
    deq_asym = dequantize(qt_asym)
    mse_asym = matrix_mse(original, deq_asym)
    print(f"  Scale factor: {qt_asym.scale:.6f}")
    print(f"  Zero point:   {qt_asym.zero_point}")
    print(f"  MSE error:    {mse_asym:.8f}")
    print(f"  RMSE:         {math.sqrt(mse_asym):.6f}")

    # 3. Different bit widths
    print(f"\n{'─' * 60}")
    print("  3. BIT-WIDTH COMPARISON")
    print(f"{'─' * 60}")
    print(f"  {'Bits':>5s}  {'Levels':>7s}  {'Scale':>10s}  {'MSE':>12s}  {'RMSE':>10s}")
    for bits in [2, 4, 8, 16]:
        qt = symmetric_quantize(original, bits)
        deq = dequantize(qt)
        mse = matrix_mse(original, deq)
        levels = 1 << bits
        print(f"  {bits:>5d}  {levels:>7d}  {qt.scale:>10.6f}  {mse:>12.8f}  {math.sqrt(mse):>10.6f}")

    # 4. Memory savings (scaled to real model dimensions)
    print(f"\n{'─' * 60}")
    print("  4. MEMORY SAVINGS (Scaled to Real Model Dimensions)")
    print(f"{'─' * 60}")

    model_configs = [
        ("Phi-3 (3.8B params)", 3_800_000_000),
        ("Llama-3 7B",          7_000_000_000),
        ("Llama-3 70B",        70_000_000_000),
        ("GPT-4 (est. 200B)", 200_000_000_000),
    ]

    print(f"  {'Model':<22s}  {'FP32':>8s}  {'FP16':>8s}  {'INT8':>8s}  {'INT4':>8s}")
    for name, params in model_configs:
        fp32 = params * 4 / (1024**3)       # GB
        fp16 = params * 2 / (1024**3)
        int8 = params * 1 / (1024**3)
        int4 = params * 0.5 / (1024**3)
        print(f"  {name:<22s}  {fp32:>6.1f}GB  {fp16:>6.1f}GB  {int8:>6.1f}GB  {int4:>6.1f}GB")

    # 5. Per-channel demo
    print(f"\n{'─' * 60}")
    print("  5. PER-TENSOR vs PER-CHANNEL QUANTIZATION")
    print(f"{'─' * 60}")

    # Create a matrix with channels of very different scales
    unbalanced = create_random_matrix(4, 8, scale=1.0)
    # Make one channel have much larger values
    unbalanced[2] = [x * 10 for x in unbalanced[2]]

    qt_tensor = symmetric_quantize(unbalanced)
    deq_tensor = dequantize(qt_tensor)
    mse_tensor = matrix_mse(unbalanced, deq_tensor)

    # Per-channel
    channel_qts = per_channel_quantize(unbalanced)
    deq_channels: Matrix = []
    for cqt in channel_qts:
        deq_channels.extend(dequantize(cqt))
    mse_channel = matrix_mse(unbalanced, deq_channels)

    print(f"  Per-tensor MSE:  {mse_tensor:.8f}")
    print(f"  Per-channel MSE: {mse_channel:.8f}")
    print(f"  Improvement:     {((mse_tensor - mse_channel) / mse_tensor * 100):.1f}%")
    print(f"  (Per-channel uses separate scale per output channel,")
    print(f"   reducing error when channel magnitudes vary widely)")

    # Architecture summary
    print(f"\n{'═' * 72}")
    print("  QUANTIZATION PIPELINE:")
    print("  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐")
    print("  │  FP32 Weights│    │  Calibration │    │  INT8 Weights│")
    print("  │  (Original)  │───▶│  (Scale, ZP) │───▶│  (Compressed)│")
    print("  │  4 bytes/val │    │  statistics   │    │  1 byte/val  │")
    print("  └──────────────┘    └──────────────┘    └──────────────┘")
    print("                                                │")
    print("  ┌──────────────┐    ┌──────────────┐         │")
    print("  │  FP32 Output │◀───│  Dequantize  │◀────────┘")
    print("  │  (Inference) │    │  scale×(q-zp) │   (at inference)")
    print("  └──────────────┘    └──────────────┘")
    print("═" * 72)


if __name__ == "__main__":
    run_demo()
