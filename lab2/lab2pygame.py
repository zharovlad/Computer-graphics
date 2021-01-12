import pygame
import sys
from itertools import tee
from math import sin, cos, pi, inf

WIDTH = 640
HEIGHT = 480
FPS = 30

# Задаем цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
NAVY = (0, 0, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 255, 255)
PINK = (255, 0, 255)
COLORS = (WHITE, RED, GREEN, NAVY, YELLOW, BLUE, PINK)

# Создаем  окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lab2 graphic")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group() 

# путь к obj файлу
MODEL = 'model\\cube.obj'

# Каждый элемент соответствует пикселю на экране. Записывает удаленность (координату z)
z_buffer = [[-inf for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Масштаб
SCALE = 50

# Если "c" меньше этого числа, заменим на это число
EPS = 10e-2

# Градус в радианах для матрицы вращения
RADIAN = pi / 90

VERTICES = []  # Список координат вершин 3D-объекта
SURFACES = []  # Список вершин поверхностей, составляющих 3D-объект
NORMALS = []   # Список нормалей

# Списки выше хранят дефолтные координаты для сброса
# К спискам ниже применяются преобразования
vertices = []
surfaces = []
normals = []

def obj_to_vertices():
    VERTICES.clear()
    SURFACES.clear()
    with open(MODEL) as r:
        for line in r.readlines():
            d = line.split(' ')
            if d[0] == 'v':
                # Преобразует тройку в кортеж вещественных чисел
                vertex = (SCALE * float(d[1]), SCALE * float(d[2]), SCALE * float(d[3]))
                VERTICES.append(vertex)
            elif d[0] == 'f':
                surface = tuple(map(lambda v: int(v.split('/')[0]) - 1, d[1:]))
                SURFACES.append(surface)
            elif d[0] == 'vn':
                # Нормали
                if float(d[3]) < EPS:
                    if float(d[3]) < 0:
                        d[3] = -EPS
                    else:
                        d[3] = EPS
                NORMALS.append((float(d[1]), float(d[2]), float(d[3])))

    global vertices, surfaces, normals
    vertices = VERTICES
    surfaces = SURFACES
    normals = NORMALS

def transform(m):
    """
    Применяет матричное преобразование m ко всем точкам vertices.
    """
    v = []
    global vertices
    for vertice in vertices:
        v.append(
            (vertice[0] * m[0] + vertice[1] * m[4] + vertice[2] * m[8] + m[12],
            vertice[0] * m[1] + vertice[1] * m[5] + vertice[2] * m[9] + m[13],
            vertice[0] * m[2] + vertice[1] * m[6] + vertice[2] * m[10] + m[14]))
    vertices = v


def draw():
    """
    Отрисовка модели
    """
    # Очистка экрана
    screen.fill(BLACK)

    global z_buffer
    # Очистка z буффера
    z_buffer = [[-inf for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for i, surface in enumerate(surfaces):
        c = i % len(COLORS)
        draw_polygon(surface, COLORS[c], normals[i])

# В полигоне точка или нет
def rotate(A, B, C):
    return (B[0] - A[0]) * (C[1] - B[1]) - (B[1] - A[1]) * (C[0] - B[0])

def intersect(A, B, C, D): 
    return rotate(A, B, C) * rotate(A, B, D) <= 0 and rotate(C, D, A) * rotate(C, D, B) < 0

def pointloc(P, A):
    n = len(P)
    if rotate(P[0], P[1], A) < 0 or rotate(P[0], P[n - 1], A) > 0:
        return False
    p, r = 1, n - 1
    while r - p > 1:
        q = int((p + r) / 2)
        if rotate(P[0], P[q], A) < 0: 
            r = q
        else: 
            p = q
    return not intersect(P[0], A, P[p], P[r])     


def draw_polygon(p, color, normal):
    """
    Рисует полигон p по точкам в цвет color
    """

    v_poly = []
    for corner in p:
        v_poly.append((vertices[corner][0], vertices[corner][1], vertices[corner][2]))
    xmin = inf
    ymin = inf
    xmax = -inf
    ymax = -inf
    
    for corner in v_poly:
        if corner[0] > xmax:
            xmax = corner[0]

        if corner[0] < xmin:
            xmin = corner[0]

        if corner[1] > ymax:
            ymax = corner[1]

        if corner[1] < ymin:
            ymin = corner[1]

    # Вычислим d из уравнения плоскости d = -(ax + by + cz)
    d = -(normal[0] * v_poly[0][0] + normal[1] * v_poly[0][1] + normal[2] * v_poly[0][2])

    xmin, xmax, ymin, ymax = round(xmin), round(xmax), round(ymin), round(ymax)
    for y in range(ymin, ymax):
        for x in range(xmin, xmax):
            if pointloc(v_poly, (x, y)):
                # z = -(ax + by + d) / c
                z = -(normal[0] * v_poly[0][0] + normal[1] * v_poly[0][1] + d) / normal[2]
                dotx, doty = project((x, y, z))
                if z > z_buffer[x][y]:
                    pygame.draw.line(screen, color, (dotx, doty), (dotx, doty))
                    z_buffer[x][y] = z

def project(point):
    """
    Проецирует точку на некоторую картинную плоскость.
    Возвращает пару значений в оконных координатах.
    """
    # Коэфициент смещения центра картинной плоскости (см. комментарий ниже)
    pk = 50

    # Матрица преобразования перспективного проецирования.
    project_transformation = [
       1, 0, 0, 0,
       0, 1, 0, 0,
       0, 0, 0, 0,
    #    0, 0, 1, -1/pk,
       0, 0, 0, 1
    ]

    x, y, z = point[0], point[1], point[2]

    w = x * project_transformation[3] + \
        y * project_transformation[7] + \
        z * project_transformation[11] + \
        project_transformation[15]

    # отражаем относительно плоскости YZ, так как координаты x в окне увеличиваются в противоположном направлении, а не как привыкли
    x, y = x / w, -y / w

    offset_x = WIDTH / 2
    offset_y = HEIGHT / 2

    x, y = round(x + offset_x), round(y + offset_y)
    return min(max(0, round(x)), WIDTH - 1), min(max(0, round(y)), HEIGHT - 1)

def rotation(angle=RADIAN):
    """
    Возвращает матрицу вращения в зависимости от оси 
    """
    return [
        cos(angle), sin(angle), -sin(angle), 0,
        -sin(angle), cos(angle), sin(angle),    0,
        sin(angle), -sin(angle), cos(angle),   0,
        0, 0,           0,              1
    ]


if __name__ == "__main__":
    obj_to_vertices()
    # Цикл обработки
    mode = 'running'
    while mode != 'quit':
        # Держим цикл на правильной скорости
        clock.tick(FPS)
        # Ввод процесса (события)
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                mode = 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    obj_to_vertices()
        
        transform(rotation())

        # Обновление
        all_sprites.update()

        # Рендеринг
        draw()

        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()

    pygame.quit()
