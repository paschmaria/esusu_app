"""esusu_app URL Configuration

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from core.forms import LoginForm


class CustomLoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
             self.request.session.set_expiry(0)
             self.request.session.modified = True
        return super(CustomLoginView, self).form_valid(form)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/", CustomLoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login/'), name='logout'),
    path('password/reset/',
        auth_views.PasswordResetView.as_view(from_email='paschmaria@email.com',
        html_email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt',
        template_name='password_reset_form.html'),
        name='password_reset'),
    path('password/reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password/reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),

    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
