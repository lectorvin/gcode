# python2.7
# to python3.x change axes3d -> Axes3D

import os
import sys
import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import axes3d as Axes3D
from PIL import Image as PIL_Image
from images2gif import writeGif


def get_points(points):
    """ Return DataFrame from points columns - [x, y, z] """
    point_columns = ['x', 'y', 'z']
    df = pd.DataFrame(points, columns=point_columns)
    try:
        df = df.drop(labels='', axis=1)
    except:
        pass
    return df


def get_plot_3d(points, height=8, width=10, remove_ticks=True,
                elev=25, azim=240, dist=10, size=5, alpha=0.7, color='r'):
    """
    Create 3d image from points

    Parameters
    ----------
    points : DataFrame
        DataFrame with points, columns - [x, y, z].
    height : float, optional
        height of plot in inches.
    width : float, optional
        width of plot in inches.
    remove_ticks : bool, optional
        Default `True`. Remove all ticks.
    elev : int, optional
        Elevation of image, default - 25.
    azim : float, optional
        Azimuth of image, default - 240.
    dist : int, optional
        Distance of the eye viewing point, default - 10.
    size : float, optional
        Size of image.
    alpha : float or None, optional
        Alpha value for the patches.
    color : string or sequence of strings, optional
        Color, will be used in image.

    Return
    ------
    fig : matplotlib.pyplot.figure
        Created 3d image.
    ax : fig.gca
        Subplot of fig.
    """
    xmax = points['x'].max()
    ymax = points['y'].max()
    zmax = points['z'].max()
    xmin = points['x'].min()
    ymin = points['y'].min()
    zmin = points['z'].min()

    plots = []
    names = ['value']
    fig = plt.figure(figsize=(width, height))
    ax = fig.gca(projection='3d')
    ax.elev = elev
    ax.azim = azim
    ax.dist = dist
    ax.set_title('')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_zlim(zmin, zmax)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    if remove_ticks:  # remove all ticks if argument is True
        ax.tick_params(reset=True, axis='both', which='both', pad=0, width=0,
                       length=0, bottom='off', top='off', left='off',
                       right='off', labelbottom='off', labeltop='off',
                       labelleft='off', labelright='off')
    else:
        ax.tick_params(reset=True)
    color_list = [color]
    xyz = points
    plots.append(ax.scatter(xyz['x'], xyz['y'], xyz['z'],
                            marker='8', c=color_list[0],
                            edgecolor=color_list[0], s=size, alpha=alpha))
    return fig, ax


def main(points, show=True, fl=None):
    """
    Parameters
    ----------
    points : DataFrame
        DataFrame with points, columns - [x, y, z].
    show : boolean, optional
        Show image as plot if true, else save gif-file
    fl : string, optional
        Path to file.

    Return
    ------
    Nothing, but create and save image
    """
    gif_filename = fl
    pops = get_points(points)
    fig, ax = get_plot_3d(pops, remove_ticks=False)

    steps = 36     # create 36 frames for the animated gif
    min_dist = 7.
    max_dist = 10.
    dist_range = np.arange(min_dist, max_dist, (max_dist-min_dist)/steps)
    min_elev = 10.
    max_elev = 60.
    elev_range = np.arange(max_elev, min_elev, (min_elev-max_elev)/steps)

    if show:
        plt.show()
    else:
        # now create the individual frames that will be combined later
        # into the animation
        for azimuth in range(0, 360, 360/steps):
            ax.azim = float(azimuth/3.)
            ax.elev = elev_range[int(azimuth/(360./steps))]
            ax.dist = dist_range[int(azimuth/(360./steps))]

            if not os.path.exists(gif_filename):
                os.makedirs(gif_filename)
            fig.suptitle('elev=' + str(round(ax.elev,1)) + ', azim=' +
                        str(round(ax.azim,1)) + ', dist=' + str(round(ax.dist,1)))
            plt.savefig(gif_filename + '/img' + str(azimuth).zfill(3) + '.png')

        plt.close()

        list_images = sorted(glob.glob(gif_filename+'/*.png'))
        images = [PIL_Image.open(image) for image in list_images]
        file_path_name = gif_filename + '.gif'
        writeGif(file_path_name, images, duration=0.2)
