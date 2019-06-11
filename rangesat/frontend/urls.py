"""rangesat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

from .views import ranch_view, pasture_view, register, index_view
from django.urls import path, include

urlpatterns = [
    path('', index_view, name='index'),
    path('r/<str:ranch>/', ranch_view, name='ranch'),
    path('p/<str:pasture>/', pasture_view, name='pasture'),
    path('register', register, name='register')
]
