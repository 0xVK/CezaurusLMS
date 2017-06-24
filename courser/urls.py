from django.conf.urls import url
import courser.views as courser_views


urlpatterns = [

    url(r'^c/(?P<c_id>\d+)/courses/$', courser_views.courses, name='courses'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/$', courser_views.course, name='course'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/edit/$', courser_views.edit_course, name='edit_course'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/add_lecture/$', courser_views.create_lecture, name='create_lecture'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/add_dictation/$', courser_views.create_dictation,
        name='create_dictation'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/add_independent_work/$', courser_views.create_independent_work,
        name='create_independent_work'),

    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/$', courser_views.course_step, name='course_step'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/review/$', courser_views.review_independent_work,
        name='review_independent_work'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/edit/$', courser_views.step_edit, name='edit_step'),

    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/write_dictation/$', courser_views.write_dictation,
        name='write_dictation'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/check_dictation/$', courser_views.check_dictation,
        name='check_dictation'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/dictation_result/(?P<d_id>\d+)/$',
        courser_views.dictation_result, name='dictation_result'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/upload_file$',
        courser_views.upload_answer_file, name='upload_answer_file'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/delete_file/(?P<f_id>\d+)',
        courser_views.delete_answer_file, name='delete_answer_file'),

    url(r'^a/up_course(?P<c_id>\d+)/(?P<cr_id>\d+)/(?P<s_id>\d+)/$', courser_views.action_up_step,
        name='up_course_step'),
    url(r'^a/down_course(?P<c_id>\d+)/(?P<cr_id>\d+)/(?P<s_id>\d+)/$', courser_views.action_down_step,
        name='down_course_step'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/(?P<s_id>\d+)/delete/$', courser_views.action_delete_step,
        name='course_step_delete'),
    url(r'^c/(?P<c_id>\d+)/courses/(?P<cr_id>\d+)/delete/$', courser_views.action_delete_course,
        name='course_delete'),
    url(r'^answer/(?P<a_id>\d+)/$', courser_views.review_answer, name='review_answer'),
]