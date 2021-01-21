import pygame
import sys
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
MODEL = 'model\\cylinder.obj'

# Масштаб
SCALE = 20

# Градус в радианах для матрицы вращения
RADIAN = pi / 90

vertices = []   # Список координат вершин 3D-объекта
surfaces = []   # Список вершин поверхностей, составляющих 3D-объект

def obj_to_vertices():
    global vertices, surfaces
    vertices.clear()
    surfaces.clear()
    with open(MODEL) as r:
        for line in r.readlines():
            d = line.split(' ')
            if d[0] == 'v':
                # Вершины хранятся в кортеж вещественных чисел
                vertex = (SCALE * float(d[1]), SCALE * float(d[2]), SCALE * float(d[3]))
                vertices.append(vertex)

            elif d[0] == 'f':
                # Поверхность задается индексами вершин, может быть любой длины
                surface = tuple(map(lambda v: int(v.split('/')[0]) - 1, d[1:]))
                surfaces.append(surface)

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

    # Каждый элемент соответствует пикселю на экране. Записывает удаленность (координату z)
    z_buffer = [[-inf for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # Для каждого полигона вычислим уравнение плоскости методом Ньюэла (a, b, c, d)
    for i, surface in enumerate(surfaces):
        v_poly = []
        for corner in surface:
            v_poly.append((vertices[corner][0], vertices[corner][1], vertices[corner][2]))                
        a, b, c, d = newell(v_poly)

        # Определим границы полигона
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
        
        xmin, xmax, ymin, ymax = round(xmin), round(xmax), round(ymin), round(ymax)
        # Попиксельно вычисляем z для каждой точке в границе
        for x in range(xmin, xmax):
            for y in range(ymin, ymax):
                # z = -(ax + by + d) / c
                if c == 0:
                    continue
                z = -(a * x + b * y + d) / c
                
                # если z в данной области ближе 
                if z > z_buffer[y][x]:
                    # и если (x, y) принадлежит полигону
                    if pointloc(v_poly, (x, y)):
                        # записываем значение в z буффер и индекс поверхночти
                        z_buffer[y][x] = z
                        pygame.draw.line(screen, COLORS[i % len(COLORS)], (x + WIDTH / 2, -y + HEIGHT / 2), \
                             (x + WIDTH / 2, -y + HEIGHT / 2))


def pointloc(polygon, dot):
    result = False
    for i in range(len(polygon)):
        j = i - 1
        if polygon[i][1] < polygon[j][1] and polygon[i][1] <= dot[1] and dot[1] <= polygon[j][1] and \
        (polygon[j][1] - polygon[i][1]) * (dot[0] - polygon[i][0]) > (polygon[j][0] - polygon[i][0]) * (dot[1] - polygon[i][1]) or \
        polygon[i][1] > polygon[j][1] and polygon[j][1] <= dot[1] and dot[1] <= polygon[i][1] and \
        (polygon[j][1] - polygon[i][1]) * (dot[0] - polygon[i][0]) < (polygon[j][0] - polygon[i][0]) * (dot[1] - polygon[i][1]):
            result = not result
    return result

def newell(v):
    """
    Метод Ньюэла для вычисления нормали к плоскости
    """
    a, b, c = 0, 0, 0
    for i in range(-1, len(v) - 1):
        j = i + 1
        a += (v[i][1] - v[j][1]) * (v[i][2] + v[j][2])
        b += (v[i][2] - v[j][2]) * (v[i][0] + v[j][0])
        c += (v[i][0] - v[j][0]) * (v[i][1] + v[j][1])
    d = -(a * v[0][0] + b * v[0][1] + c * v[0][2])
    return a, b, c, d

# def project(point):
#     """
#     Проецирует точку на некоторую картинную плоскость.
#     Возвращает пару значений в оконных координатах.
#     """

#     # Матрица проецирования.
#     project_transformation = [
#        1, 0, 0, 0,
#        0, 1, 0, 0,
#        0, 0, 0, 0,
#        0, 0, 0, 1
#     ]
#     x, y, z = point[0], point[1], point[2]

#     w = x * project_transformation[3] + y * project_transformation[7] + z * project_transformation[11] + project_transformation[15]

#     # отражаем относительно плоскости YZ, так как координаты x в окне увеличиваются в противоположном направлении, а не как привыкли
#     x, y = x / w, -y / w
    

#     offset_x = WIDTH / 2
#     offset_y = HEIGHT / 2

#     x, y = round(x + offset_x), round(y + offset_y)
#     return min(max(0, round(x)), WIDTH - 1), min(max(0, round(y)), HEIGHT - 1)
    

def rotation(axis, angle=RADIAN):
    """
    Возвращает матрицу вращения в зависимости от оси 
    """

    if axis == 'x':
        return [
        1, 0,           0,              0,
        0, cos(angle), sin(angle),    0,
        0, -sin(angle), cos(angle),   0,
        0, 0,           0,              1
    ]

    elif axis == 'y':
        return [
        cos(angle), 0, -sin(angle), 0,
        0, 1, 0, 0,
        sin(angle), 0, cos(angle), 0,
        0, 0, 0, 1
    ]

    elif axis == 'z':
        return [
        cos(angle), sin(angle), 0, 0,
        -sin(angle), cos(angle), 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
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

        # Обновление       
        transform(rotation('x'))
        transform(rotation('y'))
        transform(rotation('z'))

        # Рендеринг
        draw()

        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()

    pygame.quit()
