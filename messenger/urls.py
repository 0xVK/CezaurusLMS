from django.conf.urls import url
import messenger.views as mess_views

urlpatterns = [

    url(r'^messages/$', mess_views.my_messages, name='my_messages'),
    url(r'^messages/(?P<m_id>\d+)/$', mess_views.show_message, name='show_message'),
    url(r'^messages/(?P<m_id>\d+)/answer/$', mess_views.answer_message, name='answer_message'),
    url(r'^messages/(?P<m_id>\d+)/delete/$', mess_views.delete_message, name='delete_message'),
    url(r'^a/show_messages_history/(?P<m_id>\d+)/$', mess_views.show_messages_history, name='show_messages_history'),

]