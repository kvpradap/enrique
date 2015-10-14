import pyprind

bar = pyprind.ProgBar(10)
for i in range(0, 10):
    bar.update()

