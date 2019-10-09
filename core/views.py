from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now

import short_url

from .forms import RegisterForm, GroupCreationForm
from .models import User, Group, Membership, Profile, Transaction
from .tokens import account_activation_token


def index(request):
  return redirect('login')

def register(request):
  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.is_active = False
      user.save()
      current_site = get_current_site(request)
      subject = 'Activate Your Esusu Account'
      uid = short_url.encode_url(user.pk)
      message = render_to_string('account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': uid,
        'token': account_activation_token.make_token(user),
      })
      send_mail(
        subject,
        message,
        'paschmaria@email.com',
        [user.email_address],
        fail_silently=False)
      return redirect('welcome')
  else:
    form = RegisterForm()

  context = {
    'form': form
  }

  return render(request, 'register.html', context=context)

@login_required
def dashboard(request):
  return render(request, 'dashboard/dashboard.html')

@login_required
def groups(request):
  try:
    groups = Group.objects.filter(is_public=True)
    popular = Group.objects.annotate(
                    memberships_count=Count('memberships')).filter(
                      memberships_count__gte=2, is_public=True)
  except ObjectDoesNotExist:
    groups = None

  membership = None
  if groups is not None:
    for group in groups:
      membership = Membership.objects.filter(group=group)
      cg_d = short_url.encode_url(group.pk)

  context = {
    'groups': groups,
    'popular_groups': popular,
    'membership': membership,
    'cg_d': cg_d,
  }
  return render(request, 'dashboard/groups.html', context=context)

@login_required
def group(request, cg_d):
  if cg_d:
    gid = short_url.decode_url(cg_d)
    group = get_object_or_404(Group, pk=gid)

    page = request.GET.get('page', 1)
    paginator = Paginator(group.memberships.all(), 10)

    try:
        members = paginator.page(page)
    except PageNotAnInteger:
        members = paginator.page(1)
    except EmptyPage:
        members = paginator.page(paginator.num_pages)
    
  current_site = get_current_site(request)

  context = {
    'group': group,
    'members': members,
    'cg_d': cg_d,
    'domain': current_site.domain
  }
  return render(request, 'dashboard/group.html', context=context)

@login_required
def create_group(request):
  if request.method == 'POST':
    form = GroupCreationForm(request.POST, request.FILES)
    if form.is_valid():
      group = form.save(commit=False)
      group.admin = request.user
      group.save()
      group.members.add(request.user)
      group.memberships.date_joined = now()
      gid = short_url.encode_url(group.pk)
      url = reverse('group', kwargs={'cg_d': gid})
      return redirect(url)
  else:
    form = GroupCreationForm()
  
  context = {
    'form': form
  }
  return render(request, 'dashboard/create_group.html', context=context)

@login_required
def profile(request):
  return render(request, 'dashboard/profile.html')

def welcome(request):
  return render(request, 'welcome.html')

def activate(request, uidb64, token):
  if uidb64:
    uid = short_url.decode_url(uidb64)
    user = get_object_or_404(User, pk=uid)

  if user and account_activation_token.check_token(user, token):
    user.is_active = True
    user.email_confirmed = True
    user.save()
    login(request, user)
    return redirect('dashboard')
  else:
    return render(request, 'login.html')
