from django.shortcuts import render, get_object_or_404, reverse, redirect
from communities.models import *
from profiler.models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from communities.forms import *
from django.contrib import messages
from django.utils.translation import ugettext as _


@login_required()
def my_communities(request):

    user = request.user
    user_communities = user.profile.communities.all()
    user_invites = Community.objects.get_invites(request.user)

    data = {
        'my_communities': user_communities ,
        'my_invites_count': len(user_invites)
    }

    return render(request, 'communities/my-communities.html', data)


@login_required()
def my_communities_invites(request):

    user_invites = Community.objects.get_invites(request.user)
    user_communities = request.user.profile.communities.all()

    data = {
        'my_invites': user_invites,
        'user_communities_count': len(user_communities)
    }

    if request.method == 'GET':
        pass

    if request.method == 'POST':

        rez = request.POST.get('r')
        inv_id = request.POST.get('id_inv')

        inv = get_object_or_404(CommunityInvite, id=inv_id, to_user=request.user)

        if rez == 'accept':
            inv.accept()

        if rez == 'reject':
            inv.reject()

    return render(request, 'communities/my-communities-invites.html', data)


@login_required()
def create_community(request):

    if not request.user.profile.is_expanded:
        return HttpResponseForbidden('У Вас немає прав на створення стільноти. Зверніться до адміністрації сайту.')

    if request.method == 'GET':

        com_fm = CommunityForm()

        return render(request, 'communities/create-community.html', {'form': com_fm})

    if request.method == 'POST':

        com_fm = CommunityForm(request.POST)

        if com_fm.is_valid():

            name = com_fm.cleaned_data.get('name')
            description = com_fm.cleaned_data.get('description')

            new_group = Community.objects.create(name=name, description=description)
            new_group.save()
            new_group.administrators.add(request.user)
            request.user.profile.communities.add(new_group)
            return redirect(reverse('community', args=[new_group.id]))


@login_required()
def community(request, c_id):

    is_admin = False

    c = get_object_or_404(Community, id=c_id)

    if request.user in c.administrators.all():
        is_admin = True

    if c not in request.user.profile.communities.all():
        return redirect(reverse('my_communities'))

    comm_wall_posts = CommunityWallPost.objects.filter(to_community=c)

    data = {
        'posts': comm_wall_posts,
        'com': c,
        'is_admin': is_admin,
    }

    return render(request, 'communities/community.html', context=data)


