"""Настройка Django перед сбором тестов pytest."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "warranty_tracker.settings")
django.setup()
