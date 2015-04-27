# python2.7
# to python3.x change axes3d -> Axes3D
# IPython.core.display -> IPython.display
# TODO: try sys.version_info

import pandas as pd, numpy as np, random
import matplotlib.pyplot as plt, matplotlib.cm as cm
from mpl_toolkits.mplot3d import axes3d as Axes3D
import IPython.core.display as IPdisplay
import glob
from PIL import Image as PIL_Image
from images2gif import writeGif

def get_points(points):
    point_columns = ['x', 'y', 'z']
    df = pd.DataFrame(points, columns=point_columns)
    df = df.drop(labels='', axis=1)
    return df

def get_colors(color_request, length=1, color_reverse=False, default_color='r'):
    color_list = []
    if type(color_request) == list:
        color_list = color_request        
    elif type(color_request) == str:
        if len(color_request) == 1:
            color_list = [color_request]
            default_color = color_request
        elif len(color_request) > 1:
            color_map = cm.get_cmap(color_request)
            color_list = color_map([x/float(length) for x in range(length)]).tolist()
    color_list = color_list + [default_color for n in range(length-len(color_list))] if len(color_list) < length else color_list
    if color_reverse:
        color_list.reverse()
    return color_list


def get_plot_3d(points, discard_gens=1, height=8, width=10, 
                     xmin=0, xmax=1, ymin=0, ymax=1, zmin=0, zmax=1,
                     remove_ticks=True, title='', elev=25, azim=240, dist=10,
                     xlabel='Population (t)', ylabel='Population (t + 1)',
                     zlabel='Population (t + 2)', marker='.', size=5,
                     alpha=0.7, color='r', color_reverse=False, legend=False, 
                     legend_bbox_to_anchor=None):
    plots = []
    names = ['value']
    fig = plt.figure(figsize=(width, height))
    ax = fig.gca(projection='3d')
    ax.elev = elev
    ax.azim = azim
    ax.dist = dist
    ax.set_title(title)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_zlim(zmin, zmax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)  
    ax.set_zlabel(zlabel)
    if remove_ticks:  #remove all ticks if argument is True
        ax.tick_params(reset=True, axis='both', which='both', pad=0, width=0,
                       length=0, bottom='off', top='off', left='off',
                       right='off', labelbottom='off', labeltop='off',
                       labelleft='off', labelright='off')
    else:
        ax.tick_params(reset=True)
    color_list = get_colors(color, 1, color_reverse)
    xyz = points
    plots.append(ax.scatter(xyz['x'], xyz['y'], xyz['z'], 
                            marker=marker, c=color_list[0],
                            edgecolor=color_list[0], s=size, alpha=alpha))
    if legend:
        ax.legend(plots, names, loc=1, frameon=True,
                  framealpha=1, bbox_to_anchor=legend_bbox_to_anchor)        
    return fig, ax


def main(points):
    gif_filename = 'test-plot-3d'
    pops = get_points(points)
    fig, ax = get_plot_3d(pops, remove_ticks=False)

    steps = 36 # create 36 frames for the animated gif
    min_dist = 7.
    max_dist = 10.
    dist_range = np.arange(min_dist, max_dist, (max_dist-min_dist)/steps)
    min_elev = 10.
    max_elev = 60.
    elev_range = np.arange(max_elev, min_elev, (min_elev-max_elev)/steps)

    # now create the individual frames that will be combined later into the animation
    for azimuth in range(0, 360, 360/steps):
        ax.azim = float(azimuth/3.)
        ax.elev = elev_range[int(azimuth/(360./steps))]
        ax.dist = dist_range[int(azimuth/(360./steps))]
        
        fig.suptitle('random points')
        plt.savefig('images/' + gif_filename + '/img' +
                    str(azimuth).zfill(3) + '.png')

    plt.close() # don't display the static plot...
    
    # ...instead, create an animated gif of all the frames, then display it inline
    list_images = sorted(glob.glob('images/'+gif_filename+'/*.png'))
    images = [PIL_Image.open(image) for image in list_images]
    file_path_name = 'images/' + gif_filename + '.gif'
    writeGif(file_path_name, images, duration=0.2)

    print('Done!')
