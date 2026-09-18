import tableauserverclient as TSC
from tableauserverclient.server.endpoint import exceptions


def test_job_exceptions_at_top_level():
    assert TSC.JobFailedException is exceptions.JobFailedException
    assert TSC.JobCancelledException is exceptions.JobCancelledException
    assert "JobFailedException" in TSC.__all__
    assert "JobCancelledException" in TSC.__all__


def test_flow_run_exceptions_at_top_level():
    assert TSC.FlowRunFailedException is exceptions.FlowRunFailedException
    assert TSC.FlowRunCancelledException is exceptions.FlowRunCancelledException
    assert "FlowRunFailedException" in TSC.__all__
    assert "FlowRunCancelledException" in TSC.__all__
