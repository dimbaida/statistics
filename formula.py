import numpy as np
import math
import fisher_tables as ft


def calculate(X):
    l = np.shape(X)[0]  # Чмсло вариантов
    n = np.shape(X)[1]  # Число наблюдений
    V = np.sum(X, axis=1)  # Суммы
    N = np.size(X)  # Общее число наблюдений
    avg = np.average(X)

    C = pow(np.sum(X), 2) / N
    CY = np.sum(np.square(X)) - C
    CV = np.sum(np.square(V)) / n - C
    CZ = CY - CV
    s2v = CV / (l - 1)  # средний квадрат вариантов
    s2 = CZ / (N - l)  # средний кадрат ошибки
    v = 100 * math.sqrt(s2) / avg  # коэффициент вариации, %

    sx = math.sqrt(s2 / n)  # ошибка оптыта
    sd = math.sqrt(2 * s2 / n)  # ошибка разности средних
    sd_percent = 100 * sd / avg  # относительная ошибка разницы средних

    Ff = s2v / s2
    F05 = ft.f05_distr(n, N - l)
    t05 = ft.t_crit(0.95, N - l)

    HCP05 = t05 * sd
    HCP05_percent = (HCP05 * 100) / avg

    print(f'Критерій суттєвості (Ff) = {round(Ff, 2)}')
    print(f'Критерій F на 5%-му рівні значимості (F05) = {F05}')
    print(f'Помилка досліду (sx) = {round(sx, 2)}')
    print(f'Помилка різниці середніх (sd) = {round(sd, 2)}')
    print(f'Відносна помилка різниці середніх (sd_percent) = {round(sd_percent, 2)}')
    print(f'Коефіцієнт варіації % (v) = {round(v, 2)}')
    print(f'НІР абсолютне (HCP05) = {round(HCP05, 2)}')
    print(f'НІР відносне (HCP05_percent) = {round(HCP05_percent, 2)}')

    return 'result'

# output tabl 30 + results



# стр 216!!!