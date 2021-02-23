import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import axes3d, Axes3D
import re

from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
from matplotlib.markers import MarkerStyle
from matplotlib.patches import Rectangle


from core.geometry import *
from core.surfaces import *
from utils.misc import Matrix2D

grid_plot_params = {
    'show_RIS_ids'   : False,
    'scale'          : 50,
    'color_by_height': True,
    'RIS_color'      : 'black',
    'RIS_symbol'     : 's', # square
    'TX_color'       : 'blue',
    'TX_symbol'      : 'D', # diamond
    'RX_color'       : 'green',
    'RX_symbol'      : 'o', # circle
    'xlims'          : None, # tuple of (min,max)
    'ylims'          : None, # tuple of (min, max)
    'grid'           : True,
    'element_color'  : 'black',
    'alpha'          : 0.7,
    '3D'             : False,
}











def _fix_height_legend(handles, labels, heights, params):
    for i in range(len(handles)):
        handles[i]._marker = MarkerStyle('o', 'full')

    label_numbers = np.array(list(map(lambda s: float(re.sub("[^0-9]", "", s)), labels)))
    label_numbers = (label_numbers-params['min_markersize'])/params['scale']
    #label_numbers = reverse_normalize(label_numbers, heights.min(), heights.max())
    labels = list(map(lambda n: '$\\mathdefault{'+str(n)+"}$", label_numbers))
    return handles, labels

def mscatter(x,y, z=None, ax=None, m=None, **kw):
    import matplotlib.markers as mmarkers
    if not ax: ax=plt.gca()

    if z is None:
        sc = ax.scatter(x,y,**kw)
    else:
        sc = ax.scatter(x,y,z, **kw)
    if (m is not None) and (len(m)==len(x)):
        paths = []
        for marker in m:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(
                        marker_obj.get_transform())
            paths.append(path)
        sc.set_paths(paths)
    return sc



def plot_positions(RIS_positions, TX_positions, RX_positions, ax=None, params: DefaultDict=None):
    if params is None: params = grid_plot_params

    if ax is None:
        if params['3D']:
            matplotlib.use('TkAgg')
            fig = plt.figure()
            ax = Axes3D(fig)
        else:
            fig, ax = plt.subplots()

    num_RIS = RIS_positions.shape[0]
    num_TX = TX_positions.shape[0]
    num_RX = RX_positions.shape[0]

    all_coords = np.vstack([RIS_positions, TX_positions, RX_positions])
    labels     = [params['RIS_symbol']]*num_RIS + [params['TX_symbol']]*num_TX + [params['RX_symbol']]*num_RX
    sizes      = [params['scale']]*all_coords.shape[0]


    if params['color_by_height'] and not params['3D']:
        params['RIS_color'] = 'k'
        params['TX_color'] = 'k'
        params['RX_color'] = 'k'
        colors = all_coords[:,2]
    else:
        colors = [params['RIS_color']] * num_RIS + \
                 [params['TX_color']] * num_TX + \
                 [params['RX_color']] * num_RX



    if params['3D']:
        scatter = mscatter(all_coords[:,0], all_coords[:,1], all_coords[:,2], ax=ax,
                           s=sizes, c=colors, m=labels)
    else:
        scatter = mscatter(all_coords[:,0], all_coords[:,1], ax=ax,
                           s=sizes, c=colors, m=labels)


    legend_elements = [
        Line2D([0], [0], color=params['RIS_color'], marker=params['RIS_symbol'], linestyle='', label='RIS'),
        Line2D([0], [0], color=params['TX_color'],  marker=params['TX_symbol'], linestyle='', label='TX'),
        Line2D([0], [0], color=params['RX_color'],  marker=params['RX_symbol'],  linestyle='', label='RX')]

    legend1 = ax.legend(handles=legend_elements, loc='best', framealpha=0.8)

    ax.add_artist(legend1)


    if params['color_by_height'] and not params['3D']:
        cbar = plt.colorbar(scatter)
        cbar.ax.set_ylabel(r'$z \ (m)$', rotation=90)

    ax.set_xlabel(r'$x \ (m)$')
    ax.set_ylabel(r'$y \ (m)$')

    if params['3D']:
        ax.set_zlabel(r'$z \ (m)$', rotation=90)

    if params['xlims']: ax.set_xlim(params['xlims'])
    if params['ylims']: ax.set_ylim(params['ylims'])

    if params['grid']: plt.grid()
    return ax




def plot_element_matrix(ris: RIS, params=None, ax=None):


    if params is None: params = grid_plot_params





    element_coordinates = ris.get_element_coordinates()


    width               = ris.element_dimensions[0]
    height              = ris.element_dimensions[1]

    rects = []
    for i in range(element_coordinates.shape[0]):
            coords = element_coordinates[i, 0:2]
            rects.append(
                Rectangle(coords, width, height)
            )

    pc = PatchCollection(rects, facecolors=params['element_color'], alpha=params['alpha'])

    if not ax:
        fig, ax = plt.subplots()

    ax.add_collection(pc)

    if params['xlims']: ax.set_xlim(params['xlims'])
    if params['ylims']: ax.set_ylim(params['ylims'])
    return ax




def plot_ris_phase(phase2D: Matrix2D, params=None, ax=None):

    if not ax:
        fig, ax = plt.subplots()



    im = ax.imshow(phase2D)
    plt.colorbar(im)

    width = phase2D.shape[1]
    height = phase2D.shape[0]

    ax.set_xticks(np.arange(-.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-.5, height, 1), minor=True)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    ax.grid(which='minor', color='k', linestyle='-', linewidth=1)




if __name__ == '__main__':


    # # # # # # # # # # #
    #  ELEMENT MATRIX   #
    # # # # # # # # # # #

    r = RIS([0,0,0], (6,6), (3,2), [1,1], [1,1], [2,2], ('discrete', {'values':[1, np.pi]}))

    grid_plot_params['xlims'] = (-1, 13)
    grid_plot_params['ylims'] = (-1, 13)

    plot_element_matrix(r, grid_plot_params)
    plt.show()




    ########################################################


    # # # # # # # # # # # # #
    #     POSITION GRID     #
    # # # # # # # # # # # # #

    RIS_positions, TX_positions, RX_positions = from_ascii('''
    ........*......*...o
    ....................
    ....................
    x..................o
    ....................
    ....................
    ..x.*......*.......o
    ''',
    0,1,2,
    scale_x=3.7,
    scale_y=4.5)


    grid_plot_params['2D'] = True
    grid_plot_params['xlims'] = None
    grid_plot_params['ylims'] = None
    plot_positions(RIS_positions, TX_positions, RX_positions)
    plt.show(block=False)


    #############################################################

    # # # # # # # # # # # # #
    #   RIS PHASE           #
    # # # # # # # # # # # # #

    grid_shape = np.array((30,30))
    group_shape = np.array((3,2))
    ris = RIS([0,0,0], (12,12), (3,2), [1,1], [1,1], [2,2], ('discrete', {'values':[1, np.pi]}))

    ris.set_random_state()

    plot_ris_phase(ris.get_phase('2D'))
    plt.show(block=True)