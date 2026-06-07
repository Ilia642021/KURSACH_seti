import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import subprocess
import os
import re
import datetime
import logging
from pathlib import Path

# Настройка логирования
LOG_FILE = "/home/dev/6_sem/KURSACH_seti/03_results/charts_generation.log"

# Создаем логгер
logger = logging.getLogger("ChartGen")
logger.setLevel(logging.INFO)

# Обработчик для файла (с датами)
file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Обработчик для консоли (без дат для чистоты вывода по запросу)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(console_handler)

def log_data_summary(name, data_dict):
    """Выводит краткую сводку данных в консоль."""
    logger.info(f"\n[ДАННЫЕ] {name}:")
    for key, value in data_dict.items():
        if isinstance(value, float):
            logger.info(f"  > {key}: {value:.2f}")
        else:
            logger.info(f"  > {key}: {value}")

CHARTS_DIR = Path("/home/dev/6_sem/KURSACH_seti/03_results/charts")
PCAP_DIR = Path("/home/dev/6_sem/KURSACH_seti/03_results/pcap")
OMNETPP_DIR = Path("/home/dev/6_sem/KURSACH_seti/03_results/omnetpp")
REPORT_FILE = "/home/dev/6_sem/KURSACH_seti/Full_Report.md"

# Стили для Ч/Б и цветной печати (более строгие цвета)
LINE_STYLES = ['-', '--', '-.', ':', (0, (3, 5, 1, 5)), (0, (5, 10))]
MARKERS = ['o', 's', '^', 'D', 'x', 'v']
# Менее насыщенные, "строгие" цвета
COLORS = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD', '#8C8C8C', '#EAEAF2']
HATCHES = ['/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*']
BAR_HATCHES = ['///', '...', 'xxx', '\\\\\\', '+++', 'OOO']

def log_chart_info(name, params, file_path):
    logger.info(f"\n--- ГЕНЕРАЦИЯ: {name} ---")
    logger.info(f"Файл: {file_path.name}")

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stderr:
        logger.error(f"Ошибка: {result.stderr.strip()}")
    return result.stdout

def get_sim_time_limit():
    """Извлекает sim-time-limit из omnetpp.ini или .sca файлов."""
    ini_file = Path("/home/dev/6_sem/KURSACH_seti/02_model/kursach_model/omnetpp.ini")
    
    # 1. Пробуем прочитать напрямую из omnetpp.ini
    if ini_file.exists():
        try:
            with open(ini_file, 'r') as f:
                for line in f:
                    if "sim-time-limit" in line and "=" in line:
                        match = re.search(r"sim-time-limit\s*=\s*(\d+)", line)
                        if match:
                            val = int(match.group(1))
                            logger.info(f"Найдено sim-time-limit в omnetpp.ini: {val}с")
                            return val
        except Exception as e:
            logger.warning(f"Ошибка при чтении {ini_file}: {e}")

    # 2. Если не вышло, ищем в .sca файлах (берем максимум)
    sca_files = list(OMNETPP_DIR.glob("*.sca"))
    max_limit = 60
    found_any = False
    
    for sca_file in sca_files:
        try:
            with open(sca_file, 'r') as f:
                for line in f:
                    if "config sim-time-limit" in line:
                        match = re.search(r"sim-time-limit\s+(\d+)", line)
                        if match:
                            val = int(match.group(1))
                            if val > max_limit or not found_any:
                                max_limit = val
                                found_any = True
        except Exception as e:
            continue
            
    if found_any:
        logger.info(f"Найдено sim-time-limit в .sca файлах: {max_limit}с")
        return max_limit
        
    return 60

def setup_plot_style():
    plt.rcParams.update({
        'font.size': 11,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.titlesize': 14,
        'text.color': '#2f2f2f',
        'axes.labelcolor': '#2f2f2f',
        'xtick.color': '#2f2f2f',
        'ytick.color': '#2f2f2f',
        'axes.prop_cycle': plt.cycler(color=COLORS),
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--'
    })

