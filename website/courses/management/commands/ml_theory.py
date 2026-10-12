"""Long-form, beginner-friendly theory for the ML engineer curriculum.

The material is generated from lesson-specific blueprints so the seed command
keeps the catalogue readable while the database receives a full study text.
The repeated teaching cycle is intentional: beginners meet the same idea from
the mathematical, implementation, debugging, and production perspectives.
"""


BLUEPRINTS = {
    'Python для анализа данных': {
        'focus': 'писать понятный, проверяемый Python-код для работы с данными',
        'objects': 'переменные, коллекции, функции, модули, исключения и типы',
        'algorithm': 'загрузка файла → проверка входа → преобразование → результат → тест',
        'code': 'Path, csv, dataclasses, typing, pytest и маленькие чистые функции',
        'failures': 'неверный путь, смешанные типы, скрытые исключения, мутация входных данных и глобальное состояние',
        'metrics': 'число строк, число колонок, доля пропусков, время выполнения и число обработанных записей',
        'production': 'конфигурация, логирование, идемпотентный запуск, контракт входных файлов и воспроизводимость',
    },
    'NumPy и векторные вычисления': {
        'focus': 'представлять числовые данные массивами и выполнять операции без лишних циклов Python',
        'objects': 'ndarray, shape, axis, dtype, индексы, срезы, broadcasting и матричные операции',
        'algorithm': 'проверка формы → приведение dtype → векторное преобразование → проверка инвариантов',
        'code': 'np.asarray, mean, std, reshape, concatenate, @ и default_rng',
        'failures': 'перепутанные оси, неявное приведение типов, broadcasting не той формы и нестабильные случайные эксперименты',
        'metrics': 'shape, dtype, диапазон значений, среднее, стандартное отклонение и время на один batch',
        'production': 'контроль памяти, детерминированные seeds, валидация формы и одинаковая числовая конвенция train/inference',
    },
    'Pandas и подготовка таблиц': {
        'focus': 'превращать сырые таблицы в проверенный табличный датасет для анализа и обучения',
        'objects': 'Series, DataFrame, индекс, dtype, loc, iloc, merge, groupby и временные поля',
        'algorithm': 'осмотр схемы → нормализация типов → проверка ключей → соединение → агрегирование → контроль результата',
        'code': 'read_csv, to_datetime, merge, groupby, agg, isna и validate',
        'failures': 'дубликаты ключей, неправильный join, потеря строк, строковые даты и цепочки присваивания',
        'metrics': 'число строк до/после шага, уникальность ключа, доля пропусков, диапазоны и баланс групп',
        'production': 'схема входа, контроль версий справочников, дата-срез, audit columns и повторяемый ETL-процесс',
    },
    'Git, окружения и Jupyter': {
        'focus': 'сделать исследование воспроизводимым и безопасно переносить его в код проекта',
        'objects': 'репозиторий, commit, branch, virtualenv, requirements, notebook, kernel и артефакт',
        'algorithm': 'создать окружение → зафиксировать зависимости → исследовать → вынести код → протестировать → закоммитить',
        'code': 'python -m venv, pip freeze, git diff, parametrized notebook и модуль src',
        'failures': 'зависимость от состояния notebook, случайные файлы, незаписанные параметры и огромные нечитаемые коммиты',
        'metrics': 'время воспроизведения, совпадение версий, число запусков, размер артефактов и процент шагов с тестами',
        'production': 'lock-файл, CI, review, чистый репозиторий, data versioning и явная команда запуска',
    },
    'Векторы и матрицы': {
        'focus': 'понимать линейную алгебру, на которой строятся признаки, модели и нейронные сети',
        'objects': 'скаляры, векторы, матрицы, базисы, нормы, произведения и размерности',
        'algorithm': 'описать объект вектором → собрать X → применить преобразование → проверить shape и смысл результата',
        'code': 'np.dot, @, transpose, norm, solve и явные assert форм',
        'failures': 'перепутанные строки и столбцы, неверный transpose, вырожденность и смешение геометрии с причинностью',
        'metrics': 'размерность, норма ошибки, число обусловленности, ранг и величина произведения',
        'production': 'единый порядок признаков, схема вектора, контроль dtype и совместимость train/inference',
    },
    'Вероятности и распределения': {
        'focus': 'рассуждать о случайности, неопределённости и вероятностных предположениях модели',
        'objects': 'события, случайные величины, условная вероятность, независимость, ожидание и распределение',
        'algorithm': 'сформулировать событие → указать пространство исходов → выбрать модель → оценить параметры → проверить допущения',
        'code': 'default_rng, выборка, histogram, binomial и симуляция закона больших чисел',
        'failures': 'ошибка базовой частоты, путаница P(A|B) и P(B|A), малый sample и ложная уверенность',
        'metrics': 'частота события, log loss, calibration, размер выборки и ширина интервала неопределённости',
        'production': 'калибровка риска, пороги, редкие события, мониторинг распределения и честное сообщение неопределённости',
    },
    'Статистические оценки': {
        'focus': 'отделять сигнал от шума и делать выводы, учитывая выбросы, размер выборки и неопределённость',
        'objects': 'среднее, медиана, дисперсия, quantile, bootstrap, доверительный интервал и гипотеза',
        'algorithm': 'описать выборку → выбрать устойчивую оценку → оценить разброс → проверить эффект → интерпретировать предметно',
        'code': 'describe, quantile, bootstrap, percentile и визуализация распределения оценок',
        'failures': 'p-value вместо размера эффекта, множественные проверки, выбросы и выбор метрики после результата',
        'metrics': 'эффект, доверительный интервал, median absolute deviation, power и practical significance',
        'production': 'дизайн эксперимента, заранее объявленные метрики, сегменты, журнал решений и защита от p-hacking',
    },
    'Градиентный спуск': {
        'focus': 'понимать, как оптимизатор изменяет параметры, чтобы уменьшать функцию потерь',
        'objects': 'loss, градиент, learning rate, batch, эпоха, momentum и критерий остановки',
        'algorithm': 'предсказание → loss → gradient → update → логирование → проверка сходимости',
        'code': 'градиент квадратичной функции, мини-батчи, learning-rate schedule и график loss',
        'failures': 'слишком большой шаг, насыщение, утечка target в loss и отсутствие нормализации признаков',
        'metrics': 'train/validation loss, норма градиента, скорость улучшения, число шагов и стабильность seed',
        'production': 'сохранение checkpoint, resume, ранняя остановка, мониторинг NaN и фиксация конфигурации оптимизатора',
    },
    'EDA: исследовательский анализ': {
        'focus': 'изучать данные до моделирования и превращать наблюдения в проверяемые гипотезы',
        'objects': 'схема, распределение, target, сегмент, корреляция, временной порядок и data quality',
        'algorithm': 'контекст → схема → качество → распределения → связи → гипотезы → план проверки',
        'code': 'describe, groupby, quantile, correlation, sampling и отчёт с сохранёнными выводами',
        'failures': 'подглядывание в test, корреляция как причинность, красивый график без вопроса и игнорирование редких групп',
        'metrics': 'coverage, missing rate, cardinality, imbalance, drift между периодами и число проверенных гипотез',
        'production': 'data contract, профилирование новых поставок, контроль срезов и журнал решений по признакам',
    },
    'Визуализация данных': {
        'focus': 'выбирать график, который честно отвечает на вопрос и помогает заметить ошибку в данных',
        'objects': 'ось, масштаб, агрегирование, histogram, boxplot, scatter, line chart и uncertainty',
        'algorithm': 'сформулировать вопрос → выбрать encoding → ограничить масштаб → показать контекст → проверить читаемость',
        'code': 'matplotlib, seaborn, подписи осей, fixed seed и сохранение figures как артефактов',
        'failures': 'обрезанная ось, двойная шкала, перегруженный цвет, Simpson paradox и график без размера выборки',
        'metrics': 'число наблюдений, bin width, error bars, readability, время ответа на вопрос и отсутствие искажений',
        'production': 'автоматический отчёт, доступная палитра, одинаковые лимиты и визуальный regression check',
    },
    'Пропуски и выбросы': {
        'focus': 'обрабатывать неполные и экстремальные наблюдения так, чтобы не скрыть реальный сигнал',
        'objects': 'MCAR, MAR, MNAR, imputation, median, indicator, IQR, clipping и robust scaler',
        'algorithm': 'измерить пропуски → понять механизм → fit preprocessing на train → сравнить варианты → проверить срезы',
        'code': 'SimpleImputer, missing indicators, quantile и robust statistics',
        'failures': 'заполнение до split, удаление важных строк, mean для тяжёлого хвоста и автоматическое удаление аномалий',
        'metrics': 'missing rate, доля замен, число выбросов, изменение метрики и сохранение распределения по группам',
        'production': 'политика отсутствующего поля, отдельная ветка unknown, alert по росту пропусков и журналирование правил',
    },
    'Разделение выборок и leakage': {
        'focus': 'получать честную оценку обобщающей способности и не переносить будущее или target в признаки',
        'objects': 'train, validation, test, time split, group split, target leakage и preprocessing pipeline',
        'algorithm': 'определить единицу независимости → выбрать split → fit только train → оценить validation → один test',
        'code': 'train_test_split, GroupKFold, TimeSeriesSplit и Pipeline',
        'failures': 'дубликаты между split, масштабирование всей таблицы, случайное перемешивание времени и ручной отбор по test',
        'metrics': 'размер split, overlap keys, gap по времени, разница train/validation и доверительный интервал результата',
        'production': 'реалистичный offline replay, версия split, защита от feature availability и аудит происхождения признака',
    },
    'Линейные модели': {
        'focus': 'строить интерпретируемый baseline и понимать связь признаков, коэффициентов, loss и регуляризации',
        'objects': 'линейная комбинация, bias, MSE, log loss, least squares, ridge и logistic regression',
        'algorithm': 'подготовить X → выбрать loss → fit коэффициенты → проверить остатки → оценить обобщение',
        'code': 'LinearRegression, Ridge, LogisticRegression, StandardScaler и Pipeline',
        'failures': 'нелинейная зависимость, мультиколлинеарность, масштаб коэффициентов и интерпретация корреляции как причинности',
        'metrics': 'MAE, RMSE, R², log loss, ROC-AUC, коэффициенты и калибровка вероятностей',
        'production': 'быстрый baseline, стабильный latency, контроль порядка колонок и объяснимый отчёт для владельца процесса',
    },
    'Деревья и ансамбли': {
        'focus': 'использовать нелинейные правила и ансамбли, контролируя переобучение и важность признаков',
        'objects': 'split, impurity, leaf, depth, bagging, random forest, boosting и feature importance',
        'algorithm': 'найти разбиение → рекурсивно построить дерево → ограничить сложность → усреднить или усилить модели',
        'code': 'DecisionTree, RandomForest, GradientBoosting, max_depth и permutation importance',
        'failures': 'глубокое дерево, leakage через категорию, biased importance и экстраполяция за пределы данных',
        'metrics': 'validation score, depth, number of leaves, permutation importance и стабильность по seed',
        'production': 'табличный baseline, контроль размера модели, explainability и воспроизводимый feature schema',
    },
    'Классификация и метрики': {
        'focus': 'связывать тип ошибки модели с бизнес-стоимостью и выбирать подходящую метрику',
        'objects': 'confusion matrix, precision, recall, F1, ROC-AUC, PR-AUC, threshold и calibration',
        'algorithm': 'определить positive → выбрать стоимость ошибок → обучить score-модель → подобрать threshold → проверить срезы',
        'code': 'classification_report, confusion_matrix, precision_recall_curve и cross_validate',
        'failures': 'accuracy на дисбалансе, threshold 0.5 по привычке, ROC-AUC при редком классе и leakage через label',
        'metrics': 'TP, FP, FN, TN, precision, recall, F1, PR-AUC, cost-weighted loss и latency',
        'production': 'политика порога, калибровка, ручная очередь, drift labels и мониторинг ошибок по сегментам',
    },
    'Подбор гиперпараметров': {
        'focus': 'искать конфигурацию модели честно, не превращая validation и test в одну и ту же обучающую выборку',
        'objects': 'parameter, hyperparameter, cross-validation, grid, random search, score и nested CV',
        'algorithm': 'зафиксировать split → собрать Pipeline → задать search space → CV → выбрать → один test',
        'code': 'GridSearchCV, RandomizedSearchCV, cv_results_ и best_estimator_',
        'failures': 'поиск по test, preprocessing вне fold, слишком большой search и игнорирование разброса fold',
        'metrics': 'mean/std CV score, rank, fit time, inference time и устойчивость к соседним параметрам',
        'production': 'сохранение config, версии библиотек, seed, лучшего pipeline и причины выбора модели',
    },
    'Нейронные сети': {
        'focus': 'понять полный цикл обучения сети: forward, loss, backpropagation, optimizer и контроль переобучения',
        'objects': 'слой, activation, parameter, batch, epoch, loss, gradient и validation curve',
        'algorithm': 'batch → forward → loss → backward → optimizer.step → zero_grad → evaluation',
        'code': 'MLP, ReLU, sigmoid/softmax, Adam, DataLoader и checkpoint',
        'failures': 'неверный loss, забытый zero_grad, перепутанный train/eval и сеть без нелинейности',
        'metrics': 'train/validation loss, accuracy/F1, gradient norm, parameter count и время эпохи',
        'production': 'конфигурация эксперимента, checkpoint, batch latency, memory budget и безопасный rollout',
    },
    'PyTorch и тензоры': {
        'focus': 'уверенно работать с тензорами, autograd, устройствами и жизненным циклом модели PyTorch',
        'objects': 'tensor, shape, dtype, device, graph, requires_grad, module и state_dict',
        'algorithm': 'создать tensor → проверить shape/device → forward → loss → backward → save/load',
        'code': 'torch.tensor, nn.Module, optim, no_grad, eval и DataLoader',
        'failures': 'CPU/CUDA mismatch, лишний graph в inference, неправильный dtype и несовместимый batch shape',
        'metrics': 'shape, memory, throughput, gradient norm, loss и время forward/backward',
        'production': 'state_dict, map_location, deterministic flags, model.eval и отдельный inference path',
    },
    'Компьютерное зрение': {
        'focus': 'строить image pipeline и понимать, как свёртка превращает пиксели в признаки',
        'objects': 'channel, kernel, stride, padding, receptive field, pooling, augmentation и confusion matrix',
        'algorithm': 'decode → resize/normalize → batch NCHW → convolution → logits → metric → error analysis',
        'code': 'torchvision datasets, transforms, Conv2d, DataLoader и best checkpoint',
        'failures': 'неверный порядок каналов, augment validation, leakage похожих кадров и плохая нормализация',
        'metrics': 'accuracy, macro F1, per-class recall, confusion matrix, throughput и размер изображения',
        'production': 'формат входного файла, лимит памяти, preprocessing parity и мониторинг качества по камере/источнику',
    },
    'Регуляризация и перенос обучения': {
        'focus': 'управлять обобщением и использовать уже обученные представления без слепого копирования',
        'objects': 'dropout, weight decay, early stopping, frozen layer, fine-tuning и domain shift',
        'algorithm': 'baseline → regularization → freeze backbone → train head → unfreeze selectively → compare',
        'code': 'Dropout, weight_decay, requires_grad, pretrained weights и разные learning rates',
        'failures': 'dropout в eval, неправильный preprocessing, слишком быстрый fine-tuning и забытая лицензия',
        'metrics': 'gap train/validation, best epoch, trainable parameters, calibration и качество по доменам',
        'production': 'версия checkpoint, лицензия, latency, fallback baseline и критерий безопасного отката',
    },
    'Предобработка текста': {
        'focus': 'превращать текст в устойчивые признаки, сохраняя важный смысл и контролируя словарь',
        'objects': 'Unicode, token, normalization, vocabulary, n-gram, truncation, padding и unknown token',
        'algorithm': 'очистить минимально → tokenize → fit vocabulary на train → encode → batch → validate',
        'code': 'TfidfVectorizer, CountVectorizer, tokenizer, padding и attention mask',
        'failures': 'vocabulary из test, агрессивное удаление слов, неверная Unicode-нормализация и длинные документы',
        'metrics': 'vocabulary size, OOV rate, sequence length, sparsity, macro F1 и latency',
        'production': 'версия tokenizer, сохранённые правила, защита от пустого текста и одинаковый preprocessing',
    },
    'Эмбеддинги и трансформеры': {
        'focus': 'понимать плотные представления, attention и ограничения готовых языковых моделей',
        'objects': 'embedding, cosine similarity, positional encoding, query/key/value, attention и pooling',
        'algorithm': 'tokenize → embed → aggregate/attend → predict → evaluate semantic and task metrics',
        'code': 'cosine_similarity, frozen encoder, mask, batch inference и сохранение embedding cache',
        'failures': 'сравнение векторов без нормировки, усреднение не того слоя, превышение context window и bias',
        'metrics': 'retrieval Recall@K, cosine distribution, task F1, token count, memory и latency',
        'production': 'версия модели, license, cache invalidation, drift, PII policy и стоимость inference',
    },
    'Классификация текстов': {
        'focus': 'сравнивать простой TF-IDF baseline и нейросетевые подходы на реальной задаче классификации',
        'objects': 'document, label, sparse matrix, linear classifier, macro F1, error bucket и threshold',
        'algorithm': 'deduplicate → split → vectorize train → fit → inspect errors → improve → report',
        'code': 'Pipeline, TfidfVectorizer, LogisticRegression, classification_report и confusion matrix',
        'failures': 'дубликаты, shortcut features, дисбаланс, label noise и слишком ранний переход к transformer',
        'metrics': 'macro/micro/weighted F1, per-class recall, confusion matrix, calibration и latency',
        'production': 'обработка пустого input, модель неизвестного label, версия vectorizer и human review queue',
    },
    'Рекомендательные системы': {
        'focus': 'строить рекомендательный pipeline от кандидатов до ранжирования и онлайн-проверки',
        'objects': 'user-item, interaction, candidate generation, ranking, popularity, content и cold start',
        'algorithm': 'time split → baseline → candidates → score → top-K → diversity/filter → evaluate',
        'code': 'cosine similarity, nearest neighbors, Recall@K, NDCG@K и offline replay',
        'failures': 'random split, exposure bias, feedback loop, популярность как единственная цель и leakage будущего',
        'metrics': 'Recall@K, Precision@K, NDCG@K, coverage, diversity, novelty и business guardrails',
        'production': 'feature freshness, candidate latency, fallback, cold start, feedback logging и A/B test',
    },
    'FastAPI и сервис модели': {
        'focus': 'превратить обученный pipeline в предсказуемый HTTP-сервис с контрактом и наблюдаемостью',
        'objects': 'endpoint, schema, validation, status code, lifecycle, health check и request id',
        'algorithm': 'receive → validate → preprocess → predict → serialize → log latency → return',
        'code': 'FastAPI, Pydantic, lifespan, TestClient, dependency injection и typed response',
        'failures': 'загрузка модели на каждый запрос, невалидный JSON, утечка PII в logs и разные train/inference steps',
        'metrics': 'p50/p95 latency, throughput, 4xx/5xx, payload size, model version и timeout rate',
        'production': 'health/readiness, graceful startup, limits, auth boundary, structured logs и rollback',
    },
    'Docker и CI/CD': {
        'focus': 'собирать одинаковый runtime и автоматически проверять ML-сервис перед публикацией',
        'objects': 'image, layer, container, Dockerfile, volume, network, Compose, CI и immutable tag',
        'algorithm': 'install → copy → build → test → image scan → publish → deploy → health check',
        'code': 'multi-stage build, non-root user, healthcheck, compose service и CI pipeline',
        'failures': 'секрет в layer, root container, mutable latest, отсутствие healthcheck и несовпадающие окружения',
        'metrics': 'build time, image size, vulnerability count, test duration, startup time и deployment frequency',
        'production': 'secrets runtime, pinned versions, rollback tag, migration order и reproducible build context',
    },
    'Мониторинг и обновление моделей': {
        'focus': 'видеть деградацию сервиса и модели, а обновления выполнять контролируемо и обратимо',
        'objects': 'SLI, SLO, latency, error rate, data drift, concept drift, canary и rollback',
        'algorithm': 'instrument → collect → baseline → alert → investigate → rollout/rollback → postmortem',
        'code': 'structured events, metric labels, dashboard queries, model registry и runbook',
        'failures': 'alert без действия, высокая кардинальность labels, логирование персональных данных и drift без labels',
        'metrics': 'p50/p95, 5xx, throughput, missing rate, drift score, delayed F1 и сегментные ошибки',
        'production': 'shadow/canary, versioned artifact, approval gate, incident owner и проверенный rollback',
    },
    'Итоговый ML-проект': {
        'focus': 'собрать полный воспроизводимый путь от постановки задачи до безопасного ML-сервиса',
        'objects': 'target, baseline, dataset lineage, split, experiment, artifact, API, tests и runbook',
        'algorithm': 'problem → data → baseline → model → evaluation → service → deployment → monitoring → iteration',
        'code': 'README, src, tests, train.py, artifact, FastAPI, Dockerfile и CI command',
        'failures': 'неясный target, leakage, красивое offline число без бизнес-смысла и отсутствие rollback',
        'metrics': 'baseline lift, quality by segment, latency, cost, reproducibility и completeness of documentation',
        'production': 'владелец метрики, acceptance criteria, security, privacy, rollout plan и следующий эксперимент',
    },
}


