import matplotlib.pyplot
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.keep = False

    def distance_to_line(self, l1, l2):
        return distance_line_point((l1.x, l1.y), (l2.x, l2.y), (self.x, self.y))

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __repr__(self):
        return 'Point{}'.format(self.__str__())

def get_points(limit):
    c = 0
    i = 0.05
    x = []
    while c < limit:
        x.append(c)
        c += 0.005

    y = list(map(lambda i: math.exp(-i) * math.cos(2 * math.pi * i), x))
    return x, y

def distance_line_point(ls, le, point):
    x1, y1 = ls
    x2, y2 = le
    x0, y0 = point
    n1 = (y2 - y1) * x0
    n2 = (x2 - x1) * y0
    n3 = (x2 * y1)
    n4 = (y2 * x1)
    numerator = abs(n1 - n2 + n3 - n4)

    d1 = (y2 - y1) ** 2
    d2 = (x2 - x1) ** 2
    denominator = math.sqrt(d1 + d2)

    return numerator / denominator

def rdp(points, e=0.001):
    if len(points) <= 1:
        return points
    first = points.pop(0)
    last = points.pop()
    first.keep = True
    last.keep = True


    fIdx = -1
    fP = None
    fDist = 0
    for (i, p) in enumerate(points):
        dist = p.distance_to_line(first, last)
        if dist > fDist:
            fDist = dist
            fIdx = i
            fP = p
    if fDist > e:
        fP.keep = True
        result = []
        result.append(first)
        result.extend(rdp(points[:fIdx + 1], e))
        result.extend(rdp(points[fIdx:], e))
        return [p for p in result if p.keep]
    else:
        return [p for p in points if p.keep]

def main():
    x, y = get_points(5)
    matplotlib.pyplot.plot(x, y)

    points = list(map(lambda pair: Point(pair[0], pair[1]), zip(x, y)))
    simplified = rdp(points)

    x = [i.x for i in simplified]
    y = [i.y for i in simplified]

    matplotlib.pyplot.plot(x, y)

if __name__ == '__main__':
    main()
