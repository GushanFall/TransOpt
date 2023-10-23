import numpy as np
import GPy
from Acquisition.ConstructACF import get_ACF
from Acquisition.sequential import Sequential
from typing import Dict, Union, List
from Optimizer.BayesianOptimizerBase import BayesianOptimizerBase
from Util.Data import InputData, TaskData, vectors_to_ndarray, output_to_ndarray, ndarray_to_vectors
from Util.Register import optimizer_register

from Util.Normalization import get_normalizer



@optimizer_register('BO')
class VanillaBO(BayesianOptimizerBase):
    def __init__(self, config:Dict, **kwargs):
        super(VanillaBO, self).__init__(config=config)

        self.init_method = 'Random'
        self.model = None

        if 'verbose' in config:
            self.verbose = config['verbose']
        else:
            self.verbose = True

        if 'init_number' in config:
            self.ini_num = config['init_number']
        else:
            self.ini_num = None

        if 'acf' in config:
            self.acf = config['acf']
        else:
            self.acf = 'EI'

    def reset(self, design_space:Dict, search_sapce:Union[None, Dict] = None):
        self.set_space(design_space, search_sapce)
        self.obj_model = None
        self.var_model = None
        self._X = np.empty((0,))  # Initializes an empty ndarray for input vectors
        self._Y = np.empty((0,))
        self.acqusition = get_ACF(self.acf, model=self, search_space=self.search_space, config=self.config)
        self.evaluator = Sequential(self.acqusition)

    def initial_sample(self):
        return self.random_sample(self.ini_num)

    def suggest(self, n_suggestions:Union[None, int] = None) ->List[Dict]:
        if self._X.size == 0:
            suggests = self.initial_sample()
            return suggests
        elif self._X.shape[0] < self.ini_num:
            pass
        else:
            if 'normalize' in self.config:
                self.normalizer = get_normalizer(self.config['normalize'])


            Data = {'Target':{'X':self._X, 'Y':self._Y}}
            self.update_model(Data)
            suggested_sample, acq_value = self.evaluator.compute_batch(None, context_manager=None)
            suggested_sample = self.search_space.zip_inputs(suggested_sample)
            suggested_sample = ndarray_to_vectors(self._get_var_name('search'), suggested_sample)
            design_suggested_sample = self.inverse_transform(suggested_sample)

            return design_suggested_sample

    def update_model(self, Data):
        assert 'Target' in Data
        target_data = Data['Target']
        X = target_data['X']
        Y = target_data['Y']

        if self.normalizer is not None:
            Y = self.normalizer(Y)

        if self.obj_model == None:
            self.create_model(X, Y)
        else:
            self.obj_model.set_XY(X, Y)

        try:
            self.obj_model.optimize_restarts(num_restarts=1, verbose=self.verbose, robust=True)
        except np.linalg.linalg.LinAlgError as e:
            # break
            print('Error: np.linalg.linalg.LinAlgError')

    def create_model(self, X, Y):
        k1 = GPy.kern.Linear(self.input_dim, ARD=False)
        k2 = GPy.kern.Matern32(self.input_dim, ARD=True)
        k2.lengthscale = np.std(X, axis=0).clip(min=0.02)
        k2.variance = 0.5
        k2.variance.set_prior(GPy.priors.Gamma(0.5, 1), warning=False)
        kern = k1 + k2

        self.obj_model = GPy.models.GPRegression(X, Y, kernel=kern)
        # self.obj_model.likelihood.variance.set_prior(GPy.priors.LogGaussian(-4.63, 0.5), warning=False)
        self.obj_model['Gaussian_noise.*variance'].constrain_bounded(1e-9, 1e-3)


    def predict(self, X):
        """
        Predictions with the model. Returns posterior means and standard deviations at X. Note that this is different in GPy where the variances are given.

        Parameters:
            X (np.ndarray) - points to run the prediction for.
            with_noise (bool) - whether to add noise to the prediction. Default is True.
        """
        if X.ndim == 1:
            X = X[None,:]

        m, v = self.obj_model.predict(X)

        # We can take the square root because v is just a diagonal matrix of variances
        return m, v



    def random_sample(self, num_samples: int) -> List[Dict]:
        """
        Initialize random samples.

        :param num_samples: Number of random samples to generate
        :return: List of dictionaries, each representing a random sample
        """
        if self.input_dim is None:
            raise ValueError("Input dimension is not set. Call set_search_space() to set the input dimension.")

        random_samples = []
        for _ in range(num_samples):
            sample = {}
            for var_info in self.search_space.config_space:
                var_name = var_info['name']
                var_domain = var_info['domain']
                # Generate a random floating-point number within the specified range
                random_value = np.random.uniform(var_domain[0], var_domain[1])
                sample[var_name] = random_value
            random_samples.append(sample)

        random_samples = self.inverse_transform(random_samples)
        return random_samples

    def get_fmin(self):
        "Get the minimum of the current model."
        m, v = self.predict(self.obj_model.X)

        return m.min()

    def posterior_samples(self, X, model_id, size=10):
        """
        Samples the posterior GP at the points X.

        :param X: the points at which to take the samples.
        :type X: np.ndarray (Nnew x self.input_dim.)
        :param size: the number of a posteriori samples.
        :type size: int.
        :param noise_model: for mixed noise likelihood, the noise model to use in the samples.
        :type noise_model: integer.
        :returns: Ysim: set of simulations,
        :rtype: np.ndarray (D x N x samples) (if D==1 we flatten out the first dimension)
        """
        fsim = self.posterior_samples_f(X, model_id=model_id, size=size)

        if fsim.ndim == 3:
            for d in range(fsim.shape[1]):
                fsim[:, d] = self.samples(fsim[:, d])
        else:
            fsim = self.samples(fsim)
        return fsim