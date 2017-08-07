import sys
sys.path.append("~/git/server-client-python")

import tableauserverclient as TSC

rob = TSC.RequestOptions.Builder()
ro = rob.file("==", "MyFile").project("==", "Default")._sort("foo", "desc")._pagesize(50)._build()
print ro.filters