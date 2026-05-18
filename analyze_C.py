import re
from pathlib import Path

# Paths to results
LOG_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_C_FailurePrimary.txt")

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
    
    # Analyze paths over time
    current_time = 0.0
    ppp2_before = 0
    ppp3_during = 0
    ppp2_after = 0
    
    for line in log_text.splitlines():
        time_match = re.search(r"\*\* Event.*t=([0-9.]+)", line)
        if time_match: current_time = float(time_match.group(1))
        
        if "destination = 10.0.0.1" in line:
            if "interface = ppp2" in line:
                if current_time < 10.0: ppp2_before += 1
                elif current_time > 25.0: ppp2_after += 1
            elif "interface = ppp3" in line:
                if 10.0 <= current_time <= 25.0: ppp3_during += 1

    print("=== Scenario C (Failure Primary) ===")
    print(f"Internal RTT (HQ): {rtts['internal'][0]:.4f} ms ({rtts['internal'][1]} samples)")
    print(f"Branch-to-HQ RTT: {rtts['branch'][0]:.4f} ms ({rtts['branch'][1]} samples)")
    print(f"Internet RTT: {rtts['internet'][0]:.4f} ms ({rtts['internet'][1]} samples)")
    
    print("\n--- Анализ переключения (Failover) ---")
    print(f"Пакетов через ppp2 до аварии (t<10): {ppp2_before}")
    print(f"Пакетов через ppp3 во время аварии (10<t<25): {ppp3_during}")
    print(f"Пакетов через ppp2 после восстановления (t>25): {ppp2_after}")
    
    if ppp3_during > 0:
        print("[OK] Переключение на резервный канал ppp3 подтверждено.")
    else:
        print("[FAIL] Переключение на резервный канал ppp3 не зафиксировано.")
        
    if ppp2_after > 0:
        print("[OK] Возврат на основной канал (Preemption) подтвержден.")

if __name__ == "__main__":
    main()
