"""
The AI Decision Engine for the Adaptive Encryption System.

THIS IS THE CORE NOVELTY OF THE PROJECT.

Takes multiple context signals together (not just one factor, unlike the
3 papers in our literature survey) and decides which encryption algorithm
from our pool (AES / ChaCha20 / Hybrid) is the best fit RIGHT NOW:

  1. Data sensitivity       (from the Random Forest classifier - Phase 1)
  2. File size               (large files change the speed/security tradeoff)
  3. User role                (admin / employee / guest)
  4. Device performance       (CPU load, battery level - Phase 3 device_stats.py)
  5. Current threat level     (normal / elevated / high)

Every decision comes with a REASON string explaining why - this is the
"explainability" feature that makes the AI's choice transparent instead
of a black box, and it directly supports the patent claim (a documented,
justifiable decision process).
"""

from dataclasses import dataclass


@dataclass
class DecisionContext:
    sensitivity: str          # "Low" | "Medium" | "High" | "Critical" (from classifier)
    file_size_kb: float
    user_role: str             # "admin" | "employee" | "guest"
    cpu_percent: float         # 0-100
    battery_percent: float     # 0-100, or None if no battery (desktop/plugged in)
    threat_level: str          # "normal" | "elevated" | "high"


LARGE_FILE_THRESHOLD_KB = 50_000   # ~50 MB
LOW_BATTERY_THRESHOLD = 20          # percent
HIGH_CPU_THRESHOLD = 80             # percent


def decide_algorithm(ctx: DecisionContext) -> dict:
    """
    Returns:
    {
        "algorithm": "AES" | "ChaCha20" | "Hybrid",
        "reason": str   # human-readable explanation of the decision
    }
    """
    reasons = []

    # --- Device constraint check (used to justify lighter algorithm choices) ---
    device_constrained = False
    if ctx.battery_percent is not None and ctx.battery_percent < LOW_BATTERY_THRESHOLD:
        device_constrained = True
        reasons.append(f"battery low ({ctx.battery_percent}%)")
    if ctx.cpu_percent > HIGH_CPU_THRESHOLD:
        device_constrained = True
        reasons.append(f"CPU load high ({ctx.cpu_percent}%)")

    is_large_file = ctx.file_size_kb > LARGE_FILE_THRESHOLD_KB
    if is_large_file:
        reasons.append(f"large file ({ctx.file_size_kb:.0f} KB)")

    # --- RULE 1: Critical sensitivity or high threat level -> always Hybrid ---
    # No compromise here regardless of device constraints - security wins.
    if ctx.sensitivity == "Critical" or ctx.threat_level == "high":
        reasons.insert(0, f"sensitivity={ctx.sensitivity}, threat={ctx.threat_level}")
        return {
            "algorithm": "Hybrid",
            "reason": "Selected Hybrid (ECC+AES): " + "; ".join(reasons)
        }

    # --- RULE 2: Guest role accessing High/Medium data -> escalate one tier ---
    # Extra caution for less-trusted users, even if the raw file isn't Critical.
    if ctx.user_role == "guest" and ctx.sensitivity in ("High", "Medium") and ctx.threat_level == "elevated":
        reasons.insert(0, f"sensitivity={ctx.sensitivity}, user_role=guest, threat=elevated")
        return {
            "algorithm": "Hybrid",
            "reason": "Selected Hybrid (ECC+AES): " + "; ".join(reasons)
        }

    # --- RULE 3: High sensitivity -> AES-256 (strong, standard choice) ---
    if ctx.sensitivity == "High":
        reasons.insert(0, f"sensitivity={ctx.sensitivity}")
        return {
            "algorithm": "AES",
            "reason": "Selected AES-256: " + "; ".join(reasons)
        }

    # --- RULE 4: Medium sensitivity -> AES normally, ChaCha20 if device constrained ---
    if ctx.sensitivity == "Medium":
        if device_constrained:
            reasons.insert(0, f"sensitivity={ctx.sensitivity}")
            return {
                "algorithm": "ChaCha20",
                "reason": "Selected ChaCha20 (lighter, device-friendly): " + "; ".join(reasons)
            }
        else:
            reasons.insert(0, f"sensitivity={ctx.sensitivity}")
            return {
                "algorithm": "AES",
                "reason": "Selected AES-256: " + "; ".join(reasons)
            }

    # --- RULE 5: Low sensitivity -> ChaCha20 (fast, lightweight default) ---
    reasons.insert(0, f"sensitivity={ctx.sensitivity}")
    return {
        "algorithm": "ChaCha20",
        "reason": "Selected ChaCha20 (fast, lightweight): " + "; ".join(reasons)
    }


if __name__ == "__main__":
    # --- Test across several realistic scenarios ---

    scenarios = [
        DecisionContext(
            sensitivity="Low", file_size_kb=15, user_role="employee",
            cpu_percent=20, battery_percent=80, threat_level="normal"
        ),
        DecisionContext(
            sensitivity="High", file_size_kb=45, user_role="employee",
            cpu_percent=30, battery_percent=90, threat_level="normal"
        ),
        DecisionContext(
            sensitivity="Critical", file_size_kb=300, user_role="admin",
            cpu_percent=40, battery_percent=95, threat_level="normal"
        ),
        DecisionContext(
            sensitivity="Medium", file_size_kb=8000, user_role="employee",
            cpu_percent=50, battery_percent=15, threat_level="normal"
        ),
        DecisionContext(
            sensitivity="High", file_size_kb=100, user_role="guest",
            cpu_percent=25, battery_percent=70, threat_level="elevated"
        ),
        DecisionContext(
            sensitivity="Low", file_size_kb=20, user_role="employee",
            cpu_percent=10, battery_percent=60, threat_level="high"
        ),
    ]

    for i, ctx in enumerate(scenarios, 1):
        decision = decide_algorithm(ctx)
        print(f"Scenario {i}: {ctx}")
        print(f"  -> {decision['algorithm']}")
        print(f"  -> {decision['reason']}\n")