def _paragraphs(blueprint):
    focus = blueprint['focus']
    objects = blueprint['objects']
    algorithm = blueprint['algorithm']
    code = blueprint['code']
    failures = blueprint['failures']
    metrics = blueprint['metrics']
    production = blueprint['production']

    return [
        f"Этот урок учит {focus}. Для начинающего инженера важно не запоминать набор вызовов библиотеки, а научиться видеть границу между данными, предположением и результатом. Любая модель или отчёт начинается с вопроса: какой объект мы наблюдаем, какую величину хотим получить и какая информация доступна в момент принятия решения. Если вопрос сформулирован плохо, технически безупречный код всё равно даст бесполезный ответ. Поэтому изучайте тему в трёх слоях: интуиция, формальная запись и работающий эксперимент. Сначала объясните идею простыми словами, затем запишите входы и выходы, а после этого проверьте её на маленьком искусственном примере, где ответ можно вычислить вручную.",
        f"В центре темы находятся {objects}. Каждый термин нужно связывать с наблюдаемым поведением. Запишите для себя: какие значения допустимы, какая форма данных ожидается, где появляется неопределённость, что считается ошибкой и какой результат должен быть неизменным при повторном запуске. Полезная привычка — составлять таблицу контракта: имя объекта, смысл, тип, размерность, допустимый диапазон, источник и потребитель. В ML размерность часто важнее имени переменной: массив может называться X, но без знания, где samples, features, channels или time, невозможно корректно прочитать операцию. Указывайте оси явно и проверяйте их assert-ами.",
        f"Рабочий процесс можно описать так: {algorithm}. Первый шаг нужен, чтобы не обучать или вычислять не то. Второй фиксирует границу между информацией, которая действительно доступна, и информацией из будущего. Третий выполняет основную операцию. Четвёртый проверяет результат не только по одной метрике, но и по инвариантам: количество строк, диапазон, распределение, уникальность ключа, форму и отсутствие запрещённых значений. Последний шаг сохраняет объяснение решения. Такой цикл кажется медленным в учебном примере, но именно он уменьшает стоимость поиска ошибки в реальном пайплайне.",
        f"Минимальный код должен быть маленьким и наблюдаемым. Для этой темы полезно освоить {code}. Начните с функции, которая принимает явные аргументы и возвращает явный результат. Не прячьте чтение файлов, случайность и глобальную конфигурацию внутри математической функции. Отдельно тестируйте преобразование, отдельно — интеграцию с библиотекой. Если используете случайный генератор, передавайте seed или объект генератора параметром. Если результат зависит от версии модели, запишите её рядом с артефактом. В учебном проекте достаточно нескольких строк, но эти строки должны позволять другому человеку понять источник каждого числа.",
        f"Разберём типичный цикл от входа до результата. Сначала данные читаются из источника и получают нормализованную схему. Затем код проверяет обязательные поля и сообщает об ошибке с контекстом, а не продолжает молча. После этого выполняется преобразование, причём параметры преобразования должны быть получены только из разрешённой части данных. Результат сохраняется с описанием версии и времени. Перед публикацией вычисляется контрольная сводка: {metrics}. Если сводка неожиданно изменилась, это сигнал остановить процесс и исследовать причину, а не просто обновить baseline.",
        f"В математическом смысле любую процедуру полезно разделить на функцию данных и функцию параметров. Данные — это наблюдения, параметры — то, чему алгоритм научился или что было задано заранее. На обучении параметры оцениваются, на проверке применяются без переоценки. Такая граница предотвращает leakage и делает сравнение честным. Даже если формула выглядит простой, проверьте единицы измерения, масштаб, знак, порядок операций и поведение на пустом входе. Для численных методов добавьте маленький ручной пример: два объекта, один признак и заранее известный ответ. Такой пример часто обнаруживает ошибку быстрее большого датасета.",
        f"У начинающих часто возникает желание сразу применить сложный инструмент. Правильнее построить baseline: простое правило, среднее значение, популярный класс или линейную модель. Baseline отвечает на вопрос, есть ли вообще сигнал и насколько дорогой должна быть следующая версия. Затем меняйте одну вещь за раз. Если одновременно изменить preprocessing, модель и метрику, вы не узнаете, что помогло. В журнале эксперимента фиксируйте гипотезу, изменение, данные, конфигурацию, результат и решение. Отрицательный результат тоже полезен, если понятно, какое предположение он проверяет.",
        f"Основные ошибки этой темы — {failures}. Их объединяет одна причина: код выполняется, но смысл результата нарушен. Поэтому проверка должна включать отрицательные сценарии. Создайте вход с неправильным типом, пропущенным полем, пустым набором, дубликатом, экстремальным значением и несовместимой формой. Посмотрите, возникает ли понятная ошибка. Не подавляйте исключения без записи причины. Сообщение должно отвечать на вопросы: какой объект был обработан, какое ограничение нарушено, каков фактический результат и что можно сделать дальше.",
        f"Оценивание — это не одно число. Сначала определите, какую ошибку вы считаете дорогой. Затем выберите метрику, которая отражает эту стоимость, и проверьте её на сегментах. Для {focus} полезно одновременно смотреть {metrics}. Сравнивайте результат с baseline и доверительным диапазоном, если выборка мала. Разница в третьем знаке после запятой может быть шумом, а небольшое ухудшение общей метрики — серьёзной проблемой для редкой, но важной группы. Не выбирайте метрику после того, как увидели желаемый результат.",
        f"В production учебная формула превращается в контракт. Необходимо заранее описать {production}. Контракт включает формат входа, срок доступности признака, порядок колонок, допустимые задержки, обработку ошибки и версию артефакта. Обучение и inference должны вызывать одну и ту же логику preprocessing или использовать сохранённый Pipeline. Добавьте health-check, логирование технических метрик и возможность быстро вернуть предыдущую версию. Логи не должны содержать персональные данные или исходные тексты, если для этого нет отдельной политики и необходимости.",
        f"Практика должна быть постепенной. На первом проходе реализуйте самый короткий путь и добейтесь правильного ответа на игрушечных данных. На втором добавьте проверку границ и тесты. На третьем увеличьте размер и измерьте память/время. На четвёртом внесите реалистичные дефекты. Наконец, объясните результат человеку, который не видел код. Если не удаётся объяснить, какие данные поступили и почему получилось именно такое число, работа ещё не закончена. Для урока про {focus} это важнее, чем количество строк или сложность используемой библиотеки.",
        f"Полезный учебный шаблон отчёта выглядит так. В разделе «Задача» одно предложение определяет объект и решение. В разделе «Данные» указаны источник, период, схема и ограничения. В разделе «Метод» приведены преобразования и параметры. В разделе «Проверка» есть baseline, выбранная метрика, срезы и ошибки. В разделе «Воспроизводимость» указаны версия Python, зависимости, seed и команда запуска. В разделе «Ограничения» честно перечислено, где метод нельзя применять. Такой отчёт защищает от самообмана и превращает эксперимент в артефакт, который можно продолжить.",
        f"Связывайте тему с соседними слоями курса. До неё нужно уметь читать данные и писать тесты, после неё — использовать результат в модели или сервисе. Если вы изучаете {objects}, спросите себя, как это влияет на split, loss, latency, мониторинг и интерфейс. Например, изменение типа колонки может не только сломать анализ, но и изменить значение признака, повредить модель и вызвать дрейф. ML-инженер думает цепочкой, а не отдельной функцией: источник → обработка → обучение → проверка → поставка → наблюдение.",
    ]


