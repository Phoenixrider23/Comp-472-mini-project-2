import copy
import time
from array import *

################################
# Global variables and Methods #
################################

global open_list
open_list = []
global tmp_open_list
tmp_open_list = []
global closed_list
closed_list = {}
global solution_found
solution_found = False
global solution_board_state
solution_board_state = []

global heuristic
heuristic = ""


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

def string_to_6x6_string(board_string):
    board_string_6x6 = ""
    for i in range(36):
        if (i+1)%6 == 0:
            board_string_6x6 = board_string_6x6 + board_string[i] + "\n"
        else:
            board_string_6x6 = board_string_6x6 + board_string[i]
    return board_string_6x6


#############
# Car Class #
#############

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


##############################
# State (of the Board) Class #
##############################

class state:
    def __init__(self, previous_move):
        self.f_n = 0
        self.g_n = 0
        self.h_n = 0
        self.gas_consumption = 0
        self.previous_move = previous_move
        self.move = ""
        self.moves_that_got_us_there = ""
        self.possible_future_moves = {}
        self.exit = [2, 5]
        self.cars = {}
        self.board_string = ""
        self.board_matrix = copy.deepcopy(empty_board)


    def update_new_state(self, f_n, g_n, h_n, moves_that_got_us_there, cars, board_string, board_matrix, move):
        self.f_n = f_n
        self.g_n = g_n
        self.h_n = h_n
        self.moves_that_got_us_there = moves_that_got_us_there
        self.cars = cars
        self.board_matrix = board_matrix
        self.board_string = board_string
        self.move = move


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


    def gas_remaining_calc(self):
        s = ""
        for car in self.cars:
            if self.cars[car].gas != 99:
                s = s + " " + car + str(self.cars[car].gas)
        return s


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


    def h1_h3_calc(self, board_matrix, param_lambda):
        cars_blocking = {}
        h_n = 0
        i = 5
        while ((board_matrix[2][i] != 'A') and (i > 0)):
            if board_matrix[2][i] != '.':
                cars_blocking[board_matrix[2][i]] = True
            i -= 1
        h_n = len(cars_blocking)
        return h_n * param_lambda

    def h2_h4_calc(self, board_matrix, param_lambda):
        h_n = 0
        i = 5
        while ((board_matrix[2][i] != 'A') and (i > 0)):
            if board_matrix[2][i] != '.':
                h_n += 1
            i -= 1
        return h_n * param_lambda


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


        if not(board_string in closed_list) or \
            (closed_list[board_string].g_n > (self.g_n + 1)) or \
                (closed_list[board_string].g_n == (self.g_n + 1) and \
                    closed_list[board_string].gas_consumption > (self.gas_consumption)):
            move_sequence = ""
            if self.moves_that_got_us_there == "":
                move_sequence = move
            else:
                move_sequence = self.moves_that_got_us_there + "; " + move

            global heuristic
            if heuristic == "h1":
                h_n = self.h1_h3_calc(board_matrix, 1)
            elif heuristic == "h2":
                h_n = self.h2_h4_calc(board_matrix, 1)
            elif heuristic == "h3":
                h_n = self.h1_h3_calc(board_matrix, 3)
            elif heuristic == "h4":
                h_n = self.h2_h4_calc(board_matrix, 3)
            else:
                h_n = 0


            new_state = state(self)
            new_state.update_new_state(self.g_n + h_n + 1, self.g_n + 1, h_n, move_sequence, next_board_cars, board_string, board_matrix, move)
            closed_list[board_string] = new_state
            self.possible_future_moves[move] = new_state


    def check_moves(self):
        for car in self.cars:
            move = ""
            if self.cars[car].horizontal == True:
                # check right
                check = self.cars[car].x + self.cars[car].length
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                spaces = 1
                while (check <= 5 and blocked == False and gas > 0):
                    if self.board_matrix[self.cars[car].y][check] == '.':
                        gas -= 1
                        move = car + " right " + str(spaces)
                        # special case where car leaves parking
                        if [self.cars[car].y, check] == self.exit:
                            if car == "A":
                                next_board_cars = self.next_board_with_exit(car)
                                self.next_state_creation(next_board_cars, move)

                                global solution_found
                                solution_found = True
                                global solution_board_state
                                solution_board_state.append(self.possible_future_moves[move])

                            else:
                                next_board_cars = self.next_board_with_exit(car)
                                self.next_state_creation(next_board_cars, move)
                        else:
                            next_board_cars = self.next_board_no_exit(car, gas, self.cars[car].x + spaces, self.cars[car].y)
                            self.next_state_creation(next_board_cars, move)
                    else:
                        blocked = True
                    check += 1
                    spaces += 1

                # check left
                check = self.cars[car].x - 1
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                spaces = 1
                while (check >= 0 and blocked == False and gas > 0):
                    if self.board_matrix[self.cars[car].y][check] == '.':
                        move = car + " left " + str(spaces)
                        gas -= 1
                        next_board_cars = self.next_board_no_exit(car, gas, check, self.cars[car].y)
                        self.next_state_creation(next_board_cars, move)
                    else:
                        blocked = True
                    check -= 1
                    spaces += 1

            # car is vertical
            else:
                # check below
                check = self.cars[car].y + self.cars[car].length
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                spaces = 1
                while (check <= 5 and blocked == False and gas > 0):
                    if self.board_matrix[check][self.cars[car].x] == '.':
                        move = car + " down " + str(spaces)
                        gas -= 1
                        next_board_cars = self.next_board_no_exit(car, gas, self.cars[car].x, self.cars[car].y + spaces)
                        self.next_state_creation(next_board_cars, move)
                    else:
                        blocked = True
                    check += 1
                    spaces += 1
                
                # check above
                check = self.cars[car].y - 1
                blocked = False
                gas = copy.deepcopy(self.cars[car].gas)
                spaces = 1
                while (check >= 0 and blocked == False and gas > 0):
                    if self.board_matrix[check][self.cars[car].x] == '.':
                        move = car + " up " + str(spaces)
                        gas -= 1
                        next_board_cars = self.next_board_no_exit(car, gas, self.cars[car].x, check)
                        self.next_state_creation(next_board_cars, move)
                    else:
                        blocked = True
                    check -= 1
                    spaces += 1



