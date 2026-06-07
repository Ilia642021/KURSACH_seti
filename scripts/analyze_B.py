from analyze_common import (
    OMNETPP_DIR,
    RESULTS_DIR,
    avg,
    count_lines_with_substrings,
    count_targeted_events,
    find_scalar,
    find_stat_field,
    find_all_stat_fields,
    hq_host_modules,
    load_lines,
)

SCA_PATH = OMNETPP_DIR / "B_ReserveEnabled-0.sca"
LOG_PATH = RESULTS_DIR / "log_B_ReserveEnabled.txt"


def main():
    sca_lines = load_lines(SCA_PATH)
    log_lines = load_lines(LOG_PATH)

    hq_sessions = [
        find_scalar(sca_lines, "KursachNetwork.adminPc[0].app[0]", "numSessions:last") or 0,
        find_scalar(sca_lines, "KursachNetwork.dirPc[0].app[0]", "numSessions:last") or 0,
        find_scalar(sca_lines, "KursachNetwork.kitPc[0].app[0]", "numSessions:last") or 0,
    ]
    branch_sessions = [
        find_scalar(sca_lines, "KursachNetwork.br1Host[0].app[0]", "numSessions:last") or 0,
    ]
    internet_sessions = [
        find_scalar(sca_lines, "KursachNetwork.hallPc[0].app[0]", "numSessions:last") or 0,
        find_scalar(sca_lines, "KursachNetwork.adminPc[1].app[0]", "numSessions:last") or 0,
    ]

    ppp2_mentions = count_lines_with_substrings(log_lines, "ppp2")
    ppp3_mentions = count_lines_with_substrings(log_lines, "ppp3")
    primary_shutdown = count_targeted_events(log_lines, "shutdown", "KursachNetwork.core.ppp[2]")
    reserve_shutdown = count_targeted_events(log_lines, "shutdown", "KursachNetwork.core.ppp[3]")

    # Исправлено: PingApp может быть на разных индексах
    ping_rtt_results = find_all_stat_fields(sca_lines, r"KursachNetwork\.adminPc\[0\]", "rtt:stats", "mean")
    ping_rtt_mean = ping_rtt_results[0] if ping_rtt_results else None
    
    ping_rtt_max_results = find_all_stat_fields(sca_lines, r"KursachNetwork\.adminPc\[0\]", "rtt:stats", "max")
    ping_rtt_max = ping_rtt_max_results[0] if ping_rtt_max_results else None
    
    hq_modules = hq_host_modules(sca_lines)
    # Исправлено: учитываем все TCP приложения для всех HQ хостов
    hq_pattern = r"KursachNetwork\.(admin|acc|dir|war|kit|hall)(Pc|Extra)\[\d+\]"
    tcp_delay_means = find_all_stat_fields(sca_lines, hq_pattern, "endToEndDelay:histogram", "mean")
    
    tcp_delay_max_candidates = find_all_stat_fields(sca_lines, hq_pattern, "endToEndDelay:histogram", "max")

    print("=== Scenario B (Reserve Enabled) ===")
    print(f"HQ TCP sessions (sample avg): {avg(hq_sessions):.2f}")
    print(f"Branch-to-HQ TCP sessions: {avg(branch_sessions):.2f}")
    print(f"Internet TCP sessions (sample avg): {avg(internet_sessions):.2f}")
    print(f"Log mentions ppp2: {ppp2_mentions}")
    print(f"Log mentions ppp3: {ppp3_mentions}")
    print(f"Primary link shutdown events: {primary_shutdown}")
    print(f"Reserve link shutdown events: {reserve_shutdown}")

    if ping_rtt_mean is not None or tcp_delay_means:
        print("\n--- RTT / Delay ---")
        if ping_rtt_mean is not None:
            print(f"Ping RTT mean: {ping_rtt_mean * 1000:.3f} ms")
        if ping_rtt_max is not None:
            print(f"Ping RTT max: {ping_rtt_max * 1000:.3f} ms")
        if tcp_delay_means:
            print(f"TCP end-to-end delay mean (HQ hosts avg): {avg(tcp_delay_means) * 1000:.3f} ms")
        if tcp_delay_max_candidates:
            print(f"TCP end-to-end delay max (HQ hosts worst): {max(tcp_delay_max_candidates) * 1000:.3f} ms")

    print("\n--- Доказательства (Proofs) ---")
    if avg(hq_sessions) > 0:
        print(f"[OK] Внутренний трафик HQ подтвержден (среднее число сессий {avg(hq_sessions):.2f}).")
    if branch_sessions[0] > 0:
        print(f"[OK] Трафик филиал → HQ подтвержден ({int(branch_sessions[0])} сессий от br1Host[0]).")
    if avg(internet_sessions) > 0:
        print(f"[OK] Внешняя прикладная нагрузка активна (среднее число сессий {avg(internet_sessions):.2f}).")
    if primary_shutdown == 0 and reserve_shutdown == 0:
        print("[OK] В сценарии резерв включен без отключения каналов: оба интернет-линка доступны.")
    if ppp2_mentions > 0 and ppp3_mentions > 0:
        print(f"[OK] В логах присутствуют оба интерфейса доступа в Интернет: ppp2={ppp2_mentions}, ppp3={ppp3_mentions}.")
    if ping_rtt_mean is not None:
        print(f"[OK] Контрольный Ping RTT остается измеримым ({ping_rtt_mean * 1000:.3f} ms в среднем).")
    if tcp_delay_means:
        print(f"[OK] TCP end-to-end delay также собирается по всем основным хостам HQ ({avg(tcp_delay_means) * 1000:.3f} ms в среднем).")


if __name__ == "__main__":
    main()
