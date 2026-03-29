import unittest

from domain.energy_balance_calculator import EnergyBalanceCalculator


class TestEnergyBalanceCalculator(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.calculator = EnergyBalanceCalculator()

    def test_normal_loss(self):
        result = self.calculator.compute(common_kwh=1000.0, individual_sum_kwh=900.0)
        self.assertAlmostEqual(result.loss_kwh, 100.0)
        self.assertAlmostEqual(result.loss_percent, 10.0)

    def test_zero_loss(self):
        result = self.calculator.compute(common_kwh=1000.0, individual_sum_kwh=1000.0)
        self.assertAlmostEqual(result.loss_kwh, 0.0)
        self.assertAlmostEqual(result.loss_percent, 0.0)

    def test_zero_common_meter_no_division_error(self):
        result = self.calculator.compute(common_kwh=0.0, individual_sum_kwh=0.0)
        self.assertAlmostEqual(result.loss_kwh, 0.0)
        self.assertAlmostEqual(result.loss_percent, 0.0)

    def test_negative_loss_is_not_clamped(self):
        # Individual meters report more than common — possible sensor miscalibration
        result = self.calculator.compute(common_kwh=900.0, individual_sum_kwh=1000.0)
        self.assertAlmostEqual(result.loss_kwh, -100.0)
        self.assertLess(result.loss_percent, 0.0)

    def test_small_loss_percent(self):
        result = self.calculator.compute(common_kwh=200.0, individual_sum_kwh=198.0)
        self.assertAlmostEqual(result.loss_percent, 1.0)


class TestAverageLoadCalculator(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from domain.average_load_calculator import AverageLoadCalculator
        self.calculator = AverageLoadCalculator()

    def test_empty_values_returns_none(self):
        result = self.calculator.compute([])
        self.assertIsNone(result)

    def test_single_value(self):
        result = self.calculator.compute([42.0])
        self.assertAlmostEqual(result.mean_value, 42.0)

    def test_mean_of_multiple_values(self):
        result = self.calculator.compute([10.0, 20.0, 30.0])
        self.assertAlmostEqual(result.mean_value, 20.0)

    def test_mean_with_floats(self):
        result = self.calculator.compute([1.5, 2.5, 3.0])
        self.assertAlmostEqual(result.mean_value, 7.0 / 3.0)
