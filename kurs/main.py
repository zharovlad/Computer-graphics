import pygame
from random import randrange
from math import sqrt
from itertools import tee

# Максимальное значение для цвета 255
RGB_MAX = 255

# Шаг для изменения координат точек
STEP_COORDINATE = 1

# Шаг для изменения значения канала
STEP_RGB = 1

# Коэффициент аппроксимации (все, что меньше 50 - выглядит допустимым)
APPROXIMATION = 15

# Ширина и высота окна
width = 800
height = 600

# Ширина линий для отрисовки
WIDTH_LINE = 1
WIDTH_BEZIER_LINE = 1

# Черный цвет для задания фона
SCREEN_COLOR = (0, 0, 0)

# Количество кадров в секунду (обновлений экрана)
FPS = 60

# Количество линий 
AMOUNT_OF_LINES = 1
# Количество точек для задания линии
AMOUNT_OF_DOTS = 10

# Инициализация окна
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Screensaver")
clock = pygame.time.Clock()

class Color:
    """
    В классе Color содержатся поля R G B, соответствующие трем каналам, а также методы для динамического изменения цвета и удобного получения данных в кортеже
    """
    def __init__(self):
        """
        При инициализации указываются рандомные значения, а также изменение для каждого канала
        """
        self.R = randrange(0, RGB_MAX)
        self.G = randrange(0, RGB_MAX)
        self.B = randrange(0, RGB_MAX)

        self.changeR = STEP_RGB if randrange(0, RGB_MAX) > RGB_MAX / 2 else -STEP_RGB
        self.changeG = STEP_RGB if randrange(0, RGB_MAX) > RGB_MAX / 2 else -STEP_RGB
        self.changeB = STEP_RGB if randrange(0, RGB_MAX) > RGB_MAX / 2 else -STEP_RGB

    def color_change(self):
        """
        Функция вызывается при каждом обновлении кадра. Меняет значение каждого канала в диапазоне (0, 255)
        """
        self.R += self.changeR
        self.G += self.changeG
        self.B += self.changeB

        if self.R > RGB_MAX or self.R < 0:
            self.changeR = -self.changeR
            self.R = RGB_MAX - 1 if self.R > RGB_MAX else 1
        
        if self.G > RGB_MAX or self.G < 0:
            self.changeG = -self.changeG
            self.G = RGB_MAX - 1 if self.G > RGB_MAX else 1

        if self.B > RGB_MAX or self.B < 0:
            self.changeB = -self.changeB
            self.B = RGB_MAX - 1 if self.B > RGB_MAX else 1
    
    def get_color(self):
        """
        Возвращает в кортеже значения R G B
        """
        return (self.R, self.G, self.B)


class Dot:
    """
    В классе Dot хранятся поля x и y соответствующие точке на плоскости, а также методы для динамического изменения координат и удобного получения данных в кортеже
    """
    def __init__(self, xy=None):
        """
        При инициализации указываются рандомные значения, а также изменение для каждой оси
        """
        self.x = randrange(0, width) if not xy else xy[0]
        self.y = randrange(0, height) if not xy else xy[1]

        self.changex = STEP_COORDINATE if randrange(0, width) > width / 2 else -STEP_COORDINATE
        self.changey = STEP_COORDINATE if randrange(0, height) > height / 2 else -STEP_COORDINATE
    
    def coordinate_change(self):
        """
        Функция вызывается при каждом обновлении кадра. Меняет значение каждой оси.
        Для x в диапазоне (0, width)
        Для y в диапазоне (0, height)
        """
        self.x += self.changex
        self.y += self.changey

        if self.x > width or self.x < 0:
            self.changex = -self.changex
            self.x = width - 1 if self.x > width else 1

        if self.y > height or self.y < 0:
            self.changey = -self.changey
            self.y = height - 1 if self.y > height else 1
        

    def get_coordinate(self):
        """
        Получение координат в кортеже, используется для отрисовки
        """
        return (self.x, self.y)

