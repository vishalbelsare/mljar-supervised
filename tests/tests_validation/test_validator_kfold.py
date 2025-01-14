import os
import tempfile
import unittest
import pytest

import numpy as np
import pandas as pd

from supervised.utils.utils import dump_data
from supervised.validation.validator_kfold import KFoldValidator


class KFoldValidatorTest(unittest.TestCase):
    def test_create(self):
        with tempfile.TemporaryDirectory() as results_path:
            data = {
                "X": pd.DataFrame(
                    np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), columns=["a", "b"]
                ),
                "y": pd.DataFrame(np.array([0, 0, 1, 1]), columns=["target"]),
            }

            X_path = os.path.join(results_path, "X.data")
            y_path = os.path.join(results_path, "y.data")

            dump_data(X_path, data["X"])
            dump_data(y_path, data["y"])

            params = {
                "shuffle": False,
                "stratify": True,
                "k_folds": 2,
                "results_path": results_path,
                "X_path": X_path,
                "y_path": y_path,
            }
            vl = KFoldValidator(params)

            self.assertEqual(params["k_folds"], vl.get_n_splits())
            # for train, validation in vl.split():
            for k_fold in range(vl.get_n_splits()):
                train, validation = vl.get_split(k_fold)

                X_train, y_train = train.get("X"), train.get("y")
                X_validation, y_validation = validation.get("X"), validation.get("y")

                self.assertEqual(X_train.shape[0], 2)
                self.assertEqual(y_train.shape[0], 2)
                self.assertEqual(X_validation.shape[0], 2)
                self.assertEqual(y_validation.shape[0], 2)

    def test_missing_target_values(self):
        with tempfile.TemporaryDirectory() as results_path:
            data = {
                "X": pd.DataFrame(
                    np.array([[1, 0], [2, 1], [3, 0], [4, 1], [5, 1], [6, 1]]),
                    columns=["a", "b"],
                ),
                "y": pd.DataFrame(
                    np.array(["a", "b", "a", "b", np.nan, np.nan]), columns=["target"]
                ),
            }

            X_path = os.path.join(results_path, "X.data")
            y_path = os.path.join(results_path, "y.data")

            dump_data(X_path, data["X"])
            dump_data(y_path, data["y"])

            params = {
                "shuffle": False,
                "stratify": True,
                "k_folds": 2,
                "results_path": results_path,
                "X_path": X_path,
                "y_path": y_path,
            }
            vl = KFoldValidator(params)

            self.assertEqual(params["k_folds"], vl.get_n_splits())

            for k_fold in range(vl.get_n_splits()):
                train, validation = vl.get_split(k_fold)
                X_train, y_train = train.get("X"), train.get("y")
                X_validation, y_validation = validation.get("X"), validation.get("y")

                self.assertEqual(X_train.shape[0], 3)
                self.assertEqual(y_train.shape[0], 3)
                self.assertEqual(X_validation.shape[0], 3)
                self.assertEqual(y_validation.shape[0], 3)

    def test_create_with_target_as_labels(self):
        with tempfile.TemporaryDirectory() as results_path:
            data = {
                "X": pd.DataFrame(
                    np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), columns=["a", "b"]
                ),
                "y": pd.DataFrame(np.array(["a", "b", "a", "b"]), columns=["target"]),
            }

            X_path = os.path.join(results_path, "X.data")
            y_path = os.path.join(results_path, "y.data")

            dump_data(X_path, data["X"])
            dump_data(y_path, data["y"])

            params = {
                "shuffle": True,
                "stratify": True,
                "k_folds": 2,
                "results_path": results_path,
                "X_path": X_path,
                "y_path": y_path,
            }
            vl = KFoldValidator(params)

            self.assertEqual(params["k_folds"], vl.get_n_splits())

            for k_fold in range(vl.get_n_splits()):
                train, validation = vl.get_split(k_fold)
                X_train, y_train = train.get("X"), train.get("y")
                X_validation, y_validation = validation.get("X"), validation.get("y")

                self.assertEqual(X_train.shape[0], 2)
                self.assertEqual(y_train.shape[0], 2)
                self.assertEqual(X_validation.shape[0], 2)
                self.assertEqual(y_validation.shape[0], 2)

    def test_repeats(self):
        with tempfile.TemporaryDirectory() as results_path:
            data = {
                "X": pd.DataFrame(
                    np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), columns=["a", "b"]
                ),
                "y": pd.DataFrame(np.array([0, 0, 1, 1]), columns=["target"]),
            }

            X_path = os.path.join(results_path, "X.data")
            y_path = os.path.join(results_path, "y.data")

            dump_data(X_path, data["X"])
            dump_data(y_path, data["y"])

            params = {
                "shuffle": True,
                "stratify": False,
                "k_folds": 2,
                "repeats": 10,
                "results_path": results_path,
                "X_path": X_path,
                "y_path": y_path,
                "random_seed": 1,
            }
            vl = KFoldValidator(params)

            self.assertEqual(params["k_folds"], vl.get_n_splits())
            self.assertEqual(params["repeats"], vl.get_repeats())

            for repeat in range(vl.get_repeats()):
                for k_fold in range(vl.get_n_splits()):
                    train, validation = vl.get_split(k_fold, repeat)

                    X_train, y_train = train.get("X"), train.get("y")
                    X_validation, y_validation = validation.get("X"), validation.get(
                        "y"
                    )

                    self.assertEqual(X_train.shape[0], 2)
                    self.assertEqual(y_train.shape[0], 2)
                    self.assertEqual(X_validation.shape[0], 2)
                    self.assertEqual(y_validation.shape[0], 2)

    def test_disable_repeats_when_disabled_shuffle(self):
        with tempfile.TemporaryDirectory() as results_path:
            data = {
                "X": pd.DataFrame(
                    np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), columns=["a", "b"]
                ),
                "y": pd.DataFrame(np.array([0, 0, 1, 1]), columns=["target"]),
            }

            X_path = os.path.join(results_path, "X.data")
            y_path = os.path.join(results_path, "y.data")

            dump_data(X_path, data["X"])
            dump_data(y_path, data["y"])

            params = {
                "shuffle": False,
                "stratify": False,
                "k_folds": 2,
                "repeats": 10,
                "results_path": results_path,
                "X_path": X_path,
                "y_path": y_path,
                "random_seed": 1,
            }

            with pytest.warns(
                expected_warning=UserWarning,
                match="Disable repeats in validation because shuffle is disabled",
            ) as record:
                vl = KFoldValidator(params)

            # check that only one warning was raised
            self.assertEqual(len(record), 1)

            self.assertEqual(params["k_folds"], vl.get_n_splits())
            self.assertEqual(1, vl.get_repeats())
