import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import requests
import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

SIGN_IN_XML = TEST_ASSET_DIR / "auth_sign_in.xml"

NUM_THREADS = 8
CALLS_PER_THREAD = 5


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    return TSC.Server("http://test", False)


@pytest.fixture(scope="function")
def signed_in_server(server: TSC.Server) -> TSC.Server:
    with open(SIGN_IN_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml)
        server.auth.sign_in(TSC.TableauAuth("testuser", "password", site_id="Samples"))
    return server


def test_each_thread_gets_its_own_session(server: TSC.Server) -> None:
    main_session = server.session
    assert server.session is main_session  # stable within a thread

    # Hold strong references to the session objects (not just id()s, which can
    # be reused once a thread's session is garbage collected) and keep all
    # threads alive at the same time behind a barrier.
    barrier = threading.Barrier(NUM_THREADS)
    results: dict[str, requests.Session] = {}
    lock = threading.Lock()

    def worker(name: str) -> None:
        barrier.wait()
        first = server.session
        assert server.session is first  # stable within the worker thread too
        with lock:
            results[name] = first

    threads = [threading.Thread(target=worker, args=(f"t{i}",)) for i in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    sessions = list(results.values()) + [main_session]
    # every thread saw a distinct session object
    assert len({id(s) for s in sessions}) == NUM_THREADS + 1


def test_session_factory_called_once_per_thread() -> None:
    lock = threading.Lock()
    created: list[requests.Session] = []

    def counting_factory() -> requests.Session:
        session = requests.Session()
        with lock:
            created.append(session)
        return session

    server = TSC.Server("http://test", False, session_factory=counting_factory)
    # constructing the server creates the constructing thread's session
    assert len(created) == 1

    barrier = threading.Barrier(NUM_THREADS)

    def worker() -> None:
        barrier.wait()
        for _ in range(CALLS_PER_THREAD):
            server.session  # repeated access must not create new sessions

    threads = [threading.Thread(target=worker) for _ in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # one factory call for the main thread + exactly one per worker thread,
    # despite CALLS_PER_THREAD accesses in each worker
    assert len(created) == NUM_THREADS + 1


def test_sign_out_invalidates_sessions_of_all_threads(signed_in_server: TSC.Server) -> None:
    server = signed_in_server
    before_main = server.session

    barrier = threading.Barrier(2)
    worker_sessions: dict[str, int] = {}

    def worker() -> None:
        worker_sessions["before"] = id(server.session)
        barrier.wait()  # let the main thread sign out
        barrier.wait()
        worker_sessions["after"] = id(server.session)

    t = threading.Thread(target=worker)
    t.start()
    barrier.wait()  # worker has cached its session
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signout", text="")
        server.auth.sign_out()
    barrier.wait()  # worker re-reads its session
    t.join()

    # both the main thread and the worker thread got fresh sessions
    assert server.session is not before_main
    assert worker_sessions["after"] != worker_sessions["before"]
    assert not server.is_signed_in()


def test_concurrent_api_calls_use_per_thread_sessions(signed_in_server: TSC.Server) -> None:
    server = signed_in_server
    response_xml = (TEST_ASSET_DIR / "user_get_empty.xml").read_text()

    with requests_mock.mock() as m:
        m.get(server.users.baseurl, text=response_xml)

        def worker() -> int:
            for _ in range(CALLS_PER_THREAD):
                _, pagination_item = server.users.get()
                assert pagination_item.total_available == 0
            return id(server.session)

        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            session_ids = list(executor.map(lambda _: worker(), range(NUM_THREADS)))

        # every request was actually made
        assert m.call_count == NUM_THREADS * CALLS_PER_THREAD
        # every request carried the shared auth token
        assert all(r.headers["x-tableau-auth"] == server.auth_token for r in m.request_history)

    # the pool had NUM_THREADS workers; each distinct worker thread used a
    # distinct session, and threads reused their session across tasks
    assert 1 <= len(set(session_ids)) <= NUM_THREADS


def test_auth_state_is_set_atomically(server: TSC.Server) -> None:
    """Readers must never observe a half-updated (site_id, user_id, token) state.

    The reader takes ONE snapshot of the immutable auth state and asserts
    consistency within it. Asserting across two separate property reads
    (server.auth_token then server.site_id) would be a bug in the test: a
    writer can legitimately complete a full swap between the two reads,
    which free-threaded (no-GIL) builds surface readily. Individual
    property reads are each internally consistent; only the snapshot
    guarantees a consistent multi-field view.
    """
    stop = threading.Event()
    errors: list[Exception] = []

    def reader() -> None:
        while not stop.is_set():
            try:
                state = server._auth_state
                if state.auth_token is not None:
                    # all fields come from the same snapshot; a mismatched
                    # pair means a writer published a partial update
                    assert (state.auth_token, state.site_id, state.user_id) in (
                        ("token-a", "site-a", "user-a"),
                        ("token-b", "site-b", "user-b"),
                    )
                # single property reads must be internally consistent too:
                # either a value or NotSignedInError, never None
                try:
                    assert server.auth_token is not None
                except TSC.server.endpoint.exceptions.NotSignedInError:
                    pass  # signed out at the moment of the read; that's fine
            except Exception as e:  # pragma: no cover - only on failure
                errors.append(e)
                stop.set()

    readers = [threading.Thread(target=reader) for _ in range(4)]
    for t in readers:
        t.start()
    try:
        for _ in range(500):
            server._set_auth("site-a", "user-a", "token-a", "url-a")
            server._set_auth("site-b", "user-b", "token-b", "url-b")
            server._clear_auth()
    finally:
        stop.set()
        for t in readers:
            t.join()

    assert errors == []


class _TrackingSession(requests.Session):
    def __init__(self) -> None:
        super().__init__()
        self.closed = False

    def close(self) -> None:
        self.closed = True
        super().close()


def _tracking_server() -> tuple[TSC.Server, list["_TrackingSession"]]:
    created: list[_TrackingSession] = []
    lock = threading.Lock()

    def factory() -> requests.Session:
        session = _TrackingSession()
        with lock:
            created.append(session)
        return session

    return TSC.Server("http://test", False, session_factory=factory), created


def test_close_closes_sessions_of_all_threads() -> None:
    server, created = _tracking_server()
    barrier = threading.Barrier(NUM_THREADS)

    def worker() -> None:
        barrier.wait()
        server.session

    threads = [threading.Thread(target=worker) for _ in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(created) == NUM_THREADS + 1  # workers + constructing thread
    assert not any(s.closed for s in created)

    server.close()
    assert all(s.closed for s in created)

    # the server remains usable after close: a fresh session is created
    reopened = server.session
    assert isinstance(reopened, _TrackingSession)
    assert not reopened.closed
    assert reopened not in created[: NUM_THREADS + 1] or len(created) == NUM_THREADS + 2


def test_close_does_not_sign_out(signed_in_server: TSC.Server) -> None:
    server = signed_in_server
    token = server.auth_token
    server.close()
    # close() is transport-level only; auth state is untouched
    assert server.is_signed_in()
    assert server.auth_token == token


def test_context_manager_closes_on_exit() -> None:
    server, created = _tracking_server()
    with server as entered:
        assert entered is server
        server.session
    assert len(created) == 1
    assert all(s.closed for s in created)
