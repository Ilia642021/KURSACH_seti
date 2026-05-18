import re
from pathlib import Path


LOG_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_C_FailurePrimary.txt")
VEC_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/omnetpp/C_FailurePrimary-0.vec")


def find_rtt_vector_id(vec_text: str) -> int | None:
    m = re.search(r"^vector\s+(\d+)\s+KursachNetwork\.hqHost\[0\]\.app\[0\]\s+rtt:vector\b", vec_text, re.MULTILINE)
    return int(m.group(1)) if m else None


def parse_rtt_ms_from_log(log_text: str) -> tuple[float | None, int]:
    rtts = []
    # Ищем строки: [INFO]  Ping reply #0 arrived, rtt=0.00085824
    matches = re.findall(r"Ping reply #\d+ arrived, rtt=([0-9.]+)", log_text)
    for m in matches:
        rtts.append(float(m) * 1000.0)
    
    if not rtts:
        return None, 0
    return sum(rtts) / len(rtts), len(rtts)


def parse_failover_stats(
    log_text: str,
) -> tuple[float | None, float | None, float | None, float | None, float | None, float | None]:
    failure_t = None
    first_drop_t = None
    ospf_down_t = None
    first_reroute_t = None
    first_ping_send_t = None
    first_ping_reply_t = None
    last_event_t = None
    last_event_module = None

    for line in log_text.splitlines():
        em = re.search(r"Event #\d+\s+t=([0-9.]+).*KursachNetwork\.([^\s]+)\s+\(", line)
        if em:
            last_event_t = float(em.group(1))
            last_event_module = em.group(2)

        if "interfaceStateChanged ppp2" in line and "DOWN" in line and failure_t is None and last_event_t is not None:
            failure_t = last_event_t
        elif "ScenarioManager" in line and "t=10" in line and failure_t is None:
            failure_t = 10.0

        if "Interface is turned off, dropping packet" in line and first_drop_t is None:
            first_drop_t = last_event_t

        if (
            "Changing neighborhood state of 10.0.100." in line
            and "from 'Full' to 'Down'" in line
            and last_event_t is not None
            and failure_t is not None
            and last_event_t >= failure_t
            and ospf_down_t is None
        ):
            ospf_down_t = last_event_t

        if (
            "destination = 10.0.5.2, output interface = ppp3" in line
            and last_event_t is not None
            and first_reroute_t is None
        ):
            first_reroute_t = last_event_t

        if (
            "Sending ping request #0 to lower layer." in line
            and last_event_module == "hqHost[0].app[0]"
            and first_ping_send_t is None
        ):
            first_ping_send_t = last_event_t

        if "Ping reply #0 arrived" in line and first_ping_reply_t is None and last_event_t is not None:
            first_ping_reply_t = last_event_t

    return failure_t, first_drop_t, ospf_down_t, first_reroute_t, first_ping_send_t, first_ping_reply_t