class Line:
    """
    В классе Line хранятся координаты точек ломаной линии, по которой строится кривая Безье и цвет для вывода этой кривой на экран.
    Методы отрисовки и динамического изменения
    """
    def __init__(self):
        self.dots = [Dot() for _ in range(AMOUNT_OF_DOTS)]
        self.color = Color()

    def smooth_line_change(self):
        """
        Изменение линии
        """
        for dot in self.dots:
            dot.coordinate_change()
        self.color.color_change()

    def draw(self):
        """
        Отрисовка 
        """
        a, b = tee(self.dots)
        next(b, None)
        for segment in zip(a, b):
            pygame.draw.line(
                screen,
                self.color.get_color(),     
                segment[0].get_coordinate(),
                segment[1].get_coordinate(),
                WIDTH_LINE
            )

class Bezier:
    """ Класс содержит методы для вычисления и отображения кривой Безье на экране """
    @staticmethod
    def draw(dots, color):
        """
        Если отрезок из dots не напоминает форму кривой Безье - увеличить количество отрезов аппроксимации, иначе вывести отрезочек на экран
        """
        if Bezier.is_flat(dots):
            Bezier.draw_segments(dots, color)
        else:
            pieces = Bezier.subdivide(dots)
            Bezier.draw(pieces[0], color)
            Bezier.draw(pieces[1], color)


    @staticmethod
    def subdivide(segments_dots):
        """
        Разбивает кривую Безье на 2 кусочка
        """
        midpoints = [segments_dots]
        for i in range(len(segments_dots) - 1):
            midpoints.append(Bezier.get_midpoints(midpoints[i]))

        return [
            [midpoints[i][0] for i in range(len(midpoints))],
            [midpoints[len(midpoints) - i - 1][i] for i in range(len(midpoints))]
        ]


    @staticmethod
    def get_midpoints(point_list):
        """ 
        Возвращает последовательные средние точки отрезков из передаваемых точек
        """
        midpoint_list = []
        a, b = tee(point_list)
        next(b, None)
        for segment in zip(a, b):
            midpoint_list.append(Dot(Bezier.midpoint(segment[0], segment[1])))
        return midpoint_list

    @staticmethod
    def midpoint(a, b):
        """
        Считает среднюю точку отрезка
        """
        return [(a.x + b.x) / 2.0, (a.y + b.y) / 2.0]

    @staticmethod
    def is_flat(segments_dots):
        """
        Определяет, нужно ли увеличивать количество отрезков аппроксимации
        """
        ax = 3.0 * segments_dots[1].x - 2.0 * segments_dots[0].x - segments_dots[3].x
        ay = 3.0 * segments_dots[1].y - 2.0 * segments_dots[0].y - segments_dots[3].y
        bx = 3.0 * segments_dots[2].x - segments_dots[0].x - 2.0 * segments_dots[3].x
        by = 3.0 * segments_dots[2].y - segments_dots[0].y - 2.0 * segments_dots[3].y

        return True if max(ax ** 2, bx ** 2) + max(ay ** 2, by ** 2) <= APPROXIMATION else False


    @staticmethod
    def draw_segments(line, color):
        """
        Рисует отрезки аппроксимации
        """
        a, b = tee(line)
        next(b, None)
        for segment in zip(a, b):
            pygame.draw.line(
                screen,
                color,
                segment[0].get_coordinate(),
                segment[1].get_coordinate(),
                WIDTH_BEZIER_LINE
            )



if __name__ == "__main__":
    # Цикл обработки
    mode = 'running'
    lines = [Line() for _ in range(AMOUNT_OF_LINES)]
    while mode != 'quit':
        # Держим цикл на правильной скорости
        clock.tick(FPS)

        # Ввод процесса (события)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mode = 'quit'
            elif event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 'draw'
                elif event.key == pygame.K_2:
                    mode = 'running'
        
        # Очистка экрана
        screen.fill(SCREEN_COLOR)

        # Рендеринг 
        for line in lines:
            line.smooth_line_change()
            Bezier.draw(line.dots, line.color.get_color())
            if mode == 'draw':
                line.draw()

        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()

    pygame.quit()