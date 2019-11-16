"""feedback URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path
from django.urls import path
from webapp.views import IndexView, ProductView, ProductCreateView, \
    ProductUpdateView, ProductDeleteView, ReviewCreateView, ReviewForProductCreateView, \
    ReviewListView, ReviewUpdateView, ReviewDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('product/<int:pk>/', ProductView.as_view(), name='product_view'),
    path('product/add/', ProductCreateView.as_view(), name='product_add'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('comments/', ReviewListView.as_view(), name='comment_list'),
    path('comment/add/', ReviewCreateView.as_view(), name='comment_add'),
    path('comment/<int:pk>/edit/', ReviewUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', ReviewDeleteView.as_view(), name='comment_delete'),
    path('product/<int:pk>/add-comment/', ReviewForProductCreateView.as_view(), name='article_comment_create'),
]
