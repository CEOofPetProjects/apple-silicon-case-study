# Аналитический кейс по Apple Silicon (ПЕРЕВОД В ПРОЦЕССЕ!)

<small>Этот репозиторий защищён лицензией **CC BY-NC 4.0**.<small>

> <small><b>Язык:</b> Русский | <a href="README.md">Read in English</a></small>

## О чём кейс

Данный кейс был разработан для демонстрации комплексных возможностей проектирования и анализа данных, охватывающих планирование баз данных, моделирование ERD, реализацию схем SQL и анализ данных на языке Python (с использованием pandas, sqlite3, Matplotlib, Seaborn).

## Область применения и границы данных

Набор данных посвящен исключительно чипам Apple Silicon, использовавшимся в компьютерах Mac: всем чипам серии M, за исключением вариантов, предназначенных только для iPad, и варианта A18 Pro, используемого в MacBook Neo; никаких реальных устройств — только сами чипы, их варианты и все конфигурации, когда-либо доступные для Mac.
Данные, полученные со страницы «Сравнение моделей Mac» на веб-сайте Apple и из проверенных баз данных оборудования, содержат основные технические характеристики оборудования для всех конфигураций:
* Технологический процесс (например, TSMC 5nm, 3nm)
* Вычислительные ядра (количества ядер центрального, графического и нейронного процессоров)
* ИИ и память (производительность нейронного процессора, тип, скорость частота и пропускная способность объединённой памяти)
* Ограничения по количеству подключаемых дисплеев, конфигурации памяти и хранилища

## Диаграмма «сущность-связь»

Чтобы устранить избыточность и сохранить третью нормальную форму (3NF), набор данных структурирован по 5 реляционным таблицам, организованным в 3 логических уровня:

* **Поколения и техпроцессы** (`chip_families`) – поколения/семейства процессоров и технологические процессы TSMC
* **Модели чипов и биннинг** (`chips`, `chip_configs`) — общие варианты чипов, а также отдельно вариации чипов: с полным набором ядер и с неполным
* **Ёмкость** (`chip_memory_options`, `chip_storage_options`) — доступные конфигурации ёмкости памяти и хранилища для каждого чипа

![Apple Silicon Database ERD](visualizations/apple_silicon_erd.png)

<details>
<summary><b>Нажмите, чтобы раскрыть словарь данных</b></summary>

### Словарь данных

#### `chip_families`
*Семейства (поколения) чипов и используемые техпроцессы*

| Имя атрибута | Тип данных | Описание и контекст предметной области | Источник |
| :--- | :--- | :--- | :--- |
| `family_id` | `INTEGER` | **PK** Первичный ключ для семейства чипов | — |
| `family_name` | `TEXT` | Поколение/семейство/линейка чипов (от M1 до M5) | Страница сравнения моделей Mac на сайте Apple |
| `family_node` | `TEXT` | Техпроцесс TSMC в нанометрах (*например, 3 нм, 5 нм*) | TechInsights, презентации Apple |

---

#### `chips`
*Модели систем на чипе (SoC)*

| Имя атрибута | Тип данных | Описание и контекст предметной области | Источник |
| :--- | :--- | :--- | :--- |
| `chip_id` | `INTEGER` | **PK** Первичный ключ для конкретного чипа | — |
| `family_id` | `INTEGER` | **FK** Соединяет чип с семейством/поколением из `chip_families` | — |
| `chip_name` | `TEXT` | Коммерческое название чипа (*например, M1, M2 Pro, M3 Max*) | Страница сравнения моделей Mac на сайте Apple |
| `chip_announcement_date` | `DATE` | Дата презентации (`YYYY-MM-DD`) | Пресс-релизы Apple Newsroom |

---

#### `chip_configs`
*Вариации чипов, распределение ядер, вычислительные характеристики конфигурации каждого чипа*

