from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'management'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('search-visitor/', views.search_visitor, name='search_visitor'),
    path('create-visitor/', views.create_visitor, name='create_visitor'), 
    path('update-visitor/', views.update_visitor, name='update_visitor'),  
    path('search-user/', views.search_user, name='search_user'),         
    path('create-user/', views.create_user, name='create_user'),         
    path('update-user/', views.update_user, name='update_user'), 
    path('entrance-log/', views.entrance_log, name='entrance_log'),
    path('save_user/', views.save_user, name='save_user'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('save_visitor/', views.save_visitor, name='save_visitor'),
    path('delete-visitor/', views.delete_visitor, name='delete_visitor'),
    path('insert_user/', views.insert_user, name='insert_user'),
    path('insert_visitor/', views.insert_visitor, name='insert_visitor'),
    path('enroll_fingerprint/', views.enroll_fingerprint, name='enroll_fingerprint'),
    path('approve_entry/', views.approve_entry, name='approve_entry'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)