import math
import logging
import numpy as np
import matplotlib.pyplot as plt
import os
from typing import Union, Dict
import ConfigSpace as CS
from Util.Register import benchmark_register, benchmark_registry
from Benchmark.BenchBase.ConfigOptBenchmark import NonTabularOptBenchmark
logger = logging.getLogger('MultiObjBenchmark')




@benchmark_register('AckleySphere')
class AckleySphereOptBenchmark(NonTabularOptBenchmark):
    def __init__(self,task_name, budget, seed, task_id, task_type='non-tabular', **kwargs):
        assert 'params' in kwargs
        parameters = kwargs['params']
        self.input_dim = parameters['input_dim']

        if 'shift' in parameters:
            self.shift = parameters['shift']
        else:
            shift = np.random.random(size=(self.input_dim, 1)).T
            self.shift = (shift * 2 - 1) * 0.02

        if 'stretch' in parameters:
            self.stretch = parameters['stretch']
        else:
            self.stretch = np.array([1] * self.input_dim, dtype=np.float64)

        self.optimizers = tuple(self.shift)
        self.dtype =np.float64

        super(AckleySphereOptBenchmark, self).__init__(task_name=task_name, seed=seed, task_id=task_id, task_type=task_type, budget=budget)

    def objective_function(self, configuration: Union[CS.Configuration, Dict],
                           fidelity: Union[Dict, CS.Configuration, None] = None,
                           seed: Union[np.random.RandomState, int, None] = None,
                           **kwargs) -> Dict:

        X = np.array([[configuration[k] for idx, k in enumerate(configuration.keys())]])

        X = self.stretch * (X - self.shift)

        a = 20
        b = 0.2
        c = 2 * np.pi
        f_1 = -a * np.exp(-b * np.sqrt(np.sum(X ** 2) / 2)) - np.exp(np.sum(np.cos(c * X)) / 2) + a + np.e
        f_2 = np.sum(X ** 2)
        return {'function_value_1': float(f_1),
                'function_value_2': float(f_2),
                'info': {'fidelity': fidelity}
                }

    def get_configuration_space(self, seed: Union[int, None] = None) -> CS.ConfigurationSpace:
        """
        Creates a ConfigSpace.ConfigurationSpace containing all parameters for
        the XGBoost Model

        Parameters
        ----------
        seed : int, None
            Fixing the seed for the ConfigSpace.ConfigurationSpace

        Returns
        -------
        ConfigSpace.ConfigurationSpace
        """
        seed = seed if seed is not None else np.random.randint(1, 100000)
        cs = CS.ConfigurationSpace(seed=seed)
        cs.add_hyperparameters([CS.UniformFloatHyperparameter(f'x{i}', lower=-5.12, upper=5.12) for i in range(self.input_dim)])

        return cs

    def get_fidelity_space(self, seed: Union[int, None] = None) -> CS.ConfigurationSpace:
        """
        Creates a ConfigSpace.ConfigurationSpace containing all fidelity parameters for
        the XGBoost Benchmark

        Parameters
        ----------
        seed : int, None
            Fixing the seed for the ConfigSpace.ConfigurationSpace

        Returns
        -------
        ConfigSpace.ConfigurationSpace
        """
        seed = seed if seed is not None else np.random.randint(1, 100000)
        fidel_space = CS.ConfigurationSpace(seed=seed)

        return fidel_space


    def get_meta_information(self) -> Dict:
        return {'number_objective':2}



