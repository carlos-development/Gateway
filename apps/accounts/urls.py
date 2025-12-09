from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Perfil
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('profile/change-password/', views.change_password_view, name='change_password'),

    # Direcciones de envío
    path('address/create/', views.address_create_view, name='address_create'),
    path('address/<int:address_id>/update/', views.address_update_view, name='address_update'),
    path('address/<int:address_id>/delete/', views.address_delete_view, name='address_delete'),

    # Perfil empresarial
    path('business-profile/', views.business_profile_view, name='business_profile'),
]
