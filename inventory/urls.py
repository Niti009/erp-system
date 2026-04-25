from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Leave Applications
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('leave/view/', views.view_leaves, name='view_leaves'),

    # Attendance - punch in/out and history
    path('attendance/punch_in/', views.punch_in_view, name='punch_in'),
    path('attendance/punch_out/', views.punch_out_view, name='punch_out'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),

    # File Upload & Export
    path('upload/', views.upload_file, name='upload_file'),
    path('export/products/', views.export_products_csv, name='export_products_csv'),
]
