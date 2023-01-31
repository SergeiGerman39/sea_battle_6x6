
from random import randint

# класс точки поля, сравнения двух точек
# и метод для отображения точек
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

# исключения
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы выстрелилили за пределы игрового поля! " \
               "Попробуйте сделать это ещё раз!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "В эту клетку уже стреляли!" \
               "Попробуйте сделать ещё раз!"

class BoardWrongShipException(BoardException):
    pass

# класс Корабль
# длина, нос корабля, ориентация на игровом поле
# количество жизней  = длина корабля
class Ship:
    def __init__(self, bow_ship, length, orient):
        self.bow_ship = bow_ship
        self.length = length
        self.orient = orient
        self.lives = length
# создаем метод-свойство, который будет в списке хранить точки корабля
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            current_x = self.bow_ship.x
            current_y = self.bow_ship.y

            if self.orient == 0:
                current_x += i

            elif self.orient == 1:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots


# игровое поле

class Board:
    def __init__(self, hidden = False, size = 6):
        self.size = size
        self.hidden = hidden

        self.count = 0 # кол-во пораженных кораблей

        self.field =[['O'] * size for _ in range(size)] # сетка

        self.buzy = [] # список занятых точек
        self.ships = [] # список кораблей доски

# размещения корабля. Проверяем точки корабля
# не выходят за границы игрового поля
# и точка не занята
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.buzy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.buzy.append(d)

        self.ships.append(ship)
        self.contour(ship)

# контур корабля, чтобы точки кораблей не пересекались
    def contour(self, ship, verb = False):
        #список всех точек вокруг корабля
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)
                ]
        # все сдвиги вверх/вниз/по диагонали
        for d in ship.dots:
            for dx, dy in near:
                current = Dot(d.x + dx, d.y + dy)
                if not(self.out(current)) and current not in self.buzy:
                    if verb:
                        self.field[current.x][current.y] = "."
                    self.buzy.append(current)

# игровое поле
    def __str__(self):
        res = ''
        res += "   | 1  | 2  | 3 | 4  | 5  | 6  |"
        for i, row in enumerate(self.field):
            res += f"\n{i +1} | " + " | ".join(row) + " |"

        if self.hidden:
            res = res.replace('■', 'O')
        return res

#  проверка по координатам, корабль находится в игровом поле
    def out(self,d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

# стрельба
# попадает ли точка в поле и не занята ли она
# если не занята,  добавляем в занятые и проверяем  не попала ли она в корабль
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.buzy:
            raise BoardUsedException()

        self.buzy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print('Убит!')
                    return False
                else:
                    print('Ранен!')
                    return True

        self.field[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def begin(self):
        self.buzy = [] # обнуляем список

# Игрок
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class Ai(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d

class User(Player):
    def ask(self):
        while True:
            coordinates = input('Ваш ход:  ').split()

            if len(coordinates) != 2:
                print('Введите две координаты')
                continue

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите целые числа')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

# Игра
class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        comp = self.random_board()
        comp.hidden = True

        self.ai = Ai(comp, pl)
        self.us = User(pl, comp)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        vse_dliny = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for length in vse_dliny:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board


    def greet(self):
        print(' Добро пожаловать ')
        print('      в игру      ')
        print('  МОРСКОЙ БОЙ')
        print('-'*23)
        print('формат ввода – целые числа ')
        print ('     через пробел    ')
        print(' x – по горизонтали')
        print(' у – по вертикали')
        print('-'*25)

    def loop(self):
        num = 0
        while True:
            print('~'*16)
            print('Игровое поле игрока: ')
            print(self.us.board)
            print('~'*23)
            print('Игровое поле компьютера: ')
            print(self.ai.board)
            print('~'*22)
            if num % 2 == 0:
                print('Ваш ход! Ждём приказа')
                repeat = self.us.move()
            else:
                print('Ход компьютера')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('       ~~~~~      ')
                print('ТЫ ПОБЕДИЛ!')
                break

            if self.us.board.count == 7:
                print('       ~~~~~      ')
                print('ТЫ ПРОИГРАЛ =(')
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

