from pandemic.simulator import LockdownSimulator

if __name__=="__main__":
    simulator = LockdownSimulator(baseline='town')
    simulator.set_param(parameter='vi',value=0.5)
    simulator.run()