def generate_io_graph_a():
    name = "wireshark_io_graph.png"
    pcap = PCAP_DIR / "A_Base-core.pcap"
    log_chart_info("Wireshark IO Graph (A_Base)", {"pcap": str(pcap)}, CHARTS_DIR / name)
    
    cmd = f"tshark -r {pcap} -T fields -e frame.time_relative -e frame.len"
    data = run_command(cmd)
    
    df = pd.DataFrame([l.split('\t') for l in data.strip().split('\n') if '\t' in l], columns=['time', 'len'])
    df['time'] = pd.to_numeric(df['time'])
    df['len'] = pd.to_numeric(df['len'])
    df['time_sec'] = df['time'].astype(int)
    io_data = df.groupby('time_sec')['len'].sum() * 8 / 1000 # Kbps
    
    log_data_summary(name, {
        "Макс. нагрузка": f"{io_data.max():.2f} Кбит/с",
        "Сред. нагрузка": f"{io_data.mean():.2f} Кбит/с",
        "Всего передано": f"{(df['len'].sum() / 1024 / 1024):.2f} Мбайт"
    })

    setup_plot_style()
    plt.figure(figsize=(9, 4.5))
    plt.plot(io_data.index, io_data.values, linestyle='-', color=COLORS[0], linewidth=1.5, label='Трафик (Kbps)')
    plt.fill_between(io_data.index, io_data.values, color=COLORS[0], alpha=0.15)
    
    sim_limit = get_sim_time_limit()
    plt.xlim(0, max(sim_limit, io_data.index.max() if not io_data.empty else 0))
    
    plt.title('Интенсивность трафика на Core-маршрутизаторе (Сценарий A)')
    plt.xlabel('Относительное время (с)')
    plt.ylabel('Пропускная способность (Кбит/с)')
    plt.legend()
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def generate_protocol_hierarchy():
    name = "protocol_hierarchy.png"
    pcap = PCAP_DIR / "A_Base-core.pcap"
    log_chart_info("Protocol Hierarchy", {"pcap": str(pcap)}, CHARTS_DIR / name)
    
    # Используем tshark -G protocols для получения списка протоколов не поможет тут.
    # Используем -T fields для подсчета конкретных пакетов
    protos = {
        'TCP': 'tcp',
        'OSPF': 'ospf',
        'ICMP': 'icmp',
        'ARP': 'arp'
    }
    
    proto_counts = {}
    for label, filter_str in protos.items():
        cmd = f"tshark -r {pcap} -Y '{filter_str}' -T fields -e frame.number | wc -l"
        count = int(run_command(cmd).strip())
        if count > 0:
            proto_counts[label] = count

    labels = list(proto_counts.keys())
    sizes = list(proto_counts.values())
    
    if not sizes:
        logger.warning(f"Нет данных для {name}")
        return

    # Сортировка по убыванию и вывод всех протоколов
    sorted_protos = sorted(proto_counts.items(), key=lambda x: x[1], reverse=True)
    total_pkts = sum(sizes)
    summary = {label: f"{count} пкт ({count/total_pkts*100:.1f}%)" for label, count in sorted_protos}
    log_data_summary(name, summary)

    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(aspect="equal"))
    
    # Рисуем саму диаграмму без стандартных подписей внутри
    wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.5, alpha=0.8, edgecolor='#2f2f2f'), startangle=140, colors=COLORS[:len(labels)])

    # Настройка выносок (bbox и стрелки)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="0.5", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

    # Собираем данные для всех подписей
    label_data = []
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        pct = sizes[i]/total_pkts*100
        label_text = f"{labels[i]}\n({pct:.1f}%)"
        label_data.append({
            'x': x, 'y': y, 'ang': ang, 'text': label_text, 'i': i
        })

    # Сортируем подписи по вертикали (y) для каждой стороны (лево/право)
    # Это поможет распределить их равномерно
    for side in [-1, 1]: # -1 для левой, 1 для правой
        side_labels = [d for d in label_data if np.sign(d['x']) == side]
        if not side_labels: continue
        
        # Сортируем по y сверху вниз
        side_labels.sort(key=lambda d: d['y'], reverse=True)
        
        # Минимальное расстояние между подписями по вертикали
        min_dist = 0.25
        y_positions = [d['y'] for d in side_labels]
        
        # Итеративно раздвигаем подписи, если они слишком близко
        for _ in range(50): # Максимум 50 итераций для сходимости
            changed = False
            for j in range(len(y_positions) - 1):
                if y_positions[j] - y_positions[j+1] < min_dist:
                    diff = min_dist - (y_positions[j] - y_positions[j+1])
                    y_positions[j] += diff / 2
                    y_positions[j+1] -= diff / 2
                    changed = True
            if not changed: break

        # Рисуем аннотации с учетом скорректированных y
        for j, d in enumerate(side_labels):
            horizontalalignment = "left" if side > 0 else "right"
            connectionstyle = f"angle,angleA=0,angleB={d['ang']}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            
            # xy - точка на сегменте, xytext - позиция текста
            # Уменьшаем вынос (с 1.5 до 1.2, т.е. на 20%)
            ax.annotate(d['text'], xy=(d['x'], d['y']), 
                        xytext=(1.2 * side, y_positions[j] * 1.2),
                        horizontalalignment=horizontalalignment, **kw)

    # Применяем штриховку к сегментам
    for i, p in enumerate(wedges):
        p.set_hatch(HATCHES[i % len(HATCHES)])

    plt.title('Распределение протоколов в канале (Сценарий A)', pad=20)
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def get_sca_file(config_name):
    """Находит .sca файл для заданного конфига, пробуя разные варианты имен."""
    variants = [
        OMNETPP_DIR / f"{config_name}-0.sca",
        OMNETPP_DIR / f"{config_name}-#0.sca"
    ]
    for v in variants:
        if v.exists():
            return v
    return None

