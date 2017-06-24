from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.translation import ugettext as _
from core.forms import SignUpForm
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from communities.models import Community
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from profiler.models import ProfileWallPost


def index(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not User.objects.filter(username=username).exists():
                messages.error(request, _('Користувача з таким логіном не існує'))

            else:
                if user:
                    login(request, user)
                else:
                    messages.error(request, _('Неправильний пароль'))

        return redirect(reverse('index'))

    if request.method == 'GET':

        if request.user.is_authenticated():
            username = request.user.username

            return redirect(reverse('profile', args=[username]))

        else:

            return render(request, 'core/index.html')


def signup(request):

    if request.method == 'GET':

        signup_fm = SignUpForm()

        return render(request, 'core/registration.html', context={'form': signup_fm})

    if request.method == 'POST':

        signup_fm = SignUpForm(request.POST)
        if signup_fm.is_valid():
            username = signup_fm.cleaned_data.get('username')
            first_name = signup_fm.cleaned_data.get('first_name')
            last_name = signup_fm.cleaned_data.get('last_name')
            email = signup_fm.cleaned_data.get('email')
            password = signup_fm.cleaned_data.get('password1')
            sex = signup_fm.cleaned_data.get('sex')
            birthday = signup_fm.cleaned_data.get('birthday')
            location = signup_fm.cleaned_data.get('location')
            school = signup_fm.cleaned_data.get('school')
            form = signup_fm.cleaned_data.get('form')

            u = User.objects.create_user(username=username, first_name=first_name,
                                         last_name=last_name, email=email, password=password)

            u.profile.sex = sex
            u.profile.birthday = birthday
            u.profile.location = location
            u.profile.school = school
            u.profile.form = form
            u.profile.save()

            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect(reverse('profile', args=[username]))
        else:
            print(signup_fm.errors)

    return render(request, 'core/registration.html', context={'form': signup_fm})


def username_validate(request):

    username = request.GET.get('username')
    sign_up_fm = SignUpForm()
    data = {}

    try:
        for validator in sign_up_fm.fields['username'].validators:
            validator(username)

    except ValidationError as e:
        data['info'] = e.message

    if data.get('info'):
        is_okey = False
    else:
        is_okey = True
        data['info'] = _('Логін доступний')

    data['is_okey'] = is_okey

    return JsonResponse(data)


@login_required()
def people(request):

    users = User.objects.all().order_by('-date_joined')[:30]

    return render(request, 'core/people.html', context={'users': users})


@login_required()
def communities(request):

    c = Community.objects.all().order_by('name')[:30]

    return render(request, 'core/all_communities.html', context={'communities': c})


@login_required()
def search(request):

    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()

        if len(querystring) == 0:
            return redirect('/search/')

        try:
            search_type = request.GET.get('type')
            if search_type not in ['users', 'feed']:
                search_type = 'feed'

        except Exception:
            search_type = 'feed'

        count = {}
        results = {}

        results['users'] = User.objects.filter(
            Q(username__icontains=querystring) |
            Q(first_name__icontains=querystring) |
            Q(last_name__icontains=querystring))

        results['feed'] = ProfileWallPost.objects.filter(text__icontains=querystring)

        count['users'] = results['users'].count()
        count['feed'] = results['feed'].count()

        if not count['feed'] and count['users']:
            search_type = 'users'

        elif count['feed'] and not count['users']:
            search_type = 'feed'

        data = {
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        }

        return render(request, 'core/search_results.html', data)

    else:
        return render(request, 'core/search.html')

