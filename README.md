# Pandemic

An agent model in which commuting, compliance, testing and contagion parameters drive
infection in a population. Agents follow OU drift processes
on the plane. Viral load is estimated from geohashing. A population 
of 5,000,000 or so can be used without computational issue, although the default
parameters for city generation assume something closer to 40,000. 

![](https://github.com/microprediction/pandemic/blob/master/images/pandemic.png)

### Usage 

The author is not an epidemiologist. There is nothing sacrosanct about the default parameters. 

    pip install pandemic
    >> from pandemic import run
    >> run()
    
 There are a few example of modifying the parameters in pandemic.main


### Basic elements of the model 

Covered in this [post](https://www.linkedin.com/pulse/pandemic-minimalist-2d-ornstein-uhlenbeck-model-peter-cotton-phd) with 
the followup [here](https://www.linkedin.com/pulse/dear-new-zealand-heres-how-simulate-covid-19-all-your-cotton-phd/) where possible
improvements are also discussed and acknowledgements are made.   

### Contributing 

Opinions and issues are most welcome. 