from check404 import testing


def test_is_CheckResult(create_check):
    assert create_check.run().state is testing.CheckState.ERROR
