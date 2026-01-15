import tableauserverclient as TSC


def test_filter_equal():
    filter = TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "Superstore")

    assert str(filter) == "name:eq:Superstore"


def test_filter_in():
    # create a IN filter condition with project names that
    # contain spaces and "special" characters
    projects_to_find = ["default", "Salesforce Sales Projeśt"]
    filter = TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.In, projects_to_find)

    assert str(filter) == "name:in:[default,Salesforce Sales Projeśt]"
