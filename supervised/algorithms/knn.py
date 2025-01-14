import logging

import sklearn
from sklearn.base import ClassifierMixin, RegressorMixin
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

from supervised.algorithms.registry import (
    BINARY_CLASSIFICATION,
    MULTICLASS_CLASSIFICATION,
    REGRESSION,
    AlgorithmsRegistry,
)
from supervised.algorithms.sklearn import SklearnAlgorithm
from supervised.utils.config import LOG_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


KNN_ROWS_LIMIT = 1000


class KNNFit(SklearnAlgorithm):
    def file_extension(self):
        return "k_neighbors"

    def is_fitted(self):
        return (
            hasattr(self.model, "n_samples_fit_")
            and self.model.n_samples_fit_ is not None
            and self.model.n_samples_fit_ > 0
        )

    def fit(
        self,
        X,
        y,
        sample_weight=None,
        X_validation=None,
        y_validation=None,
        sample_weight_validation=None,
        log_to_file=None,
        max_time=None,
    ):
        rows_limit = self.params.get("rows_limit", KNN_ROWS_LIMIT)
        if X.shape[0] > rows_limit:
            X1, _, y1, _ = train_test_split(
                X, y, train_size=rows_limit, stratify=y, random_state=1234
            )
            self.model.fit(X1, y1)
        else:
            self.model.fit(X, y)

    @property
    def _classes(self):
        # Returns the unique classes based on the fitted model
        if hasattr(self.model, "classes_"):
            return self.model.classes_
        else:
            return None


class KNeighborsAlgorithm(ClassifierMixin, KNNFit):
    algorithm_name = "k-Nearest Neighbors"
    algorithm_short_name = "Nearest Neighbors"

    def __init__(self, params):
        super(KNeighborsAlgorithm, self).__init__(params)
        logger.debug("KNeighborsAlgorithm.__init__")
        self.library_version = sklearn.__version__
        self.max_iters = 1
        self.model = KNeighborsClassifier(
            n_neighbors=params.get("n_neighbors", 3),
            weights=params.get("weights", "uniform"),
            algorithm="kd_tree",
            n_jobs=params.get("n_jobs", -1),
        )


class KNeighborsRegressorAlgorithm(RegressorMixin, KNNFit):
    algorithm_name = "k-Nearest Neighbors"
    algorithm_short_name = "Nearest Neighbors"

    def __init__(self, params):
        super(KNeighborsRegressorAlgorithm, self).__init__(params)
        logger.debug("KNeighborsRegressorAlgorithm.__init__")
        self.library_version = sklearn.__version__
        self.max_iters = 1
        self.model = KNeighborsRegressor(
            n_neighbors=params.get("n_neighbors", 3),
            weights=params.get("weights", "uniform"),
            algorithm="ball_tree",
            n_jobs=params.get("n_jobs", -1),
        )


knn_params = {"n_neighbors": [3, 5, 7], "weights": ["uniform", "distance"]}

default_params = {"n_neighbors": 5, "weights": "uniform"}

additional = {"max_rows_limit": 100000, "max_cols_limit": 100}

required_preprocessing = [
    "missing_values_inputation",
    "convert_categorical",
    "datetime_transform",
    "text_transform",
    "scale",
    "target_as_integer",
]

AlgorithmsRegistry.add(
    BINARY_CLASSIFICATION,
    KNeighborsAlgorithm,
    knn_params,
    required_preprocessing,
    additional,
    default_params,
)
AlgorithmsRegistry.add(
    MULTICLASS_CLASSIFICATION,
    KNeighborsAlgorithm,
    knn_params,
    required_preprocessing,
    additional,
    default_params,
)

AlgorithmsRegistry.add(
    REGRESSION,
    KNeighborsRegressorAlgorithm,
    knn_params,
    required_preprocessing,
    additional,
    default_params,
)
