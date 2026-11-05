
"""Игра «Змейка»

Это реализация классической игры «Змейка» с использованием библиотеки Pygame.
Основные возможности:
* движение змейки по игровому полю;
* поедание яблок для роста;
* увеличение скорости игры со временем;
* сброс игры при столкновении змейки с собой.


Классы:
* GameObject — базовый класс для всех игровых объектов;
* Apple — класс, представляющий яблоко на игровом поле;
* Snake — класс змейки с логикой движения и роста.


Функции:
* handle_keys() — обработка нажатий клавиш;
* update_game_state() — обновление состояния игры;
* draw_game() — отрисовка игрового поля;
* main() — главный игровой цикл.
"""

import random
import sys

import pygame as pg

# Инициализация Pygame
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь для сопоставления нажатий клавиш с направлениями
KEY_TO_DIRECTION = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT
}

# Константы цветов:
WHITE = (255, 255, 255)
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 8


# Создаём экран и часы
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=WHITE):
        """Инициализирует объект с позицией и цветом."""
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """
        Абстрактный метод отрисовки объекта целиком.
        Должен быть реализован в классах‑потомках.
        Использует глобальную переменную screen.
        """
        raise NotImplementedError

    def _draw_cell(self, position, color=None, border_width=1):
        """
        Отрисовывает одну ячейку сетки по заданным координатам.

        Args:
            position: кортеж (x, y) — позиция ячейки.
            color: цвет ячейки. Если None, используется self.body_color.
            border_width: толщина границы. Если 0, граница не рисуется.
        """
        cell_color = color if color is not None else self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, cell_color, rect)
        if border_width > 0:
            pg.draw.rect(screen, BORDER_COLOR, rect, border_width)


class Apple(GameObject):
    """Яблоко: появляется в случайной клетке, не выходит за границы."""

    def __init__(self, occupied_positions=None):
        """
        Инициализирует яблоко: задаёт цвет и случайную позицию.

        Args:
            occupied_positions: множество занятых позиций (координат),
                в которых яблоко не должно появляться.
        """
        super().__init__(body_color=APPLE_COLOR)
        # Передаём занятые позиции в randomize_position
        self.randomize_position(occupied_positions or set())

    def randomize_position(self, occupied_positions):
        """
        Генерирует новую случайную позицию яблока, избегая занятых клеток.

        Args:
            occupied_positions: множество занятых позиций на игровом поле.
        """
        available_positions = []

        # Собираем все возможные позиции на поле
        for grid_x in range(GRID_WIDTH):
            for grid_y in range(GRID_HEIGHT):
                position = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)
                if position not in occupied_positions:
                    available_positions.append(position)

        if available_positions:
            self.position = random.choice(available_positions)
        else:
            # Если все клетки заняты (крайне редкий случай), ставим в центр
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def draw(self):
        """Отрисовывает яблоко как одну ячейку."""
        self._draw_cell(self.position)


