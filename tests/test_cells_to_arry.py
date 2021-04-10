import sys

# main.pyをimportするのに上位階層に移動する必要がある
from pathlib import Path
sys.path.append(str(Path('__file__').resolve().parent))

import cells_to_arry

def test_cellsto2darray():
    '''
    1次元配列を2次元の配列に変換する
    '''
    # cells_to_arry.cellsto2darray(cells, col)


def test_cellsto1darray():
    '''
    1次元配列を2次元の配列に変換する
    '''
    # cells_to_arry.cellsto1darray(cells2d)
