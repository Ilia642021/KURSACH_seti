# Доказательства успешной работы сети (Сценарий C: Отказ канала)

Этот файл содержит описание ключевых событий в логах симуляции, подтверждающих корректную работу механизмов отказоустойчивости (Fast OSPF) и успешное переключение на резервный канал.

## Файл логов
Все данные взяты из файла: `02_model/kursach_model/simulation_log_c.txt`

---

## 1. Событие обрыва связи (T = 10.0 сек)
**Строки: 79599 – 79610**
Здесь `ScenarioManager` выполняет команду `shutdown` для интерфейса `ppp2` (основной канал между Core и ISP).

```text
79599: ** Event #4319  t=10 ... KursachNetwork.scenarioManager (ScenarioManager, id=3)
79600: [INFO] processing <at> command...
79601: [INFO] processing <shutdown> command...
79602: [INFO] Doing stage 0/8 of operation inet::ModuleStopOperation on KursachNetwork.core.ppp[2]
...
79608: [INFO] ** Signal at T=10 ... interfaceStateChanged ppp2 ... DOWN
```

---

## 2. Реакция протокола OSPF
**Строка: 79612**
Протокол OSPF мгновенно обнаруживает потерю соседа на упавшем интерфейсе.

```text
79612: [INFO] Changing neighborhood state of 10.0.100.6 from 'Full' to 'Down'
```

---

## 3. Переключение на резервный канал (ppp3)
**Строка: 178132**
Доказательство того, что пакеты (на примере `ping24` в момент T=54с) теперь маршрутизируются через резервный интерфейс `ppp3`.

```text
178132: [INFO] Routing (inet::Packet)ping24 ... destination = 10.0.5.2, output interface = ppp3, next hop address = 10.0.100.6
```

---

## 4. Успешная доставка пакетов и замеры RTT
**Строки: 189652 – 189653**
Подтверждение получения ответов (ICMP Echo Reply) и замер задержки (RTT) после переключения.

```text
189652: KursachNetwork.hqHost[0].app[0]: reply of 56 bytes from 10.0.0.31 ... time=0.4352 msec
189653: [INFO] Ping reply #29 arrived, rtt=0.0004352
```

---

## Резюме
Логи подтверждают, что:
1. Система имитирует отказ в заданное время (10с).
2. OSPF перестраивает таблицу маршрутизации.
3. Связь восстанавливается через резервный канал `ppp3`.
4. Задержки (RTT) соответствуют расчетным параметрам резервного канала.
