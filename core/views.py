from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from .models import UserProfile, Post, Save, Follow, Notification, Album

# Create your views here.
def index(request):
    return render(request, 'core/index.html')

@login_required
def create_album(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if title:
            album = Album.objects.create(
                user=request.user,
                title=title,
                description=description
            )
            return JsonResponse({
                'success': True,
                'album_id': album.id,
                'title': album.title
            })
        else:
            return JsonResponse({'error': 'Title is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_to_album(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id, user=request.user)
            album_id = request.POST.get('album_id')
            album = Album.objects.get(id=album_id, user=request.user)
            
            if post in album.posts.all():
                album.posts.remove(post)
                added = False
            else:
                album.posts.add(post)
                added = True
                
                # Set as cover photo if it's the first photo in the album
                if not album.cover_photo:
                    album.cover_photo = post
                    album.save()
            
            return JsonResponse({
                'success': True,
                'added': added,
                'album_title': album.title
            })
        except (Post.DoesNotExist, Album.DoesNotExist):
            return JsonResponse({'error': 'Post or album not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def delete_album(request, album_id):
    if request.method == 'POST':
        try:
            album = Album.objects.get(id=album_id, user=request.user)
            album.delete()
            return JsonResponse({'success': True})
        except Album.DoesNotExist:
            return JsonResponse({'error': 'Album not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def profile(request):
    user_posts = Post.objects.filter(user=request.user)
    user_albums = Album.objects.filter(user=request.user)
    followers_count = Follow.objects.filter(following=request.user).count()
    following_count = Follow.objects.filter(follower=request.user).count()
    
    context = {
        'user_posts': user_posts,
        'user_albums': user_albums,
        'followers_count': followers_count,
        'following_count': following_count
    }
    return render(request, 'core/profile.html', context)

def home(request):
    posts_per_page = 12  # Number of posts per page
    page_number = request.GET.get('page', 1)
    
    if request.user.is_authenticated:
        # Show recent posts from other users (not the current user)
        all_posts = Post.objects.exclude(user=request.user).select_related('user').order_by('-created_at')
        unread_notifications_count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
    else:
        # Show all recent posts for non-authenticated users
        all_posts = Post.objects.select_related('user').order_by('-created_at')
        unread_notifications_count = 0
    
    # Create paginator
    paginator = Paginator(all_posts, posts_per_page)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'unread_notifications_count': unread_notifications_count,
        'is_paginated': paginator.num_pages > 1,
    }
    return render(request, 'core/home.html', context)

@require_GET
def load_more_posts(request):
    """AJAX view to load more posts for infinite scroll"""
    page_number = request.GET.get('page', 1)
    posts_per_page = 12  # Same as home view
    
    try:
        if request.user.is_authenticated:
            # Show posts from other users (not the current user)
            all_posts = Post.objects.exclude(user=request.user).select_related('user').order_by('-created_at')
        else:
            # Show all posts for non-authenticated users
            all_posts = Post.objects.select_related('user').order_by('-created_at')
        
        # Create paginator
        paginator = Paginator(all_posts, posts_per_page)
        page_obj = paginator.get_page(page_number)
        
        # Prepare post data for JSON response
        posts_data = []
        for post in page_obj:
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'photo_url': post.photo.url if post.photo else '',
                'username': post.user.username,
                'created_at': post.created_at.isoformat(),
            })
        
        return JsonResponse({
            'posts': posts_data,
            'has_more': page_obj.has_next(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to load posts',
            'message': str(e)
        }, status=500)

def post1(request):
    return render(request, 'core/post1.html')

@login_required
def edit_profile(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        
        # Update user's first and last name from display_name
        display_name = request.POST.get('display_name', '')
        if display_name:
            name_parts = display_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
        
        # Update profile bio
        bio = request.POST.get('bio', '')
        profile.bio = bio
        
        # Update photo genres
        photo_genres = request.POST.getlist('photo_genres')
        profile.photo_genres = photo_genres
        
        # Handle profile photo upload
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'genre_choices': UserProfile.PHOTO_GENRES,
        'user_genres': profile.photo_genres if profile.photo_genres else []
    }
    return render(request, 'core/edit_profile.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        location = request.POST.get('location', '')
        
        if photo and title:
            new_post = Post.objects.create(
                user=request.user,
                photo=photo,
                title=title,
                description=description,
                location=location
            )
            
            # Create notifications for followers about the new post
            followers = Follow.objects.filter(following=request.user)
            for follow in followers:
                Notification.objects.create(
                    recipient=follow.follower,
                    sender=request.user,
                    notification_type='post',
                    post=new_post,
                    message=f'posted: "{title}"'
                )
            
            messages.success(request, 'Photo posted successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please provide a photo and title.')
    
    return render(request, 'core/post.html')

def view_post(request, post_id):
    post = Post.objects.get(id=post_id)
    user_has_saved = False
    if request.user.is_authenticated:
        user_has_saved = Save.objects.filter(user=request.user, post=post).exists()
    
    saves_count = post.saves.count()
    context = {
        'post': post,
        'user_has_saved': user_has_saved,
        'saves_count': saves_count
    }
    return render(request, 'core/post_detail.html', context)

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)[:10]
    notifications_data = []
    
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'message': notification.message,
            'sender_username': notification.sender.username,
            'post_id': notification.post.id if notification.post else None,
            'post_title': notification.post.title if notification.post else None,
            'created_at': notification.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'notification_type': notification.notification_type
        })
    
    return JsonResponse({'notifications': notifications_data})

@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def toggle_save(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        save, created = Save.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            # Unsave the post
            save.delete()
            saved = False
        else:
            # Save the post and create notification
            saved = True
            if post.user != request.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='save',
                    post=post,
                    message=f'saved your post: "{post.title}"'
                )
        
        saves_count = post.saves.count()
        return JsonResponse({
            'saved': saved,
            'saves_count': saves_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def toggle_follow(request, username):
    if request.method == 'POST':
        user_to_follow = User.objects.get(username=username)
        
        if user_to_follow == request.user:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user, 
            following=user_to_follow
        )
        
        if not created:
            # Unfollow
            follow.delete()
            following = False
        else:
            # Follow and create notification
            following = True
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow',
                message='started following you'
            )
        
        followers_count = Follow.objects.filter(following=user_to_follow).count()
        
        return JsonResponse({
            'following': following,
            'followers_count': followers_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def saved_posts(request):
    saved_posts = Post.objects.filter(saves__user=request.user).order_by('-saves__created_at')
    context = {'saved_posts': saved_posts}
    return render(request, 'core/saved_posts.html', context)

@login_required
def delete_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id, user=request.user)
            post.delete()
            messages.success(request, 'Post deleted successfully!')
            return JsonResponse({'success': True})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found or you do not have permission to delete it'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def view_user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(user=user)
    user_albums = Album.objects.filter(user=user)
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    is_following = False
    
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    context = {
        'user': user,
        'user_posts': user_posts,
        'user_albums': user_albums,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following
    }
    return render(request, 'core/user_profile.html', context)

@login_required
def get_following(request):
    following_relationships = Follow.objects.filter(follower=request.user).select_related('following__profile')
    following_data = []
    
    for follow in following_relationships:
        following_user = follow.following
        following_data.append({
            'username': following_user.username,
            'display_name': f"{following_user.first_name} {following_user.last_name}".strip(),
            'profile_photo': following_user.profile.profile_photo.url if hasattr(following_user, 'profile') and following_user.profile.profile_photo else None
        })
    
    return JsonResponse({'following': following_data})

@login_required
def set_favorite_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id, user=request.user)
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            if profile.favorite_post == post:
                # Remove as favorite
                profile.favorite_post = None
                is_favorite = False
            else:
                # Set as favorite
                profile.favorite_post = post
                is_favorite = True
            
            profile.save()
            return JsonResponse({
                'success': True,
                'is_favorite': is_favorite
            })
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found or not owned by user'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, user=request.user)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        location = request.POST.get('location', '')
        
        if title:
            post.title = title
            post.description = description
            post.location = location
            post.save()
            
            return JsonResponse({
                'success': True,
                'title': post.title,
                'description': post.description,
                'location': post.location
            })
        else:
            return JsonResponse({'error': 'Title is required'}, status=400)
    
    return JsonResponse({
        'title': post.title,
        'description': post.description,
        'location': post.location
    })

@login_required
def edit_album(request, album_id):
    try:
        album = Album.objects.get(id=album_id, user=request.user)
    except Album.DoesNotExist:
        return JsonResponse({'error': 'Album not found'}, status=404)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if title:
            album.title = title
            album.description = description
            album.save()
            
            return JsonResponse({
                'success': True,
                'title': album.title,
                'description': album.description
            })
        else:
            return JsonResponse({'error': 'Title is required'}, status=400)
    
    return JsonResponse({
        'title': album.title,
        'description': album.description
    })

@login_required
def get_albums(request):
    albums = Album.objects.filter(user=request.user)
    albums_data = []
    
    for album in albums:
        albums_data.append({
            'id': album.id,
            'title': album.title,
            'description': album.description or '',
            'posts_count': album.posts.count()
        })
    
    return JsonResponse({'albums': albums_data})

def search_users(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'users': []})
    
    # Search users by username, first name, or last name
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).select_related('profile')[:10]
    
    users_data = []
    for user in users:
        users_data.append({
            'username': user.username,
            'display_name': f"{user.first_name} {user.last_name}".strip(),
            'bio': user.profile.bio if hasattr(user, 'profile') and user.profile.bio else None,
            'profile_photo': user.profile.profile_photo.url if hasattr(user, 'profile') and user.profile.profile_photo else None
        })
    
    return JsonResponse({'users': users_data})

