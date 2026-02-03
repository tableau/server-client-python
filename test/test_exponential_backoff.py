import pytest

from tableauserverclient.exponential_backoff import ExponentialBackoffTimer
from ._utils import mocked_time


def test_exponential() -> None:
    with mocked_time() as mock_time:
        exponentialBackoff = ExponentialBackoffTimer()
        # The creation of our mock shouldn't sleep
        pytest.approx(mock_time(), 0)
        # The first sleep sleeps for a rather short time, the following sleeps become longer
        exponentialBackoff.sleep()
        pytest.approx(mock_time(), 0.5)
        exponentialBackoff.sleep()
        pytest.approx(mock_time(), 1.2)
        exponentialBackoff.sleep()
        pytest.approx(mock_time(), 2.18)
        exponentialBackoff.sleep()
        pytest.approx(mock_time(), 3.552)
        exponentialBackoff.sleep()
        pytest.approx(mock_time(), 5.4728)


def test_exponential_saturation() -> None:
    with mocked_time() as mock_time:
        exponentialBackoff = ExponentialBackoffTimer()
        for _ in range(99):
            exponentialBackoff.sleep()
        # We don't increase the sleep time above 30 seconds.
        # Otherwise, the exponential sleep time could easily
        # reach minutes or even hours between polls
        for _ in range(5):
            s = mock_time()
            exponentialBackoff.sleep()
            slept = mock_time() - s
            pytest.approx(slept, 30)


def test_timeout() -> None:
    with mocked_time() as mock_time:
        exponentialBackoff = ExponentialBackoffTimer(timeout=4.5)
        for _ in range(4):
            exponentialBackoff.sleep()
        pytest.approx(mock_time(), 3.552)
        # Usually, the following sleep would sleep until 5.5, but due to
        # the timeout we wait less; thereby we make sure to take the timeout
        # into account as good as possible
        exponentialBackoff.sleep()
        pytest.approx(mock_time(), 4.5)
        # The next call to `sleep` will raise a TimeoutError
        with pytest.raises(TimeoutError):
            exponentialBackoff.sleep()


def test_timeout_zero() -> None:
    with mocked_time() as mock_time:
        # The construction of the timer doesn't throw, yet
        exponentialBackoff = ExponentialBackoffTimer(timeout=0)
        # But the first `sleep` immediately throws
        with pytest.raises(TimeoutError):
            exponentialBackoff.sleep()