| Имя атрибута | Тип данных | Описание и контекст предметной области | Источник |
| :--- | :--- | :--- | :--- |
| `config_id` | `INTEGER` | **PK** Первичный ключ для конкретной вариации чипа | — |
| `chip_id` | `INTEGER` | **FK** Соединяет конкретную вариацию чипа с его общим названием из `chips` | — |
| `chip_cpu_cores` | `INTEGER` | Общее кол-во ядер CPU | Страница сравнения моделей Mac на сайте Apple |
| `chip_perf_cores` | `INTEGER` | Кол-во производительных ядер CPU | Страница сравнения моделей Mac на сайте Apple |
| `chip_eff_cores` | `INTEGER` | Кол-во энергоэффективных ядер CPU | Страница сравнения моделей Mac на сайте Apple |
| `chip_super_cores` | `INTEGER` | Кол-во супер-ядер CPU (*появились в M5*) | Страница сравнения моделей Mac на сайте Apple |
| `chip_gpu_cores` | `INTEGER` | Количество ядер графического процессора | Страница сравнения моделей Mac на сайте Apple |
| `chip_npu_cores` | `INTEGER` | Количество ядер нейронного процессора | Страница сравнения моделей Mac на сайте Apple |
| `chip_npu_tops` | `REAL` | Производительность нейронного процессора в TOPS | Пресс-релизы и презентации Apple |
| `chip_mem_type` | `TEXT` | Тип памяти (*например, LPDDR5, LPDDR5X*) | Википедия |
| `chip_mem_speed` | `INTEGER` | Тактовая частота памяти в мегагерцах (МГц) | Википедия |
| `chip_mem_bw` | `REAL` | Пиковая пропускная способность памяти в ГБ/с | Страница сравнения моделей Mac на сайте Apple |
| `chip_max_displays` | `INTEGER` | Максимально поддерживаемое количество подключаемых дисплеев | Сайт поддержки Apple |

---

#### `chip_memory_options`
*Поддерживаемые объёмы оперативной памяти в зависимости от аппаратной конфигурации*

| Имя атрибута | Тип данных | Описание и контекст предметной области | Источник |
| :--- | :--- | :--- | :--- |
| `mem_option_id` | `INTEGER` | **PK** Первичный ключ по конфигурации памяти | — |
| `config_id` | `INTEGER` | **FK** Связывает параметр памяти с конфигурацией в `chip_configs` | — |
| `memory_size_gb` | `INTEGER` | Поддерживаемый объём памяти в гигабайтах (ГБ) | Страница сравнения моделей Mac на сайте Apple |

---

#### `chip_storage_options`
*Поддерживаемые объёмы накопителей в зависимости от аппаратной конфигурации*

| Имя атрибута | Тип данных | Описание и контекст предметной области | Источник |
| :--- | :--- | :--- | :--- |
| `storage_option_id` | `INTEGER` | **PK** Первичный ключ по конфигурации накопителей | — |
| `config_id` | `INTEGER` | **FK** Связывает параметр накопителей с конфигурацией в `chip_configs` | — |
| `storage_size_gb` | `INTEGER` | Поддерживаемый объём накопителей в гигабайтах (ГБ) | Страница сравнения моделей Mac на сайте Apple |

</details>

## Анализ

### Матрица корреляций

![Correlation Matrix](visualizations/1_correlation_matrix.png)

Полученная матрица показывает высокую корреляцию между количеством ядер центрального процессора, количеством ядер графического процессора, пропускной способностью памяти и максимальным количеством поддерживаемых дисплеев. Производительность нейронного вроцессора (TOPS) является заметным исключением, демонстрируя слабую связь с другими переменными.

Эта закономерность отражает масштабирование чипов Apple. С каждым уровнем, от серии A до процессоров серии M базового, Pro, Max и Ultra уровней, количество ядер центрального процессора, ядер графического процессора, пропускная способность памяти и поддержка дисплеев увеличиваются синхронно, но производительность нейронного вроцессора (TOPS) остаётся постоянной от серии A до уровня Max серии M, поскольку Apple оснащает все эти чипы нейронными процессорами (NPU) с одинаковым количеством ядер. Единственное исключение наблюдается на уровне Ultra, где производительность NPU удваивается. Однако это скорее структурное масштабирование, поскольку чипы Ultra создаются путём объединения двух чипов Max.

