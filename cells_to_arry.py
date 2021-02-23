
def cellsto2darray(cells, col):  # colは列の数
    cells2d = []
    for i in range(len(cells) // col):
        cells2d.append(cells[i * col:(i + 1) * col])
    return cells2d

def cellsto1darray(cells2d):
    cells1d = []
    for cells in cells2d:
        cells1d.extend(cells)
    return cells1d
