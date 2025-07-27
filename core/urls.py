from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.index, name='index'), # Home Page (because there is no extra url path)
    path('profile/', views.profile, name='profile'),
    path('home/', views.home, name='home'),
    path('post1/', views.post1, name='post1'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('create-post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('user/<str:username>/', views.view_user_profile, name='view_user_profile'),
    path('toggle-save/<int:post_id>/', views.toggle_save, name='toggle_save'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('toggle-follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('saved-posts/', views.saved_posts, name='saved_posts'),
    path('get-notifications/', views.get_notifications, name='get_notifications'),
    path('mark-notifications-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('get-following/', views.get_following, name='get_following'),
    path('set-favorite/<int:post_id>/', views.set_favorite_post, name='set_favorite_post'),
    path('create-album/', views.create_album, name='create_album'),
    path('add-to-album/<int:post_id>/', views.add_to_album, name='add_to_album'),
    path('delete-album/<int:album_id>/', views.delete_album, name='delete_album'),
    path('edit-post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('edit-album/<int:album_id>/', views.edit_album, name='edit_album'),
    path('search-users/', views.search_users, name='search_users'),
    path('get-albums/', views.get_albums, name='get_albums'),
]