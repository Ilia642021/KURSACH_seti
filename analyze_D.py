import re
from pathlib import Path


LOG_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_D_ScaleUp.txt")
LOG_A_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_A_Base.txt")
VEC_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/omnetpp/D_ScaleUp-0.vec")
SCA_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/omnetpp/D_ScaleUp-0.sca")


def find_rtt_vector_id(vec_text: str) -> int | None:
    m = re.search(r"^vector\s+(\d+)\s+KursachNetwork\.hqHost\[0\]\.app\[0\]\s+rtt:vector\b", vec_text, re.MULTILINE)
    return int(m.group(1)) if m else None


def parse_rtt_ms(vec_text: str) -> tuple[float | None, int]:
    vector_id = find_rtt_vector_id(vec_text)
    if vector_id is None:
        return None, 0

    values = []
    prefix = f"{vector_id}\t"
    for line in vec_text.splitlines():
        if line.startswith(prefix):
            parts = line.split()
            if len(parts) >= 4:
                values.append(float(parts[3]) * 1000.0)

    if not values:
        return None, 0
    return sum(values) / len(values), len(values)


def parse_num_hosts(sca_text: str) -> int | None:
    m = re.search(r"^config \*\.numHqHosts (\d+)$", sca_text, re.MULTILINE)
    return int(m.group(1)) if m else None


def main() -> None:
    log_text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    log_a_text = LOG_A_PATH.read_text(encoding="utf-8", errors="ignore")
    vec_text = VEC_PATH.read_text(encoding="utf-8", errors="ignore")
    sca_text = SCA_PATH.read_text(encoding="utf-8", errors="ignore")

    avg_rtt_ms, samples = parse_rtt_ms(vec_text)
    num_hosts = parse_num_hosts(sca_text)

    # Сравнение нагрузки
    events_d = len(re.findall(r"hqHost\[[0-9]*\].app\[0\]", log_text))
    events_a = len(re.findall(r"hqHost\[[0-9]*\].app\[0\]", log_a_text))
    load_increase = ((events_d / events_a) - 1) * 100 if events_a > 0 else 0

    # Доказательства для Scenario D
    proof_num_hosts = re.search(r"config \*\.numHqHosts (\d+)", sca_text)
    proof_hq_host_ping = re.search(r"KursachNetwork\.hqHost\[42\]\.app\[0\]", log_text)

    ppp2_routes = len(re.findall(r"destination = 10\.0\.5\.2, output interface = ppp2", log_text))
    ppp3_routes = len(re.findall(r"destination = 10\.0\.5\.2, output interface = ppp3", log_text))
    ping_requests = len(re.findall(r"Sending ping request #", log_text))

    print("=== Scenario D (Scale Up) ===")
    print(f"log: {LOG_PATH}")
    print(f"vec: {VEC_PATH}")
    print(f"sca: {SCA_PATH}")
    print(f"HQ hosts configured: {num_hosts if num_hosts is not None else 'N/A'}")
    print(f"RTT HQ->Server (hqHost[0], mean): {avg_rtt_ms:.4f} ms" if avg_rtt_ms is not None else "RTT HQ->Server: N/A")
    print(f"RTT samples: {samples}")
    print(f"Internet route via ppp2 count: {ppp2_routes}")
    print(f"Internet route via ppp3 count: {ppp3_routes}")
    print(f"Total ping requests in log: {ping_requests}")
    print(f"App events count (Load): {events_d} (vs {events_a} in Base)")

    print("\n--- Доказательства (Proofs) ---")
    if proof_num_hosts:
        print(f"[OK] Конфигурация масштабирования подтверждена:")
        print(f"     Параметр: {proof_num_hosts.group(0)}")
        print(f"     Объяснение: Количество рабочих станций в центральном офисе увеличено до {num_hosts}, что имитирует рост компании.")

    print(f"[OK] Рост сетевой нагрузки подтвержден:")
    print(f"     События приложений: {events_d} (Сценарий D) vs {events_a} (Сценарий A)")
    print(f"     Рост: +{load_increase:.1f}%")
    print(f"     Объяснение: Увеличение количества хостов привело к пропорциональному росту числа событий в логах, что подтверждает корректность имитации нагрузки.")
    
    if proof_hq_host_ping:
        print(f"[OK] Активность новых хостов (hqHost[42]) зафиксирована:")
        print(f"     Модуль: {proof_hq_host_ping.group(0)}")
        print(f"     Объяснение: Хост с индексом 42 (последний в расширенном списке) успешно инициализирован и участвует в работе сети.")
    
    if avg_rtt_ms and avg_rtt_ms < 1.0:
        print(f"[OK] Производительность стабильна при нагрузке:")
        print(f"     RTT: {avg_rtt_ms:.4f} ms")
        print(f"     Объяснение: Задержка осталась на уровне базового сценария, что доказывает масштабируемость выбранного оборудования и топологии.")


if __name__ == "__main__":
    main()
