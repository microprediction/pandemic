from pandemic.simulator import BaseSimulator
import os
from pprint import pprint
import uuid

class AmphoraSimulator(BaseSimulator):

    # An example of logging simulation metrics somewhere

    def __init__(self, params=None, baseline=None):
        super().__init__(params=params, baseline=baseline)
        self.credentials = os.environ.get('AMPHORA')

    def start_of_run_callback(self):
        super().start_of_run_callback()
        self.run_id = str(uuid.uuid4())

    def end_of_day_callback(self):
        super().end_of_day_callback()
        payload = {'run_id':self.run_id,
                   'day':self.state['day'],
                   'metrics':self.daily_metrics(),
                   'positions':self.state['positions'],
                   'status': self.state['status']
                   }
        print('Pretending to send')
        pprint(payload)


if __name__=="__main__":
    os.environ['AMPHORA'] = 'Collosal Oca'
    simulator = AmphoraSimulator(baseline='town')
    simulator.run()
