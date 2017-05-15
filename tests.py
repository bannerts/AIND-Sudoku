# -*- coding: utf-8 -*-
from solution import *







if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    g = grid_values(diag_sudoku_grid)
    g1 = solve(diag_sudoku_grid, True)

    display(g)    
    display(g1)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')