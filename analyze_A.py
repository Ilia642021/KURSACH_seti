import re
from pathlib import Path

# Paths to results
LOG_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_A_Base.txt")

def parse_rtt_by_type(log_text: str):
    # We have 3 types of pings:
    # 1. cab1.h1 -> hqSrv[0] (Internal) - RTT ~0.4ms
    # 2. br1Host[0] -> hqSrv[1] (Branch to HQ) - RTT ~10.9ms
    # 3. cab1.h2 -> inetHost (Internet) - RTT ~40.9ms
    
    internal_rtts = []
    branch_rtts = []
    internet_rtts = []
    
    # In the log, we can distinguish by the RTT value since they are very different
    # Or by looking at the lines preceding the reply (but that's harder)
    # Let's use RTT ranges:
    # < 2ms -> Internal
    # 5ms - 20ms -> Branch
    # > 30ms -> Internet
    
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
    if not LOG_PATH.exists():
        print(f"Error: {LOG_PATH} not found")
        return

    log_text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    rtts = parse_rtt_by_type(log_text)
    
    # Check routes to 10.0.0.1 (inetHost)
    ppp2_routes = len(re.findall(r"destination = 10\.0\.0\.1, output interface = ppp2", log_text))
    ppp3_routes = len(re.findall(r"destination = 10\.0\.0\.1, output interface = ppp3", log_text))
    
    print("=== Scenario A (Base) ===")
    print(f"Internal RTT (HQ): {rtts['internal'][0]:.4f} ms ({rtts['internal'][1]} samples)")
    print(f"Branch-to-HQ RTT: {rtts['branch'][0]:.4f} ms ({rtts['branch'][1]} samples)")
    print(f"Internet RTT: {rtts['internet'][0]:.4f} ms ({rtts['internet'][1]} samples)")
    print(f"Internet routes via ppp2: {ppp2_routes}")
    print(f"Internet routes via ppp3: {ppp3_routes}")
    
    print("\n--- Доказательства (Proofs) ---")
    if ppp2_routes > 0:
        print(f"[OK] Маршрут через основной канал (ppp2) подтвержден ({ppp2_routes} пакетов)")
    if rtts['internet'][1] > 0:
        print(f"[OK] Доступ к Internet подтвержден ({rtts['internet'][1]} ответов)")

if __name__ == "__main__":
    main()
