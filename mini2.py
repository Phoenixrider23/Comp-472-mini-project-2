import copy
from array import *

# <= is \u2190
# ^ is \u2191
# => is \u2192
# v is \u2193

previously_found_states = {}

empty_board = [['.','.','.','.','.','.'],
            ['.','.','.','.','.','.'],
            ['.','.','.','.','.','.'],
            ['.','.','.','.','.','.'],
            ['.','.','.','.','.','.'],
            ['.','.','.','.','.','.']]


def board_matrix_to_string(board_matrix):
    board_string = ""
    for i in range(len(board_matrix)):
        for j in range(len(board_matrix[i])):
            board_string += board_matrix[i][j]
    return board_string

class car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.length = 1
        self.horizontal = False
        self.gas = 99
    
    def update(self, new_horizontal):
        self.length += 1
        self.horizontal = new_horizontal
    
    def set_gas(self, gas):
        self.gas = gas



class state:
    def __init__(self, previous_move):
        self.move_number = 0
        self.previous_move = previous_move
        self.moves_that_got_us_there = ""
        self.possible_future_moves = {}
        self.exit = [2, 5]
        self.cars = {}
        self.board_string = ""
        self.board_matrix = copy.deepcopy(empty_board)


    def update_new_state(self, move_number, moves_that_got_us_there, cars, board_string, board_matrix):
        self.move_number = move_number
        self.moves_that_got_us_there = moves_that_got_us_there
        self.cars = cars
        self.board_matrix = board_matrix
        self.board_string = board_string


    def read_input_string(self, state_string):
        param = state_string.split(' ')
        for j in range(len(param)):
            if j == 0:
                self.board_string = param[0]
                for i in range(len(param[0])):
                    id = state_string[i]
                    x = i % 6
                    y = i // 6
                    self.board_matrix[y][x] = id
                    if (id != '.') and not(id in self.cars):
                        new_car = car(x, y)
                        self.cars[id] = new_car
                    elif (id in self.cars):
                        horizontal = (previous_character == id)
                        self.cars[id].update(horizontal)
                    previous_character = id
            else:
                car_id = param[j][0]
                gas_value = int(param[j][1])
                self.cars[car_id].set_gas(gas_value)
        print(self.board_matrix)


    def print_cars(self):
        for car in self.cars:
            print(car + 
                    "= x: " + str(self.cars[car].x) + 
                    ", y: " + str(self.cars[car].y) + 
                    ", length: " + str(self.cars[car].length) +
                    ", horizontal: " + str(self.cars[car].horizontal) + 
                    ", gas: " + str(self.cars[car].gas))


    def next_board_no_exit(self, car_id, gas_remaining, new_x, new_y):
        next_board_cars = copy.deepcopy(self.cars)
        next_board_cars[car_id].x = new_x
        next_board_cars[car_id].y = new_y
        next_board_cars[car_id].gas = gas_remaining
        return next_board_cars


    def next_board_with_exit(self, car_id):
        next_board_cars = copy.deepcopy(self.cars)
        next_board_cars.pop(car_id)
        return next_board_cars


    def next_state_creation(self, next_board_cars, move):
        board_string = ""
        board_matrix = copy.deepcopy(empty_board)

        for car in next_board_cars:
            if next_board_cars[car].horizontal == True:
                for i in range(next_board_cars[car].length):
                    board_matrix[next_board_cars[car].y][next_board_cars[car].x + i] = car
            else:
                for i in range(next_board_cars[car].length):
                    board_matrix[next_board_cars[car].y + i][next_board_cars[car].x] = car

        board_string = board_matrix_to_string(board_matrix)

        if not(board_string in previously_found_states) or (previously_found_states[board_string].move_number > (self.move_number + 1)):
            move_sequence = ""
            if self.moves_that_got_us_there == "":
                move_sequence = move
            else: move_sequence = self.moves_that_got_us_there + "; " + move

            new_state = state(self)
            new_state.update_new_state(self.move_number + 1, move_sequence, next_board_cars, board_string, board_matrix)
            self.possible_future_moves[move] = new_state
            previously_found_states[board_string] = new_state


    def check_moves(self):
        for car in self.cars:
            move = ""
            if self.cars[car].horizontal == True:
                # check right
                check = self.cars[car].x + self.cars[car].length
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                while (check < 5 and blocked == False and gas > 0):
                    check += 1
                    if self.board_matrix[self.cars[car].y][check] == '.':
                        gas -= 1
                        move = car + " \u2192 " + str(check - self.cars[car].x - self.cars[car].length)
                        print(move)
                        # special case where car leaves parking
                        if [self.cars[car].y, check] == self.exit:
                            if car == "A":
                                print("Solution found!")
                                next_board_cars = self.next_board_with_exit(car)
                                self.next_state_creation(next_board_cars, move)
                                print(self.possible_future_moves[move].moves_that_got_us_there)
                            else:
                                next_board_cars = self.next_board_with_exit(car)
                                self.next_state_creation(next_board_cars, move)
                        else:
                            next_board_cars = self.next_board_no_exit(car, gas, check, self.cars[car].y)
                            self.next_state_creation(next_board_cars, move)
                    else: blocked = True

                # check left
                check = self.cars[car].x
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                while (check > 0 and blocked == False):
                    check -= 1
                    if self.board_matrix[self.cars[car].y][check] == '.':
                        move = car + " \u2190 " + str(self.cars[car].x - check)
                        gas -= 1
                        next_board_cars = self.next_board_no_exit(car, gas, check, self.cars[car].y)
                        self.next_state_creation(next_board_cars, move)
                    else: blocked = True
            # car is vertical
            else:
                # check above
                check = self.cars[car].y + self.cars[car].length
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                while (check < 5 and blocked == False and gas > 0):
                    check += 1
                    if self.board_matrix[check][self.cars[car].x] == '.':
                        move = car + " \u2191 " + str(self.cars[car].y - check)
                        gas -= 1
                        next_board_cars = self.next_board_no_exit(car, gas, self.cars[car].x, check)
                        self.next_state_creation(next_board_cars, move)
                    else: blocked = True

                # check below
                check = self.cars[car].y
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                while (check > 0 and blocked == False and gas > 0):
                    check -= 1
                    if self.board_matrix[check][self.cars[car].x] == '.':
                        move = car + " \u2193 " + str(check - self.cars[car].y)
                        gas -= 1
                        next_board_cars = self.next_board_no_exit(car, gas, self.cars[car].x, check)
                        self.next_state_creation(next_board_cars, move)
                    else: blocked = True



test_puzzle = "............AA......................"

new_state = state(None)
new_state.read_input_string(test_puzzle)
new_state.print_cars()
new_state.check_moves()
