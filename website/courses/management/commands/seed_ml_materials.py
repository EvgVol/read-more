from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial
from courses.management.commands.ml_theory import build_theory


def entry(title, objectives, theory, practice, self_check, resources):
    return {
        'title': title,
        'objectives': objectives,
        'theory': theory,
        'practice': practice,
        'self_check': self_check,
        'resources': resources,
    }


MATERIALS = (
    entry('Python для анализа данных',
          'Организовать Python-проект; выбирать структуры данных; писать функции; обрабатывать ошибки.',
          'ML-код начинается с воспроизводимого скрипта. Списки хранят порядок, словари дают доступ по ключу, множества — уникальность. Разделяйте чтение данных, преобразования и обучение по функциям. Проверяйте входные данные явно и не скрывайте дефекты через `except Exception: pass`.',
          'Создайте `src/data_summary.py`: путь к CSV приходит аргументом, функция возвращает число строк, колонки и долю пропусков. Добавьте `FileNotFoundError`, типы и тест пустого файла.',
          'Почему словарь лучше списка пар для доступа по ключу? Чем `raise` отличается от `return None`? Какие части функции тестируются? Почему путь не должен быть глобальной константой?',
          '[Python Tutorial](https://docs.python.org/3/tutorial/)\n[Errors and exceptions](https://docs.python.org/3/tutorial/errors.html)'),
    entry('NumPy и векторные вычисления',
          'Создавать `ndarray`; читать `shape`, `ndim`, `dtype`; применять broadcasting; фиксировать генератор случайных чисел.',
          '`ndarray` хранит однородные значения и описывается формой, осями и dtype. `*` — поэлементное умножение, `@` — матричное. Broadcasting выравнивает совместимые формы, но требует проверки shape. Для повторяемых экспериментов используйте `np.random.default_rng(seed)`.',
          'Реализуйте стандартизацию `X` без циклов: среднее и std по `axis=0`, защититесь от константных колонок. Проверьте формы, среднее столбцов и сравните скорость с двойным циклом на матрице 2000x50.',
          'Что означает форма `(n_samples, n_features)`? Чем `*` отличается от `@`? Когда broadcasting ломается? Зачем фиксировать seed?',
          '[NumPy quickstart](https://numpy.org/doc/stable/user/quickstart.html)\n[Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)'),
    entry('Pandas и подготовка таблиц',
          'Загружать DataFrame; выбирать строки; объединять таблицы; группировать и считать агрегаты.',
          '`DataFrame` имеет индекс и типы колонок. Перед анализом проверяйте `shape`, `dtypes`, диапазоны и уникальность ключей. `loc` выбирает по меткам, `iloc` — по позициям. `merge` требует явных ключей и типа join; цепочку преобразований делайте читаемой.',
          'Загрузите таблицы заказов и пользователей, приведите даты к datetime, объедините по `user_id`, посчитайте выручку по стране и найдите пользователей без заказов. Проверьте, что left join не уменьшил число пользователей.',
          'Разница `loc`/`iloc`? Когда нужен left join? Почему тип даты важен? Как обнаружить дубли ключей до merge?',
          '[Pandas tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/)\n[Merge and join](https://pandas.pydata.org/docs/user_guide/merging.html)') ,
    entry('Git, окружения и Jupyter',
          'Создавать virtualenv; фиксировать зависимости; отделять notebook от production-кода; делать атомарные коммиты.',
          'Виртуальное окружение отделяет зависимости проекта от системного Python. Ноутбук удобен для исследования, но его состояние может быть скрытым. Устойчивые преобразования переносите в `.py`, очищайте выводы и сохраняйте параметры эксперимента. Коммит должен описывать одну логическую операцию.',
          'Создайте `.venv`, установите NumPy/Pandas, зафиксируйте зависимости и напишите README. Исследуйте данные в notebook, затем вынесите подготовку в `src/features.py` и вызовите её из теста.',
          'Чем окружение отличается от контейнера? Почему notebook невоспроизводим? Что нужно README? Каким должен быть хороший коммит?',
          '[venv](https://docs.python.org/3/library/venv.html)\n[Jupyter documentation](https://docs.jupyter.org/en/latest/)\n[Git documentation](https://git-scm.com/doc)'),
    entry('Векторы и матрицы',
          'Представлять признаки векторами; проверять размерности; объяснять скалярное произведение и линейную зависимость.',
          'Вектор признаков описывает объект, матрица `X` — набор объектов. Линейная модель вычисляет `Xw+b`, поэтому формы должны согласовываться. Нормы измеряют величину, скалярное произведение — согласованность направления. Линейная зависимость признаков делает решение плохо обусловленным.',
          'Реализуйте `X @ w + b` для трёх объектов и двух признаков, вычислите MSE вручную и добавьте понятную ошибку несовместимых shape.',
          'Форма X для 100 объектов и 5 признаков? Когда матричное умножение невозможно? Зачем bias? Чем корреляция отличается от причинности?',
          '[NumPy linear algebra](https://numpy.org/doc/stable/reference/routines.linalg.html)\n[Linear models](https://scikit-learn.org/stable/modules/linear_model.html)'),
    entry('Вероятности и распределения',
          'Различать событие и выборку; интерпретировать условную вероятность; выбирать распределение; учитывать неопределённость малой выборки.',
          'Распределение описывает неопределённость случайной величины. Условная вероятность `P(A|B)` зависит от контекста, независимость означает `P(A∩B)=P(A)P(B)`. Частота на маленькой выборке шумная, поэтому указывайте размер выборки и интервал неопределённости.',
          'Смоделируйте 10 000 бросков монеты с p=0.7, стройте частоту после каждого блока 100 и сравните с истинным параметром. Используйте `default_rng(42)` и опишите закон больших чисел.',
          'Что означает P(A|B)? Почему частота на 10 наблюдениях ненадёжна? Что меняется при дисбалансе? Почему симуляция не доказывает причинность?',
          '[NumPy random](https://numpy.org/doc/stable/reference/random/generator.html)\n[Python random](https://docs.python.org/3/library/random.html)'),
    entry('Статистические оценки',
          'Различать среднее, медиану, дисперсию; оценивать выбросы; строить доверительный интервал; формулировать гипотезы.',
          'Среднее чувствительно к выбросам, медиана устойчивее. Дисперсия измеряет разброс в квадратных единицах. Доверительный интервал описывает процедуру оценки, а тест не заменяет размер эффекта и предметный смысл. Множественные проверки повышают риск ложных открытий.',
          'Для двух выборок времени ответа посчитайте среднее/медиану, бутстрэпом получите 95% интервал разности медиан и сравните результат после добавления экстремального значения.',
          'Когда медиана полезнее? Что означает 95% CI? Чем значимость отличается от практической пользы? Как выброс меняет дисперсию?',
          '[SciPy statistics](https://docs.scipy.org/doc/scipy/reference/stats.html)\n[Pandas descriptive statistics](https://pandas.pydata.org/docs/user_guide/basics.html#descriptive-statistics)'),
    entry('Градиентный спуск',
          'Связывать loss и градиент; вычислять градиент квадратичной функции; выбирать learning rate; распознавать расходимость.',
          'Градиент показывает направление роста, поэтому для минимизации параметры идут против него. Большой шаг вызывает колебания, маленький — медленное обучение. Масштаб признаков влияет на поверхность оптимизации, поэтому стандартизация и мониторинг loss практически важны.',
          'Реализуйте gradient descent для `f(w)=(w-3)^2`, добейтесь `w≈3`, затем сравните сходимость двух признаков до и после стандартизации.',
          'Почему шаг идёт против градиента? Что делает слишком большой learning rate? Зачем нормализация? Как заметить раннюю остановку?',
          '[PyTorch autograd](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)\n[Scikit-learn preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html)'),
    entry('EDA: исследовательский анализ',
          'Составлять чек-лист EDA; проверять типы и диапазоны; находить дефекты; формулировать гипотезы до обучения.',
          'EDA проверяет, что данные соответствуют вопросу. Начните с размера, происхождения, пропусков, дублей, кардинальности, временного диапазона и target. Визуализация помогает увидеть нелинейность, но количественная проверка и журнал решений обязательны.',
          'Составьте отчёт из 10 проверок, 4 графиков и 3 гипотез. Для каждого дефекта запишите способ обнаружения, риск, принятое преобразование и проверку результата.',
          'Что проверить до графиков? Как отличить ошибку от редкого случая? Почему target анализируется отдельно? Что фиксировать в журнале?',
          '[Pandas tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/)\n[Scikit-learn inspection](https://scikit-learn.org/stable/inspection.html)'),
    entry('Визуализация данных',
          'Выбирать график под вопрос; показывать распределение и связь; не искажать масштабы; сохранять подписи и единицы.',
          'Гистограмма показывает распределение, scatter — связь, boxplot — медиану и выбросы, line plot — динамику. Подписывайте оси, единицы и размер выборки. Сглаживание и логарифмическая шкала допустимы только с пояснением; корреляция не доказывает причинность.',
          'Постройте распределение, связь с target, динамику и сравнение категорий. Для каждого графика напишите корректный вывод и вывод, который делать нельзя.',
          'Как показать выбросы по группам? Когда нужна log-шкала? Почему line plot опасен для категорий? Как показать неопределённость?',
          '[Pandas visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)\n[Matplotlib](https://matplotlib.org/stable/contents.html)'),
    entry('Пропуски и выбросы',
          'Классифицировать пропуски; выбирать удаление/импутацию; обнаруживать выбросы; не допускать leakage статистик.',
          'Пропуск может означать неизвестность, неприменимость или ошибку. Средняя импутация искажает дисперсию, медиана устойчивее, индикатор пропуска сохраняет сигнал. Параметры вычисляйте только на train и применяйте к остальным выборкам.',
          'Сравните удаление, медианную импутацию и импутацию с индикатором в `Pipeline`. Оцените на одинаковом split и объясните изменение метрики.',
          'Почему медиану нельзя считать на всей таблице? Когда выброс нужно сохранить? Что делает missing indicator? Чем MCAR отличается от MNAR?',
          '[Missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)\n[Scikit-learn imputation](https://scikit-learn.org/stable/modules/impute.html)'),
    entry('Разделение выборок и leakage',
          'Разделять train/validation/test; находить target leakage; учитывать время и группы; строить preprocessing в Pipeline.',
          'Train подгоняет параметры, validation выбирает подход, test даёт финальную независимую оценку. Leakage — информация, недоступная в момент прогноза. Для времени нужен порядок, для пользователей — группировка; split является частью постановки задачи.',
          'Сравните случайный и time-based split для прогноза оттока, найдите искусственный leakage-признак и реализуйте Pipeline с `StandardScaler` и моделью.',
          'Почему test нельзя выбирать для tuning? Пример target leakage? Когда GroupKFold? Как Pipeline защищает?',
          '[Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)\n[Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)'),
    entry('Линейные модели',
          'Объяснять линейную и логистическую регрессию; интерпретировать коэффициенты; применять L1/L2; выбирать метрику.',
          'Линейная регрессия предсказывает число, логистическая — вероятность через sigmoid. Коэффициент зависит от масштаба признака. L1 может занулять коэффициенты, L2 уменьшает их; регуляризацию подбирайте внутри cross-validation.',
          'Обучите Ridge и LogisticRegression в Pipeline со StandardScaler, подберите alpha/C через GridSearchCV и объясните знак двух коэффициентов.',
          'Что выдаёт logistic regression до порога? Чем L1 отличается от L2? Почему нужен scaling? Как выбрать метрику при дисбалансе?',
          '[Linear models](https://scikit-learn.org/stable/modules/linear_model.html)\n[Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)'),
    entry('Деревья и ансамбли',
          'Объяснять split дерева; диагностировать переобучение; различать bagging и boosting; осторожно читать importance.',
          'Дерево выбирает разбиения, уменьшающие ошибку, но глубокое дерево запоминает train. Random Forest усредняет разнообразные деревья, boosting последовательно исправляет ошибки. Встроенная importance может быть смещена, поэтому сравнивайте permutation importance.',
          'Сравните DecisionTree, RandomForest и GradientBoosting, постройте качество от глубины и сопоставьте встроенную и permutation importance.',
          'Почему глубокое дерево переобучается? Что усредняет Random Forest? Как boosting использует ошибки? Почему importance не доказывает причинность?',
          '[Decision trees](https://scikit-learn.org/stable/modules/tree.html)\n[Ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html)'),
    entry('Классификация и метрики',
          'Читать confusion matrix; выбирать precision/recall/F1/ROC-AUC/PR-AUC; менять threshold; проверять калибровку.',
          'Accuracy скрывает ошибки редкого класса. Precision показывает долю верных positive, recall — найденную долю positive, F1 балансирует их. При сильном дисбалансе PR-AUC часто информативнее ROC-AUC; threshold выбирают по стоимости ошибок на validation.',
          'Постройте таблицу метрик для порогов 0.2–0.8. Выберите threshold с recall не ниже 0.9, отчитайте false positive и только затем один раз измерьте test.',
          'Что такое false negative? Почему accuracy может обманывать? Когда PR-AUC лучше ROC-AUC? На какой выборке выбирать threshold?',
          '[Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)\n[Calibration](https://scikit-learn.org/stable/modules/calibration.html)'),
    entry('Подбор гиперпараметров',
          'Отличать параметры от гиперпараметров; строить честную CV; использовать Grid/RandomizedSearch; сохранять pipeline.',
          'Параметры учатся по данным, гиперпараметры задаются до обучения. Поиск должен быть внутри Pipeline, чтобы каждый fold учил preprocessing на своей train-части. После выбора конфигурации test измеряется один раз; сохраняйте seed, версии, сетку и метрики.',
          'Настройте RandomizedSearchCV для pipeline с ColumnTransformer, сохраните best_params_ и cv_results_, сравните с baseline и отчитайте разброс по fold.',
          'Почему нельзя выбирать параметры по test? Чем GridSearch отличается от RandomizedSearch? Что такое nested CV? Какие артефакты сохранять?',
          '[Model selection](https://scikit-learn.org/stable/model_selection.html)\n[Pipeline](https://scikit-learn.org/stable/modules/compose.html)'),
    entry('Нейронные сети',
          'Объяснять layer/activation/loss/optimizer; понимать forward/backward; отличать underfitting/overfitting; планировать эксперимент.',
          'Forward строит предсказание, loss сравнивает его с target, backpropagation получает градиенты, optimizer меняет параметры. Активация добавляет нелинейность. Больше параметров повышает выразительность и риск переобучения, поэтому отслеживайте train и validation loss.',
          'Сделайте MLP для синтетической бинарной классификации, сравните один слой и два скрытых слоя, добавьте dropout или weight decay и объясните кривые обучения.',
          'Что вычисляет loss? Зачем backward? Почему validation ухудшается при падающем train loss? Для чего нелинейная активация?',
          '[PyTorch tutorials](https://docs.pytorch.org/tutorials/)\n[Build model](https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html)'),
    entry('PyTorch и тензоры',
          'Создавать tensors; контролировать dtype/device; менять shape; отключать autograd при inference.',
          'Тензор имеет shape, dtype и device; модель и данные должны быть на совместимом device. `requires_grad` строит граф, `torch.no_grad()` экономит память при inference. Batch dimension обычно первая; ошибки shape часто означают перепутанные axes.',
          'Напишите функцию для входа `[batch, features]`, линейного слоя и выхода `[batch, 1]`. Проверьте CPU/device, dtype, backward и inference под no_grad; добавьте assert shape.',
          'Чем tensor отличается от list? Что хранит graph? Зачем model.eval вместе с no_grad? Почему model и data должны быть на одном device?',
          '[Tensor basics](https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html)\n[Autograd](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)'),
    entry('Компьютерное зрение',
          'Понимать формат изображения CNN; объяснять convolution/pooling; готовить transforms; оценивать качество по классам.',
          'CNN использует локальные фильтры и общие веса. Pooling/stride уменьшают разрешение и увеличивают receptive field. В PyTorch формат обычно `[N,C,H,W]`. Аугментации реалистичны и применяются только к train; validation получает детерминированные transforms.',
          'Обучите классификатор на двух классах или CIFAR-10, реализуйте train/validation transforms, confusion matrix и сохранение лучших weights по validation metric.',
          'Почему channel отдельно от height/width? Зачем augment только train? Как найти слабый класс? Что фиксирует early stopping?',
          '[CIFAR-10 tutorial](https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)\n[Vision transforms](https://docs.pytorch.org/vision/stable/transforms.html)'),
    entry('Регуляризация и перенос обучения',
          'Объяснять dropout/weight decay/early stopping; использовать pretrained backbone; замораживать слои; сравнивать кривые.',
          'Dropout выключает активации только в train, weight decay ограничивает веса, early stopping останавливает обучение при ухудшении validation. Transfer learning переносит представления, но требует проверки preprocessing, доменного сдвига и лицензии.',
          'Возьмите pretrained backbone, замените голову, сначала заморозьте backbone, затем разморозьте последние слои с меньшим learning rate. Сравните режимы и число обучаемых параметров.',
          'Почему dropout отключается в eval? Что такое frozen layer? Когда fine-tuning ухудшает результат? Почему preprocessing pretrained модели критичен?',
          '[Transfer learning](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)\n[Dropout](https://docs.pytorch.org/docs/stable/generated/torch.nn.Dropout.html)'),
    entry('Предобработка текста',
          'Выбирать токенизацию; нормализовать Unicode; строить train-only vocabulary; обрабатывать длинные документы.',
          'Токенизация и нормализация зависят от языка и задачи. Vocabulary строится только по train, иначе статистика test просачивается в обучение. Длинные документы требуют truncation/chunking, редкие токены — unknown-стратегии. Не удаляйте сигнал без проверки примеров.',
          'Соберите TF-IDF + LogisticRegression для русских текстов, сравните count vectorizer, изучите ошибки и отдельно обработайте короткие или пустые документы.',
          'Что такое токен? Почему vocabulary нельзя строить на всей выборке? Что теряется при агрессивной очистке? Как обрабатывать длинный документ?',
          '[Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)\n[Tokenizer summary](https://huggingface.co/docs/transformers/main/en/tokenizer_summary)'),
    entry('Эмбеддинги и трансформеры',
          'Различать sparse/dense representation; понимать embedding; описывать attention; проверять ограничения pretrained модели.',
          'TF-IDF кодирует статистику слов, embedding — плотное представление, где близость может отражать контекст. Transformer использует attention, но имеет ограничения длины и стоимости. Проверяйте язык, домен, license, bias, latency и pooling; embedding не является универсальной истиной.',
          'Получите embeddings для пар текстов, сравните cosine similarity, обучите простой классификатор на frozen embeddings и сделайте error analysis минимум по 10 примерам.',
          'Чем TF-IDF отличается от embedding? Что делает attention? Почему нужна нормировка? Какие риски есть у pretrained модели?',
          '[PyTorch transformer tutorial](https://docs.pytorch.org/tutorials/beginner/transformer_tutorial.html)\n[Transformers docs](https://huggingface.co/docs/transformers/index)'),
    entry('Классификация текстов',
          'Создавать text baseline; считать macro/micro F1; исследовать ошибки; сравнивать linear и transformer подходы.',
          'Классификатор состоит из vectorizer/tokenizer, модели и decision rule. TF-IDF + linear model быстро показывает наличие сигнала. Macro F1 одинаково взвешивает классы, micro сильнее отражает частые классы. Дубликаты между train и test завышают качество.',
          'Решите задачу классификации отзывов на 3 класса: baseline TF-IDF, macro F1, 20 ошибок и план перехода к transformer на основе измерений.',
          'Чем macro F1 отличается от weighted? Почему дубликаты опасны? Что даёт error analysis? Когда linear baseline достаточен?',
          '[Text extraction](https://scikit-learn.org/stable/modules/feature_extraction.html)\n[Sequence classification](https://huggingface.co/docs/transformers/tasks/sequence_classification)'),
    entry('Рекомендательные системы',
          'Различать candidate generation/ranking; сравнивать popularity/content/collaborative; считать offline метрики; учитывать cold start.',
          'Рекомендатель состоит из кандидатов, ранжирования и постобработки. Popularity — обязательный baseline. Collaborative filtering использует взаимодействия, content-based — свойства объектов. Offline NDCG/Recall не гарантируют online uplift; нужен time split и контроль feedback loop.',
          'Сделайте popularity baseline и content-based recommender по TF-IDF описаний. Посчитайте Recall@K/NDCG@K по времени и спланируйте A/B-тест с guardrail-метриками.',
          'Что такое candidate generation? Почему random split завышает качество? Что такое cold start? Зачем guardrail metrics?',
          '[Nearest neighbors](https://scikit-learn.org/stable/modules/neighbors.html)\n[NDCG](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html)'),
    entry('FastAPI и сервис модели',
          'Проектировать endpoint predict; валидировать request/response; загружать модель один раз; делать health check.',
          'API-контракт фиксирует вход, выход и ошибки. Pydantic проверяет типы и диапазоны до вызова модели. Модель и tokenizer не загружайте на каждый запрос. Разделяйте `/health` и `/predict`, логируйте request id и latency без персональных данных, указывайте версию модели.',
          'Создайте `POST /predict` и `GET /health` с Pydantic-схемами. Загрузите sklearn-модель при старте, проверьте плохой JSON и диапазоны, добавьте тесты через TestClient.',
          'Что проверяет Pydantic? Почему нельзя загружать модель на каждый запрос? Чем health отличается от predict? Что нельзя писать в лог?',
          '[FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)\n[Request body](https://fastapi.tiangolo.com/tutorial/body/)\n[Testing](https://fastapi.tiangolo.com/tutorial/testing/)'),
    entry('Docker и CI/CD',
          'Собирать воспроизводимый image; отделять build/runtime config; связывать сервисы Compose; определять CI quality gates.',
          'Image состоит из слоёв, container запускает процесс. Dockerfile не должен содержать секреты; зависимости кэшируются, конфигурация приходит runtime. Compose описывает сеть и volumes. CI проверяет lint/test/build, CD публикует immutable tag; миграции должны быть идемпотентны.',
          'Соберите Dockerfile ML-сервиса с non-root пользователем и healthcheck. Создайте Compose с web/redis и CI-шагами check, tests, build; убедитесь, что секрет отсутствует в image layers.',
          'Почему секрет нельзя хранить в Dockerfile? Что делает volume? Image против container? Какие проверки блокируют публикацию?',
          '[Docker get started](https://docs.docker.com/get-started/)\n[Dockerfile reference](https://docs.docker.com/reference/dockerfile/)\n[Compose reference](https://docs.docker.com/reference/compose-file/)'),
    entry('Мониторинг и обновление моделей',
          'Определять latency/throughput/error rate; отслеживать drift; версионировать artifact/schema; планировать rollback.',
          'Наблюдаемость ML включает технические SLI и качество данных/предсказаний. Data drift может появиться до labels, но не всегда означает ухудшение. Prediction связывайте с версией модели и схемой. Обновление делайте через shadow/canary с быстрым возвратом предыдущего artifact; чувствительные данные не логируйте без политики.',
          'Опишите dashboard: p50/p95 latency, 5xx, throughput, missing rate, drift и delayed F1. Напишите alert rules, runbook и rollback-план для модели v2, ухудшившей recall одного сегмента.',
          'Data drift против concept drift? Почему важен p95? Как связать prediction с версией? Когда остановить rollout?',
          '[FastAPI deployment](https://fastapi.tiangolo.com/deployment/)\n[OpenTelemetry primer](https://opentelemetry.io/docs/concepts/observability-primer/)\n[MLflow registry](https://mlflow.org/docs/latest/ml/model-registry/)'),
    entry('Итоговый ML-проект',
          'Формулировать target; пройти путь от данных до API; документировать риски; защищать решение метриками и ошибками.',
          'Итог оценивается не только качеством модели: нужны постановка, происхождение данных, split, baseline, журнал экспериментов, artifact, API, тесты, мониторинг и ограничения. Production-ready проект воспроизводится одной командой и имеет README. Offline результат не обещает business uplift без online проверки.',
          'Соберите репозиторий с README, src, tests, train.py, моделью, FastAPI, Dockerfile и error analysis. Защитите baseline, leakage, метрики по сегментам, latency, безопасность, rollback и следующий эксперимент.',
          'Как сформулирован target и горизонт? Какой baseline? Какие ошибки опаснее? Как другой инженер воспроизведёт результат?',
          '[Model persistence](https://scikit-learn.org/stable/model_persistence.html)\n[FastAPI deployment](https://fastapi.tiangolo.com/deployment/)\n[Docker get started](https://docs.docker.com/get-started/)'),
)

