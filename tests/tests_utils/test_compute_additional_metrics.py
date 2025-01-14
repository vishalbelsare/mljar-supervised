import unittest

import numpy as np

from supervised.algorithms.registry import BINARY_CLASSIFICATION, REGRESSION
from supervised.utils.additional_metrics import AdditionalMetrics


class ComputeAdditionalMetricsTest(unittest.TestCase):
    def test_compute(self):
        target = np.array([0, 0, 0, 0, 1, 1, 1, 1])
        pred = np.array([0.1, 0.8, 0.1, 0.1, 0.8, 0.1, 0.8, 0.8])
        info = AdditionalMetrics.compute(target, pred, None, BINARY_CLASSIFICATION)
        details = info["metric_details"]
        max_metrics = info["max_metrics"]
        conf = info["confusion_matrix"]
        self.assertEqual(conf.iloc[0, 0], 3)
        self.assertEqual(conf.iloc[1, 1], 3)
        self.assertTrue(details is not None)
        self.assertTrue(max_metrics is not None)

    def test_compute_f1(self):
        target = np.array([0, 0, 0, 0, 1, 1, 1, 1])
        pred = np.array([0.01, 0.2, 0.1, 0.1, 0.8, 0.8, 0.8, 0.8])
        info = AdditionalMetrics.compute(target, pred, None, BINARY_CLASSIFICATION)
        details = info["metric_details"]
        max_metrics = info["max_metrics"]
        conf = info["confusion_matrix"]
        self.assertEqual(max_metrics["f1"]["score"], 1)
        self.assertTrue(details is not None)
        self.assertTrue(conf is not None)

    def test_compute_for_regression(self):
        target = np.array([0, 0, 0, 0, 1, 1, 1, 1])
        pred = np.array([0.01, 0.2, 0.1, 0.1, 0.8, 0.8, 0.8, 0.8])
        info = AdditionalMetrics.compute(target, pred, None, REGRESSION)
        all_metrics = list(info["max_metrics"]["Metric"].values)
        for m in ["MAE", "MSE", "RMSE", "R2"]:
            self.assertTrue(m in all_metrics)

    def test_compute_constant_preds(self):
        target = np.array([0, 0, 1, 1, 0, 0, 0, 0])
        pred = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        info = AdditionalMetrics.compute(target, pred, None, BINARY_CLASSIFICATION)
        details = info["metric_details"]
        max_metrics = info["max_metrics"]
        conf = info["confusion_matrix"]
        self.assertTrue(max_metrics["f1"]["score"] < 1)
        self.assertTrue(max_metrics["mcc"]["score"] < 1)
