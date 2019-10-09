from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.index, name='landing'),
    path("register/", views.register, name="register"),
    path("welcome/", views.welcome, name="welcome"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("groups/", views.groups, name="groups"),
    path("create-group/", views.create_group, name="create_group"),
    path("profile/", views.profile, name="profile"),

    re_path(r'^group/(?P<cg_d>[0-9A-Za-z]+)/$', views.group, name="group"),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
