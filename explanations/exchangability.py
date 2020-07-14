from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np



def plot4(x,y,z,c,title):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    img = ax.scatter(x, y, z, c=c, cmap=plt.hot())
    fig.colorbar(img)
    ax.set_xlabel('Die 1')
    ax.set_ylabel('Die 2')
    ax.set_zlabel('Die 3')
    ax.set_title(title)
    return fig, ax

def model_e_unnormalized(x,y,z):
    return 1.0/(1.0+abs(x*z-y)) + 1.0/(1.0+abs(x*y-x)) + 1.0/(1.0+abs(x*y-z))

def model_a_unnormalized(x,y,z):
    return 1.0/(1.0+abs(x*z-y))

def model_b_unnormalized(x,y,z):
    return 1.0/(1.0+abs(x*y-z))

class Thrice():
    # Represents three dice

    def __init__(self, unnormalized_model,title='' ):
        self.unnormalized_model = unnormalized_model
        self.rolls = [ (x,y,z) for x in range(1,7) for y in range(1,7) for z in range(1,7) ]
        self.partition = sum([self.unnormalized_model(x, y, z) for (x, y, z) in self.rolls])
        self.model = lambda x, y, z: self.unnormalized_model(x, y, z) / self.partition
        self.probabilities =  [self.model(x,y,z) for (x,y,z) in self.rolls ]
        self.title = title

    def plot(self):
        x,y,z = zip(*self.rolls)
        c     = [c for c in self.probabilities ]
        self.fig, self.ax = plot4(x=x,y=y,z=z,c=c,title=self.title)

    def animate(self):
        for angle in range(0, 360):
            self.ax.view_init(30, angle)
            self.ax.figure
            plt.draw()
            plt.pause(.1)


def demo_test():
    x = np.random.standard_normal(10)
    y = np.random.standard_normal(10)
    z = np.random.standard_normal(10)
    c = np.random.standard_normal(10)
    plot4(x,y,z,c)


if __name__=="__main__":
    model_e = Thrice(unnormalized_model=model_e_unnormalized,title='Symmetrized Model')
    model_e.plot()
    #model_e.animate()
    plt.show()

