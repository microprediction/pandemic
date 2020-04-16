# Explaining the use of space filling curves
import matplotlib.pyplot as plt
import numpy as np
from pandemic.zcurves import from_zcurve

#----------------------------------------------------------


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
step = 0.0005

vs = list()
ts = list()
tail_len = 100

for step_no, t in enumerate(list(np.linspace(0,1,1000))):
    ts.append(t)
    v = from_zcurve(t,dim=3)
    vs.append(v)
    trailing = vs[-tail_len:]
    tail = max(ts[:-tail_len]+[0.0001])
    x,y,z = zip(*trailing)
    ax.clear()
    ax.plot(x, y, z)
    ax.scatter([x[-1]],[y[-1]],[z[-1]],s=100)
    ax.set_xlim([0,1])
    ax.set_ylim([0, 1])
    ax.set_zlim([0, 1])
    ax.set_xlabel('z1')
    ax.set_ylabel('z2')
    ax.set_zlabel('z3')
    ax.set_title('t -> ('+str(np.round(tail,4)).zfill(4)+','+str(np.round(t,4)).zfill(4)+')')
    plt.show(block=False)
    plt.pause(0.05)
    if step_no==0:
        plt.pause(2)

x,y,z = zip(*vs)
ax.plot(x, y, z)
plt.show()
