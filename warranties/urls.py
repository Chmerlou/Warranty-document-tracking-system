"""Маршруты страниц гарантийных документов."""

from django.urls import path

from . import views

app_name = "warranties"

urlpatterns = [
    path("", views.warranty_list, name="list"),
    path("search/", views.warranty_search, name="search"),
    path("statistics/", views.warranty_statistics, name="statistics"),
    path("<int:document_id>/", views.warranty_detail, name="detail"),
]
