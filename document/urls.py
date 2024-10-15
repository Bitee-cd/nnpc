from django.urls import path
from . import views

urlpatterns = [
    path ( '' , views.index,name='index'),
    path('step-two/', views.step_two, name='step_two'),
    path('step-three/', views.step_three, name='step_three'),
    path('step-four/', views.step_four, name='step_four'),
    path('generate',views.generate,name='generate'),
    path('download/duplicates/', views.download_duplicates, name='download_duplicates'),
    path('download/non-duplicates/',views.download_non_duplicates, name='download_non_duplicates'),
  
]
