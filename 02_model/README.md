# Подготовка среды OMNeT++/INET

## Текущий статус

- OMNeT++ `6.0.3` распакован и собран в `02_model/omnetpp-6.0.3`.
- INET `4.5.4` распакован и собран в `02_model/inet4.5`.
- Проверочный запуск OMNeT++ sample (`aloha`) выполнен успешно.
- Проверочный запуск INET example (`udp_OK_ipv4`) выполнен успешно.
- Создан базовый каркас проекта: `02_model/kursach_model`.

## Быстрый запуск окружения

Из директории `/home/dev/6_sem/KURSACH_seti/02_model`:

```bash
source ./use_env.sh
```

## Запуск симуляции (GUI и Текст)

Перейдите в папку модели:
```bash
cd /home/dev/6_sem/KURSACH_seti/02_model/kursach_model
```

**1. Запуск в графическом режиме (Qtenv):**
```bash
inet -u Qtenv -c A_Base omnetpp.ini
```
*Примечание: Вы можете менять `-c A_Base` на `B_ReserveEnabled`, `C_FailurePrimary` или `D_ScaleUp` для запуска разных сценариев.*

**2. Запуск в текстовом режиме (Cmdenv) для быстрого сбора данных:**
```bash
inet -u Cmdenv -c A_Base omnetpp.ini
```

## Что дальше

1. Расширить `KursachNetwork.ned` до топологии варианта (6 кабинетов, 30 рабочих мест, 2 сервера, 2 филиала).
2. Ввести резервный канал и сценарий отказа канала.
3. Добавить конфигурации экспериментов A/B/C/D в `omnetpp.ini`.
4. Подготовить сбор метрик задержки и экспорт результатов в `03_results`.
