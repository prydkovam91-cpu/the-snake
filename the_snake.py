
from random import randint
import pygame

# Инициализация Pygame
pygame.init()

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

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 8

# Создаём экран и часы
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует объект с позицией и цветом."""
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        if body_color is None:
            body_color = (255, 255, 255)
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """Отрисовывает объект на поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко: появляется в случайной клетке, не выходит за границы."""

    def __init__(self):
        """Инициализирует яблоко: задаёт цвет и случайную позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Генерирует новую случайную позицию яблока."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """Отрисовывает яблоко на экране как квадрат с границей."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка: движется, растёт, не может развернуться на 180°."""

    def __init__(self):
        """Инициализирует змейку: стартовая позиция, направление, длина."""
        start_x = (GRID_WIDTH // 2) * GRID_SIZE
        start_y = (GRID_HEIGHT // 2) * GRID_SIZE
        super().__init__((start_x, start_y), SNAKE_COLOR)

        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.eaten_apples = 0
        self.length = 1  # Добавляем атрибут length

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения, если оно задано."""
        if self.next_direction is not None:
            opposite_dir = (-self.direction[0], -self.direction[1])
            if self.next_direction != opposite_dir:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Двигает змейку на один шаг по текущему направлению."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.last = self.positions[-1]
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def check_eat_apple(self, apple):
        """Проверяет, съела ли змейка яблоко."""
        return self.get_head_position() == apple.position

    def grow(self):
        """Увеличивает длину змейки на 1 сегмент."""
        self.length += 1
        self.eaten_apples += 1  # Увеличиваем счётчик съеденных яблок

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        start_x = (GRID_WIDTH // 2) * GRID_SIZE
        start_y = (GRID_HEIGHT // 2) * GRID_SIZE
        self.position = (start_x, start_y)
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.length = 1
        self.eaten_apples = 0

    def get_current_speed(self):
        """Возвращает текущую скорость змейки."""
        base_speed = SPEED
        speed_increase = self.eaten_apples // 3
        return base_speed + speed_increase

    def draw(self, surface):
        """Отрисовывает змейку: голову, тело и затирает старый хвост."""
        # Затираем последний сегмент
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)
        # Рисуем голову
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)
        # Рисуем тело
        for position in self.positions[1:]:
            body_rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, body_rect)
            pygame.draw.rect(surface, BORDER_COLOR, body_rect, 1)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def update_game_state(snake, apple):
    """Обновляет состояние игры: движение, поедание, столкновение."""
    snake.update_direction()
    snake.move()
    if snake.check_eat_apple(apple):
        snake.grow()
        apple.randomize_position()
    head = snake.get_head_position()
    if head in snake.positions[1:]:
        snake.reset()
        apple.randomize_position()


def draw_game(surface, snake, apple):
    """Отрисовывает всё игровое поле: фон, объекты."""
    surface.fill(BOARD_BACKGROUND_COLOR)
    apple.draw(surface)
    snake.draw(surface)
    pygame.display.flip()


def main():
    """Запускает и управляет игровым циклом Змейки."""
    snake = Snake()
    apple = Apple()
    running = True
    while running:
        current_speed = snake.get_current_speed()
        clock.tick(current_speed)
        handle_keys(snake)
        update_game_state(snake, apple)
        draw_game(screen, snake, apple)


if __name__ == '__main__':
    main()