################
# Main Program #
################


input = open("input.txt", "r")
spreadsheet = open("spreadsheet.csv", "w")
spreadsheet.write("Puzzle Number, Algorithm, Length of Solution, Length of Search Path, Number of States Seen, Execution Time\n")

puzzle_number = 0

lines = input.readlines()
input.close()

for line in lines:
    if line.strip() == "":
        pass
    elif line.startswith("#") == True:
        pass
    else:
        puzzle_number += 1
        puzzle = line.strip()

        #######
        # UCS #
        #######

        heuristic = "N/A"

        print("Searching solution for puzzle " + str(puzzle_number))

        output = open("ucs-sol-" + str(puzzle_number) + ".txt", "w")
        output.write("Initial board configuration: " + puzzle + "\n\n")
        output.write(string_to_6x6_string(puzzle) + "\n")
        output.write("Car fuel available: ")

        search = open("ucs-search-" + str(puzzle_number) + ".txt", "w")
        search.write("f(n) g(n) h(n) State of the Board\n")

        open_list = []
        tmp_open_list = []
        closed_list = {}
        solution_found = False
        solution_board_state = []

        new_state = state(None)
        new_state.read_input_string(puzzle)

        i = 1
        for car_id in new_state.cars:
            if i < len(new_state.cars):
                output.write(car_id + ": " + str(new_state.cars[car_id].gas) + ", ")
            else:
                output.write(car_id + ": " + str(new_state.cars[car_id].gas) + "\n")
            i += 1

        start_time = time.time()
        open_list.append(new_state)

        length_of_search = 0

        while (len(open_list) > 0 and solution_found == False):
            length_of_search += 1

            current_state = open_list.pop(0)
            search.write(str(current_state.f_n) +" "+ str(current_state.g_n) + " " \
                + str(current_state.h_n) + " " + current_state.board_string + " " + current_state.gas_remaining_calc() + "\n")
            current_state_children = []
            current_state.check_moves()
            current_state_children = current_state.possible_future_moves.values()
            tmp_open_list.extend(current_state_children)

            if len(open_list) == 0:
                tmp_open_list.sort(key=lambda x: x.gas_consumption)
                open_list.extend(tmp_open_list)
                tmp_open_list.clear()

        stop_time = time.time() - start_time

        if solution_found == False:
            spreadsheet.write(str(puzzle_number) + ", " + puzzle + ", UCS, " \
                + "No solution found, " + str(length_of_search) + ", " + str(len(closed_list)) + ", " + str(stop_time) + "\n")
            output.write("Runtime: " + str(stop_time) + " seconds\n")
            output.write("Search path length: " + str(len(closed_list)) + "\n")
            output.write("There is no solution for this puzzle.")

        else: 
            spreadsheet.write(str(puzzle_number) + ", " + puzzle + ", UCS, " \
                + str(solution_board_state[0].g_n) + ", " + str(length_of_search) + ", " + str(len(closed_list)) + ", " + str(stop_time) + " seconds\n")
            output.write("Runtime: " + str(stop_time) + "\n")
            output.write("Search path length: " + str(len(closed_list)) + "\n")
            output.write("Solution path: " + solution_board_state[0].moves_that_got_us_there + "\n\n")

            big_string = solution_board_state[0].move + "\t" + solution_board_state[0].board_string + " " + solution_board_state[0].gas_remaining_calc()
            parent_pointer = solution_board_state[0].previous_move
            while parent_pointer.previous_move != None:
                big_string = parent_pointer.move + "\t" + parent_pointer.board_string + " " + parent_pointer.gas_remaining_calc() + "\n" + big_string
                parent_pointer = parent_pointer.previous_move
            
            output.write(big_string)
            output.write("\n\n" + string_to_6x6_string(solution_board_state[0].board_string))
        
        output.close()


        ########
        # GBFS #
        ########

        for i in range(4):
            heuristic = "h" + str(i + 1)

            print("Searching solution for puzzle " + str(puzzle_number))

            output = open("gbfs-" + heuristic +"-sol-" + str(puzzle_number) + ".txt", "w")
            output.write("Initial board configuration: " + puzzle + "\n\n")
            output.write(string_to_6x6_string(puzzle) + "\n")
            output.write("Car fuel available: ")

            search = open("gbfs-" + heuristic +"-search-" + str(puzzle_number) + ".txt", "w")
            search.write("f(n), g(n), h(n), State of the Board\n")

            open_list = []
            closed_list = {}
            solution_found = False
            solution_board_state = []

            new_state = state(None)
            new_state.read_input_string(puzzle)

            i = 1
            for car_id in new_state.cars:
                if i < len(new_state.cars):
                    output.write(car_id + ": " + str(new_state.cars[car_id].gas) + ", ")
                else:
                    output.write(car_id + ": " + str(new_state.cars[car_id].gas) + "\n")
                i += 1

            start_time = time.time()
            open_list.append(new_state)

            length_of_search = 0

            while (len(open_list) > 0 and solution_found == False):
                length_of_search += 1
                
                current_state = open_list.pop(0)
                search.write(str(current_state.f_n) +" "+ str(current_state.g_n) + " " \
                    + str(current_state.h_n) + " " + current_state.board_string + " " + current_state.gas_remaining_calc() + "\n")
                current_state_children = []
                current_state.check_moves()
                current_state_children = current_state.possible_future_moves.values()
                open_list.extend(current_state_children)

                open_list.sort(key=lambda x: x.h_n)

                length_of_search += 1

            stop_time = time.time() - start_time

            if solution_found == False:
                spreadsheet.write(str(puzzle_number) + ", " + puzzle + ", GBFS-" + heuristic + ", " \
                    + "No solution found, " + str(length_of_search) + ", " + str(len(closed_list)) + ", " + str(stop_time) + "\n")
                output.write("Runtime: " + str(stop_time) + " seconds\n")
                output.write("Search path length: " + str(len(closed_list)) + "\n")
                output.write("No solution was found.")

            else: 
                spreadsheet.write(str(puzzle_number) + ", " + puzzle + ", GBFS-" + heuristic + ", " \
                    + str(solution_board_state[0].g_n) + ", " + str(length_of_search) + ", " + str(len(closed_list)) + ", " + str(stop_time) + " seconds\n")
                output.write("Runtime: " + str(stop_time) + "\n")
                output.write("Search path length: " + str(len(closed_list)) + "\n")
                output.write("Solution path: " + solution_board_state[0].moves_that_got_us_there + "\n\n")

                big_string = solution_board_state[0].move + "\t" + solution_board_state[0].board_string + " " + solution_board_state[0].gas_remaining_calc()
                parent_pointer = solution_board_state[0].previous_move
                while parent_pointer.previous_move != None:
                    big_string = parent_pointer.move + "\t" + parent_pointer.board_string  + " " + parent_pointer.gas_remaining_calc() + "\n" + big_string
                    parent_pointer = parent_pointer.previous_move
                
                output.write(big_string)
                output.write("\n\n" + string_to_6x6_string(solution_board_state[0].board_string))
            
            output.close()

        ########
        # A/A* #
        ########

        for i in range(4):
            heuristic = "h" + str(i + 1)

            print("Searching solution for puzzle " + str(puzzle_number))

            output = open("a-" + heuristic +"-sol-" + str(puzzle_number) + ".txt", "w")
            output.write("Initial board configuration: " + puzzle + "\n\n")
            output.write(string_to_6x6_string(puzzle) + "\n")
            output.write("Car fuel available: ")

            search = open("a-" + heuristic +"-search-" + str(puzzle_number) + ".txt", "w")
            search.write("f(n), g(n), h(n), State of the Board\n")

            open_list = []
            closed_list = {}
            solution_found = False
            solution_board_state = []

            new_state = state(None)
            new_state.read_input_string(puzzle)

            i = 1
            for car_id in new_state.cars:
                if i < len(new_state.cars):
                    output.write(car_id + ": " + str(new_state.cars[car_id].gas) + ", ")
                else:
                    output.write(car_id + ": " + str(new_state.cars[car_id].gas) + "\n")
                i += 1

            start_time = time.time()
            open_list.append(new_state)

            length_of_search = 0

            while (len(open_list) > 0 and solution_found == False):
                length_of_search += 1

                current_state = open_list.pop(0)
                search.write(str(current_state.f_n) +" "+ str(current_state.g_n) + " " \
                    + str(current_state.h_n) + " " + current_state.board_string + " " + current_state.gas_remaining_calc() + "\n")
                current_state_children = []
                current_state.check_moves()
                current_state_children = current_state.possible_future_moves.values()
                open_list.extend(current_state_children)

                open_list.sort(key=lambda x: x.f_n)

            stop_time = time.time() - start_time

            if solution_found == False:
                spreadsheet.write(str(puzzle_number) + ", " + puzzle + ", A-" + heuristic + ", " \
                    + "No solution found, " + str(length_of_search) + ", " + str(len(closed_list)) + ", " + str(stop_time) + "\n")
                output.write("Runtime: " + str(stop_time) + " seconds\n")
                output.write("Search path length: " + str(len(closed_list)) + "\n")
                output.write("No solution was found.")

            else: 
                spreadsheet.write(str(puzzle_number) + ", " + puzzle + ", A-" + heuristic + ", " \
                    + str(solution_board_state[0].g_n) + ", " + str(length_of_search) + ", " + str(len(closed_list)) + ", " + str(stop_time) + " seconds\n")
                output.write("Runtime: " + str(stop_time) + "\n")
                output.write("Search path length: " + str(len(closed_list)) + "\n")
                output.write("Solution path: " + solution_board_state[0].moves_that_got_us_there + "\n\n")

                big_string = solution_board_state[0].move + "\t" + solution_board_state[0].board_string + " " + solution_board_state[0].gas_remaining_calc()
                parent_pointer = solution_board_state[0].previous_move
                while parent_pointer.previous_move != None:
                    big_string = parent_pointer.move + "\t" + parent_pointer.board_string + " " + parent_pointer.gas_remaining_calc() + "\n" + big_string
                    parent_pointer = parent_pointer.previous_move
                
                output.write(big_string)
                output.write("\n\n" + string_to_6x6_string(solution_board_state[0].board_string))
            
            output.close()
