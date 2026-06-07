import re
from math import isfinite
from pathlib import Path

RESULTS_DIR = Path("/home/dev/6_sem/KURSACH_seti/03_results")
OMNETPP_DIR = RESULTS_DIR / "omnetpp"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def load_lines(path: Path) -> list[str]:
    text = load_text(path)
    return text.splitlines() if text else []


def _parse_float(value: str) -> float | None:
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if isfinite(parsed) else None


def find_scalar(lines: list[str], module: str, scalar_name: str) -> float | None:
    prefix = f"scalar {module} {scalar_name} "
    for line in lines:
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
            return _parse_float(value)
    return None


def find_stat_field(lines: list[str], module: str, statistic_name: str, field_name: str) -> float | None:
    prefix = f"statistic {module} {statistic_name}"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            for nested in lines[index + 1:]:
                if nested.startswith("statistic "):
                    break
                field_prefix = f"field {field_name} "
                if nested.startswith(field_prefix):
                    value = nested[len(field_prefix):].strip()
                    return _parse_float(value)
    return None


def count_lines_with_substrings(lines: list[str], *parts: str) -> int:
    total = 0
    for line in lines:
        if all(part in line for part in parts):
            total += 1
    return total


def count_targeted_events(lines: list[str], command: str, target: str, lookahead: int = 6) -> int:
    total = 0
    marker = f"processing <{command}> command"
    for index, line in enumerate(lines):
        if marker not in line:
            continue
        window = lines[index + 1:index + 1 + lookahead]
        if any(target in candidate for candidate in window):
            total += 1
    return total


def avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def find_all_stat_fields(lines: list[str], module_pattern: str, statistic_name: str, field_name: str, min_count: int = 1) -> list[float]:
    """Находит значения поля для статистики во всех приложениях модуля, подходящих под паттерн"""
    results = []
    content = "\n".join(lines)
    
    # Ищем блоки статистики. Мы должны убедиться, что field count >= min_count
    # Используем re.DOTALL для поиска по нескольким строкам внутри блока statistic
    # Блок заканчивается следующей директивой (scalar, statistic, и т.д.) или концом файла
    
    # Паттерн для поиска блока статистики
    stat_pattern = rf"statistic\s+({module_pattern}\.app\[\d+\])\s+{re.escape(statistic_name)}"
    
    for match in re.finditer(stat_pattern, content):
        start_pos = match.end()
        # Ищем до следующей директивы
        end_match = re.search(r"\n(statistic|scalar|par|attr|run|version)\s", content[start_pos:])
        block_end = start_pos + end_match.start() if end_match else len(content)
        block = content[start_pos:block_end]
        
        # Проверяем count
        count_match = re.search(r"field\s+count\s+(\d+)", block)
        if count_match:
            count = int(count_match.group(1))
            if count < min_count:
                continue
        
        # Ищем нужное поле
        field_match = re.search(rf"field\s+{re.escape(field_name)}\s+([\d\.e\-nan]+)", block)
        if field_match:
            val = _parse_float(field_match.group(1))
            if val is not None:
                results.append(val)
                
    return results


def hq_host_modules(lines: list[str]) -> list[str]:
    """Динамически находит все модули хостов в HQ из SCA-файла"""
    modules = set()
    # Ищем строки вида 'scalar KursachNetwork.adminPc[0].app[0] ...'
    # или 'statistic KursachNetwork.adminExtra[0].app[0] ...'
    pattern = re.compile(r"(scalar|statistic)\s+(KursachNetwork\.(admin|acc|dir|war|kit|hall)(Pc|Extra)\[\d+\])")
    for line in lines:
        match = pattern.search(line)
        if match:
            modules.add(match.group(2))
    return sorted(list(modules))