---

### Все конфигурационные профили процессоров по каждому полокению

![All Hardware Specifications](visualizations/2_1_specs_all.png)

Каждое поколение включает по 4 модели чипов, за исключением M5, на данный момент состоящего из трёх, так как оно является текущим (анонса чипа уровня Ultra не было, обновления MacBook Neo до чипа A19 Pro – тоже). Предыдущие поколения включали в себя по четыре типа чипа и 8 вариаций чипов, за исключением M1, где было 9 вариаций чипов из-за трёх вариаций M1 Pro.

Несмотря на наибольшее количество вариаций за ним, поколение M1 не произвёл наибольшее количество конфигурационных профилей, так как размах его опций объединённой (оперативной) памяти был узок, при том, что размах накопителей были относительно широк. Поколение M2, в противопоставление, произвело наибольшее количество конфигурационных профилей, так как привнесло больше вариантов объединённой памяти.

В линейке M4 наблюдается дальнейшее сокращение количества конфигурационных профилей: A18 Pro подразумевает только один вариант объединённой памяти и два варианта хранилища, а базовая версия M4 больше не включает 8 ГБ объединённой памяти, вместо этого она начинается с 16 ГБ. Хотя выпуск Mac поколения M5 ещё не завершён, уже очевидно, что в целом количество вариантов комплектации есть и будет меньше, поскольку вариант с 256 ГБ хранилища полностью исключён, что примножает эффект от отменённого ранее варианта с 8 ГБ оперативной памяти в поколении M4.

---

![Hardware Specifications for Base, Pro, Max](visualizations/2_2_specs_base_pro_max.png)

Если ограничить сравнение только базовыми, Pro и Max версиями, то можно выявить более устойчивую закономерность среди поколений. M2, M3 и M5 имеют по шесть конфигураций, что соответствует двум вариантам для каждой версии (базовая, Pro, Max). M1 и M4 выделяются как исключения, каждая из них имеет дополнительную конфигурацию: у M1 Pro и у базового M4 было по три варианта – выборка не очень большая, но закономерность желания Apple придерживаться 2 вариантов на каждую модель чипа намечается (одна полноценная версия, одна – урезанная/отбракованная).

Что интересно, именно причины, почему именно M1 Pro и M4 стали жертвами такого отбраковывания, не особо очевидно выделяются, поскольку M1 Pro доступен только в MacBook Pro 2021 года, а M4 – в более широком наборе устройств: MacBook Pro 14", MacBook Air, iPad Pro, iPad Air, iMac, Mac mini (к тому же, если учитывать версии M4 для iPad Pro и iPad Air, то мы получаем 5 вариаций чипов M4, но, к сожалению, это не входит в охват данного кейса).

Исходя из всего этого и временнóго контекста, я могу лишь предположить, что у M1 Pro было 3 варианта, поскольку это был следующий после M1 по временным рамкам и по сложности производства чип, и поэтому было отбраковано много чипов, а у M4 было много вариантов просто потому что он построен на более экономически эффективном техпроцессе, чем M3, и Apple решили произвести его в бóльшем объёме (также далее в одной из последующих схем будет отображено, что между выходом M4 и M5 был самый длинный промежуток на данный момент между поколениями), поэтому и бóльшее количество вариантов отбракованных чипов. Но это всё лишь спекуляции, которые я не могу абсолютно точно подтвердить без конкретных данных (на данный момент).

---

![Memory Specifications](visualizations/2_3_memory.png)

Поколение M1 показывает достаточно равномерное распределение, при этом каждый уровень чипов предлагает ровно два варианта памяти. С поколением M2 каждый уровень получает три варианта, за исключением M2 Pro. M3 следует той же схеме: M3 Pro снова предлагает два варианта, в то время как базовый M3 и M3 Ultra предлагают три, а M3 Max выделяется пятью различными конфигурациями памяти.

