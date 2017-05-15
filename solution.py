# IMPORTS
from collections import Counter
import copy


# CONSTANTS
_CROSS = lambda A, B: [s+t for s in A for t in B]
ROWS = 'ABCDEFGHI'
COLS = '123456789'
BOX_VALS = '123456789'
BOXES = list(_CROSS(ROWS, COLS))
DIAG = False

# unit lists
_row_units = [_CROSS(r, COLS) for r in ROWS]
_column_units = [_CROSS(ROWS, c) for c in COLS]
_square_units = [_CROSS(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
_diag_units = [[ROWS[i]+COLS[::j][i] for i in range(len(ROWS))] for j in (1, -1)]

# UNITLIST: Consists of a tuple of the 27 (or 29 with diagonals) units as a tuple 
UNITLIST = {_diag: _row_units + _column_units + _square_units + _diag_units * _diag for _diag in (True, False)}
# UNITS: Dictionary mapping each box to the UNIT tuples it is in
UNITS = {_diag: dict((s, [u for u in UNITLIST[_diag] if s in u]) for s in BOXES) for _diag in (True, False)}
# PEERS: Dictionary mapping each box to its peers
PEERS = {_diag: dict((s, set(sum(UNITS[_diag][s],[]))-set([s])) for s in BOXES) for _diag in (True, False)}


assignments = []
def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return _CROSS(A, B)

def grid_values(grid, LEN_GRID=81):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == LEN_GRID, "Input grid must be a string of length 81 (9x9)"
    assert all((c in (COLS + '.')) for c in grid), "Input contains invalid characters"
    grid_list = [(BOX_VALS if (c in '.') else c) for c in grid]
    return {BOXES[i]: grid_list[i] for i in range(LEN_GRID)} 

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if not values:
        return
    width = 1+max([len(values[s]) for s in BOXES])
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in COLS))
        if r in 'CF': print(line)
    return

def eliminate(values, diag=DIAG):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    _values = copy.copy(values)
    _B = [b for b in _values.keys() if len(_values[b]) == 1]
    for _b in _B:
        _v = _values[_b]
        for _p in PEERS[diag][_b]:
            _values[_p] = _values[_p].replace(_v, '')
    return _values


def only_choice(values, diag=DIAG):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    tOUT[1]
    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    _values = copy.copy(values)
    for unit in UNITLIST[diag]:
        for digit in '123456789':
            dplaces = [b for b in unit if (digit in _values[b])]
            if len(dplaces) == 1:
                _values[dplaces[0]] = digit
    return _values

def naked_twins(values, diag=DIAG):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    _values = copy.copy(values)
    
    # Find all instances of naked twins
    _dbs = set([b for b in BOXES if (len(values[b])==2)]) # All boxes with 2 possible values
    for UNIT in UNITLIST[diag]:
        UNIT_len = len(UNIT)
        for i in range(UNIT_len-1):
            vi = values[UNIT[i]]
            for j in range(i+1, UNIT_len):
                if (values[UNIT[j]] == vi) and (UNIT[j] in _dbs):
                    v1, v2 = vi[0], vi[1]
                    for k in range(UNIT_len):
                        if k not in [i,j]:
                            _v = values[UNIT[k]]
                            _vout = _v.replace(v1, '').replace(v2, '')
                            _values[UNIT[k]] = _vout
    return _values
    
def reduce_puzzle(values, diag=DIAG):
    """
    Iterate eliminate(), only_choice(), and naked_twin(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """

    _values = copy.copy(values)
    stalled = False
    while not stalled:
        _len_i = len(''.join(_values.values()))        
        _values = eliminate(_values, diag)
        _values = only_choice(_values, diag)
        _values = naked_twins(_values, diag)
        _len_f = len(''.join(_values.values()))
        stalled = _len_i == _len_f        
    return _values

def search(values, diag=DIAG):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku."
    ARGS: values as dictionary mapping box to constraints
    Output: (VALID, values)
    """

    _val_len = [(len(_v), _b) for _b, _v in values.items()]
    _val_len.sort()
    if _val_len[0][0] == 0:
        return (False, values)
    elif _val_len[-1][0] == 1: # Solution arrived at
        return (True, values)
    else:
        i = 0
        while _val_len[i][0] <= 1:
            i += 1
        _b = _val_len[i][1]
        for _v in values[_b]:
            _values = copy.copy(values)
            _values[_b] = _v
            _values = reduce_puzzle(_values, diag)  
            OUT = search(_values, diag)
            if OUT[0]:
                return (True, OUT[1])
        values[_b] = ''
        return (False, values)
            


        

def solve(grid, diag=True):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    _values = copy.copy(values)
    
    # Constraint propogation  
    _values = reduce_puzzle(_values) # Reduce is an abssolute reduction
    # Apply constraint propogation to grid
    for _b, _v in _values.items():
        values = assign_value(values, _b, _v)
    
    OUT = search(_values, diag)
    return OUT[1]
    

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
