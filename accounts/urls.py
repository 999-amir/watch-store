from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.UserRegisterView.as_view(), name='signup'),
    path('verify/code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('cancel/signup/', views.CancelSignupView.as_view(), name='cancel_signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('reset/password/', views.UserPasswordResetView.as_view(), name='reset_password'),
    path('reset/done/', views.UserPasswordResetDoneView.as_view(), name='reset_done'),
    path('reset/confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='reset_confirm'),
    path('reset/complete/', views.UserPasswordResetCompleteView.as_view(), name='reset_complete'),
    path('bookmark/', views.BookmarkView.as_view(), name='bookmark'),
    path('show/change/profile/', views.ShowChangeProfileView.as_view(), name='show_change_profile'),
    path('change/profile/password/', views.ChangePasswordView.as_view(), name='change_password_profile'),
    path('change/profile/info/', views.ChangeProfileView.as_view(), name='change_info_profile'),
    path('delete/send/otpcode/', views.OtpDeleteUserView.as_view(), name='send_otp_delete'),
    path('delete/user/', views.DeleteUserView.as_view(), name='delete_user')
]