Ограниченность уровня Pro наконец-то уходит в поколениях M4 и M5, которые предлагают по три варианта памяти для Pro. В поколении M4 также появился процессор A18 Pro в линейке Mac, хотя он поддерживает только одну конфигурацию – 8 ГБ, что является ограничением самого чипа.

---

![Storage Specifications](visualizations/2_4_storage.png)

Варианты конфигураций объёма памяти были идентичны для поколений M1 и M2: базовые процессоры M1 и M2 поддерживали объем от 256 ГБ до 2 ТБ, в то время как версии Pro и Max поддерживали от 512 ГБ до 8 ТБ, а Ultra — от 1 ТБ до 8 ТБ.

В поколении M3 версия Pro и тут не получила широкой вариативности конфигураций, максимальная конфигурация стала ограничена значением в 4 ТБ, в то время как версия M3 Ultra расширяется до 16 ТБ; все остальные версии остались без изменений. В поколении M4 максимальный объём памяти M4 Pro возвращается к 8 ТБ, а A18 Pro поддерживает только 256 ГБ и 512 ГБ.

Поколение M5 знаменует собой явный сдвиг: базовая версия теперь начинается с 512 ГБ (вариант 256 ГБ полностью исключается в M-серии) и достигает максимума в 4 ТБ, в то время как версии Pro и Max полностью исключают вариант 512 ГБ, начиная с 1 ТБ. В результате, поколение M5 представляет собой наиболее ограниченное по разнообразию конфигураций накопителей в рамках базового, Pro и Max уровней, что может быть связано с текущим дефицитом устройств хранения данных.

___

### Хронология релизов поколений процессоров Apple Silicon

![Rollout Timeline](visualizations/3_rollout_timeline.png)

The M1 and M3 generations had the longest overall rollout durations, though for different reasons. M1's extended timeline reflects a genuinely staggered release: the base M1 launched in 2020, M1 Pro and Max followed in 2021, and M1 Ultra arrived in 2022. M3's rollout, while technically the longest, is largely an artifact of timing: M3 Ultra wasn't released until after the M4 cycle had already concluded, and even then it launched exclusively for the Mac Studio, unveiled alongside the M4 Max at the same time. This was because the M4 generation wasn't intended to include an Ultra variant, which likely explains why the M4 cycle was the shortest of all.

M4 was also the fastest successor generation, as the shortest interval between generation start dates occurred between M3 and M4, though this is largely attributable to the M4 debuting in the iPad Pro almost six months before reaching the Mac lineup. Conversely, the longest gap between consecutive generations occurred between M4 and M5.

While the M5 cycle is still ongoing and cannot be fully assessed, it already shows the shortest interval between the base chip release and the Pro/Max releases of any generation apart from M3, where the base, Pro, and Max variants were announced simultaneously at the same event.

---

### Производительность нейронных процессоров по поколениям

![NPU Performance Scaling](visualizations/4_npu_tops.png)

As noted in the correlation matrix description, NPU performance does not scale across chip tiers within a generation, with the sole exception of Ultra, whose 2x TOPS figure is simply a byproduct of its dual-die construction rather than genuine architectural scaling.

Across generations, however, the NPU has scaled substantially over time. From M1 to M3, performance grew from 11 to 18 TOPS, a gain of more than 1.6x, though this increase appears modest on the chart relative to the jumps that follow. M4 delivers more than double the NPU performance of M3, and M5 reaches roughly six times the performance of M1, bringing the base-tier progression from 11 TOPS to 60 TOPS across five generations.

Notably, the Ultra tier's advantage has narrowed considerably: M3 Ultra's performance is now roughly on par with the base M4 chip, and sits at only about half the NPU performance of the base M5 chip, despite Ultra's dual-NPU design.

---

### Масштабирование пропускной способности памяти в зависимости от уровня и поколения чипов

![Memory Bandwidth Scaling](visualizations/5_bandwidth.png)

Given the growing importance of local AI workloads on Mac hardware, along with other bandwidth-dependent tasks, memory bandwidth stands out as a particularly meaningful metric to examine.

