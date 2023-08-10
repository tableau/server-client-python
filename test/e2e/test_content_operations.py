import pytest
import tableauserverclient as TSC

"""
A very brief set of calls to establish basic perf for the library
"""

server_url = ""
site_name = ""
pat = ""
value = ""

# global session
server: TSC.Server
project: TSC.ProjectItem
workbook: TSC.WorkbookItem


@pytest.mark.order(1)
def test_server_connect(benchmark):
    result = benchmark(TSC.Server, server_url)
    assert result is not None


@pytest.mark.order(1)
def test_server_login(benchmark):
    tableau_auth = TSC.PersonalAccessTokenAuth(pat, value, site_id=site_name)
    global server
    server = TSC.Server(server_url, use_server_version=True, http_options={"verify": False})
    result = benchmark(server.auth.sign_in, tableau_auth)
    assert result is not None


@pytest.mark.order(2)
def test_query_server(benchmark):
    global project
    projects, paging = benchmark(server.projects.get)
    assert paging.total_available > 0
    project = projects[0]
    assert project is not None


@pytest.mark.order(3)
def test_publish_to_server(benchmark):
    global workbook
    workbook = TSC.WorkbookItem(name="benchmarker-upload", project_id=project.id)
    file = "../assets/Data/Tableau Samples/T(L-F,SZ&V-MY) - PC.twbx"
    workbook = benchmark(server.workbooks.publish, workbook, file, "Overwrite")
    assert workbook.id is not None


@pytest.mark.order(4)
def test_export_pdf(benchmark):
    assert workbook.id is not None

    @benchmark
    def export():
        filename = "exported.pdf"
        server.workbooks.populate_pdf(workbook)
        with open(filename, "wb") as f:
            f.write(workbook.pdf)
