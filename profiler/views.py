from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from profiler.exceptions import AlreadyFriendsError, AlreadyExistsError, AlreadySentRequestToYouError
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from profiler.models import ProfileWallPost, Friendship, FriendshipRequest
from profiler.forms import ProfileForm, ChangePasswordForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth import update_session_auth_hash
from PIL import Image
from django.conf import settings as django_settings
import os
from django.http import HttpResponseForbidden


@login_required()
def _profile(request, profile_user, active):

    is_user_profile = request.user.username == profile_user.username
    is_friend = False
    if not is_user_profile:
        is_friend = Friendship.objects.are_friends(profile_user, request.user)

    data = {
        'profile_user': profile_user,
        'active': active,
        'is_user_profile': is_user_profile,
        'is_friend': is_friend
            }

    if active == 'W':
        user_wall_posts = profile_user.profile.get_wall_posts()
        data['posts'] = user_wall_posts

    elif active == 'F':
        user_friends = Friendship.objects.get_friends(profile_user)
        data['friends'] = user_friends

    elif active == 'C':
        user_communities = profile_user.profile.get_communities()
        data['communities'] = user_communities

    elif active == 'A':
        pass

    if not is_friend and not is_user_profile:
        is_sent_request = Friendship.objects.is_sent_request(to_user=profile_user, from_user=request.user)
        is_request = Friendship.objects.is_sent_request(to_user=request.user, from_user=profile_user)

        data['is_sent_request'] = is_sent_request
        data['is_request'] = is_request

    return render(request, 'profiler/profile.html', context=data)


@login_required()
def profile_wall_posts(request, username):

    profile_user = get_object_or_404(User, username=username)
    return _profile(request, profile_user, 'W')


@login_required()
def profile_friends(request, username):

    profile_user = get_object_or_404(User, username=username)
    return _profile(request, profile_user, 'F')


@login_required()
def profile_communities(request, username):

    profile_user = get_object_or_404(User, username=username)
    return _profile(request, profile_user, 'C')


@login_required()
def profile_awards(request, username):

    profile_user = get_object_or_404(User, username=username)
    return _profile(request, profile_user, 'A')


@login_required()
def add_wallpost(request, username):

    if request.method == 'POST':

        profile_user = get_object_or_404(User, username=username)

        if Friendship.objects.are_friends(profile_user, request.user) or profile_user == request.user:
            text = request.POST.get('wall_post_text')[:800]
            text = text.strip()

            if len(text) > 0:
                ProfileWallPost(to_user=User.objects.get(username=username),
                                from_user=request.user,
                                text=text).save()

        return redirect(reverse('profile', args=[username]))


@login_required()
def action_delete_wall_post(request, username, p_id):

    post = get_object_or_404(ProfileWallPost, id=p_id)

    if not post.to_user == request.user and not post.from_user == request.user:
        return redirect(reverse('profile', args=[username]))

    post.delete()
    return redirect(reverse('profile', args=[username]))


@login_required()
def friends(request):

    user_friends = Friendship.objects.get_friends(request.user)
    friends_requests_count = Friendship.objects.requests(request.user)
    friends_sent_requests_count = Friendship.objects.sent_requests(request.user)

    data = {'friends_list': user_friends,
            'friends_requests_count': len(friends_requests_count),
            'friends_count': len(user_friends),
            'friends_sent_requests_count': len(friends_sent_requests_count),
            }

    return render(request, 'profiler/friends.html', context=data)


@login_required()
def friends_requests(request):

    user_friends = Friendship.objects.get_friends(request.user)
    user_friends_requests = Friendship.objects.requests(request.user)
    friends_sent_requests_count = Friendship.objects.sent_requests(request.user)

    data = {
        'friends_requests': user_friends_requests,
        'friends_requests_count': len(user_friends_requests),
        'friends_count': len(user_friends),
        'friends_sent_requests_count': len(friends_sent_requests_count),
    }

    return render(request, 'profiler/friends_requests.html', context=data)


@login_required()
def friends_sent_requests(request):

    user_sent_friends_requests = Friendship.objects.sent_requests(request.user)
    user_friends = Friendship.objects.get_friends(request.user)
    user_friends_requests = Friendship.objects.requests(request.user)

    data = {
        'friends_sent_requests': user_sent_friends_requests,
        'friends_sent_requests_count': len(user_sent_friends_requests),
        'friends_count': len(user_friends),
        'friends_requests_count': len(user_friends_requests),

    }

    return render(request, 'profiler/friends_sent_requests.html', context=data)


@login_required()
def action_send_friend_request(request):

    if request.method == 'POST':
        to_username = request.POST.get('to_user')
        to_user = User.objects.get(username=to_username)
        from_user = request.user

        try:
            Friendship.objects.add_friend_request(to_user=to_user, from_user=from_user)
        except (ValidationError, AlreadyExistsError, AlreadyFriendsError, AlreadySentRequestToYouError):
            pass

        finally:
            go_next = request.META.get('HTTP_REFERER')
            if go_next:
                return redirect(go_next)

    return redirect(reverse('profile', args=[to_username]))


@login_required()
def action_cancel_friend_request(request):

    if request.method == 'POST':
        to_username = request.POST.get('to_user')
        to_user = User.objects.get(username=to_username)
        from_user = request.user

        get_object_or_404(FriendshipRequest, to_user=to_user, from_user=from_user).delete()

        go_next = request.META.get('HTTP_REFERER')
        if go_next:
            return redirect(go_next)

    return redirect(reverse('profile', args=[to_username]))


