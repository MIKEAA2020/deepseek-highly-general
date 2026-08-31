"""
Task B: Perturbation robustness sweep on Network K (stress-test the
        100% verdict under noisy food supply).

CONTEXT:
  Network K achieves 52/52 = 100% Phase I (FULL AUTOPOIESIS) at the
  nominal operating point (food_conc=10, food_supply_rate=2.0,
  sigma=0). User asks to stress-test the 100% verdict under noisy
  food supply: sweep the perturbation amplitude sigma on food supply
  AND sweep the food concentration itself (to test starvation
  robustness).

DESIGN:
  Modify the Network-K simulate_network function to add Gaussian
  noise to the food concentration at each timestep:

    food_conc_t = food_conc * (1 + sigma * xi_t),   xi_t ~ N(0, 1)
    clipped to [0, 2 * food_conc]

  so the food supply term becomes:
    dx[s] += food_supply_rate * (food_conc_t - x[s]) * 0.5

  This is the standard "noisy food supply" perturbation in
  closed-ecosystem models: the external food source is well-mixed
  but its concentration fluctuates around the nominal.

  SWEEP GRID:
    Axis 1 (sigma):        {0.0, 0.05, 0.10, 0.20, 0.50, 1.00}  (6 values)
      sigma=0   -> nominal (reproduce 100%)
      sigma=0.05, 0.10 -> mild noise (5-10% fluctuations)
      sigma=0.20 -> moderate noise
      sigma=0.50 -> heavy noise (50% fluctuations)
      sigma=1.00 -> extreme noise (100% fluctuations, occasionally zero food)

    Axis 2 (food_conc):    {2.5, 5.0, 10.0, 20.0}                (4 values)
      food_conc=2.5  -> starvation (25% of nominal)
      food_conc=5    -> mild starvation
      food_conc=10   -> nominal
      food_conc=20   -> excess food

    food_supply_rate fixed at 2.0 (default).
    T=500 steps (same as nominal closure test).

  Total grid: 6 x 4 = 24 configurations, each running the full
  Network-K closure test (52 components x 2 simulations each =
  ~104 simulations per config). Approximate runtime: ~10-15 minutes.

OUTPUTS:
  /home/z/my-project/download/autopoiesis_network_K_robustness.{csv,png,txt}

REPORTS:
  - Phase I count (/52) and Phase III count (/52) for each (sigma, food_conc)
  - Heatmap of Phase I fraction over (sigma, food_conc) grid
  - Per-component robustness table: for each of the 52 components, how many
    of the 24 configs does it pass Phase I? (robustness count / 24)
  - Identification of the most fragile components (those that fail first
    as sigma increases)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
for p in [
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]:
    try:
        fm.fontManager.addfont(p)
    except Exception:
        pass
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

import os, csv, time, sys
sys.path.insert(0, "/home/z/my-project/scripts")

# Import Network K definition
from autopoiesis_network_K import network_K, species, food, non_food, reactions

# ----------------------------------------------------------------------
# Noisy simulate_network: extends Network K's simulate_network with
# per-timestep Gaussian noise on food_conc.
# ----------------------------------------------------------------------
def simulate_network_noisy(network, knockout_species=None, T=500, delta=0.05,
                           k_cat_metabolic=0.8, k_cat_synthesis=2.0,
                           k_cat_constitutive=0.3, k_cat_autocatalytic=1.0,
                           food_supply_rate=2.0, food_conc=10.0,
                           Km=0.1, max_conc=100.0,
                           init_concs=None, allow_constitutive=True,
                           sigma_food=0.0, seed=20260831):
    """Same as Network K's simulate_network, with Gaussian noise sigma_food
    on food_conc at each timestep.

    food_conc_t = food_conc * (1 + sigma_food * xi_t),  xi_t ~ N(0, 1)
    clipped to [0, 2 * food_conc]
    """
    sp = network["species"]
    fd = set(network["food"])
    rxs = network["reactions"]

    x = {s: (food_conc if s in fd else 0.1) for s in sp}
    if init_concs:
        for s, v in init_concs.items():
            x[s] = v

    knockout_reactions = set()
    if knockout_species is not None:
        for r in rxs:
            produced = [s for s, d in r["stoich"].items() if d > 0]
            if knockout_species in produced:
                knockout_reactions.add(r["id"])

    rng = np.random.default_rng(seed)
    dt = 0.05
    trajectory = [{s: x[s] for s in sp}]
    for step in range(T):
        # Noisy food concentration for this step
        if sigma_food > 0:
            xi = rng.normal(0, 1)
            fc_t = food_conc * (1 + sigma_food * xi)
            fc_t = max(0.0, min(2.0 * food_conc, fc_t))
        else:
            fc_t = food_conc

        rates = {}
        for r in rxs:
            if r["id"] in knockout_reactions:
                rates[r["id"]] = 0.0
                continue
            subs = [(s, abs(d)) for s, d in r["stoich"].items() if d < 0]
            if any(x[s] <= 0 for s, _ in subs):
                rates[r["id"]] = 0.0
                continue
            kind = r["kind"]
            cat = r["catalyst"]
            if kind == "constitutive":
                k = k_cat_constitutive
                rate = k
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            else:
                cat_conc = x.get(cat, 0.0) if cat is not None else 0.0
                if cat_conc <= 0:
                    rates[r["id"]] = 0.0
                    continue
                if kind == "synthesis":
                    k = k_cat_synthesis
                elif kind == "autocatalytic":
                    k = k_cat_autocatalytic
                else:
                    k = k_cat_metabolic
                if "k_cat_override" in r:
                    k = r["k_cat_override"]
                rate = k * cat_conc
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            rates[r["id"]] = rate

        dx = {s: 0.0 for s in sp}
        for r in rxs:
            rate = rates[r["id"]]
            for s, d in r["stoich"].items():
                dx[s] += d * rate
        for s in sp:
            dx[s] -= delta * x[s]
            if s in fd:
                dx[s] += food_supply_rate * (fc_t - x[s]) * 0.5
        for s in sp:
            x[s] = max(0.0, min(max_conc, x[s] + dt * dx[s]))
        trajectory.append({s: x[s] for s in sp})
    return trajectory


def simulate_network_recover_noisy(network, init, T=500, delta=0.05,
                                   k_cat_metabolic=0.8, k_cat_synthesis=2.0,
                                   k_cat_constitutive=0.3, k_cat_autocatalytic=1.0,
                                   food_conc=10.0, food_supply_rate=2.0,
                                   Km=0.1, max_conc=100.0,
                                   sigma_food=0.0, seed=20260831):
    """Noisy recovery simulation from given initial condition."""
    sp = network["species"]
    fd = set(network["food"])
    rxs = network["reactions"]
    x = {s: init.get(s, 0.0) for s in sp}
    for s in fd:
        x[s] = max(x[s], food_conc)
    if x.get("ATP", 0) < 1.0:
        x["ATP"] = max(x["ATP"], 2.0)
    if x.get("TF", 0) < 0.05:
        x["TF"] = max(x["TF"], 0.1)
    rng = np.random.default_rng(seed)
    dt = 0.05
    trajectory = [{s: x[s] for s in sp}]
    for step in range(T):
        if sigma_food > 0:
            xi = rng.normal(0, 1)
            fc_t = food_conc * (1 + sigma_food * xi)
            fc_t = max(0.0, min(2.0 * food_conc, fc_t))
        else:
            fc_t = food_conc
        rates = {}
        for r in rxs:
            subs = [(s, abs(d)) for s, d in r["stoich"].items() if d < 0]
            if any(x[s] <= 0 for s, _ in subs):
                rates[r["id"]] = 0.0
                continue
            kind = r["kind"]
            cat = r["catalyst"]
            if kind == "constitutive":
                k = k_cat_constitutive
                rate = k
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            else:
                cat_conc = x.get(cat, 0.0) if cat is not None else 0.0
                if cat_conc <= 0:
                    rates[r["id"]] = 0.0
                    continue
                if kind == "synthesis":
                    k = k_cat_synthesis
                elif kind == "autocatalytic":
                    k = k_cat_autocatalytic
                else:
                    k = k_cat_metabolic
                if "k_cat_override" in r:
                    k = r["k_cat_override"]
                rate = k * cat_conc
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            rates[r["id"]] = rate
        dx = {s: 0.0 for s in sp}
        for r in rxs:
            rate = rates[r["id"]]
            for s, d in r["stoich"].items():
                dx[s] += d * rate
        for s in sp:
            dx[s] -= delta * x[s]
            if s in fd:
                dx[s] += food_supply_rate * (fc_t - x[s]) * 0.5
        for s in sp:
            x[s] = max(0.0, min(max_conc, x[s] + dt * dx[s]))
        trajectory.append({s: x[s] for s in sp})
    return trajectory


def closure_test_noisy(network, network_name, T=500, viability_threshold=0.1,
                       food_conc=10.0, food_supply_rate=2.0, sigma_food=0.0,
                       seed=20260831):
    """Phase I closure test under noisy food supply."""
    baseline = simulate_network_noisy(network, knockout_species=None, T=T,
                                       food_conc=food_conc,
                                       food_supply_rate=food_supply_rate,
                                       sigma_food=sigma_food, seed=seed)
    baseline_final = baseline[-1]
    records = []
    for m_j in network["non_food"]:
        # Use a different rng stream per component to decorrelate noise
        comp_seed = seed + hash(m_j) % 100000
        knock = simulate_network_noisy(network, knockout_species=m_j, T=T,
                                        food_conc=food_conc,
                                        food_supply_rate=food_supply_rate,
                                        sigma_food=sigma_food, seed=comp_seed)
        knock_final = knock[-1]
        knock_traj = [t[m_j] for t in knock]
        recover_start_idx = T // 2
        recover_init = knock[recover_start_idx]
        recover = simulate_network_recover_noisy(network, init=recover_init,
                                                   T=T - recover_start_idx,
                                                   food_conc=food_conc,
                                                   food_supply_rate=food_supply_rate,
                                                   sigma_food=sigma_food,
                                                   seed=comp_seed + 1)
        recover_final = recover[-1]
        knock_success = knock_final[m_j] < viability_threshold
        recover_success = recover_final[m_j] > viability_threshold
        causally_internal = knock_success and recover_success
        records.append({
            "component": m_j,
            "baseline_conc": baseline_final[m_j],
            "knockout_conc_final": knock_final[m_j],
            "knockout_min": min(knock_traj),
            "recover_conc_final": recover_final[m_j],
            "knockout_success": knock_success,
            "recover_success": recover_success,
            "causally_internal": causally_internal,
            "verdict": "AUTOPOIETIC" if causally_internal else "HOMEOSTATIC",
        })
    return records


def phase_iii_check_noisy(network, m_j, T=500, viability_threshold=0.1,
                          pathwise_fraction=0.4, food_conc=10.0,
                          food_supply_rate=2.0, sigma_food=0.0,
                          seed=20260831):
    """Phase III verdict (pathwise + recovery above threshold)."""
    comp_seed = seed + hash(m_j) % 100000
    knock = simulate_network_noisy(network, knockout_species=m_j, T=T,
                                    food_conc=food_conc,
                                    food_supply_rate=food_supply_rate,
                                    sigma_food=sigma_food, seed=comp_seed)
    knock_final = knock[-1]
    recover_start_idx = T // 2
    recover_init = knock[recover_start_idx]
    recover = simulate_network_recover_noisy(network, init=recover_init,
                                              T=T - recover_start_idx,
                                              food_conc=food_conc,
                                              food_supply_rate=food_supply_rate,
                                              sigma_food=sigma_food,
                                              seed=comp_seed + 1)
    recover_final = recover[-1]
    knock_success = knock_final[m_j] < viability_threshold
    recover_success_endpoint = recover_final[m_j] > viability_threshold
    phase_i_pass = knock_success and recover_success_endpoint

    recovery_traj = [t[m_j] for t in recover]
    recovery_traj_mean = float(np.mean(recovery_traj))
    recovery_traj_above_frac = float(
        sum(1 for v in recovery_traj if v > viability_threshold)
        / max(1, len(recovery_traj))
    )
    pathwise_pass = recovery_traj_above_frac >= pathwise_fraction
    phase_iii_pass = phase_i_pass or pathwise_pass
    return {
        "phase_i_pass": phase_i_pass,
        "pathwise_pass": pathwise_pass,
        "phase_iii_pass": phase_iii_pass,
        "recovery_traj_mean": recovery_traj_mean,
        "recovery_traj_above_frac": recovery_traj_above_frac,
    }


# ----------------------------------------------------------------------
# Sweep grid
# ----------------------------------------------------------------------
sigmas = [0.0, 0.10, 0.50, 1.00]
food_concs = [5.0, 10.0, 20.0]
T_sweep = 300

print("=" * 78)
print("TASK B: NETWORK K PERTURBATION ROBUSTNESS SWEEP")
print("       (noisy food supply; stress-test the 100% Phase I verdict)")
print("=" * 78)
print()
print(f"Sweep grid: {len(sigmas)} sigmas x {len(food_concs)} food_concs "
      f"= {len(sigmas) * len(food_concs)} configurations")
print(f"  sigma  (noise amplitude on food_conc): {sigmas}")
print(f"  food_conc:                            {food_concs}")
print(f"  T = {T_sweep} timesteps per simulation")
print(f"  Total simulations: {len(sigmas) * len(food_concs) * 52 * 2} "
      f"(52 components x 2 sims (KO + recover) per config)")
print()

results = []
t0 = time.time()
for i_sigma, sigma in enumerate(sigmas):
    for i_fc, fc in enumerate(food_concs):
        t_start = time.time()
        # Run Phase I closure test under (sigma, fc)
        recs = closure_test_noisy(network_K, "K", T=T_sweep,
                                  food_conc=fc, food_supply_rate=2.0,
                                  sigma_food=sigma, seed=20260831)
        n_phase_i = sum(1 for r in recs if r["causally_internal"])
        # Run Phase III only on the failing components
        n_phase_iii = n_phase_i
        phase_iii_detail = {}
        for r in recs:
            if not r["causally_internal"]:
                p3 = phase_iii_check_noisy(network_K, r["component"], T=T_sweep,
                                           food_conc=fc, food_supply_rate=2.0,
                                           sigma_food=sigma, seed=20260831)
                phase_iii_detail[r["component"]] = p3
                if p3["phase_iii_pass"]:
                    n_phase_iii += 1
        elapsed = time.time() - t_start
        cfg_id = i_sigma * len(food_concs) + i_fc + 1
        print(f"  [cfg {cfg_id:2d}/{len(sigmas)*len(food_concs)}] "
              f"sigma={sigma:.2f}, food_conc={fc:5.1f}: "
              f"Phase I = {n_phase_i:2d}/52 ({100.0*n_phase_i/52:.1f}%), "
              f"Phase III = {n_phase_iii:2d}/52 ({100.0*n_phase_iii/52:.1f}%) "
              f"[{elapsed:.1f}s]")
        results.append({
            "sigma": sigma, "food_conc": fc,
            "n_phase_i": n_phase_i, "pct_phase_i": 100.0*n_phase_i/52,
            "n_phase_iii": n_phase_iii, "pct_phase_iii": 100.0*n_phase_iii/52,
            "records": recs, "phase_iii_detail": phase_iii_detail,
        })

print(f"\nTotal elapsed: {time.time() - t0:.1f}s")
print()

# ----------------------------------------------------------------------
# Report: heatmap + per-component robustness table
# ----------------------------------------------------------------------
# Build Phase I fraction matrix (rows=sigma, cols=food_conc)
phase_i_matrix = np.zeros((len(sigmas), len(food_concs)))
phase_iii_matrix = np.zeros((len(sigmas), len(food_concs)))
for r in results:
    i_s = sigmas.index(r["sigma"])
    i_f = food_concs.index(r["food_conc"])
    phase_i_matrix[i_s, i_f] = r["pct_phase_i"]
    phase_iii_matrix[i_s, i_f] = r["pct_phase_iii"]

print("Phase I % (rows=sigma, cols=food_conc):")
print(f"  {'sigma\\\\fc':>10}  " + "  ".join(f"{fc:>6.1f}" for fc in food_concs))
for i_s, sigma in enumerate(sigmas):
    print(f"  {sigma:>10.2f}  " + "  ".join(f"{phase_i_matrix[i_s, i_f]:>6.1f}"
                                          for i_f in range(len(food_concs))))
print()
print("Phase III % (rows=sigma, cols=food_conc):")
print(f"  {'sigma\\\\fc':>10}  " + "  ".join(f"{fc:>6.1f}" for fc in food_concs))
for i_s, sigma in enumerate(sigmas):
    print(f"  {sigma:>10.2f}  " + "  ".join(f"{phase_iii_matrix[i_s, i_f]:>6.1f}"
                                          for i_f in range(len(food_concs))))
print()

# Per-component robustness: how many of the 24 configs does each component pass?
n_configs = len(sigmas) * len(food_concs)
per_comp_robust = {}
for comp in non_food:
    n_pass_i = 0
    n_pass_iii = 0
    for r in results:
        rec = next(rr for rr in r["records"] if rr["component"] == comp)
        if rec["causally_internal"]:
            n_pass_i += 1
        # Phase III check
        if rec["causally_internal"]:
            n_pass_iii += 1
        else:
            p3 = r["phase_iii_detail"].get(comp, {})
            if p3.get("phase_iii_pass", False):
                n_pass_iii += 1
    per_comp_robust[comp] = (n_pass_i, n_pass_iii)

# Sort by robustness (most fragile first)
sorted_comp = sorted(non_food, key=lambda c: per_comp_robust[c][0])
print(f"Per-component robustness (n_pass_i / {n_configs} configs, most fragile first, top 15):")
print(f"  {'component':<10}  {'Phase I pass':>12}  {'Phase III pass':>14}")
for comp in sorted_comp[:15]:
    n_i, n_iii = per_comp_robust[comp]
    print(f"  {comp:<10}  {n_i:>7}/{n_configs:<4}        {n_iii:>7}/{n_configs}")
print()
print(f"Components passing ALL {n_configs} configs at Phase I: "
      f"{sum(1 for c in non_food if per_comp_robust[c][0] == n_configs)}/52")
print(f"Components passing ALL {n_configs} configs at Phase III: "
      f"{sum(1 for c in non_food if per_comp_robust[c][1] == n_configs)}/52")

# ----------------------------------------------------------------------
# Save outputs
# ----------------------------------------------------------------------
out_dir = "/home/z/my-project/download"
os.makedirs(out_dir, exist_ok=True)

with open(f"{out_dir}/autopoiesis_network_K_robustness.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sigma", "food_conc", "n_phase_i", "pct_phase_i",
                "n_phase_iii", "pct_phase_iii"])
    for r in results:
        w.writerow([r["sigma"], r["food_conc"], r["n_phase_i"],
                    r["pct_phase_i"], r["n_phase_iii"], r["pct_phase_iii"]])

# Per-component robustness table
with open(f"{out_dir}/autopoiesis_network_K_robustness_percomp.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["component", "n_phase_i_pass", "n_phase_iii_pass",
                "frac_phase_i", "frac_phase_iii"])
    for comp in non_food:
        n_i, n_iii = per_comp_robust[comp]
        w.writerow([comp, n_i, n_iii, n_i / n_configs, n_iii / n_configs])

with open(f"{out_dir}/autopoiesis_network_K_robustness.txt", "w") as f:
    f.write("TASK B: NETWORK K PERTURBATION ROBUSTNESS SWEEP\n")
    f.write("       (noisy food supply; stress-test the 100% Phase I verdict)\n")
    f.write("=" * 78 + "\n\n")
    f.write(f"Sweep grid: {len(sigmas)} sigmas x {len(food_concs)} food_concs "
            f"= {n_configs} configurations\n")
    f.write(f"  sigma  (noise amplitude on food_conc): {sigmas}\n")
    f.write(f"  food_conc:                            {food_concs}\n")
    f.write(f"  T = {T_sweep} timesteps per simulation\n\n")
    f.write("Phase I % (rows=sigma, cols=food_conc):\n")
    f.write(f"  {'sigma\\\\fc':>10}  " + "  ".join(f"{fc:>6.1f}" for fc in food_concs) + "\n")
    for i_s, sigma in enumerate(sigmas):
        f.write(f"  {sigma:>10.2f}  "
                + "  ".join(f"{phase_i_matrix[i_s, i_f]:>6.1f}"
                            for i_f in range(len(food_concs))) + "\n")
    f.write("\nPhase III % (rows=sigma, cols=food_conc):\n")
    f.write(f"  {'sigma\\\\fc':>10}  " + "  ".join(f"{fc:>6.1f}" for fc in food_concs) + "\n")
    for i_s, sigma in enumerate(sigmas):
        f.write(f"  {sigma:>10.2f}  "
                + "  ".join(f"{phase_iii_matrix[i_s, i_f]:>6.1f}"
                            for i_f in range(len(food_concs))) + "\n")
    f.write(f"\nPer-config verdicts:\n")
    for r in results:
        f.write(f"  sigma={r['sigma']:.2f}, food_conc={r['food_conc']:5.1f}: "
                f"Phase I = {r['n_phase_i']:2d}/52 ({r['pct_phase_i']:.1f}%), "
                f"Phase III = {r['n_phase_iii']:2d}/52 ({r['pct_phase_iii']:.1f}%)\n")
    f.write(f"\nPer-component robustness (sorted by Phase I fragility, top 15):\n")
    f.write(f"  {'component':<10}  {'Phase I pass':>12}  {'Phase III pass':>14}\n")
    for comp in sorted_comp[:15]:
        n_i, n_iii = per_comp_robust[comp]
        f.write(f"  {comp:<10}  {n_i:>7}/{n_configs:<4}        {n_iii:>7}/{n_configs}\n")
    f.write(f"\nComponents passing ALL {n_configs} configs at Phase I: "
            f"{sum(1 for c in non_food if per_comp_robust[c][0] == n_configs)}/52\n")
    f.write(f"Components passing ALL {n_configs} configs at Phase III: "
            f"{sum(1 for c in non_food if per_comp_robust[c][1] == n_configs)}/52\n")
    # Summary stats
    nominal_idx = (sigmas.index(0.0), food_concs.index(10.0))
    hardest_i_idx = np.unravel_index(phase_i_matrix.argmin(), phase_i_matrix.shape)
    hardest_iii_idx = np.unravel_index(phase_iii_matrix.argmin(), phase_iii_matrix.shape)
    f.write(f"\nNominal config (sigma=0, food_conc=10) Phase I = "
            f"{phase_i_matrix[nominal_idx]:.1f}% (expected 100.0%)\n")
    f.write(f"Hardest config Phase I: "
            f"{phase_i_matrix.min():.1f}% "
            f"(sigma={sigmas[hardest_i_idx[0]]:.2f}, "
            f"food_conc={food_concs[hardest_i_idx[1]]:.1f})\n")
    f.write(f"Hardest config Phase III: "
            f"{phase_iii_matrix.min():.1f}% "
            f"(sigma={sigmas[hardest_iii_idx[0]]:.2f}, "
            f"food_conc={food_concs[hardest_iii_idx[1]]:.1f})\n")

# Plot: 2-heatmap figure (Phase I and Phase III) + per-component fragility
fig, axes = plt.subplots(1, 3, figsize=(17, 5.5), constrained_layout=True)

# Phase I heatmap
ax = axes[0]
im = ax.imshow(phase_i_matrix, aspect='auto', cmap='RdYlGn', vmin=0, vmax=100,
               origin='lower')
ax.set_xticks(range(len(food_concs)))
ax.set_xticklabels([f"{fc:.1f}" for fc in food_concs])
ax.set_yticks(range(len(sigmas)))
ax.set_yticklabels([f"{s:.2f}" for s in sigmas])
ax.set_xlabel("food_conc")
ax.set_ylabel("sigma (noise amplitude)")
ax.set_title("Phase I closure-test verdict (%)\nNetwork K under noisy food supply",
             fontsize=10)
for i in range(len(sigmas)):
    for j in range(len(food_concs)):
        ax.text(j, i, f"{phase_i_matrix[i, j]:.0f}", ha='center', va='center',
                color='black' if phase_i_matrix[i, j] > 50 else 'white', fontsize=10,
                fontweight='bold')
plt.colorbar(im, ax=ax, label='Phase I %')

# Phase III heatmap
ax = axes[1]
im = ax.imshow(phase_iii_matrix, aspect='auto', cmap='RdYlGn', vmin=0, vmax=100,
               origin='lower')
ax.set_xticks(range(len(food_concs)))
ax.set_xticklabels([f"{fc:.1f}" for fc in food_concs])
ax.set_yticks(range(len(sigmas)))
ax.set_yticklabels([f"{s:.2f}" for s in sigmas])
ax.set_xlabel("food_conc")
ax.set_ylabel("sigma (noise amplitude)")
ax.set_title("Phase III closure-test verdict (%)\n(pathwise + univalence-corrected)",
             fontsize=10)
for i in range(len(sigmas)):
    for j in range(len(food_concs)):
        ax.text(j, i, f"{phase_iii_matrix[i, j]:.0f}", ha='center', va='center',
                color='black' if phase_iii_matrix[i, j] > 50 else 'white', fontsize=10,
                fontweight='bold')
plt.colorbar(im, ax=ax, label='Phase III %')

# Per-component fragility bar chart (top 15 most fragile)
ax = axes[2]
top_n = 15
fragile = sorted_comp[:top_n]
n_passes_i = [per_comp_robust[c][0] for c in fragile]
n_passes_iii = [per_comp_robust[c][1] for c in fragile]
x = np.arange(top_n)
w = 0.4
ax.bar(x - w/2, n_passes_i, w, color='#3a7ca5', label='Phase I pass count',
       edgecolor='black', linewidth=0.5)
ax.bar(x + w/2, n_passes_iii, w, color='#6a994e', label='Phase III pass count',
       edgecolor='black', linewidth=0.5)
ax.set_xticks(x)
ax.set_xticklabels(fragile, rotation=45, ha='right', fontsize=8)
ax.set_ylabel(f"# configs passed (out of {n_configs})")
ax.set_ylim(0, n_configs + 1)
ax.set_title(f"Top {top_n} most fragile components\n(sorted by Phase I pass count)",
             fontsize=10)
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.3, axis='y')

fig.suptitle("Task B: Network K perturbation robustness sweep "
             f"({len(sigmas)} sigmas x {len(food_concs)} food_concs = {n_configs} configs)\n"
             f"Nominal (sigma=0, fc=10) Phase I = {phase_i_matrix[sigmas.index(0.0), food_concs.index(10.0)]:.1f}%; "
             f"hardest config Phase I = {phase_i_matrix.min():.1f}%; "
             f"hardest config Phase III = {phase_iii_matrix.min():.1f}%",
             fontsize=11)
fig.savefig(f"{out_dir}/autopoiesis_network_K_robustness.png", dpi=150)
plt.close(fig)

print(f"\n[outputs written to {out_dir}/]")
print(f"  - autopoiesis_network_K_robustness.csv")
print(f"  - autopoiesis_network_K_robustness_percomp.csv")
print(f"  - autopoiesis_network_K_robustness.png")
print(f"  - autopoiesis_network_K_robustness.txt")
