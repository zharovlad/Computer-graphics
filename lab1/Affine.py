import sys
import sdl2.ext
from itertools import tee
from math import sin, cos, pi

MODEL = 'model\\z.obj'

WIDTH = 800
HEIGHT = 800

# для задания по варианту - по умолчанию отражается оносительно плоскости YZ
mirror_vector = (-1, 1, 1)

# 0.5 градуса в радианах для матрицы вращения
RADIAN = pi / 360

BLACK = sdl2.ext.Color(0, 0, 0)
RED = sdl2.ext.Color(255, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)
GREEN = sdl2.ext.Color(0, 255, 0)

WINDOW = sdl2.ext.Window("Affine transformation", size=(WIDTH, HEIGHT))
WINDOW_SURFACE = WINDOW.get_surface()

VERTICES = []  # Список координат вершин 3D-объекта
SURFACES = []  # Список вершин поверхностей, составляющих 3D-объект

# Списки выше хранят дефолтные координаты для сброса
# К спискам ниже применяются преобразования
vertices = []
surfaces = []

def obj_to_vertices():
    VERTICES.clear()
    SURFACES.clear()
    with open(MODEL) as r:
        for line in r.readlines():
            d = line.split(' ')
            if d[0] == 'v':
                # Преобразует тройку в кортеж вещественных чисел
                vertex = (float(d[1]), float(d[2]), float(d[3]))
                VERTICES.append(vertex)
            elif d[0] == 'f':
                surface = tuple(map(lambda v: int(v.split('/')[0]) - 1, d[1:]))
                SURFACES.append(surface)
    global vertices, surfaces
    vertices = VERTICES
    surfaces = SURFACES

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


def scale_and_mirror(x=1, y=1, z=1):
    """
    scale - чтобы расширить по координате --> соответствующее значение > 1
    чтобы сузить по координате --> соответствующее значение 0 < значение < 1

    mirror - чтобы отразить по плоскости, координата, которую нужно отразить = -1
    """
    return [
    x, 0, 0, 0,
    0, y, 0, 0,
    0, 0, z, 0,
    0, 0, 0, 1
    ]

def draw():
    """
    Отрисовка модели
    """
    # Очистка экрана

    sdl2.ext.fill(WINDOW_SURFACE, BLACK)

    sdl2.ext.line(WINDOW_SURFACE, GREEN, (0, round(HEIGHT / 2), WIDTH, round(HEIGHT / 2)))
    sdl2.ext.line(WINDOW_SURFACE, GREEN, (round(WIDTH / 2), 0, round(WIDTH / 2), HEIGHT))


    for each in surfaces:
        a, b = tee(each)
        next(b, None)
        for e in zip(a, b):

            x1, y1 = project(e[0])
            x2, y2 = project(e[1])

            sdl2.ext.line(WINDOW_SURFACE, WHITE, (x1, y1, x2, y2))

            # отраженный объект

            x1, y1 = project(e[0], mirror_vector)
            x2, y2 = project(e[1], mirror_vector)

            sdl2.ext.line(WINDOW_SURFACE, RED, (x1, y1, x2, y2))

        # Соединяем первую вершину грани с последней
        x1, y1 = project(each[0])
        x2, y2 = project(each[-1])
        sdl2.ext.line(WINDOW_SURFACE, WHITE, (x1, y1, x2, y2))

        x1, y1 = project(each[0], mirror_vector)
        x2, y2 = project(each[-1], mirror_vector)
        sdl2.ext.line(WINDOW_SURFACE, RED, (x1, y1, x2, y2))