@login_required()
def action_accept_friend_request(request):

    if request.method == 'POST':
        request_from_username = request.POST.get('request_from_user')
        request_from_user = User.objects.get(username=request_from_username)
        friends_request = get_object_or_404(FriendshipRequest, to_user=request.user, from_user=request_from_user)

        friends_request.accept()

        go_next = request.META.get('HTTP_REFERER')
        if go_next:
            return redirect(go_next)

    return redirect(reverse('friends_requests'))


@login_required()
def action_reject_friend_request(request):

    if request.method == 'POST':
        request_from_username = request.POST.get('request_from_user')
        request_from_user = User.objects.get(username=request_from_username)
        friends_request = get_object_or_404(FriendshipRequest, to_user=request.user, from_user=request_from_user)

        friends_request.reject()

        go_next = request.META.get('HTTP_REFERER')
        if go_next:
            return redirect(go_next)

    return redirect(reverse('friends_requests'))


@login_required()
def action_remove_friend(request):

    if request.method == 'POST':
        to_username = request.POST.get('to_user')
        to_user = get_object_or_404(User, username=to_username)

        if Friendship.objects.are_friends(to_user, request.user):
            Friendship.objects.remove_friend(request.user, to_user)

            go_next = request.META.get('HTTP_REFERER')

            if go_next:
                return redirect(go_next)

    return redirect(reversed('friends'))


@login_required()
def action_send_message(request):
    pass


@login_required()
def groups(request):

    data = {}

    return render(request, 'profiler/groups.html', context=data)


@login_required()
def settings_profile(request):

    user = request.user

    if request.method == 'POST':
        profile_fm = ProfileForm(request.POST)

        if profile_fm.is_valid():
            user.first_name = profile_fm.cleaned_data.get('first_name')
            user.last_name = profile_fm.cleaned_data.get('last_name')
            user.email = profile_fm.cleaned_data.get('email')
            user.profile.location = profile_fm.cleaned_data.get('location')
            user.profile.school = profile_fm.cleaned_data.get('school')
            user.profile.form = profile_fm.cleaned_data.get('form')
            user.profile.birthday = profile_fm.cleaned_data.get('birthday')
            user.profile.status = profile_fm.cleaned_data.get('status')
            user.save()
            messages.success(request, _('Профіль успішно збережено'))

    if request.method == 'GET':

        try:
            profile_fm = ProfileForm(instance=user, initial={
                'location': user.profile.location,
                'school': user.profile.school,
                'form': user.profile.form,
                'status': user.profile.status,
                'birthday': user.profile.birthday.strftime('%d.%m.%Y'),
            })
        except:
            pass

    return render(request, 'profiler/settings_profile.html', {'form': profile_fm})


@login_required()
def settings_picture(request):

    uploaded_picture = False
    try:
        if request.GET.get('upload_picture') == 'uploaded':
            uploaded_picture = True

    except Exception:
        pass

    return render(request, 'profiler/settings_picture.html', {'uploaded_picture': uploaded_picture})


@login_required()
def upload_picture(request):
    try:
        profile_pictures_folder = django_settings.MEDIA_ROOT + '/profile_pictures/'

        f = request.FILES['picture']
        filename = profile_pictures_folder + request.user.username + '_tmp.jpg'

        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        Image.open(filename).convert('RGB').save(filename)
        im = Image.open(filename)
        width, height = im.size

        if width < 200 or height < 200:
            messages.error(request, _('Зображення замале'))
            im.save(filename)
            os.remove(filename)
            return redirect(reverse('settings_picture'))

        if width > 460:
            new_width = 460
            new_height = (height * 460) / width
            new_size = new_width, new_height
            im.thumbnail(new_size, Image.ANTIALIAS)
            im.save(filename)

        return redirect('/settings/picture/?upload_picture=uploaded')

    except Exception as e:
        print(e)
        return redirect(reverse('settings_picture'))


@login_required()
def save_uploaded_picture(request):
    try:
        sx = str(request.POST.get('x'))
        sy = str(request.POST.get('y'))
        sw = str(request.POST.get('w'))
        sh = str(request.POST.get('h'))

        if sx.count('.'):
            tx = sx.split('.')[0]
        if not sx.count('.'):
            tx = sx
        if sy.count('.'):
            ty = sy.split('.')[0]
        if not sy.count('.'):
            ty = sy
        if sw.count('.'):
            tw = sw.split('.')[0]
        if not sw.count('.'):
            tw = sw
        if sh.count('.'):
            th = sh.split('.')[0]
        if not sh.count('.'):
            th = sh

        x = int(tx)
        y = int(ty)
        w = int(tw)
        h = int(th)

        tmp_filename = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '_tmp.jpg'
        filename = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '.jpg'

        if w < 180 or h < 220:
            messages.error(request, _('Занадто мала область виділення. Спробуйте виділити більше.'))
            os.remove(tmp_filename)
            return redirect(reverse('settings_picture'))

        im = Image.open(tmp_filename)
        cropped_im = im.crop((x, y, w+x, h+y))
        cropped_im.save(filename)
        os.remove(tmp_filename)

        messages.success(request, _('Фотографію успішно оновлено!'))

    except Exception as e:
        print(e)
        pass

    return redirect(reverse('settings_picture'))


@login_required()
def settings_password(request):

    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Пароль успішно змінено.'))
    else:
        form = ChangePasswordForm(instance=user)

    return render(request, 'profiler/settings_password.html', {'form': form})