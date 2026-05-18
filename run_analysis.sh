#!/bin/bash

OUTPUT_FILE="/home/dev/6_sem/KURSACH_seti/03_results/full_analysis_report.txt"

# Очистить файл если он существует
> "$OUTPUT_FILE"

echo "=== Сбор результатов анализа сценариев ===" >> "$OUTPUT_FILE"
echo "Дата: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

scripts=(
    "/home/dev/6_sem/KURSACH_seti/analyze_A.py"
    "/home/dev/6_sem/KURSACH_seti/analyze_B.py"
    "/home/dev/6_sem/KURSACH_seti/analyze_C.py"
    "/home/dev/6_sem/KURSACH_seti/analyze_D.py"
)

for script in "${scripts[@]}"; do
    echo "--- Запуск $script ---" | tee -a "$OUTPUT_FILE"
    python3 "$script" >> "$OUTPUT_FILE" 2>&1
    echo -e "\n" >> "$OUTPUT_FILE"
done

echo "Анализ завершен. Результаты сохранены в $OUTPUT_FILE"
