## cellsto2darray, cellsto1darryaについて
cellsto2darray, cellsto1darryaに関してはこのqiitaを使った
https://qiita.com/yH3PO4/items/6517481b1e7128ca7b36

範囲指定でスプレッドシートから得たCellオブジェクトは、複数列に渡るものであっても一次元配列に入っています。配列の順序は以下の通りです。

行\列	A	B
1	cells[0]	cells[1]
2	cells[2]	cells[3]
3	cells[4]	cells[5]

以下のコードで二次元配列に整形して使いやすくできます。

```
def cellsto2darray(cells, col):  # colは列の数
    cells2d = []
    for i in range(len(cells) // col):
        cells2d.append(cells[i * col:(i + 1) * col])
    return cells2d
```

ただしupdate_cellsするときには一次元配列に戻さないといけません。戻すときは次のようにします。
```
def cellsto1darray(cells2d):
    cells1d = []
    for cells in cells2d:
        cells1d.extend(cells)
    return cells1d
```
