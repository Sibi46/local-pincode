from django.urls import path
from . import views

urlpatterns = [
    path('play/', views.quiz_play, name='quiz_play'),
    # Employer
    path('', views.employer_quiz_list, name='quiz_list'),
    path('create/', views.employer_quiz_create, name='quiz_create'),
    path('<int:pk>/', views.employer_quiz_manage, name='quiz_manage'),
    path('<int:pk>/toggle/', views.employer_quiz_toggle, name='quiz_toggle'),
    path('<int:quiz_pk>/questions/add/', views.employer_question_add, name='quiz_question_add'),
    path('<int:quiz_pk>/questions/<int:q_pk>/edit/', views.employer_question_edit, name='quiz_question_edit'),

    # User AJAX
    path('api/next/', views.quiz_next_question, name='quiz_api_next'),
    path('api/answer/', views.quiz_submit_answer, name='quiz_api_answer'),
]