class Snake(GameObject):
    """Змейка: движется, растёт, не может развернуться на 180°."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку: стартовая позиция, направление, длина."""
        start_x, start_y = self._get_center_position()
        super().__init__((start_x, start_y), body_color)
        self.reset()

    def _get_center_position(self):
        """Возвращает координаты центральной клетки игрового поля."""
        x = (GRID_WIDTH // 2) * GRID_SIZE
        y = (GRID_HEIGHT // 2) * GRID_SIZE
        return x, y

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        start_x, start_y = self._get_center_position()
        self.position = (start_x, start_y)
        self.positions = [self.position]
        directions = [UP, DOWN, LEFT, RIGHT]
        self.direction = random.choice(directions)
        self.last = None
        self.eaten_apples = 0
        self.length = 1
        self.just_reset = True

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction=None):
        """
        Обновляет направление движения, если задано новое направление.


        Args:
            new_direction: кортеж (dx, dy) — новое направление движения.
                Если None, направление не меняется.
        """
        if new_direction is not None:
            # Проверка на нулевое направление
            if new_direction == (0, 0):
                return  # игнорируем команду «стоять»

            current_dx, current_dy = self.direction
            opposite_dir = (-current_dx, -current_dy)
            if new_direction != opposite_dir:
                self.direction = new_direction

    def move(self):
        """Двигает змейку на один шаг по текущему направлению."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )

        # Сохраняем позицию старого хвоста (до удаления)
        if len(self.positions) >= self.length:
            self.last = self.positions[-1]  # позиция хвоста до удаления
        else:
            self.last = None  # если хвост не удаляется, зануляем last

        # Вставляем новую голову в начало списка
        self.positions.insert(0, new_head)

        # Удаляем хвост, если длина превышает допустимую
        if len(self.positions) > self.length:
            self.positions.pop()  # удаляем последний элемент (старый хвост)

    def check_eat_apple(self, apple):
        """Проверяет, съела ли змейка яблоко."""
        return self.get_head_position() == apple.position

    def grow(self):
        """Увеличивает длину змейки на 1 сегмент."""
        self.length += 1
        self.eaten_apples += 1  # Увеличиваем счётчик съеденных яблок

    def get_current_speed(self):
        """Возвращает текущую скорость змейки."""
        base_speed = SPEED
        speed_increase = self.eaten_apples // 3
        return base_speed + speed_increase

    def draw(self):
        """Отрисовывает змейку: голову, тело и затирает старый хвост."""
        # Затираем последний сегмент
        if self.last:
            self._draw_cell(self.last, BOARD_BACKGROUND_COLOR, 0)

        # Рисуем голову
        head_position = self.positions[0]
        self._draw_cell(head_position)

        # Рисуем тело
        for position in self.positions[1:]:
            self._draw_cell(position)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш и события выхода из игры.

    Для каждого события проверяет:
      - QUIT: завершает работу программы;
      - KEYDOWN: пытается получить новое направление по нажатой клавише
        и передаёт его змейке, если направление найдено.

    Args:
        snake (Snake): экземпляр змейки, у которой нужно обновить направление.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            new_direction = KEY_TO_DIRECTION.get(event.key)
            if new_direction is not None:
                snake.update_direction(new_direction)


def update_game_state(snake, apple):
    """Обновляет состояние игры: движение, поедание, столкновение."""
    snake.move()

    need_reposition = False

    # Проверяем поедание яблока
    if snake.check_eat_apple(apple):
        snake.grow()
        need_reposition = True

    # Проверяем столкновение головы со своим телом
    head = snake.get_head_position()
    if head in snake.positions[1:]:
        snake.reset()
        need_reposition = True

    # Перепозиционируем яблоко один раз, если нужно
    if need_reposition:
        occupied_positions = set(snake.positions)
        apple.randomize_position(occupied_positions)


def draw_game(snake, apple, first_draw=False):
    """
    Отрисовывает игровое поле.
    first_draw: True при первом запуске или сбросе игры.
    """
    # Заполняем фон только при старте или сбросе
    if first_draw or snake.just_reset:
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.just_reset = False  # Сбрасываем флаг после отрисовки
    else:
        # Стираем только старый хвост змейки
        if snake.last is not None:
            snake._draw_cell(snake.last, BOARD_BACKGROUND_COLOR, 0)
    # Отрисовываем объекты (они сами используют глобальный screen)
    apple.draw()
    snake.draw()
    pg.display.flip()


def main():
    """Запускает и управляет игровым циклом Змейки."""
    snake = Snake()
    # Создаём множество занятых позиций (позиции змейки)
    occupied_positions = set(snake.positions)
    # Передаём занятые позиции в конструктор яблока
    apple = Apple(occupied_positions=occupied_positions)

    running = True
    first_draw = True  # Флаг для первой отрисовки

    while running:
        current_speed = snake.get_current_speed()
        clock.tick(current_speed)
        handle_keys(snake)
        update_game_state(snake, apple)
        # Отрисовываем игру, передавая флаг первой отрисовки
        draw_game(snake, apple, first_draw=first_draw)
        # После первой итерации сбрасываем флаг
        first_draw = False


if __name__ == '__main__':
    main()
