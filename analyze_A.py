import re
from pathlib import Path


LOG_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/log_A_Base.txt")
VEC_PATH = Path("/home/dev/6_sem/KURSACH_seti/03_results/omnetpp/A_Base-0.vec")


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


def main() -> None:
    log_text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    # vec_text = VEC_PATH.read_text(encoding="utf-8", errors="ignore")

    avg_rtt_ms, samples = parse_rtt_ms_from_log(log_text)

    # Доказательства для Scenario A
    proof_route_ppp2 = re.search(r"destination = 10\.0\.5\.2, output interface = ppp2", log_text)
    proof_ping_send = re.search(r"Sending ping request #0", log_text)
    proof_ping_reply = re.search(r"Ping reply #0 arrived", log_text)

    ppp2_routes = len(re.findall(r"destination = 10\.0\.5\.2, output interface = ppp2", log_text))
    ppp3_routes = len(re.findall(r"destination = 10\.0\.5\.2, output interface = ppp3", log_text))
    ping_requests = len(re.findall(r"Sending ping request #", log_text))

    print("=== Scenario A (Base) ===")
    print(f"log: {LOG_PATH}")
    print(f"vec: {VEC_PATH}")
    print(f"RTT HQ->Server (hqHost[0], mean): {avg_rtt_ms:.4f} ms" if avg_rtt_ms is not None else "RTT HQ->Server: N/A")
    print(f"RTT samples: {samples}")
    print(f"Internet route via ppp2 count: {ppp2_routes}")
    print(f"Internet route via ppp3 count: {ppp3_routes}")
    print(f"Total ping requests in log: {ping_requests}")

    print("\n--- Доказательства (Proofs) ---")
    if proof_route_ppp2:
        print(f"[OK] Маршрут через основной канал (ppp2) подтвержден:")
        print(f"     Лог: {proof_route_ppp2.group(0)}")
        print(f"     Объяснение: Пакеты до сервера 10.0.5.2 отправляются через интерфейс ppp2, как и положено в штатном режиме.")
    
    if proof_ping_send and proof_ping_reply:
        print(f"[OK] Обмен ICMP пакетами (Ping) активен:")
        print(f"     Отправка: {proof_ping_send.group(0)}")
        print(f"     Получение: {proof_ping_reply.group(0)}")
        print(f"     Объяснение: Хосты успешно обмениваются данными с сервером с первых секунд работы приложений.")


if __name__ == "__main__":
    main()
