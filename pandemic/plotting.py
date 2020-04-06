from pandemic.conventions import STATE_DESCRIPTIONS, STATE_COLORS
from collections import Counter

def plot_points(plt, positions, status, title=None):
    x = [p[0] for p in positions]
    y = [p[1] for p in positions]
    if status is not None:
        c = [ STATE_COLORS[s] for s in status ]
        scatter = plt.scatter(x=x, y=y, c=status )
        running = Counter(status).values()
        labels  = [ sd + " ("+str(rc)+")" for sd,rc in zip( list(STATE_DESCRIPTIONS.values()), running) ]
        plt.legend(handles=scatter.legend_elements()[0], labels=labels, loc='upper left')
        if title:
            plt.title(title)
    else:
        scatter = plt.scatter(x=x, y=y)
    return scatter
