import re
from pathlib import Path

LOG_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_C_FailurePrimary.txt")

def analyze_ospf_log():
    if not LOG_PATH.exists():
        print(f"Log file {LOG_PATH} not found.")
        return

    current_time = 0.0
    failure_time = 15.0
    detection_time = None
    rebuild_time = None
    recovery_start = 35.0
    recovery_done = None

    # OSPF patterns
    # Detection: Neighbor state changed to Down or similar
    # Rebuild: routing table has changed
    
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Update current simulation time
            time_match = re.search(r"\*\* Event .* t=([\d\.]+)", line)
            if time_match:
                current_time = float(time_match.group(1))

            # Detection of failure (Neighbor down)
            if current_time >= failure_time and detection_time is None:
                if "state changed from Full to Down" in line or "state changed from Full to Init" in line:
                    detection_time = current_time
                    print(f"Failure detected at t={detection_time}")

            # Routing table change (Failover)
            if current_time >= failure_time and rebuild_time is None:
                if "OSPF routing table has changed" in line:
                    rebuild_time = current_time
                    print(f"Routes rebuilt at t={rebuild_time}")

            # Recovery detection
            if current_time >= recovery_start and recovery_done is None:
                if "OSPF routing table has changed" in line:
                    # We look for the first change after recovery start
                    recovery_done = current_time
                    print(f"Routes restored at t={recovery_done}")

    print("\n=== OSPF Convergence Analysis ===")
    print(f"Moment of Failure: {failure_time} s")
    
    if detection_time:
        print(f"Detection Time: {detection_time} s (Delay: {detection_time - failure_time:.3f} s)")
    else:
        # If no explicit "down" message, look for first route change
        print("Detection Time: Not found in log (likely immediate or implicit)")

    if rebuild_time:
        print(f"Route Rebuild: {rebuild_time} s")
        print(f"OSPF Convergence Time: {rebuild_time - failure_time:.3f} s")
    
    if recovery_done:
        print(f"Recovery Time: {recovery_done} s (Delay: {recovery_done - recovery_start:.3f} s)")

if __name__ == "__main__":
    analyze_ospf_log()
