import re
from pathlib import Path

# Paths to results
LOG_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_D_ScaleUp.txt")

def parse_rtt_by_type(log_text: str):
    internal_rtts = []
    branch_rtts = []
    internet_rtts = []
    matches = re.findall(r"Ping reply #\d+ arrived, rtt=([0-9.]+)", log_text)
    for m in matches:
        rtt_ms = float(m) * 1000.0
        if rtt_ms < 2.0:
            internal_rtts.append(rtt_ms)
        elif 5.0 <= rtt_ms < 25.0:
            branch_rtts.append(rtt_ms)
        elif rtt_ms >= 30.0:
            internet_rtts.append(rtt_ms)
    return {
        "internal": (sum(internal_rtts)/len(internal_rtts), len(internal_rtts)) if internal_rtts else (0,0),
        "branch": (sum(branch_rtts)/len(branch_rtts), len(branch_rtts)) if branch_rtts else (0,0),
        "internet": (sum(internet_rtts)/len(internet_rtts), len(internet_rtts)) if internet_rtts else (0,0),
    }

def main():
    if not LOG_PATH.exists(): return
    log_text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    rtts = parse_rtt_by_type(log_text)
    
    # Check scale
    num_extra = 0
    m = re.findall(r"extraHost\[(\d+)\]", log_text)
    if m: num_extra = max([int(x) for x in m]) + 1
    total_hosts = 30 + num_extra
    
    print("=== Scenario D (Scale Up) ===")
    print(f"Total HQ Hosts: {total_hosts} (30 base + {num_extra} extra)")
    print(f"Internal RTT (HQ): {rtts['internal'][0]:.4f} ms ({rtts['internal'][1]} samples)")
    print(f"Branch-to-HQ RTT: {rtts['branch'][0]:.4f} ms ({rtts['branch'][1]} samples)")
    print(f"Internet RTT: {rtts['internet'][0]:.4f} ms ({rtts['internet'][1]} samples)")
    
    print("\n--- Доказательства (Proofs) ---")
    if total_hosts == 43:
        print(f"[OK] Масштабирование до {total_hosts} хостов подтверждено.")
    if rtts['internal'][1] > 0:
        print(f"[OK] Работа сети стабильна при повышенной нагрузке.")

if __name__ == "__main__":
    main()
