from pandemic.conventions import STATE_DESCRIPTIONS, STATE_COLORS
from collections import Counter

def plot_points(plt, positions, status, title=None):
    x = [p[0] for p in positions]
    y = [p[1] for p in positions]
    if status is not None:
        c = [ STATE_COLORS[s] for s in status ]
        sizes = [ 1, 16, 9, 9, 4, 16 ]
        scatter = plt.scatter(x=x, y=y, c=status, alpha=0.9, s=[ sizes[s]+4 for s in status ] )
        running = Counter(status)
        descriptions = list(STATE_DESCRIPTIONS.values())
        running_totals  = [ (descriptions[k]+ " ("+str(v)+")",k) for k,v in running.items() ]
        running_totals.sort( key=lambda rt: rt[1] )
        labels = [ desc for desc,_ in running_totals ]
        plt.legend(handles=scatter.legend_elements()[0], labels=labels, loc='upper left')
        if title:
            plt.title(title)
    else:
        scatter = plt.scatter(x=x, y=y)
    return scatter
