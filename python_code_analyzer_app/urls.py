"""Defines URL patterns for python_code_analyzer_app."""

from django.urls import path

from . import views

app_name = 'python_code_analyzer_app'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Page that shows all Repositories.
    path('repositories/', views.repositories, name='repositories'),
    # Detail page for a single repository.
    path('repositories/<int:repository_id>/', views.repository, name='repository'),
    # Page for adding a new repository
    path('new_repository/', views.new_repository, name='new_repository'),
    # Page for adding a repositories in a massive way
    path('massive_upload/', views.massive_upload, name='massive_upload'),
    # Page for adding a new analysis
    path('new_analysis/<int:repository_id>/', views.new_analysis, name='new_analysis'),
    # Detail page for a single analysis.
    path('analyzes/<int:analysis_id>/', views.analysis, name='analysis'),
    # Reult page for a single analysis.
    path('analysis_result/<int:analysis_id>/', views.analysis_result, name='analysis_result'),
    # Cancel a single analysis.
    path('cancel_analysis/<int:analysis_id>/', views.cancel_analysis, name='cancel_analysis'),
    # Delete a single analysis.
    path('delete_analysis/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),
    # Delete a single repository.
    path('delete_repository/<int:repo_id>/', views.delete_repository, name='delete_repository'),
    # Delete a all analizes.
    path('delete_all_analyzes/<int:repo_id>/', views.delete_all_analyzes, name='delete_all_analyzes'),
    # Delete a all repositories.
    path('delete_all_repositories/', views.delete_all_repositories, name='delete_all_repositories'),
]