@login_required()
def add_wallpost_to_com(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    if c not in request.user.profile.communities.all():
        return redirect(reverse('my_communities'))

    text = request.POST.get('wall_post_text')
    text = text.strip()

    if len(text) > 0:
        CommunityWallPost(to_community=c, from_user=request.user, text=text).save()

    return redirect(reverse('community', args=[c.id]))


@login_required()
def discussions(request, c_id):

    c = get_object_or_404(Community, id=c_id)
    is_admin = False

    if request.user in c.administrators.all():
        is_admin = True

    topics = Discussion.objects.filter(community=c)

    if c not in request.user.profile.communities.all():
        return redirect(reverse('my_communities'))

    data = {
        'com': c,
        'discussions': topics,
        'is_admin': is_admin,
    }
    return render(request, 'communities/discussions.html', data)


@login_required()
def discussion(request, c_id, d_id):

    d = get_object_or_404(Discussion, id=d_id)
    c = get_object_or_404(Community, id=c_id)
    is_admin = False

    if request.user in c.administrators.all():
        is_admin = True
    else:
        if request.user == d.author:
            is_admin = True

    if c not in request.user.profile.communities.all():
        return redirect(reverse('my_communities'))

    data = {
        'discussion': d,
        'comments': d.get_comments(),
        'com': c,
        'is_admin': is_admin,
    }

    return render(request, 'communities/discussion.html', data)


@login_required()
def create_discussion(request, c_id):

    c = get_object_or_404(Community, id=c_id)
    u = request.user

    if request.method == 'GET':

        d_fm = DiscussionForm()

        data = {
            'com': c,
            'form': d_fm,
        }

    if request.method == 'POST':

        d_fm = DiscussionForm(request.POST)

        if d_fm.is_valid():

            title = d_fm.cleaned_data.get('title')
            title = title.capitalize()
            text = d_fm.cleaned_data.get('text')
            d = Discussion(community=c, author=u, title=title, text=text)
            d.save()

            return redirect(reverse('discussion', args=[c.id, d.id]))

    return render(request, 'communities/discussion-create.html', data)


@login_required()
def discussion_edit(request, c_id, d_id):

    d = get_object_or_404(Discussion, id=d_id)
    c = get_object_or_404(Community, id=c_id)

    if (request.user not in c.administrators.all()) and (not request.user == d.author):
        return redirect(reverse('community', args=[c.id]))

    data = {
        'com': c,
        'discussion': d,
    }

    if request.method == 'POST':

        d_fm = DiscussionForm(request.POST)

        if d_fm.is_valid():
            title = d_fm.cleaned_data.get('title')
            text = d_fm.cleaned_data.get('text')

            d.title = title
            d.text = text
            d.save()

            return redirect(reverse('discussion', args=[c.id, d.id]))

        else:

            data['form'] = d_fm

            return render(request, 'communities/discussion-edit.html', data)

    if request.method == 'GET':

        if not (request.user == d.author or request.user in c.administrators.all()):
            return HttpResponseForbidden('Немає доступу до редагування')

        d_fm = DiscussionForm(initial={
            'title': d.title,
            'text': d.text,
        })

        data['form'] = d_fm

        return render(request, 'communities/discussion-edit.html', data)


@login_required()
def discussion_remove(request, c_id, d_id):

    d = get_object_or_404(Discussion, id=d_id)
    c = get_object_or_404(Community, id=c_id)

    if (request.user not in c.administrators.all()) and (not request.user == d.author):
        return redirect(reverse('community', args=[c.id]))

    d.delete()

    return redirect(reverse('discussions', args=[c.id]))


@login_required()
def add_comment_to_discussion(request, c_id, d_id):

    if request.method == 'POST':
        c = get_object_or_404(Community, id=c_id)
        d = get_object_or_404(Discussion, id=d_id, community=c)

        if c not in request.user.profile.communities.all():
            return HttpResponseForbidden('Немає доступу до коментування обговорень цієї спільноти!')

        text = request.POST.get('comment_text')[:1000]
        text = text.strip()

        if len(text) > 0:
            DiscussionComment(to_discussion=d, from_user=request.user, text=text).save()

        return redirect(d)
    return HttpResponseForbidden('Неправильний тип запиту.')


@login_required()
def settings(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    if request.user not in c.administrators.all():
        return redirect(reverse('community', args=[c.id]))

    if request.method == 'GET':
        com_fm = CommunityForm(initial={
            'name': c.name,
            'description': c.description,
        })

        data = {
            'form': com_fm,
            'com': c,
        }

    if request.method == 'POST':

        com_fm = CommunityForm(request.POST)

        data = {
            'form': com_fm,
            'com': c,
        }

        if com_fm.is_valid():
            c.name = com_fm.cleaned_data.get('name')
            c.description = com_fm.cleaned_data.get('description')
            c.save()
            messages.success(request, _('Інформацію успішно змінено'))
        else:
            messages.error(request, com_fm.errors)

    return render(request, 'communities/community-settings.html', data)


@login_required()
def settings_members(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    if request.user not in c.administrators.all():
        return redirect(reverse('community', args=[c.id]))

    if request.method == 'GET':

        all_members = c.get_members.all()  # ссылается на профиль
        # list_members = []

        data = {
            'com': c,
            'members': all_members,
        }

    return render(request, 'communities/settings-members.html', data)


@login_required()
def settings_invitation_code(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    if request.user not in c.administrators.all():
        return redirect(reverse('community', args=[c.id]))

    if request.method == 'POST':
        action = request.POST.get('code_act')

        if action:
            if action == 'create':
                c.generate_invitation_code()
            if action == 'delete':
                c.invitation_code = ''
                c.save()

    data = {
        'com': c,
        'code': c.invitation_code,
    }

    return render(request, 'communities/settings_invitation_code.html', data)


@login_required()
def send_invite(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    data = {
        'com': c,
    }

    if request.user not in c.administrators.all():
        return redirect(reverse('community', args=[c.id]))

    if request.method == 'GET':
        pass

    if request.method == 'POST':

        username = request.POST.get('username')

        try:
            user = User.objects.get(username__iexact=username)
            Community.objects.invite(user, c)
            messages.success(request, _('Запрошення надіслано.'))

        except User.DoesNotExist:
            messages.error(request, _('Користувача з таким логіном не існує'))

        except (AlreadyMemberError, InviteAlreadyExistsError) as ex:
            messages.error(request, ex.message)

        except:
            pass

    return render(request, 'communities/community-send-invite.html', data)


@login_required()
def community_leave(request, c_id):

    if request.method == 'GET':
        return redirect(reverse('community', args=[c_id]))

    if request.method == 'POST':

        com_id = request.POST.get('com_id')
        c = get_object_or_404(Community, id=com_id)

        if Community.objects.is_member(request.user, c):
            request.user.profile.communities.remove(c)

        return redirect(reverse('my_communities'))


@login_required()
def members(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    is_admin = False
    if request.user in c.administrators.all():
        is_admin = True

    all_members = c.get_members.all()  # ссылается на профиль

    data = {
        'com': c,
        'members': all_members,
        'is_admin': is_admin,
    }

    return render(request, 'communities/members.html', data)


@login_required()
def remove_member(request, c_id, username):

    c = get_object_or_404(Community, id=c_id)

    if request.method == 'POST':

        user_to_remove = get_object_or_404(User, username=username)
        administrators = c.administrators.all()

        if request.user not in administrators:
            return HttpResponseForbidden('Тільки адміністратор може видаляти учасників.')

        if request.user == user_to_remove:
            return HttpResponseForbidden('Не можна видалити себе')

        if c not in user_to_remove.profile.communities.all():
            return HttpResponseForbidden('Це не учасник спільноти')

        if user_to_remove in administrators:
            return HttpResponseForbidden('Ви не можете видалити адмінісратора спільноти.')

        user_to_remove.profile.communities.remove(c)

        messages.success(request, '{} був успішно видалений із спільноти'.format(user_to_remove.get_full_name()))

    return redirect(reverse('community_settings_members', args=[c.id]))


@login_required()
def make_administrator(request, c_id, username):

    c = get_object_or_404(Community, id=c_id)
    administrators = c.administrators.all()

    if request.method == 'POST':

        new_admin = get_object_or_404(User, username=username)

        if new_admin in administrators:
            return HttpResponseForbidden('Ця людина вже адміністратор.')

        if not new_admin.profile.is_expanded:
            return HttpResponseForbidden('Назначити адміністратора можна тільки з розширеним профілем.')

        if c not in new_admin.profile.communities.all():
            return HttpResponseForbidden('Адміністратор повинен бути учасником спільноти.')

        c.administrators.add(new_admin)

        messages.success(request, '{} був(ла) успішно назначеним адміністратором'.format(new_admin.get_full_name()))

    return redirect(reverse('community_settings_members', args=[c.id]))


@login_required()
def remove_administrator(request, c_id, username):

    c = get_object_or_404(Community, id=c_id)
    administrators = c.administrators.all()

    if request.method == 'POST':

        old_admin = get_object_or_404(User, username=username)

        if old_admin not in administrators:
            return HttpResponseForbidden('Це не адміністратор спільноти')

        if old_admin == request.user:
            return HttpResponseForbidden('Не можна забрати в себе абміністраторські права.')

        if c not in old_admin.profile.communities.all():
            return HttpResponseForbidden('Адміністратор повинен бути учасником спільноти.')

        c.administrators.remove(old_admin)

        messages.success(request, '{} був(ла) успішно позбавлений адміністраторських прав.'.format(old_admin.get_full_name()))

    return redirect(reverse('community_settings_members', args=[c.id]))


@login_required()
def sent_invites(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    if request.user not in c.administrators.all():
        return HttpResponseForbidden('Ви не адміністратор цієї спільноти.')

    data = {
        'com': c,
        'invites': c.get_sent_invites()
    }

    return render(request, 'communities/sent-invites.html', data)


@login_required()
def cancel_invite(request, c_id, i_id):

    c = get_object_or_404(Community, id=c_id)
    invite = get_object_or_404(CommunityInvite, id=i_id, from_community=c)

    if request.user not in c.administrators.all():
        return HttpResponseForbidden('Ви не адміністратор цієї спільноти.')

    messages.success(request, 'Запрошення до {} успішно видалено.'.format(invite.to_user.get_full_name()))
    invite.reject()

    return redirect(reverse('community_sent_invites', args=[c.id]))


@login_required()
def action_delete_com_wall_post(request, c_id, p_id):

    c = get_object_or_404(Community, id=c_id)
    post = get_object_or_404(CommunityWallPost, id=p_id, to_community=c)

    if request.user not in c.administrators.all() and not post.from_user == request.user:
        return redirect(reverse('community', args=[c.id]))

    post.delete()
    return redirect(reverse('community', args=[c.id]))


@login_required()
def input_invite_code(request):

    if request.method == 'POST':

        code = request.POST.get('code')
        try:
            comm = Community.objects.get(invitation_code=code)

            if comm in request.user.profile.communities.all():
                raise AlreadyMemberError('Ви вже є учасником цієї спільноти.')

            if CommunityInvite.objects.filter(to_user=request.user, from_community=comm).exists():
                invite = CommunityInvite.objects.get(to_user=request.user, from_community=comm)
                invite.reject()

            request.user.profile.communities.add(comm)
            return redirect(comm)

        except Community.DoesNotExist:
            messages.error(request, 'Такого інвайт коду не існує.')
        except AlreadyMemberError as ex:
            messages.error(request, ex.message)

    all_my_communities = request.user.profile.communities.all()
    all_my_invites = CommunityInvite.objects.filter(to_user=request.user)

    data = {
        'user_communities_count': len(all_my_communities),
        'user_communities_invites': len(all_my_invites),
    }

    return render(request, 'communities/enter_community_invite_code.html', data)