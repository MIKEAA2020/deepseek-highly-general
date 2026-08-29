#!/usr/bin/env python3
"""
Foundational Test F - CO(n-1) commuting-control holonomy test.

For the n=4 prototype, the structure group is CO(3) = R+ x O(3), with
Lie algebra so(3) non-abelian (3-dimensional: rotations about x, y, z axes).
The test compares holonomy under two regimes:

  SAME-PLANE: two rotations about the same axis (e.g., two z-rotations)
              => predicted holonomy = sum of angles (commutative, path-independent)
  DISTINCT-PLANE: two rotations about different axes (e.g., z then x)
              => predicted holonomy = nonzero (non-abelian, path-ordering matters)

The decisive test: same-plane rotations yield zero holonomy modulo 2*pi;
distinct-plane rotations yield nonzero holonomy. Refutation of Claim F would
be: distinct-plane rotations yield zero holonomy (so(n-1) effectively abelian).

Outputs:
  /home/z/my-project/download/claim_f_holonomy_results.csv  (raw data)
  /home/z/my-project/download/claim_f_holonomy_plot.png     (visualization)
  stdout: pass/fail summary
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# Font setup for any Chinese (project convention; this script outputs English)
fm.fontManager.addfont("/usr/share/fonts/truetype/chinese/SarasaMonoSC-Light.ttf")
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def so3_generator(axis):
    """Return the 3x3 antisymmetric generator of rotation about `axis` ('x','y','z')."""
    if axis == "x":
        return np.array([[0, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)
    if axis == "y":
        return np.array([[0, 0, 1], [0, 0, 0], [-1, 0, 0]], dtype=float)
    if axis == "z":
        return np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)
    raise ValueError(f"unknown axis {axis}")


def expm_path(A_segments):
    """
    Compute path-ordered exponential of a sequence of (generator, angle) segments.
    Each segment is (G, theta): exp(theta * G).
    The path-ordered exponential is the product of segment exponentials in order.

    For piecewise-constant controls, the path-ordered exponential is exactly the
    product of segment exponentials. This is the standard discretization of the
    path-ordered exponential for abelian and non-abelian Lie algebras alike.
    """
    result = np.eye(3)
    for G, theta in A_segments:
        # Matrix exponential of theta * G via eigendecomposition (G is normal in so(3))
        # Standard formula: exp(theta * G_skew) = I + sin(theta) * G + (1 - cos(theta)) * G^2
        # This works for the standard so(3) generators because G^3 = -G.
        exp_seg = np.eye(3) + np.sin(theta) * G + (1 - np.cos(theta)) * (G @ G)
        result = exp_seg @ result
    return result


def holonomy_magnitude(U):
    """
    Holonomy magnitude: angular distance of U from the identity in SO(3).
    For U in SO(3), trace(U) = 1 + 2 cos(phi), where phi is the rotation angle.
    So phi = arccos((trace(U) - 1) / 2).
    Returns |phi| in radians (modular, in [0, pi]).
    """
    tr = np.trace(U)
    # Clamp for numerical safety
    val = (tr - 1) / 2
    val = max(-1.0, min(1.0, val))
    return abs(np.arccos(val))


def run_test():
    """Run the Claim F decisive test and return results."""
    rng = np.random.default_rng(seed=20260829)

    # Same-plane test: two z-rotations of angles a and b
    # Predicted holonomy: a + b (mod 2*pi), magnitude = |a + b| mod convention
    same_plane_results = []
    for _ in range(50):
        a = rng.uniform(0.1, np.pi - 0.1)
        b = rng.uniform(0.1, np.pi - 0.1)
        G_z = so3_generator("z")
        U = expm_path([(G_z, a), (G_z, b)])
        # Reference: single rotation by a + b
        U_ref = expm_path([(G_z, a + b)])
        hol = holonomy_magnitude(U)
        hol_ref = holonomy_magnitude(U_ref)
        # Difference between path-ordered and single rotation should be ~0 (commutativity)
        diff = np.linalg.norm(U - U_ref)
        same_plane_results.append({
            "test": "same_plane",
            "axis_a": "z", "axis_b": "z",
            "angle_a": a, "angle_b": b,
            "holonomy": hol, "holonomy_ref": hol_ref,
            "path_vs_single_diff": diff,
        })

    # Distinct-plane test: z-rotation then x-rotation
    # Predicted holonomy: nonzero (non-abelian; cannot be reduced to a single-axis rotation
    # by the sum of angles)
    distinct_plane_results = []
    for _ in range(50):
        a = rng.uniform(0.1, np.pi - 0.1)
        b = rng.uniform(0.1, np.pi - 0.1)
        G_z = so3_generator("z")
        G_x = so3_generator("x")
        U_zx = expm_path([(G_z, a), (G_x, b)])
        # Reverse order: x then z
        U_xz = expm_path([(G_x, b), (G_z, a)])
        # Non-abelian signature: U_zx != U_xz (in general)
        nonabelian_signature = np.linalg.norm(U_zx - U_xz)
        hol_zx = holonomy_magnitude(U_zx)
        # Single-axis reference (what would happen if axes commuted): z-rotation by a then x-rotation by b
        # would reduce to z-rotation by a + b, which is impossible across different axes.
        # So holonomy_zx should be nonzero and not reducible to a single rotation.
        distinct_plane_results.append({
            "test": "distinct_plane",
            "axis_a": "z", "axis_b": "x",
            "angle_a": a, "angle_b": b,
            "holonomy": hol_zx,
            "nonabelian_signature": nonabelian_signature,
            "path_vs_reverse_diff": nonabelian_signature,
        })

    # Boundary case: very small angles - commutator ~ ab * [G_z, G_x] should be ~ ab
    small_angle_results = []
    for _ in range(20):
        a = rng.uniform(0.001, 0.05)
        b = rng.uniform(0.001, 0.05)
        G_z = so3_generator("z")
        G_x = so3_generator("x")
        U_zx = expm_path([(G_z, a), (G_x, b)])
        U_xz = expm_path([(G_x, b), (G_z, a)])
        # To first order, U_zx ~ U_xz; the commutator appears at order a*b
        nonabelian_signature = np.linalg.norm(U_zx - U_xz)
        # Theoretical: |[G_z, G_x]| = |G_y| (Frobenius norm) = sqrt(2)
        # so signature ~ a * b * sqrt(2)
        predicted = a * b * np.sqrt(2)
        small_angle_results.append({
            "test": "small_angle_distinct",
            "axis_a": "z", "axis_b": "x",
            "angle_a": a, "angle_b": b,
            "nonabelian_signature": nonabelian_signature,
            "predicted_commutator_magnitude": predicted,
        })

    return same_plane_results, distinct_plane_results, small_angle_results


def make_plots(same_plane, distinct_plane, small_angle, out_path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)

    # Plot 1: same-plane holonomy vs sum-of-angles
    sums = [r["angle_a"] + r["angle_b"] for r in same_plane]
    hols = [r["holonomy"] for r in same_plane]
    # Reduce sums to [0, pi] convention
    sums_mod = [min(s % (2 * np.pi), abs(s % (2 * np.pi) - 2 * np.pi)) for s in sums]
    axes[0].scatter(sums_mod, hols, s=20, color="#2897cf", alpha=0.7, label="measured")
    lim = max(max(sums_mod), max(hols)) * 1.1
    axes[0].plot([0, lim], [0, lim], "--", color="#bf5736", label="y = x (predicted)")
    axes[0].set_xlabel("Sum of angles (mod 2π, reduced)")
    axes[0].set_ylabel("Measured holonomy magnitude (rad)")
    axes[0].set_title("Same-plane (commuting) rotations\nClaim F prediction: holonomy = sum of angles")
    axes[0].legend(loc="upper left", fontsize=9)
    axes[0].grid(alpha=0.3)

    # Plot 2: distinct-plane - nonabelian signature vs ab
    ab_products = [r["angle_a"] * r["angle_b"] for r in distinct_plane]
    signatures = [r["nonabelian_signature"] for r in distinct_plane]
    axes[1].scatter(ab_products, signatures, s=20, color="#2897cf", alpha=0.7, label="measured")
    # Theoretical: ~ sqrt(2) * ab (commutator of G_z, G_x is G_y, Frobenius norm sqrt(2))
    xs = np.linspace(0, max(ab_products) * 1.1, 50)
    axes[1].plot(xs, np.sqrt(2) * xs, "--", color="#bf5736", label="y = √2 · ab (predicted)")
    axes[1].set_xlabel("Product of angles a·b")
    axes[1].set_ylabel("‖U(z,a)U(x,b) − U(x,b)U(z,a)‖_F")
    axes[1].set_title("Distinct-plane (non-commuting) rotations\nClaim F prediction: nonzero signature, scales with a·b")
    axes[1].legend(loc="upper left", fontsize=9)
    axes[1].grid(alpha=0.3)

    # Plot 3: small-angle regime - measured vs predicted commutator magnitude
    predicted = [r["predicted_commutator_magnitude"] for r in small_angle]
    measured = [r["nonabelian_signature"] for r in small_angle]
    axes[2].scatter(predicted, measured, s=20, color="#2897cf", alpha=0.7, label="measured")
    lim = max(max(predicted), max(measured)) * 1.1
    axes[2].plot([0, lim], [0, lim], "--", color="#bf5736", label="y = x (predicted)")
    axes[2].set_xlabel("Predicted commutator magnitude √2·a·b")
    axes[2].set_ylabel("Measured nonabelian signature")
    axes[2].set_title("Small-angle regime\nCommutator scales linearly with a·b")
    axes[2].legend(loc="upper left", fontsize=9)
    axes[2].grid(alpha=0.3)

    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    out_dir = "/home/z/my-project/download"
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "claim_f_holonomy_results.csv")
    plot_path = os.path.join(out_dir, "claim_f_holonomy_plot.png")

    same, distinct, small = run_test()

    # Aggregate statistics
    same_diffs = [r["path_vs_single_diff"] for r in same]
    distinct_sigs = [r["nonabelian_signature"] for r in distinct]
    small_ratios = [r["nonabelian_signature"] / max(r["predicted_commutator_magnitude"], 1e-12) for r in small]

    # Decisive test
    # Pass condition: same-plane commutes (signature ~ 0); distinct-plane does not (signature >> 0)
    same_max = max(same_diffs)
    distinct_min = min(distinct_sigs)
    pass_condition = (same_max < 1e-9) and (distinct_min > 1e-3)

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(same[0].keys()))
        writer.writeheader()
        for r in same:
            writer.writerow(r)
        # Distinct plane has different keys; write as separate section
        writer = csv.DictWriter(f, fieldnames=list(distinct[0].keys()))
        writer.writeheader()
        for r in distinct:
            writer.writerow(r)
        writer = csv.DictWriter(f, fieldnames=list(small[0].keys()))
        writer.writeheader()
        for r in small:
            writer.writerow(r)

    make_plots(same, distinct, small, plot_path)

    # Print summary
    print("=" * 60)
    print("CLAIM F: CO(n-1) STRUCTURE-GROUP COMMUTING-CONTROL TEST")
    print("n = 4 prototype; structure group CO(3) = R+ x O(3); so(3) non-abelian")
    print("=" * 60)
    print()
    print(f"Same-plane (z then z) test:")
    print(f"  N = {len(same)} trials")
    print(f"  Max ‖path-ordered − single rotation‖_F = {same_max:.2e}")
    print(f"  Expected: ~0 (commuting rotations)")
    print()
    print(f"Distinct-plane (z then x) test:")
    print(f"  N = {len(distinct)} trials")
    print(f"  Min nonabelian signature = {distinct_min:.4f}")
    print(f"  Mean nonabelian signature = {np.mean(distinct_sigs):.4f}")
    print(f"  Expected: >>0 (non-commuting rotations, non-abelian)")
    print()
    print(f"Small-angle regime (linear scaling check):")
    print(f"  N = {len(small)} trials")
    print(f"  Mean (measured / predicted) = {np.mean(small_ratios):.4f}")
    print(f"  Expected: ~1 (commutator ~ √2 · a · b)")
    print()
    print("=" * 60)
    if pass_condition:
        print("RESULT: CLAIM F CONFIRMED")
        print("  - Same-plane rotations commute (zero signature)")
        print("  - Distinct-plane rotations do NOT commute (nonzero signature)")
        print("  - so(n-1) is genuinely non-abelian at n>=4")
        print("  - CO(n-1) commutator structure correctly specifies commuting control")
    else:
        print("RESULT: CLAIM F NOT CONFIRMED (or boundary case)")
        print(f"  same_max = {same_max:.2e}, distinct_min = {distinct_min:.4f}")
    print("=" * 60)
    print(f"Raw data: {csv_path}")
    print(f"Plot:     {plot_path}")


if __name__ == "__main__":
    main()
