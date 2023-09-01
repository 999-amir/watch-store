from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('', views.ProductsView.as_view(), name='products'),
    path('detail/<int:watch_pk>/<slug>/', views.DetailView.as_view(), name='details'),
    path('user/like/<int:watch_pk>/<slug>', views.LikeWatchView.as_view(), name='user_like'),
    path('user/bookmark/<int:watch_pk>/', views.BookmarkClickView.as_view(), name='user_bookmark'),
    path('remove/bookmark/<int:watch_pk>/', views.DeleteBookmarkedView.as_view(), name='remove_bookmark'),
    path('detail/comment/reply/<int:watch_pk>/<int:comment_id>', views.CommentReplyView.as_view(), name='reply')
]