From M1 through M3, the Max and Ultra tiers remained essentially flat, though this stagnation is less concerning given their already high absolute bandwidth. The base chip saw a modest improvement from M1 to M2 before plateauing at M3. Notably, the M3 Pro actually regressed, losing roughly 25% of the bandwidth held by its M1 Pro and M2 Pro predecessors, a dip worth remembering for what follows.

The M4 generation delivered upgrades across the board, substantial enough that Apple was able to introduce an A-series chip (A18 Pro) into the Mac lineup for the first time, its 60 GB/s bandwidth now approaching M1-level performance (68.25 GB/s). M4 Pro finally saw its first real bandwidth growth since the Pro tier's introduction, and M4 Max gained meaningful bandwidth as well.

By M5, the base chip has reached 153 GB/s bandwidth, effectively landing at Pro-tier bandwidth, though this is partly a function of the M3 Pro's earlier dip lowering that bar. M5 Pro is now climbing toward Max-tier territory, and M5 Max is closer than ever to Ultra-level bandwidth.

Taken together, this trajectory suggests an inevitable reshuffling of the tier hierarchy: the A-series appears poised to take over the entry-level role currently held by the base M chip, the base M chip is edging into what was traditionally Pro territory, and the Pro tier is closing in on Max, especially now that Apple has reverted M5 Pro and Max to sharing the same CPU core configuration (differentiated mainly by GPU cores), as was the case with M1 and M2. Max may eventually approach or even match Ultra-level performance, though whether Ultra maintains a decisive lead or simply becomes an even greater outlier will likely depend on how ongoing memory, storage, and semiconductor supply constraints play out, a question beyond the scope of this analysis.

---

## Выводы

This case study set out to demonstrate a complete data engineering and analytics workflow, from a normalized relational schema through to exploratory analysis, using Apple Silicon's Mac-bound chip lineup as the subject matter. Beyond validating that approach, the analysis surfaced several genuine trends in how Apple's chip strategy has evolved across five generations.

**The Pro tier spent its early years as something of a middle child, but has since come into its own.** Through M1 to M3, the Pro chip consistently trailed the growth seen at the Base and Max tiers across memory options, storage ceilings, and memory bandwidth, culminating in M3, where Apple actively pulled back Pro-tier memory bandwidth, CPU performance-core count, and GPU core count relative to its predecessors. Since M4, however, the Pro tier has broken from that pattern, finally seeing meaningful growth in memory bandwidth and configuration options, positioning it as a genuinely distinct step up rather than a compromise between Base and Max.

**Memory bandwidth points toward a broader hierarchy reshuffle.** The steep bandwidth gains introduced in M4 and continued into M5 have pushed the Base tier to roughly where Pro once sat, and Pro toward Max territory, while Max is closer to Ultra than at any prior point. Combined with Apple reverting M5 Pro and Max to a shared CPU core configuration (as in M1/M2), this suggests the tier boundaries are shifting upward as a whole.

**A-series chips are emerging as Apple's new entry point.** With the Mac lineup's traditional entry chip (Base M-series) effectively rising to Pro-level capability by M5, Apple has room to slot A-series silicon in beneath it. This reflects Apple's familiar economies-of-scale playbook: binned A18 Pro chips, already in volume production for iPhone, let Apple build an affordable Mac capable of handling everyday tasks that no longer require even the now-elevated base M-series chip. Early demand signals support this strategy — Tim Cook has noted that MacBook Neo orders exceeded Apple's own expectations, though sales performance itself falls outside the scope of this study.

Taken together, the data suggests Apple's silicon strategy is entering a new phase: rather than simply scaling existing tiers upward, the entire hierarchy appears to be shifting, with A-series chips absorbing the entry-level role, base chips inheriting Pro-like capability, and a newly strengthened Pro tier closing in on Max. Whether Max eventually challenges Ultra, or Ultra pulls further ahead, will likely hinge on how memory, storage, and broader semiconductor supply constraints unfold in the generations to come.
