# Контрольная точка проекта (Context Checkpoint)
Дата: 18.05.2026

## 1. Что было исправлено в модели (Critical Fixes)
- **Маршрутизация ([routing.xml](file:///home/dev/6_sem/KURSACH_seti/02_model/kursach_model/routing.xml)):** 
  - Исправлены селекторы хостов: вместо `hqHost` теперь `cab*.h*` и `hqSrv*`.
  - Добавлены маршруты по умолчанию для всех сегментов (HQ через `core`, филиалы через свои роутеры).
  - Настроены интерфейсы для HQ LAN (`10.0.3.x`).
- **Топология ([KursachNetwork.ned](file:///home/dev/6_sem/KURSACH_seti/02_model/kursach_model/KursachNetwork.ned)):**
  - Подтверждена структура кабинетов (6 штук по 5 хостов = 30 в базе).
- **Конфигурация ([omnetpp.ini](file:///home/dev/6_sem/KURSACH_seti/02_model/kursach_model/omnetpp.ini)):**
  - Увеличено число портов `hqSw.numEthInterfaces = 33` (иначе хосты не могли подключиться).
  - Исправлены цели PingApp: теперь `cab1.h1` пингует `hqSrv[0]`, а `cab1.h2` пингует `inetHost`.

## 2. Результаты симуляций (Status)
- **Сценарий A (Base):** Работает. RTT ~0.443 мс.
- **Сценарий B (Reserve):** Работает. OSPF корректно выбирает основной канал (ppp2, cost 10) вместо резервного (ppp3, cost 20).
- **Сценарий C (Failure):** Работает. Отказ в 10с, переключение на резерв мгновенное (в модели). Восстановление в 25с, возврат на основной канал (preemption) подтвержден.
- **Сценарий D (Scale):** Работает. 43 хоста в HQ. Нагрузка выросла, RTT стабилен.

## 3. Скрипты анализа ([analyze_*.py](file:///home/dev/6_sem/KURSACH_seti/))
- Все скрипты обновлены: теперь они ищут векторы для `cab1.h1.app[0]` вместо несуществующих `hqHost`.
- Итоговый отчет сгенерирован в [full_analysis_report.txt](file:///home/dev/6_sem/KURSACH_seti/03_results/full_analysis_report.txt).

## 4. Следующие шаги (Next Steps)
1. Финализировать текст страниц 13-17 в `04_report_pages/` (данные уже есть в `full_analysis_report.txt`).
2. Собрать финальный отчет `Full_Report.md`.
3. Подготовить спецификацию оборудования (Страница 19-20).

**Все симуляции актуальны, данные в папке `03_results` свежие.**
