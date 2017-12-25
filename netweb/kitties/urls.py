from django.urls import path
from . import views

urlpatterns = [
    path('cnn', views.cnn_response)
]