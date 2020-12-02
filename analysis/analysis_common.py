import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.legend_handler import HandlerTuple
from matplotlib.transforms import Bbox
from matplotlib.textpath import TextPath
from pandas_ods_reader import read_ods

def plt_clean_legend():
    original = plt.gca().get_legend_handles_labels()
    result = ([], [])
    for artist, label in zip(*original):
        try:
            if label == result[1][-1]:
                continue
        except:
            pass

        result[0].append(artist)
        result[1].append(label)
    plt.legend(result[0], result[1], loc="lower left")
    
def expand_modes(df):
    if "INPUT_IN_NVRAM" in df:
        if "EXEC_IN_NVRAM" in df:
            df.loc[(df['EXEC_IN_NVRAM'] == 1) & (df['MODE'] == 'AD'), 'MODE'] = 'AD (in-place FMA)'
        df.loc[(df['INPUT_IN_NVRAM'] == 0) & (df['MODE'] == 'AD'), 'MODE'] = 'DRAM'
        df.loc[(df['RESULT_IN_NVRAM'] == 1) & (df['MODE'] == 'AD'), 'MODE'] = 'AD (store result)'
        df.loc[(df['RESULT_IN_NVRAM'] == 1) & (df['MODE'] == 'DAOS'), 'MODE'] = 'DAOS (store result)'
        df.loc[(df['INPUT_IN_NVRAM'] == 1) & (df['MODE'] == 'AD'), 'MODE'] = 'AD (volatile result)'
        df.loc[(df['INPUT_IN_NVRAM'] == 1) & (df['MODE'] == 'DAOS'), 'MODE'] = 'DAOS (volatile result)'
    else:
        df.loc[(df['EXEC_IN_NVRAM'] == 1) & (df['MODE'] == 'AD'), 'MODE'] = 'AD'
        df.loc[(df['EXEC_IN_NVRAM'] == 0) & (df['MODE'] == 'AD'), 'MODE'] = 'DRAM'

    df.loc[df['MODE'] == 'MM-DRAM', 'MODE'] = 'MM (hot)'
    df.loc[df['MODE'] == 'MM-NVM', 'MODE'] = 'MM (cold)'
    df.loc[df['MODE'] == 'AD-PRECOPY', 'MODE'] = 'AD (pre-copy)'

# First and last should be consistent, and reverse for consistency
palette = list(reversed(sns.color_palette(n_colors=6)))

def custom_kernel_palette(number_of_columns : int):
    return palette[:number_of_columns - 2] + palette[-2:]

def annotate_dram(ax):
    dram_patch = ax.patches[0]
    ax.annotate("N/A",
                (0, dram_patch.get_y()+dram_patch.get_height()),
                ha='center',
                va='center',
                xytext=(20, 0),
                size=15,
                textcoords = 'offset points')

def legend_tweaks(g, labels, title=None, placement='lower right'):
    assert len(labels) == 3
    handles, _ = g.get_legend_handles_labels()
    patchList = [
        [handles[0]], [handles[1]], [handles[2], handles[3]]
    ]
    g.legend(handles=patchList, labels=labels,
             handler_map = {list: HandlerTuple(None)}, title=title,
             loc=placement)


def kernel_plot_tweaks(g, factor, legend_title=""):
    _, max_value = g.get_xlim()

    g.set_xlabel("small objects kernel execution time (s)")
    handles, _ = g.get_legend_handles_labels()
    g.legend(title=legend_title, handles=handles,
             labels=["big objects", "small objects"])
    
    g.xaxis.set_ticks_position('top')

    ax2 = g.twiny()
    ax2.set_xlabel("big objects kernel execution time (s)")
    ax2.set_xlim(0, max_value * factor)
    
    # Colorise
    leg = g.get_legend()
    color0 = leg.legendHandles[1]._facecolor
    color1 = leg.legendHandles[0]._facecolor
    
    def dark_color(x, s):
        return x[0]*s, x[1]*s, x[2]*s, x[3]

    ax2.spines['bottom'].set_color(color0)
    g.tick_params(axis='x', colors=dark_color(color0, 0.5))
    g.xaxis.label.set_color(dark_color(color0, 0.5))
    
    ax2.spines['top'].set_color(color1)
    ax2.tick_params(axis='x', colors=dark_color(color1, 0.6))
    ax2.xaxis.label.set_color(dark_color(color1, 0.6))


def ylabel_tweaks(g, amounts, labels, distance, scale):
    assert len(amounts) == len(labels)
    g.set_ylabel("")
    position=-distance
    ticklength = 25
    text_size = 10
    total = sum(amounts)
    cum_amounts = [0]
    for a in amounts:
        cum_amounts.append(cum_amounts[-1]+a)
    yticks = [a/total for a in cum_amounts]
    ylocators = [(a+b)/2 for a, b in zip(yticks, yticks[1:])]
    for i, l in enumerate(labels):
        box = TextPath((0,0), l, size=text_size).get_extents()
        ylocators[i] += ((box.x1-box.x0)/2)*scale
    
    ax2 = g.twinx()
    ax2.spines['right'].set_position(('axes', position))
    ax2.spines['right'].set_visible(True)
    ax2.yaxis.set_major_formatter(ticker.NullFormatter())
    ax2.yaxis.set_minor_locator(ticker.FixedLocator(ylocators))
    ax2.yaxis.set_minor_formatter(ticker.FixedFormatter(labels))
    ax2.tick_params(axis='y', which='minor', width=0, length=0, rotation = 90, pad=-(text_size+3))
    ax2.tick_params(axis='y', which='major', width=1, length=ticklength, labelsize=text_size, direction='out')
    ax2.set_yticks(yticks)

def save_tweaks(filename, big=False):
    if big:
        size = (6, 4)
    else:
        size = (8, 4)
    plt.gcf().set_size_inches(size[0], size[1])
    b = plt.gcf().get_tightbbox(plt.gcf().canvas.get_renderer())
    bbox = Bbox.from_bounds(b.x0, b.y0, b.x1-b.x0+0.1, b.y1-b.y0)
    plt.savefig(filename, bbox_inches=bbox)

    
def crop_axis(ax, val):
    ax.set_xlim((0, val))
    for patch in ax.patches:
        if patch.get_width() > val:
            if val >1000:
                print_val = round(patch.get_width(), -3)
            else:
                print_val = round(patch.get_width(), -2)
            ax.annotate(">%d"%print_val,
                (val, patch.get_y()+patch.get_height()/1.7),
                ha='center',
                va='center',
                xytext=(-20, 0),
                size=10,
                color='w',
                textcoords = 'offset points')
