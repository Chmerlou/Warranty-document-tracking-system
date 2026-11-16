"""Настройка Django перед сбором тестов pytest."""

import os

import django
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "warranty_tracker.settings")
django.setup()
setup_test_environment()

_database_configuration = None


def pytest_sessionstart(session) -> None:
    """Создать изолированную тестовую базу для Django TestCase."""
    global _database_configuration
    _database_configuration = setup_databases(
        verbosity=0,
        interactive=False,
    )


def pytest_sessionfinish(session, exitstatus) -> None:
    """Удалить тестовую базу после завершения pytest."""
    if _database_configuration is not None:
        teardown_databases(_database_configuration, verbosity=0)
