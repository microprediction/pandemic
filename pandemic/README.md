
Structure of the code:


    shell.py                     surrogate.py              simulator.py
      |                               |                       |                     
      |                               |                       |                            
    simulation.py --------------------|                       |                    
      |                                                       |
      -----------------------------------------------------------------------------
      |                 |            |              |            |          |
    movement.py    health.py   conventions.py  compliance.y   city.py   plotting.py 
    

## Original code (working)
  
- Shell.py or simulation.py can be used to run the model.  
- Surrogate.py uses simulation somewhat differently, and includes some methods for interacting with a database at www.swarmprediction.com


## Newer code 

- Simulator.py contains arguably cleaner simulation code in a more object oriented style. 