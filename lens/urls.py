from django.urls import path
from . import views, drive_views

urlpatterns = [path("", views.index, name="index"), path("explore/", views.explore, name="explore"),
               path("api/analyze/", views.analyze), path("api/coach/", views.coach), path("api/reset/", views.reset),
               path("telegram/drive/callback", drive_views.drive_callback, name="telegram_drive_callback")]
