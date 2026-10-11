import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lambda"))
from risk_calculator import calculate_risk


class CalculateRiskTests(unittest.TestCase):
    def test_low_risk_example(self):
        result = calculate_risk(24, 40, 40, 82)

        self.assertEqual(result["heat_score"], 20)
        self.assertEqual(result["heat_stress"], "Low")
        self.assertEqual(result["water_score"], 20)
        self.assertEqual(result["water_stress"], "Low")
        self.assertEqual(result["overall_risk_score"], 20)
        self.assertEqual(result["risk_level"], "Low")

    def test_heat_medium_and_water_critical_example(self):
        result = calculate_risk(32, 65, 8, 150)

        self.assertEqual(result["heat_score"], 50)
        self.assertEqual(result["heat_stress"], "Medium")
        self.assertEqual(result["water_score"], 100)
        self.assertEqual(result["water_stress"], "Critical")
        self.assertEqual(result["overall_risk_score"], 75)
        self.assertEqual(result["risk_level"], "Critical")

    def test_heat_critical_when_temperature_exceeds_35(self):
        result = calculate_risk(36, 20, 40, 80)

        self.assertEqual(result["heat_score"], 100)
        self.assertEqual(result["heat_stress"], "Critical")

    def test_heat_critical_when_hot_and_humid(self):
        result = calculate_risk(31, 71, 40, 80)

        self.assertEqual(result["heat_score"], 100)
        self.assertEqual(result["heat_stress"], "Critical")

    def test_heat_medium_boundaries(self):
        result = calculate_risk(30, 100, 40, 80)
        self.assertEqual((result["heat_score"], result["heat_stress"]), (20, "Low"))

        result = calculate_risk(31, 70, 40, 80)
        self.assertEqual((result["heat_score"], result["heat_stress"]), (50, "Medium"))

    def test_water_medium_and_low_boundaries(self):
        result = calculate_risk(24, 40, 10, 121)
        self.assertEqual((result["water_score"], result["water_stress"]), (60, "Medium"))

        result = calculate_risk(24, 40, 20, 100)
        self.assertEqual((result["water_score"], result["water_stress"]), (20, "Low"))


if __name__ == "__main__":
    unittest.main()
