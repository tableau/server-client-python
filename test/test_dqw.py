import unittest
import tableauserverclient as TSC


class DQWTests(unittest.TestCase):
    def test_existence(self):
        dqw: TSC.DQWItem = TSC.DQWItem()
        dqw.message = "message"
        dqw.warning_type = TSC.DQWItem.WarningType.STALE
        dqw.active = True
        dqw.severe = True
