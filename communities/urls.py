from django.conf.urls import url
import communities.views as comm_views
urlpatterns = [

    url(r'^my_communities/$', comm_views.my_communities, name='my_communities'),
    url(r'^my_communities/requests/$', comm_views.my_communities_invites, name='communities_invites'),
    url(r'^my_communities/create/$', comm_views.create_community, name='create_community'),
    url(r'^my_communities/invite_code/$', comm_views.input_invite_code, name='input_invite_code_community'),

    url(r'^c/(?P<c_id>\d+)/$', comm_views.community, name='community'),
    url(r'^c/(?P<c_id>\d+)/leave/$', comm_views.community_leave, name='community_leave'),

    url(r'^c/(?P<c_id>\d+)/settings/$', comm_views.settings, name='community_settings'),
    url(r'^c/(?P<c_id>\d+)/settings/members/$', comm_views.settings_members, name='community_settings_members'),
    url(r'^c/(?P<c_id>\d+)/settings/invitation_code/$', comm_views.settings_invitation_code,
        name='community_settings_invitation_code'),
    url(r'^c/(?P<c_id>\d+)/settings/members/remove/(?P<username>[^/]+)/$', comm_views.remove_member,
        name='community_remove_member'),
    url(r'^c/(?P<c_id>\d+)/settings/members/make_admin/(?P<username>[^/]+)/$', comm_views.make_administrator,
        name='community_make_admin'),
    url(r'^c/(?P<c_id>\d+)/settings/members/remove_admin/(?P<username>[^/]+)/$', comm_views.remove_administrator,
        name='community_remove_admin'),
    url(r'^c/(?P<c_id>\d+)/settings/invite/$', comm_views.send_invite, name='community_invite'),
    url(r'^c/(?P<c_id>\d+)/settings/cancel_invite/(?P<i_id>\d+)/$', comm_views.cancel_invite,
        name='community_cancel_invite'),
    url(r'^c/(?P<c_id>\d+)/settings/invite/sent/$', comm_views.sent_invites, name='community_sent_invites'),

    url(r'^c/(?P<c_id>\d+)/members/$', comm_views.members, name='members'),
    url(r'^c/(?P<c_id>\d+)/add_wallpost/$', comm_views.add_wallpost_to_com, name='add_com_wallpost'),

    url(r'^c/(?P<c_id>\d+)/discussions/$', comm_views.discussions, name='discussions'),
    url(r'^c/(?P<c_id>\d+)/discussions/create/$', comm_views.create_discussion, name='create_discussion'),
    url(r'^c/(?P<c_id>\d+)/discussions/(?P<d_id>\d+)$', comm_views.discussion, name='discussion'),
    url(r'^c/(?P<c_id>\d+)/discussions/(?P<d_id>\d+)/comment/$',
        comm_views.add_comment_to_discussion, name='discussion_add_comment'),
    url(r'^c/(?P<c_id>\d+)/discussions/(?P<d_id>\d+)/remove/$', comm_views.discussion_remove, name='discussion_remove'),
    url(r'^c/(?P<c_id>\d+)/discussions/(?P<d_id>\d+)/edit$', comm_views.discussion_edit, name='discussion_edit'),

    url(r'^a/delete_com_wall_post/(?P<c_id>\d+)/(?P<p_id>\d+)/$', comm_views.action_delete_com_wall_post,
        name='delete_com_wall_post'),
]

