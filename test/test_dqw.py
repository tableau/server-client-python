import tableauserverclient as TSC


def test_dqw_existence():
    dqw: TSC.DQWItem = TSC.DQWItem()
    dqw.message = "message"
    dqw.warning_type = TSC.DQWItem.WarningType.STALE
    dqw.active = True
    dqw.severe = True
