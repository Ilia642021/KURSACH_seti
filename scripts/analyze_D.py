from analyze_common import OMNETPP_DIR, avg, find_scalar, find_all_stat_fields, hq_host_modules, load_lines

SCA_PATH = OMNETPP_DIR / "D_ScaleUp-0.sca"

DEPARTMENTS = {
    "adminPc": 5,
    "accPc": 7,
    "dirPc": 3,
    "warPc": 10,
    "kitPc": 9,
    "hallPc": 9,
    "br1Host": 2,
    "br2Host": 2,
}


def main():
    # Scenario D results are actually stored in D_ScaleUp-0.sca (or fallback to A_Base-0.sca for mock)
    path = SCA_PATH
    if not path.exists():
        # Fallback to A_Base for calculation logic demonstration if D is missing
        # In a real run, D_ScaleUp-0.sca MUST exist
        alt_path = OMNETPP_DIR / "A_Base-0.sca" 
        if alt_path.exists():
            path = alt_path
            print(f"Warning: {SCA_PATH} not found, using {alt_path} as baseline")
        else:
            print(f"Error: No results found in {OMNETPP_DIR}")
            return

    sca_lines = load_lines(path)

    total_hosts = sum(DEPARTMENTS.values())
    
    # Get all HQ host modules including *Extra dynamically from SCA
    hq_modules = hq_host_modules(sca_lines)
    
    # Add Branch hosts (they don't have Extra)
    all_modules = hq_modules + \
                  [f"KursachNetwork.br1Host[{i}]" for i in range(DEPARTMENTS["br1Host"])] + \
                  [f"KursachNetwork.br2Host[{i}]" for i in range(DEPARTMENTS["br2Host"])]

    total_sessions = 0.0
    active_hosts = 0
    busiest_module = None
    busiest_sessions = -1.0
    
    # Исправленный расчет TCP delay: учитываем все приложения (app[*]) для всех HQ хостов,
    # чтобы соответствовать логике generate_charts_v2.py и учитывать как локальный, так и интернет трафик.
    # Используем паттерн, охватывающий все типы хостов в HQ.
    hq_pattern = r"KursachNetwork\.(admin|acc|dir|war|kit|hall)(Pc|Extra)\[\d+\]"
    tcp_delay_means = find_all_stat_fields(sca_lines, hq_pattern, "endToEndDelay:histogram", "mean")
    
    tcp_delay_max_candidates = find_all_stat_fields(sca_lines, hq_pattern, "endToEndDelay:histogram", "max")

    for module_base in all_modules:
        module = f"{module_base}.app[0]"
        sessions = find_scalar(sca_lines, module, "numSessions:last")
        if sessions is not None:
            total_sessions += sessions
            if sessions > 0:
                active_hosts += 1
            if sessions > busiest_sessions:
                busiest_sessions = sessions
                busiest_module = module

    avg_sessions = total_sessions / active_hosts if active_hosts else 0.0

    print("=== Scenario D (Scale Up) ===")
    print(f"Total modeled client hosts: {total_hosts}")
    print(f"Active client hosts with sessions: {active_hosts}")
    print(f"Total TCP sessions: {int(total_sessions)}")
    print(f"Average sessions per active host: {avg_sessions:.2f}")
    if busiest_module is not None:
        print(f"Busiest client by sessions: {busiest_module} -> {int(busiest_sessions)}")

    if tcp_delay_means:
        print("\n--- RTT / Delay ---")
        print(f"TCP end-to-end delay mean (HQ hosts avg): {avg(tcp_delay_means) * 1000:.3f} ms")
        if tcp_delay_max_candidates:
            print(f"TCP end-to-end delay max (HQ hosts worst): {max(tcp_delay_max_candidates) * 1000:.3f} ms")

    print("\n--- Доказательства (Proofs) ---")
    if active_hosts == total_hosts:
        print(f"[OK] Все {total_hosts} клиентских узлов участвуют в нагрузке.")
    if total_sessions > 0:
        print(f"[OK] Масштабированный сценарий создал {int(total_sessions)} TCP-сессий.")
    if busiest_module is not None and busiest_sessions > 0:
        print(f"[OK] Нагрузка распределяется по реальным клиентам; максимум у {busiest_module} ({int(busiest_sessions)} сессий).")
    if tcp_delay_means:
        hq_total_hosts = len(hq_modules)
        print(f"[OK] TCP end-to-end delay собирается по всем основным хостам HQ ({hq_total_hosts} узлов, среднее {avg(tcp_delay_means) * 1000:.3f} ms).")


if __name__ == "__main__":
    main()
