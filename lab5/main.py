import pygame
import matplotlib.pyplot as plt

# Размер рамки
FRAME = 10

# Максимальное значение для цвета 255
RGB_MAX = 255

BRIGHTNESS_COEFFICIENT = 10
CONTRAST_INCREMENT = 2
CONTRAST_DECREASE = 0.5

FPS = 30

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Путь к bmp файлу
IMAGE_PATH = 'images\\lodka.bmp'
# IMAGE_PATH = 'images\\tiger.jpg'
# IMAGE_PATH = 'images\\billy.jpg'

# Здесь хранится поверхность изображения
surface = pygame.image.load(IMAGE_PATH)

# Размер изображения
WIDTH = pygame.Surface.get_width(surface)
HEIGHT = pygame.Surface.get_height(surface)

# Создаем  окно
pygame.init()
pygame.mixer.init()
# Изображение + рамка 
screen = pygame.display.set_mode((WIDTH + FRAME * 2, HEIGHT + FRAME * 2))
pygame.display.set_caption("Lab5 graphic")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group() 


def get_brightness(color):
    """
    Яркость считается по формуле 0,299R + 0,5876G + 0,114B
    """
    brightness = round(0.299 * color[0] + 0.5876 * color[1] + 0.114 * color[2])
    return RGB_MAX - 1 if brightness > RGB_MAX - 1 else brightness


def negative():
    """
    Негатив получается простой заменой значения каждого пикселя на его дополнение до 255 (R = 255 - R)
    """
    for x in range(WIDTH):
        for y in range(HEIGHT):
            color = surface.get_at((x, y))
            surface.set_at((x, y), (RGB_MAX - color[0], RGB_MAX - color[1], RGB_MAX - color[2])) 


def transform_to_grey():
    """
    Преобразование к оттенкам серого заключается в копировании яркости во все три канала
    """
    for x in range(WIDTH):
        for y in range(HEIGHT):
            brightness = get_brightness(surface.get_at((x, y)))
            surface.set_at((x, y), (brightness, brightness, brightness))


def binary():
    """
    Бинаризация изображения
    """
    s = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            s += get_brightness(surface.get_at((x, y)))
    average = s / (WIDTH * HEIGHT)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            brightness = get_brightness(surface.get_at((x, y)))
            color = WHITE if brightness > average else BLACK
            surface.set_at((x, y), color)


def brightness_histogram(show=False):
    """
    Выводит на экран гистограмму яркости при значении show=True
    Возвращает я
    """
    brightness_counter = [0 for i in range(RGB_MAX)]

    for x in range(WIDTH):
        for y in range(HEIGHT):
            color = surface.get_at((x, y))
            brightness_counter[get_brightness(color)] += 1
    if show:
        fig, ax = plt.subplots()
        ax.bar([i for i in range(RGB_MAX)], brightness_counter)
        ax.set_title('Brightness histogram')
        plt.xlabel('Brightness')
        plt.ylabel('Count')
        plt.show()

    return brightness_counter
    
def brightness_change(coefficient):
    """
    Изменение яркости
    """
    for x in range(WIDTH):
        for y in range(HEIGHT):
            color = surface.get_at((x, y))
            R, G, B = color[0], color[1], color[2]
            R += coefficient
            G += coefficient
            B += coefficient

            R = RGB_MAX if R > RGB_MAX else 0 if R < 0 else R
            G = RGB_MAX if G > RGB_MAX else 0 if G < 0 else G
            B = RGB_MAX if B > RGB_MAX else 0 if B < 0 else B

            surface.set_at((x, y), (R, G, B))

def contrast_change(coefficient):
    """
    Изменение контраста
    """
    s = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            s += get_brightness(surface.get_at((x, y)))
    average = s / (WIDTH * HEIGHT)

    for x in range(WIDTH):
        for y in range(HEIGHT):
            color = surface.get_at((x, y))
            R, G, B = color[0], color[1], color[2]

            R = coefficient * (R - average) + average
            G = coefficient * (G - average) + average
            B = coefficient * (B - average) + average

            R = RGB_MAX if R > RGB_MAX else 0 if R < 0 else R
            G = RGB_MAX if G > RGB_MAX else 0 if G < 0 else G
            B = RGB_MAX if B > RGB_MAX else 0 if B < 0 else B            
            
            surface.set_at((x, y), (R, G, B))


if __name__ == "__main__":
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
                # По нажатии 'q' сброс всех изменений
                if event.key == pygame.K_q:
                    surface = pygame.image.load(IMAGE_PATH)
                # По нажатии 'n' получение негативного изображения
                elif event.key == pygame.K_n:
                    negative()
                # По нажатии 'h' получение гистограммы яркости
                elif event.key == pygame.K_h:
                    brightness_histogram(show=True)
                # По нажатии 'g' преобразование к оттенкам серого
                elif event.key == pygame.K_g:
                    transform_to_grey()
                # По нажатии 'b' бинаризация
                elif event.key == pygame.K_b:
                    binary()
                elif event.key == pygame.K_1:
                    brightness_change(BRIGHTNESS_COEFFICIENT)
                elif event.key == pygame.K_2:
                    brightness_change(-BRIGHTNESS_COEFFICIENT)
                elif event.key == pygame.K_9:
                    contrast_change(CONTRAST_INCREMENT)
                elif event.key == pygame.K_0:
                    contrast_change(CONTRAST_DECREASE)

        # Рендеринг
        # Второй аргумент это координаты левого верхнего угла изображения
        screen.blit(surface, (FRAME, FRAME))

        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()

    pygame.quit()