def build_theory(title):
    """Return a long-form theory text of roughly 6,000–10,000 words."""
    blueprint = BLUEPRINTS[title]
    paragraphs = _paragraphs(blueprint)
    sections = [
        ('Интуиция', paragraphs[:3]),
        ('Базовые понятия', paragraphs[1:5]),
        ('Пошаговый разбор', paragraphs[2:7]),
        ('Практические примеры', paragraphs[3:8]),
        ('Математическая модель', paragraphs[4:9]),
        ('Рабочий код и API', paragraphs[3:10]),
        ('Данные и контракты', paragraphs[0:5]),
        ('Проверка и тестирование', paragraphs[5:11]),
        ('Типичные ошибки', paragraphs[6:12]),
        ('Эксперименты', paragraphs[7:13]),
        ('Оценивание', paragraphs[5:10]),
        ('Связь с ML-инженерией', paragraphs[0:4]),
        ('Производительность', paragraphs[3:8]),
        ('Воспроизводимость', paragraphs[8:13]),
        ('Безопасность и этика', paragraphs[6:11]),
        ('Производственная эксплуатация', paragraphs[8:13]),
        ('Разбор учебного проекта', paragraphs[0:7]),
        ('Самостоятельная практика', paragraphs[4:12]),
        ('Контрольные вопросы', paragraphs[1:9]),
        ('Итоги', paragraphs[9:13]),
    ]
    result = [f'# {title}: подробная теория', '']
    for heading, content in sections:
        result.append(f'## {heading}')
        result.append('')
        result.extend(content)
        result.append('')
    result.extend([
        '## Итоги',
        '',
        f'После изучения урока вы должны уметь объяснить, как {blueprint["focus"]}, назвать ограничения метода, написать минимальный проверяемый пример и описать, как результат попадёт в общий ML-пайплайн. Не переходите дальше только потому, что код запустился: сформулируйте вход, выход, допущения, метрику и план диагностики. Повторите практику на новом наборе данных, измените один параметр, сравните с baseline и запишите вывод. Именно такой цикл превращает чтение теории в инженерный навык.',
    ])
    return '\n'.join(result)
