from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # You can change this to your actual view
    path('get-response/', views.get_user_input, name='get_response'),

    path('new_home/', views.new_home, name='new_home'),  # You can change this to your actual view
    # path('get-new-response/', views.get_new_user_input, name='get_new_response'),
]
