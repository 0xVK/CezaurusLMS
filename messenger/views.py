from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from messenger.models import *
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, reverse
from django.contrib import messages
from profiler.models import Friendship
from django.db.models import Q


@login_required()
def my_messages(request):

    if 'show' not in request.GET:
        show_type = 'inbox'
    else:
        show_type = request.GET.get('show').strip()

        try:
            show_type = request.GET.get('show')
            if show_type not in ['inbox', 'outbox']:
                show_type = 'inbox'

        except Exception:
            show_type = 'inbox'

    data = dict()

    if show_type == 'inbox':
        inbox_messages = Message.objects.get_inbox(request.user)
        data['messages_list'] = inbox_messages
        return render(request, 'messenger/messages.html', data)

    if show_type == 'outbox':
        outbox_messages = Message.objects.get_outbox(request.user)
        data['messages_list'] = outbox_messages
        return render(request, 'messenger/messages_sent.html', data)


@login_required()
def show_message(request, m_id):

    m = get_object_or_404(Message, id=m_id)

    if request.user != m.from_user and request.user != m.to_user:
        messages.error(request, 'Ви не можете переглядати це повідомлення.')
        return redirect(reverse('my_messages'))

    is_sent = m.to_user != request.user

    data = {
        'message': m,
        'is_sent': is_sent,
    }

    if not is_sent:
        m.is_read = True
        m.save()

    return render(request, 'messenger/message.html', data)


@login_required()
def answer_message(request, m_id):

    if not request.method == 'POST':
        messages.error(request, 'Помилка відправлення.')
        return redirect(reverse('my_messages'))

    m = get_object_or_404(Message, id=m_id, to_user=request.user)

    answer_to_user = get_object_or_404(User, username=m.from_user.username)

    text = request.POST.get('text')[:1000]
    text = text.strip()

    if not text:
        return redirect(m)

    Message(to_user=answer_to_user, from_user=request.user, text=text).save()
    messages.success(request, 'Повідомлення до {} успішно відправлено.'.format(answer_to_user.get_full_name()))

    return redirect(reverse('my_messages'))


@login_required()
def delete_message(request, m_id):

    m = get_object_or_404(Message, id=m_id)

    if request.user != m.from_user and request.user != m.to_user:
        messages.error(request, 'Ви не можете видаляти це повідомлення.')
        return redirect(reverse('my_messages'))

    m.delete()
    messages.success(request, 'Повідомлення успішно видалено.')

    return redirect(reverse('my_messages'))


def send_message(request):

    if request.method == 'GET':
        return HttpResponseForbidden('Помилковий запит')

    to_username = request.POST.get('to_username')
    to_user = get_object_or_404(User, username=to_username)
    text = request.POST.get('text')
    text = text.strip()

    if Friendship.objects.are_friends(to_user, request.user) and text:
        Message(to_user=to_user, from_user=request.user, text=text).save()

    messages.success(request, 'Повідомлення успішно надіслано!')
    return redirect(reverse('profile', args=[to_username]))


def show_messages_history(request, m_id):

    m = get_object_or_404(Message, id=m_id)

    if request.user != m.from_user and request.user != m.to_user:
        messages.error(request, 'Ви не можете переглядати це повідомлення.')
        return redirect(reverse('my_messages'))

    messages_history = Message.objects.filter(
        Q(to_user=m.to_user, from_user=m.from_user) |
        Q(to_user=m.from_user, from_user=m.to_user),
    )

    return render(request, 'messenger/messages_history.html', {'m_history_list': messages_history})
