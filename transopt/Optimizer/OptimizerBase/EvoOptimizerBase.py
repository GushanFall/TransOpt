import abc
import numpy as np
import ConfigSpace
import math
from typing import Union, Dict, List
from transopt.Optimizer.OptimizerBase import OptimizerBase
import GPyOpt
from transopt.utils.Data import vectors_to_ndarray, output_to_ndarray
from transopt.utils.Visualization import visual_oned, visual_contour
from transopt.KnowledgeBase.TaskDataHandler import OptTaskDataHandler



class BayesianOptimizerBase(OptimizerBase):
    """
    The abstract Model for Evolutionary Optimization
    """
    def __init__(self, config):
        super(BayesianOptimizerBase, self).__init__(config=config)
        self._X = np.empty((0,))  # Initializes an empty ndarray for input vectors
        self._Y = np.empty((0,))
        self.config = config
        self.search_space = None
        self.design_space = None
        self.mapping = None
        self.ini_num = None
        self._data_handler = None
        self.population = None
        self.pop_size = None

