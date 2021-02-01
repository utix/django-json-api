from unittest import mock


def mock_json_api(target):
    target.patcher = mock.patch("django_json_api.manager.JSONAPIManager", spec=True)

    setup_fn = target.setUp
    teardown_fn = target.tearDown

    def decorated_setup(instance):
        instance.manager = instance.patcher.start()
        return setup_fn(instance)

    def decorated_teardown(instance):
        instance.patcher.stop()
        delattr(instance, "manager")
        return teardown_fn(instance)

    target.setUp = decorated_setup
    target.tearDown = decorated_teardown

    return target
