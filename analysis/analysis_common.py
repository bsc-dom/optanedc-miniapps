import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerTuple
from matplotlib import ticker
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

# First and last should be consistent, and reverse for consistency
palette = list(reversed(sns.color_palette(n_colors=6)))

def custom_kernel_palette(number_of_columns : int):
    return palette[:number_of_columns - 2] + palette[-2:]

def annotate_dram(ax):
    dram_patch = ax.patches[0]
    ax.annotate("N/A",
                (dram_patch.get_x() + dram_patch.get_width(), 0),
                ha='center',
                va='center',
                xytext=(0, 20),
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


def kernel_plot_tweaks(g, factor, legend_title="", rotate=False):
    if rotate:
        g.set_xticklabels(g.get_xticklabels(), rotation=25, horizontalalignment='right')

    _, max_value = g.get_ylim()

    g.set_ylabel("small objects kernel execution time (s)")
    handles, _ = g.get_legend_handles_labels()
    g.legend(title=legend_title, handles=handles,
             labels=["small objects", "big objects"])

    ax2 = g.twinx()
    ax2.set_ylabel("big objects kernel execution time (s)")
    ax2.set_ylim(0, max_value * factor)


def xlabel_tweaks(g, n_active, n_non_active, rotate=False):
    g.set_xlabel("")
    if rotate:
        g.set_xticklabels(g.get_xticklabels(), rotation=90, horizontalalignment='right')
        position=-0.6
        ticklength = 50
    else:
        position=-0.2
        ticklength = 25

    total = n_active + n_non_active
    midtick = n_active / total
    xticks = [0.0, midtick, 1.0]
    xlocators = [midtick / 2.0, (1 + midtick) / 2.0]

    ax2 = g.twiny()
    ax2.spines['top'].set_position(('axes', position))
    ax2.spines['top'].set_visible(True)
    ax2.xaxis.set_major_formatter(ticker.NullFormatter())
    ax2.xaxis.set_minor_locator(ticker.FixedLocator(xlocators))
    ax2.xaxis.set_minor_formatter(ticker.FixedFormatter(['active', 'non-active']))
    ax2.tick_params(which='minor', width=0, length=0, labelsize=10)
    ax2.tick_params(which='major', width=1, length=ticklength, labelsize=10)
    ax2.set_xticks(xticks)