def generate_rtt_comparison():
    name = "internet_rtt_comparison.png"
    configs = ["A_Base", "B_ReserveEnabled", "C_FailurePrimary", "D_ScaleUp"]
    labels = ["Штатный", "Резерв", "Отказ", "Масштаб"]
    log_chart_info("TCP Delay Comparison Across Scenarios", {"configs": configs}, CHARTS_DIR / name)
    
    values = []
    # Паттерны для всех типов хостов в HQ (включая Extra)
    # ВАЖНО: В сценарии D используются только Pc, без Extra (в omnetpp.ini)
    hq_patterns = [
        r"adminPc", r"adminExtra",
        r"accPc", r"accExtra",
        r"dirPc", r"dirExtra",
        r"warPc", r"warExtra",
        r"kitPc", r"kitExtra",
        r"hallPc", r"hallExtra"
    ]
    
    for config in configs:
        sca_file = get_sca_file(config)
        avg_val = 0
        if sca_file:
            with open(sca_file, 'r') as f:
                content = f.read()
            
            delays = []
            for pattern in hq_patterns:
                # Ищем статистику endToEndDelay для всех хостов HQ
                # Используем более широкий поиск, так как app[*] может меняться
                matches = re.findall(rf"statistic KursachNetwork\.{pattern}\[\d+\]\.app\[\d+\]\s+endToEndDelay:histogram\nfield count\s+[1-9]\d*\nfield mean\s+([\d\.e\-nan]+)", content)
                for m in matches:
                    if m and 'nan' not in m:
                        try:
                            delays.append(float(m))
                        except ValueError:
                            continue
            
            if delays:
                avg_val = (sum(delays) / len(delays)) * 1000
        values.append(avg_val)

    log_data_summary(name, dict(zip(labels, [f"{v:.3f} мс" for v in values])))

    setup_plot_style()
    plt.figure(figsize=(9, 5.5))
    bars = plt.bar(labels, values, color=COLORS[:len(labels)], edgecolor='#2f2f2f', linewidth=1, alpha=0.85)
    for i, bar in enumerate(bars):
        bar.set_hatch(BAR_HATCHES[i % len(BAR_HATCHES)])
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.title('Сравнение средней задержки TCP (End-to-End) по сценариям')
    plt.ylabel('Средняя задержка (мс)')
    plt.xlabel('Сценарий моделирования')
    
    max_val = max(values) if values else 0
    plt.ylim(0, max_val * 1.2 if max_val > 0 else 5)
    
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def generate_tcp_delay_dist():
    name = "rtt_types_A.png"
    pcap = PCAP_DIR / "A_Base-core.pcap"
    log_chart_info("TCP ACK RTT Distribution", {"pcap": str(pcap)}, CHARTS_DIR / name)
    
    cmd = f"tshark -r {pcap} -Y 'tcp.analysis.ack_rtt' -T fields -e tcp.analysis.ack_rtt"
    data = run_command(cmd)
    rtts = [float(x) * 1000 for x in data.strip().split('\n') if x]
    
    if not rtts: return
    
    import numpy as np
    log_data_summary(name, {
        "Пакетов": len(rtts),
        "Мин/Макс RTT": f"{min(rtts):.2f} / {max(rtts):.2f} мс",
        "Средний RTT": f"{np.mean(rtts):.2f} мс",
        "Медиана": f"{np.median(rtts):.2f} мс"
    })

    setup_plot_style()
    plt.figure(figsize=(9, 5))
    
    # Используем логарифмическую шкалу по X для наглядности разброса (0.5ms vs 40ms)
    import numpy as np
    # Увеличиваем количество бинов (шаг мельче) по запросу пользователя
    bins = np.logspace(np.log10(min(rtts)), np.log10(max(rtts)), 100)
    plt.hist(rtts, bins=bins, color=COLORS[2], edgecolor='#2f2f2f', alpha=0.7, hatch='//')
    plt.xscale('log')
    
    from matplotlib.ticker import ScalarFormatter
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.xticks([0.5, 1, 5, 10, 20, 40])
    
    plt.title('Распределение задержек TCP ACK (Сценарий A, лог-шкала)')
    plt.xlabel('RTT (мс) - Логарифмическая шкала')
    plt.ylabel('Частота (кол-во пакетов)')
    
    # Аннотации убраны по запросу пользователя
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def generate_scalability_chart():
    name = "scalability_rtt.png"
    configs = ["A_Base", "D_ScaleUp"]
    labels = ["Базовый (30 РМ)", "Масштаб (43 РМ)"]
    log_chart_info("Scalability Throughput Analysis", {"configs": configs}, CHARTS_DIR / name)
    
    throughput = []
    for config in configs:
        pcap = PCAP_DIR / f"{config}-core.pcap"
        if pcap.exists():
            # Извлекаем все кадры, считаем суммарный объем
            # В сценарии A трафик идет через ppp2 (интернет), в D тоже.
            # Но core.pcap содержит ВЕСЬ трафик на всех интерфейсах маршрутизатора.
            # Нам нужен именно интернет-трафик к externalResource (10.0.90.10)
            # Фильтруем по IP адресу внешнего ресурса
            internet_filter = "ip.addr == 10.0.90.10"
            cmd_stable = f"tshark -r {pcap} -Y 'frame.time_relative >= 20 and frame.time_relative <= 60 and {internet_filter}' -T fields -e frame.len"
            data_stable = run_command(cmd_stable)
            lengths_stable = [int(x) for x in data_stable.strip().split('\n') if x]
            
            avg_kbps = sum(lengths_stable) * 8 / 1000 / 40 if lengths_stable else 0
            throughput.append(avg_kbps)
        else:
            throughput.append(0)

    diff_pct = ((throughput[1] - throughput[0]) / throughput[0] * 100) if throughput[0] > 0 else 0
    log_data_summary(name, {
        labels[0]: f"{throughput[0]:.1f} Кбит/с",
        labels[1]: f"{throughput[1]:.1f} Кбит/с",
        "Рост трафика": f"{diff_pct:+.1f}%"
    })

    setup_plot_style()
    plt.figure(figsize=(7, 5))
    bars = plt.bar(labels, throughput, color=[COLORS[6], COLORS[0]], edgecolor='#2f2f2f', width=0.5, alpha=0.8)
    bars[0].set_hatch('...')
    bars[1].set_hatch('xxx')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f} Кбит/с', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.title('Анализ масштабируемости: Средняя интернет-нагрузка (20-60с)')
    plt.ylabel('Средняя пропускная способность (Кбит/с)')
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def generate_combined_io():
    name = "combined_io_graph.png"
    configs = ["A_Base", "B_ReserveEnabled", "C_FailurePrimary", "D_ScaleUp"]
    setup_plot_style()
    plt.figure(figsize=(12, 6))
    bw_styles = [
        {'linestyle': '-',  'marker': 'o'},
        {'linestyle': '--', 'marker': 's'},
        {'linestyle': '-.', 'marker': '^'},
        {'linestyle': ':',  'marker': 'D'},
    ]
    
    # Фильтр для интернет-трафика (как в scenario_c_channels)
    # Показываем трафик именно до внешнего ресурса, чтобы сравнение было корректным
    internet_filter = "ip.addr == 10.0.90.10"
    
    # Словарь для хранения данных всех сценариев для итогового вывода в консоль
    all_scenarios_data = {}
    max_time_found = 0
    
    for i, cfg in enumerate(configs):
        pcap = PCAP_DIR / f"{cfg}-core.pcap"
        if not pcap.exists() or pcap.stat().st_size <= 28: continue
        
        # Считаем только интернет-трафик для честного сравнения всех сценариев
        cmd = f"tshark -r {pcap} -Y '{internet_filter}' -T fields -e frame.time_relative -e frame.len"
        data = run_command(cmd)
        if not data.strip(): continue
        
        df = pd.DataFrame([l.split('\t') for l in data.strip().split('\n') if '\t' in l], columns=['time', 'len'])
        df['time'] = pd.to_numeric(df['time'])
        df['len'] = pd.to_numeric(df['len'])
        df['time_sec'] = df['time'].astype(int)
        
        current_max = int(df['time_sec'].max())
        if current_max > max_time_found:
            max_time_found = current_max
            
        # Группируем по секундам и считаем Кбит/с
        io = df.groupby('time_sec')['len'].sum() * 8 / 1000
        all_scenarios_data[cfg] = io

    # Вторая итерация для реиндексации и построения графиков с учетом общего max_time
    # Для графиков используем значение из конфига симуляции (минимум 60с)
    sim_limit = get_sim_time_limit()
    plot_limit = max(sim_limit, max_time_found)
     
    for i, cfg in enumerate(configs):
        if cfg not in all_scenarios_data: continue
        
        io = all_scenarios_data[cfg]
        # Заполняем пропуски нулями до лимита графика
        io = io.reindex(range(0, plot_limit + 1), fill_value=0)
        
        # Сглаживание
        io_smooth = io.rolling(window=2, min_periods=1).mean()
        all_scenarios_data[cfg] = io_smooth # Сохраняем сглаженные данные для таблицы
        style = bw_styles[i % len(bw_styles)]
        plt.plot(
            io_smooth.index,
            io_smooth.values,
            label=f'Сценарий {cfg[0]}',
            color=COLORS[i],
            linewidth=2,
            linestyle=style['linestyle'],
            marker=style['marker'],
            markersize=4,
            markevery=max(1, plot_limit // 12), # Адаптивные маркеры
        )

    # Логирование конкретных значений для всех сценариев (адаптивный шаг)
    if all_scenarios_data:
        logger.info(f"\n--- ГЕНЕРАЦИЯ: {name} ---")
        step = max(1, max_time_found // 10)
        logger.info(f"  Контрольные значения (с шагом {step}с):")
        header = f"  {'Время (с)':<10}"
        for cfg in configs:
            if cfg in all_scenarios_data:
                header += f" | {cfg[0]:<10}"
        logger.info(header)
        logger.info("-" * len(header))
        
        # Генерируем временные точки, включая последнюю секунду (plot_limit)
        time_points = list(range(0, plot_limit + 1, step))
        if plot_limit not in time_points:
            time_points.append(plot_limit)

        for t in time_points:
            row = f"  {t:<10}"
            for cfg in configs:
                if cfg in all_scenarios_data:
                    val = all_scenarios_data[cfg].get(t, 0)
                    row += f" | {val:<10.2f}"
            logger.info(row)

    plt.xlim(0, plot_limit) # Явно задаем границы X-оси
    plt.title('Сравнение интернет-нагрузки (TCP) во всех сценариях')
    plt.xlabel('Время (с)')
    plt.ylabel('Пропускная способность (Кбит/с)')
    
    # Установка шага временной шкалы в 5 секунд
    from matplotlib.ticker import MultipleLocator
    plt.gca().xaxis.set_major_locator(MultipleLocator(5))
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def generate_host_type_rtt():
    name = "rtt_by_host_type.png"
    sca_file = get_sca_file("A_Base")
    log_chart_info("RTT by Host Type (Scenario A)", {"sca": str(sca_file)}, CHARTS_DIR / name)
    
    if not sca_file: return
    
    types = {
        'Admin (Local HQ)': r"KursachNetwork\.adminPc\[\d+\]\.app\[2\]",
        'Accounting (Internet)': r"KursachNetwork\.accPc\[\d+\]\.app\[1\]",
        'Branch (to HQ)': r"KursachNetwork\.br1Host\[\d+\]\.app\[1\]"
    }
    
    with open(sca_file, 'r') as f:
        content = f.read()
    
    results = {}
    for t_name, pattern in types.items():
        # Более гибкий поиск для статистики
        matches = re.findall(rf"statistic {pattern}\s+rtt:stats\nfield count\s+\d+\nfield mean\s+([\d\.e\-]+)", content)
        # Фильтруем пустые или некорректные значения
        valid_matches = [m for m in matches if m and m != '-' and 'nan' not in m]
        if valid_matches:
            avg_rtt = sum(float(m) for m in valid_matches) / len(valid_matches) * 1000
            results[t_name] = avg_rtt
        else:
            # Попробуем найти просто rtt:mean если нет блока статистики
            matches = re.findall(rf"scalar {pattern}\s+rtt:mean\s+([\d\.e\-]+)", content)
            valid_matches = [m for m in matches if m and m != '-' and 'nan' not in m]
            if valid_matches:
                avg_rtt = sum(float(m) for m in valid_matches) / len(valid_matches) * 1000
                results[t_name] = avg_rtt

    if not results: return
    
    # Логируем данные для анализа в отчете
    log_data_summary(name, {k: f"{v:.2f} мс" for k, v in results.items()})

    # Сортируем результаты по значению RTT для логичного порядка на графике
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]))

    setup_plot_style()
    plt.figure(figsize=(9, 5))
    # Строгие цвета
    bars = plt.bar(sorted_results.keys(), sorted_results.values(), color=COLORS[4:7], edgecolor='#2f2f2f', alpha=0.8)
    for i, bar in enumerate(bars):
        bar.set_hatch(BAR_HATCHES[i % len(BAR_HATCHES)])
        # Добавляем подписи значений
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.2f} ms', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.title('Среднее RTT по категориям трафика (Сценарий A)')
    plt.ylabel('RTT (мс)')
    plt.ylim(0, max(sorted_results.values()) * 1.2)
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def generate_tcp_delay_series():
    name = "tcp_delay_chart.png"
    pcap = PCAP_DIR / "A_Base-core.pcap"
    log_chart_info("TCP Delay Time Series", {"pcap": str(pcap)}, CHARTS_DIR / name)
    
    cmd = f"tshark -r {pcap} -Y 'tcp.analysis.ack_rtt' -T fields -e frame.time_relative -e tcp.analysis.ack_rtt"
    data = run_command(cmd)
    
    lines = [l.split('\t') for l in data.strip().split('\n') if '\t' in l]
    if not lines: return
    
    df = pd.DataFrame(lines, columns=['time', 'rtt'])
    df['time'] = pd.to_numeric(df['time'])
    df['rtt'] = pd.to_numeric(df['rtt']) * 1000 # ms
    
    # Ресемплирование и скользящее среднее для максимальной плавности
    # Группируем по 1 секунде и берем среднее
    df['time_bin'] = df['time'].astype(int)
    resampled = df.groupby('time_bin')['rtt'].mean()
    
    # Применяем скользящее среднее (rolling mean) для еще большей стабильности
    smoothed = resampled.rolling(window=3, center=True, min_periods=1).mean()
    
    log_data_summary(name, {
        "Средний RTT": f"{smoothed.mean():.3f} мс",
        "Отклонение (std)": f"{smoothed.std():.3f} мс",
        "Стабильность": "Высокая" if smoothed.std() < 1 else "Средняя"
    })

    setup_plot_style()
    plt.figure(figsize=(10, 5))
    # Уменьшенные точки и линии для чистоты графика
    plt.plot(smoothed.index, smoothed.values, color=COLORS[3], marker='o', 
             markersize=2, linewidth=1, linestyle='-', label='RTT (сглажено, 3s window)')
    
    # Добавим область разброса (минимум/максимум в окне) для информативности
    resampled_max = df.groupby('time_bin')['rtt'].max()
    resampled_min = df.groupby('time_bin')['rtt'].min()
    plt.fill_between(resampled.index, resampled_min, resampled_max, color=COLORS[3], alpha=0.1, label='Разброс (min/max)')

    sim_limit = get_sim_time_limit()
    plt.xlim(0, max(sim_limit, smoothed.index.max() if not smoothed.empty else 0))

    plt.title('Динамика задержки TCP ACK во времени (Сценарий A)')
    plt.xlabel('Время (с)')
    plt.ylabel('RTT (мс)')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

