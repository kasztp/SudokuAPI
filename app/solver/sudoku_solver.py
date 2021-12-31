""" Sudoku board Class and solver logic. """
from copy import deepcopy


class Board:
    def __init__(self, board, size, box_size, dimensions):
        self.board = board
        self.size = size
        self.box_size = box_size
        self.dimensions = dimensions
        self.iterations = 0
        self.clues = self.set_clues()
        self.most_common_clues = self.set_most_common_clues()
        self.mask = self.create_mask()

    def __repr__(self):
        to_print = str()
        for i in range(self.size):
            if i % self.box_size == 0 and i != 0:
                to_print += '- - - - - - - - - - - -\n'

            for j in range(self.size):
                if j % self.box_size == 0 and j != 0:
                    to_print += ' | '

                if j == (self.size - 1):
                    to_print += str(self.board[i][j]) + '\n'
                else:
                    to_print += str(self.board[i][j]) + ' '
        return to_print

    def valid(self, num, pos):
        """ Check if a given value is valid for the current position. """
        # Check row
        if num in self.board[pos[0]]:
            return False

        # Check column
        if num in [item[pos[1]] for item in self.board]:
            return False

        # Check box
        box_x = pos[1] // self.box_size
        box_y = pos[0] // self.box_size

        for i in range(box_y * self.box_size, box_y * self.box_size + self.box_size):
            if num in self.board[i][box_x * self.box_size: box_x * self.box_size + self.box_size] \
                    and (i, self.board[i].index(num)) != pos:
                return False

        return True

    def find_empty(self):
        """ Find empty field on board. """
        for i, row in enumerate(self.board):
            if 0 in row:
                return i, row.index(0)  # row, col
        return None

    def find_min_empty(self):
        """ Find empty field where the number of possible valid values is the smallest. """
        def is_list(item):
            return bool(isinstance(item, list))

        min_len_list = [0, list(range(1, self.size + 1))]
        for i, row in enumerate(self.mask):
            if len(list(filter(is_list, row))) >= 1:
                sorted_sets = sorted(filter(is_list, row), key=len)
                for j, shortest in enumerate(sorted_sets):
                    if self.board[i][row.index(shortest)] == 0:
                        if len(min_len_list[1]) > len(sorted_sets[j]):
                            min_len_list[0] = i
                            min_len_list[1] = sorted_sets[j]
                            break

        if min_len_list != [0, list(range(1, self.size + 1))]:
            return min_len_list[0], self.mask[min_len_list[0]].index(min_len_list[1])  # row, col
        else:
            return self.find_empty()

    def find_min_empty_new(self) -> tuple[int, int] or None:
        """ Find empty location to be filled in Sudoku,
        where the number of possible values is optimal. """

        def not_zero_element_list(item):
            return bool(isinstance(item, list) and len(item) != 0)

        shortest_cue_lists = {}
        for y_pos, row in enumerate(self.mask):
            sorted_lists = sorted(filter(not_zero_element_list, row), key=len, reverse=True)
            if len(sorted_lists) >= 1:
                for item in sorted_lists:
                    shortest_cue_lists[(y_pos, row.index(item))] = len(sorted_lists[0])

        shortest_cue_lists = dict(sorted(shortest_cue_lists.items(), key=lambda item: item[1]))

        for coordinate in shortest_cue_lists.keys():
            if self.board[coordinate[0]][coordinate[1]] == 0:
                return coordinate[0], coordinate[1]

        return self.find_empty()

    def set_clues(self):
        """ Set clues for Board. """
        clues = []
        clue_dict = dict()
        for row in self.board:
            for number in row:
                if number != 0:
                    clues.append(number)
        for i in range(self.dimensions[0], self.dimensions[1]):
            clue_dict[i] = clues.count(i)
        return clue_dict

    def set_most_common_clues(self):
        """ Calculate most common clues on the Board. """
        mc_clues = []
        for item in sorted(self.clues.items(), key=lambda x: x[1], reverse=True):
            mc_clues.append(item[0])
        if len(mc_clues) < 9:
            missing = set(range(1, self.dimensions[1])).difference(mc_clues)
            print(f"Missing: {missing}")
            mc_clues += missing
        return mc_clues

    def create_mask(self):
        """ Create Mask of possible values for the sudoku. """
        mask = deepcopy(self.board)
        for i, row in enumerate(mask):
            if 0 in row:
                while 0 in row:
                    zero_index = row.index(0)
                    mask[i][zero_index] = set()
                    for number in range(self.dimensions[0], self.dimensions[1]):
                        if self.valid(number, (i, zero_index)):
                            mask[i][zero_index].add(number)
            else:
                for number in row:
                    if number != 0:
                        mask[i][row.index(number)] = {number}
        return mask

    def update_mask(self):
        """ Update Mask of possible values. """
        def masking(item):
            return bool(isinstance(item, set) and len(item) > 1)

        for i, row in enumerate(self.mask):
            for numbers in filter(masking, row):
                x_pos = row.index(numbers)
                to_mask = list()
                to_remove = set()
                for number in numbers:
                    if not self.valid(number, (i, x_pos)):
                        to_remove.add(number)
                for num in to_remove:
                    self.mask[i][x_pos].remove(num)
                for num in self.most_common_clues:
                    if num in self.mask[i][x_pos]:
                        to_mask.append(num)
                self.mask[i][x_pos] = to_mask

    def update_board(self):
        """ Update Board based on Mask of possible values. """
        def masking(item):
            return bool(isinstance(item, set) and len(item) == 1)

        for i, row in enumerate(self.mask):
            for number in filter(masking, row):
                x_pos = row.index(number)
                num = number.pop()
                self.board[i][x_pos] = num
                self.mask[i][x_pos] = num

    def preprocess_board(self):
        """ Preprocess Board before solving with backtracking. """
        temp_board = deepcopy(self)
        temp_board.mask = None
        passes = 0
        while temp_board.mask != self.mask:
            passes += 1
            temp_board = deepcopy(self)
            self.update_board()
            self.update_mask()

        return passes

    def solve(self):
        """ Solve Board with backtracking. """
        self.iterations += 1
        pick = self.find_min_empty_new()
        if not pick:
            return True
        else:
            row, col = pick

        for number in self.mask[row][col]:
            # ^ Only check for numbers in mask, in the order of most common cues
            if self.valid(number, (row, col)):
                self.board[row][col] = number

                if self.solve():
                    return True

                self.board[row][col] = 0

        return False

    def validate_clue(self, num, pos):
        """ Function to check if a given clue is valid for the given position in the given board. """
        # Check row
        if self.board[pos[0]].count(num) > 1:
            return False

        # Check column
        column = [item[pos[1]] for item in self.board]
        del column[pos[0]]
        if num in column:
            return False

        # Check box
        box_x = pos[1] // self.box_size
        box_y = pos[0] // self.box_size

        for i in range(box_y * self.box_size, box_y * self.box_size + self.box_size):
            if num in self.board[i][box_x * self.box_size: box_x * self.box_size + self.box_size] \
                    and (i, self.board[i].index(num)) != pos:
                return False

        return True

    def check_solvable(self):
        """ Function to check if a sudoku is possibly solvable. """
        for i, row in enumerate(self.board):
            for j, value in enumerate(row):
                if value in list(range(1, self.size + 1)):
                    if not self.validate_clue(value, (i, j)):
                        return False
        return True