# Keep the catalogue entry concise while storing a full, structured study text
# for every lesson. The lesson-specific blueprint supplies the technical
# vocabulary and production concerns used by the long-form generator.
MATERIALS = tuple(
    {**item, 'theory': build_theory(item['title'])}
    for item in MATERIALS
)


class Command(BaseCommand):
    help = 'Create or update technical materials for all ML engineer lessons.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist. Run seed_ml_course first.')

        lessons = {
            lesson.title: lesson
            for module in course.modules.prefetch_related('lessons')
            for lesson in module.lessons.all()
        }
        planned_titles = {item['title'] for item in MATERIALS}
        missing = planned_titles - lessons.keys()
        unexpected = lessons.keys() - planned_titles
        if missing:
            raise CommandError(f'Missing lesson titles: {sorted(missing)}')
        if unexpected:
            raise CommandError(f'Unexpected lesson titles: {sorted(unexpected)}')
        if len(MATERIALS) != 28:
            raise CommandError(f'Expected 28 materials, got {len(MATERIALS)}')

        for item in MATERIALS:
            lesson = lessons[item['title']]
            LessonMaterial.objects.update_or_create(
                lesson=lesson,
                defaults={key: value for key, value in item.items() if key != 'title'},
            )

        self.stdout.write(self.style.SUCCESS(
            f'Updated {len(MATERIALS)} lesson materials for "{course.title}".'
        ))