def generate_dual_channel_c():
    name = "scenario_c_channels.png"
    logger.info(f"\n--- ГЕНЕРАЦИЯ: Scenario C Failover ---")
    pcap_p2 = PCAP_DIR / "C_FailurePrimary-ppp2.pcap"
    pcap_p3 = PCAP_DIR / "C_FailurePrimary-ppp3.pcap"
    pcap_core = PCAP_DIR / "C_FailurePrimary-core.pcap"

    def get_io_data_from_pcap(pcap_file, filter_str=""):
        if not pcap_file.exists() or pcap_file.stat().st_size <= 28:
            return pd.Series(dtype=float)

        filter_cmd = f" -Y '{filter_str}'" if filter_str else ""
        cmd = f"tshark -r {pcap_file}{filter_cmd} -T fields -e frame.time_relative -e frame.len"
        data = run_command(cmd)
        if not data.strip():
            return pd.Series(dtype=float)

        df = pd.DataFrame([l.split('\t') for l in data.strip().split('\n') if '\t' in l], columns=['time', 'len'])
        df['time'] = pd.to_numeric(df['time'])
        df['len'] = pd.to_numeric(df['len'])
        df['time_sec'] = df['time'].astype(int)
        return df.groupby('time_sec')['len'].sum() * 8 / 1000

    # Фильтруем трафик, чтобы показать только интернет-трафик (к externalResource)
    # Это сделает переключение между ppp2 и ppp3 более наглядным и "стабильным" в сумме
    internet_filter = "tcp and (ip.addr == 10.0.90.10)"
    
    io_ppp2_tcp = get_io_data_from_pcap(pcap_p2, internet_filter)
    io_ppp3_tcp = get_io_data_from_pcap(pcap_p3, internet_filter)
    
    # Для общего графика берем сумму ppp2 и ppp3, так как это и есть весь интернет-трафик
    # Это гарантирует, что сумма будет стабильной, если переключение работает
    setup_plot_style()
    plt.figure(figsize=(12, 6))

    # Находим максимальное время среди обоих каналов
    max_t2 = int(io_ppp2_tcp.index.max()) if not io_ppp2_tcp.empty else 0
    max_t3 = int(io_ppp3_tcp.index.max()) if not io_ppp3_tcp.empty else 0
    max_time = max(max_t2, max_t3, 1)
    
    # Для графиков используем значение из конфига симуляции (минимум 60с)
    sim_limit = get_sim_time_limit()
    plot_limit = max(sim_limit, max_time)

    full_idx = range(0, plot_limit + 1)

    def prepare_series(s):
        return s.reindex(full_idx, fill_value=0)

    p2_plot = prepare_series(io_ppp2_tcp)
    p3_plot = prepare_series(io_ppp3_tcp)
    
    # Суммарный интернет-трафик
    total_plot = p2_plot + p3_plot

    plt.plot(total_plot.index, total_plot.values, color='black', linewidth=2.5, label='Суммарный интернет-трафик (TCP)')
    plt.fill_between(total_plot.index, total_plot.values, color='gray', alpha=0.1)
    
    plt.plot(p2_plot.index, p2_plot.values, color=COLORS[0], linewidth=2, linestyle='-.', marker='*', markersize=6, markevery=max(1, plot_limit // 12), label='Основной канал (ppp2)')
    plt.plot(p3_plot.index, p3_plot.values, color=COLORS[1], linewidth=2, linestyle='--', label='Резервный канал (ppp3)')

    plt.axvline(x=15, color='red', linestyle=':', alpha=0.8)
    plt.axvline(x=35, color='green', linestyle=':', alpha=0.8)

    ymax = max(total_plot.max(), p2_plot.max(), p3_plot.max(), 1)
    plt.text(15.2, ymax * 0.92, 'Обрыв', color='red', fontweight='bold')
    plt.text(35.2, ymax * 0.92, 'Восстановление', color='green', fontweight='bold')

    plt.xlim(0, plot_limit)
    plt.title('TCP-переключение между основным и резервным каналом (Сценарий C)')
    plt.xlabel('Время (с)')
    plt.ylabel('Пропускная способность TCP (Кбит/с)')
    
    # Установка шага временной шкалы в 5 секунд
    from matplotlib.ticker import MultipleLocator
    plt.gca().xaxis.set_major_locator(MultipleLocator(5))
    
    # Логирование конкретных значений (адаптивный шаг по запросу)
    step = max(1, max_time // 10)
    logger.info(f"  Контрольные значения (с шагом {step}с):")
    logger.info(f"  {'Время (с)':<10} | {'Total':<10} | {'ppp2':<10} | {'ppp3':<10}")
    logger.info("-" * 48)
    
    # Генерируем временные точки, включая последнюю секунду (plot_limit)
    time_points = list(range(0, plot_limit + 1, step))
    if plot_limit not in time_points:
        time_points.append(plot_limit)

    for t in time_points:
        v_total = total_plot.get(t, 0)
        v_p2 = p2_plot.get(t, 0)
        v_p3 = p3_plot.get(t, 0)
        logger.info(f"  {t:<10} | {v_total:<10.2f} | {v_p2:<10.2f} | {v_p3:<10.2f}")

    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.2)
    plt.savefig(CHARTS_DIR / name, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    os.makedirs(CHARTS_DIR, exist_ok=True)
    logger.info("===============================================")
    logger.info("   НАЧАЛО АВТОМАТИЧЕСКОЙ ГЕНЕРАЦИИ ГРАФИКОВ    ")
    logger.info("===============================================")
    
    generate_combined_io()
    generate_dual_channel_c()
    generate_host_type_rtt()
    generate_io_graph_a()
    generate_protocol_hierarchy()
    generate_rtt_comparison()
    generate_scalability_chart()
    generate_tcp_delay_dist()
    generate_tcp_delay_series()
    
    logger.info("\n===============================================")
    logger.info("        ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО           ")
    logger.info("===============================================")