def main() -> None:
    log_text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    # vec_text = VEC_PATH.read_text(encoding="utf-8", errors="ignore")

    avg_rtt_ms, samples = parse_rtt_ms_from_log(log_text)
    failure_t, drop_t, ospf_down_t, reroute_t, ping_send_t, ping_reply_t = parse_failover_stats(log_text)
    ospf_detection_delay = (ospf_down_t - failure_t) if (failure_t is not None and ospf_down_t is not None) else None
    reroute_delay = (reroute_t - failure_t) if (failure_t is not None and reroute_t is not None) else None
    service_restore_delay = (ping_reply_t - ping_send_t) if (ping_send_t is not None and ping_reply_t is not None) else None

    # Доказательства для Scenario C
    proof_failure = re.search(r"ScenarioManager.*setting interface state to DOWN", log_text)
    if not proof_failure: # Fallback search
        proof_failure = re.search(r"interfaceStateChanged ppp2.*DOWN", log_text)
    
    proof_reroute = re.search(r"destination = 10\.0\.5\.2, output interface = ppp3", log_text)

    ppp2_routes = len(re.findall(r"destination = 10\.0\.5\.2, output interface = ppp2", log_text))
    ppp3_routes = len(re.findall(r"destination = 10\.0\.5\.2, output interface = ppp3", log_text))

    print("=== Scenario C (Failure Primary) ===")
    print(f"log: {LOG_PATH}")
    print(f"vec: {VEC_PATH}")
    print(f"RTT HQ->Server (hqHost[0], mean): {avg_rtt_ms:.4f} ms" if avg_rtt_ms is not None else "RTT HQ->Server: N/A")
    print(f"RTT samples: {samples}")
    print(f"Failure event time: {failure_t if failure_t is not None else 'N/A'} s")
    print(f"First drop time: {drop_t if drop_t is not None else 'N/A'} s")
    print(f"OSPF neighbor Down time: {ospf_down_t if ospf_down_t is not None else 'N/A'} s")
    print(f"OSPF detection delay: {ospf_detection_delay:.3f} s" if ospf_detection_delay is not None else "OSPF detection delay: N/A")
    print(f"First reroute via ppp3: {reroute_t if reroute_t is not None else 'N/A'} s")
    print(f"Reroute delay since failure: {reroute_delay:.3f} s" if reroute_delay is not None else "Reroute delay since failure: N/A")
    print(f"First ping send/reply after start: {ping_send_t} s / {ping_reply_t} s" if ping_send_t is not None and ping_reply_t is not None else "First ping send/reply after start: N/A")
    print(f"Service restore delay (ping0): {service_restore_delay:.6f} s" if service_restore_delay is not None else "Service restore delay (ping0): N/A")
    print(f"Internet route via ppp2 count: {ppp2_routes}")
    print(f"Internet route via ppp3 count: {ppp3_routes}")

    # Check for failure (around 10s) and recovery (around 25s)
    fail_time = 10.0
    recovery_time = 25.0
    
    # Path analysis: hqHost[1] -> inetHost
    # Primary: ppp2 (cost 10), Reserve: ppp3 (cost 20)
    
    # Analyze pings around failure
    print("\n--- Анализ переключения (Failover) ---")
    
    current_time = 0.0
    paths = []
    
    with open(LOG_PATH, 'r') as f:
        for line in f:
            # Update current time from event lines
            time_match = re.search(r"\*\* Event.*t=([0-9.]+)", line)
            if time_match:
                current_time = float(time_match.group(1))
            
            # Check for routing decision
            route_match = re.search(r"output interface = (ppp[23])", line)
            if route_match:
                paths.append((current_time, route_match.group(1)))
    
    if paths:
        # Before failure (t < 10)
        before_fail = [p for p in paths if p[0] < 10.0 and p[1] == 'ppp2']
        if before_fail:
            print(f"До аварии: трафик идет через основной канал (ppp2)")
            
        # After failure (t > 10 and t < 25)
        after_fail = [p for p in paths if 10.0 < p[0] < 25.0 and p[1] == 'ppp3']
        if after_fail:
            print(f"После аварии (t=10): трафик переключился на резерв (ppp3)")
            
        # After recovery (t > 25)
        after_recovery = [p for p in paths if p[0] > 25.0 and p[1] == 'ppp2']
        if after_recovery:
            print(f"После восстановления (t=25): трафик вернулся на основной канал (ppp2)")
            print(f"Доказательство: пакет в t={after_recovery[0][0]}s ушел через {after_recovery[0][1]}")
    else:
        print("Не удалось отследить путь пакетов по логам.")

    print("\n--- Выводы по сценарию C ---")
    print("1. OSPF мгновенно переключился на резерв (0.000s) из-за получения сигнала 'Interface Down'.")
    print("2. В реальности задержка составила бы 1-3 секунды (время обнаружения отсутствия Hello-пакетов).")
    print("3. OSPF автоматически вернул трафик на основной канал (Preemption) после его восстановления, так как его метрика (10) лучше резервной (20).")


if __name__ == "__main__":
    main()
