def RGB_to_gl(RGB, p=0.9):
    ''' [255, 255, 255] -> [1, 1, 1, p] '''
    color = [round(float(i)/255., 2) for i in RGB] + [float(p)]
    return color


def main(start=[0.0, 1.0, 0, 0.8], finish=[1.0, 0.0, 0, 0.9], n=40):
    '''Returns a gradient list of (n) colors between
    two colors. Start and finish should be the array of colors '''
    s = start
    f = finish
    RGB_list = [s]

    for t in range(1, n):
        curr_vector = [
            round((s[j] + (float(t)/(n-1)) * (f[j]-s[j])), 2)
            for j in range(4)
        ]

        RGB_list.append(curr_vector)

    return RGB_list


if __name__ == '__main__':
    gradient = main([0.0, 1.0, 0.0, 0.8], [1.0, 0.0, 0.0, 0.9])
    for color in gradient:
        print(color)
