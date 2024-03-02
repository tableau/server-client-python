import tableauserverclient as TSC
import logging
from datetime import time

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="tsc.log", level="DEBUG")
tableau_auth = TSC.TableauAuth("test", "password")
server = TSC.Server("localhost")
server.version = "3.22"

with server.auth.sign_in(tableau_auth):
    all_workbooks, pagination_item = server.workbooks.get()
    wb1 = all_workbooks[2]
    print("\nThere are {} workbooks on site: ".format(len(all_workbooks)))
    # print(wb1.name)
    print([wb.name for wb in all_workbooks])

    wb_details = server.workbooks.get_by_id(wb1.id)
    # views = wb_details.views
    # print(views[0].data_acceleration_config)
    print(wb_details.data_freshness_policy.option)
    # print(wb_details.data_freshness_policy.fresh_every_schedule.frequency)
    # print(wb_details.data_freshness_policy.fresh_every_schedule.value)

    # wb1.name = "Superstore"
    # wb1.description = "Hmm"
    # dataacc = wb1.data_acceleration_config
    # print(dataacc)

    # server.workbooks.populate_views(wb1)
    # print([vw.name for vw in wb1.views])
    # view1 = wb1.views[0]
    # wb1.views = [view1]
    # print([vw.name for vw in wb1.views])

    # daconfig = dict()
    # daconfig['acceleration_enabled'] = True
    # daconfig['accelerate_now'] = True
    # wb1.data_acceleration_config = daconfig
    # print(wb1.data_acceleration_config)
    # server.workbooks.update(wb1, True)
    #
    # server.workbooks.populate_views(wb1)
    # view1 = wb1.views[0]

    # wb1.data_freshness_policy = TSC.DataFreshnessPolicyItem(
    #    TSC.DataFreshnessPolicyItem.Option.AlwaysLive)
    # wb1.data_freshness_policy = TSC.DataFreshnessPolicyItem(
    #     TSC.DataFreshnessPolicyItem.Option.FreshEvery)
    # freshevery = TSC.DataFreshnessPolicyItem.FreshEveryItem(
    #     TSC.DataFreshnessPolicyItem.FreshEveryItem.FreshEveryFrequency.Days,
    #     10
    # )
    # wb1.data_freshness_policy.fresh_every_schedule = freshevery

    # wb1.data_freshness_policy = TSC.DataFreshnessPolicyItem(
    #     TSC.DataFreshnessPolicyItem.Option.FreshAt)
    # time = "12:30:00"
    # freshat = TSC.DataFreshnessPolicyItem.FreshAtItem(
    #     TSC.DataFreshnessPolicyItem.FreshAtItem.FreshAtFrequency.Day,
    #     "12:30:00",
    #     "America/Los_Angeles",
    # )
    weeklies = ["Monday", "Wednesday", TSC.IntervalItem.Day.Friday]

    # monthlies = TSC.FreshAtMonthInterval(
    #     1,
    # )

    # monthlies = TSC.DataFreshnessPolicyItem.FreshAt.FreshAtMonthInterval("1","25")
    # monthlies = ["LastDay"]
    # monthlies = ["1","30","25"]
    freshat = TSC.DataFreshnessPolicyItem.FreshAt(
        TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Week, "12:00:00", "America/Los_Angeles", weeklies
    )
    wb1.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.FreshAt)
    wb1.data_freshness_policy.fresh_at_schedule = freshat
    #
    wb1 = server.workbooks.update(wb1)
    print(wb1.data_freshness_policy)
    # print(wb1.data_freshness_policy.fresh_every_schedule.frequency)
    # print(wb1.data_freshness_policy.fresh_every_schedule.value)

    wb_details2 = server.workbooks.get_by_id(wb1.id)
    print(wb_details2.data_freshness_policy.fresh_at_schedule.frequency)
    print(wb_details2.data_freshness_policy.fresh_at_schedule.timezone)
    print(wb_details2.data_freshness_policy.fresh_at_schedule.time)
    weeklyinterval = wb_details2.data_freshness_policy.fresh_at_schedule.interval_item
    print(weeklyinterval)
#    print(weeklyinterval.interval)

# print([wb.name for wb in all_workbooks])
# print(wb1.data_acceleration_config)