def project(point, vector=(1,1,1)):
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
       0, 0, 1, -1/pk,
       0, 0, 0, 1
    ]

    # Матрица кабинетной проекции
    #pk = -cos(pi / 4) / 2
    # project_transformation = [
    #    1, 0, 0, 0,
    #    0, 1, 0, 0,
    #    pk, pk, 0, 0,
    #    0, 0, 0, 1
    # ]

    x, y, z = vertices[point][0] * vector[0], vertices[point][1] * vector[1], vertices[point][2] * vector[2]

    w = x * project_transformation[3] + \
        y * project_transformation[7] + \
        z * project_transformation[11] + \
        project_transformation[15]

    # отражаем относительно плоскости YZ, так как координаты x в окне увеличиваются в противоположном направлении, а не как привыкли
    x, y = x / w, -y / w

    scale = 200
    offset_x = WIDTH / 2
    offset_y = HEIGHT / 2

    x, y = round(x * scale + offset_x), round(y * scale + offset_y)
    return min(max(0, round(x)), WIDTH - 1), min(max(0, round(y)), HEIGHT - 1)

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

# Преобразование, корректирующее представление модели в формате OBJ (меняет оси)

def translation(x=0, y=0, z=0):
    """
    Строит матрицу переноса точки в направлении (x, y, z).
    """
    return [
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    x, y, z, 1
    ]

if __name__ == '__main__':
    
    obj_to_vertices()
    WINDOW.show()
    mode = 'reset'
    while mode != 'quit':
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                mode = 'quit'
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_r:
                    mode = 'rotation'
                elif event.key.keysym.sym == sdl2.SDLK_q:
                    obj_to_vertices()
                elif event.key.keysym.sym == sdl2.SDLK_s:
                    mode = 'scale+'
                elif event.key.keysym.sym == sdl2.SDLK_d:
                    mode = 'scale-'
                elif event.key.keysym.sym == sdl2.SDLK_m:
                    mode = 'mirror'
                elif event.key.keysym.sym == sdl2.SDLK_t:
                    mode = 'translation+'
                elif event.key.keysym.sym == sdl2.SDLK_g:
                    mode = 'translation-'
                
                    
        if mode == 'rotation':
            if event.key.keysym.sym == sdl2.SDLK_x:
                transform(rotation('x'))
            elif event.key.keysym.sym == sdl2.SDLK_y:
                transform(rotation('y'))
            elif event.key.keysym.sym == sdl2.SDLK_z:
                transform(rotation('z'))

        elif mode == 'scale+':
            size = 1.001
            if event.key.keysym.sym == sdl2.SDLK_x:
                transform(scale_and_mirror(x=size))
            elif event.key.keysym.sym == sdl2.SDLK_y:
                transform(scale_and_mirror(y=size))
            elif event.key.keysym.sym == sdl2.SDLK_z:
                transform(scale_and_mirror(z=size))

        elif mode == 'scale-':
            size = 0.999
            if event.key.keysym.sym == sdl2.SDLK_x:
                transform(scale_and_mirror(x=size))
            elif event.key.keysym.sym == sdl2.SDLK_y:
                transform(scale_and_mirror(y=size))
            elif event.key.keysym.sym == sdl2.SDLK_z:
                transform(scale_and_mirror(z=size))

        elif mode == 'mirror':
            size = -1
            if event.key.keysym.sym == sdl2.SDLK_x:
                transform(scale_and_mirror(x=size))
            elif event.key.keysym.sym == sdl2.SDLK_y:
                transform(scale_and_mirror(y=size))
            elif event.key.keysym.sym == sdl2.SDLK_z:
                transform(scale_and_mirror(z=size))
            event.key.keysym.sym = sdl2.SDLK_m

        elif mode == 'translation+':
            pixels = 0.01
            if event.key.keysym.sym == sdl2.SDLK_x:
                transform(translation(x=pixels))
            elif event.key.keysym.sym == sdl2.SDLK_y:
                transform(translation(y=pixels))
            elif event.key.keysym.sym == sdl2.SDLK_z:
                transform(translation(z=pixels))
        
        elif mode == 'translation-':
            pixels = -0.01
            if event.key.keysym.sym == sdl2.SDLK_x:
                transform(translation(x=pixels))
            elif event.key.keysym.sym == sdl2.SDLK_y:
                transform(translation(y=pixels))
            elif event.key.keysym.sym == sdl2.SDLK_z:
                transform(translation(z=pixels))

        draw()
        WINDOW.refresh()
