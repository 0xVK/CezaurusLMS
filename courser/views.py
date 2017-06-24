from django.shortcuts import render, redirect, reverse, get_object_or_404
from communities.models import Community
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from courser.models import *
from courser.forms import *
from django.contrib import messages
from django.core.exceptions import ValidationError
import os
import string
import random
from courser.DMP_algorithm import diff_match_patch as Dmp


@login_required()
def courses(request, c_id):

    c = get_object_or_404(Community, id=c_id)

    if c not in request.user.profile.communities.all():
        return HttpResponseForbidden('Немає доступу до курсів спільноти.')

    is_admin = False
    if request.user in c.administrators.all():
        is_admin = True

    data = {
        'com': c,
        'is_admin': is_admin,
    }

    if request.method == 'GET':

        course_fm = CourseForm()
        data['form'] = course_fm
        community_courses = Course.objects.filter(community=c)

        data['courses'] = community_courses

        return render(request, 'courser/courses.html', data)

    if request.method == 'POST':

        if is_admin:
            course_fm = CourseForm(request.POST)

            if course_fm.is_valid():
                name = course_fm.cleaned_data.get('name')
                description = course_fm.cleaned_data.get('description')

                new_course = Course(name=name, description=description, author=request.user, community=c)
                new_course.save()
                return redirect(new_course)

    return redirect(reverse('courses', args=[c.id]))


@login_required()
def course(request, c_id, cr_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id)

    if c not in request.user.profile.communities.all():
        return HttpResponseForbidden('Немає доступу до курсів спільноти.')

    is_author = False
    if request.user == this_course.author:
        is_author = True

    steps = CourseStep.objects.filter(course=this_course).order_by('sequence_number')

    data = {
        'course_steps': steps,
        'com': c,
        'course': this_course,
        'is_author': is_author,
    }

    return render(request, 'courser/course.html', data)


@login_required()
def course_step(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id)

    if c not in request.user.profile.communities.all():
        return HttpResponseForbidden('Немає доступу до курсів спільноти.')

    step = CourseStep.objects.get(id=s_id)

    data = {'com': c,  # community
            'course': this_course,  # course
            'step': step,  # step of course
            }

    if not step.is_available:

        return redirect(this_course)

    if step.step_type == CourseStep.LECTURE:  # this is lecture

        lecture = step.lecture
        data['lecture'] = lecture

        return render(request, 'courser/lecture.html', data)

    if step.step_type == CourseStep.INDEPENDENT_WORK:  # this is independent work

        task = step.independentwork
        data['task'] = task

        try:
            answer_file = AnswerFile.objects.get(user=request.user, independent_work=task)
            is_uploaded = True
            data['answer_file'] = answer_file

        except AnswerFile.DoesNotExist:
            is_uploaded = False

        data['is_uploaded'] = is_uploaded
        return render(request, 'courser/independent_work.html', data)

    if step.step_type == CourseStep.DICTATION:

        dictation = step.dictation
        data['dictation'] = dictation

        return render(request, 'courser/dictation_description.html', data)


@login_required()
def create_lecture(request, c_id, cr_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Ви не власник цього курсу.')

    data = {
        'com': c,
        'course': this_course,
    }

    if request.method == 'POST':

        lecture_fm = LectureForm(request.POST)

        if lecture_fm.is_valid():

            name = lecture_fm.cleaned_data['name']
            description = lecture_fm.cleaned_data['description']
            text = lecture_fm.cleaned_data['text']
            is_available = lecture_fm.cleaned_data['is_available']

            new_step = CourseStep(name=name, description=description, course=this_course, step_type='L',
                                  is_available=is_available)
            new_step.save()

            new_lecture = Lecture(course_step=new_step, text=text)
            new_lecture.save()

            return redirect(this_course)

        else:
            messages.error(request, lecture_fm.errors)

    lecture_fm = LectureForm(initial={
        'name': 'Лекція №',
    })
    data['form'] = lecture_fm

    return render(request, 'courser/create-lecture.html', data)


@login_required()
def upload_answer_file(request, c_id, cr_id, s_id):

    step = get_object_or_404(CourseStep, id=s_id)
    c = get_object_or_404(Community, id=c_id)

    if c not in request.user.profile.communities.all():
        return HttpResponseForbidden('Немає доступу до завантаження файлів в цю спільноту.')

    if request.method == 'POST':
        try:

            rand_string = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                                  for _ in range(4))

            file = request.FILES.get('file')

            if not file:
                raise ValidationError('Виберіть файл.')

            if file.size > 31457280:  # 30 mb limit
                raise ValidationError('Максимальний розмір файлу 30Mb, було завантажено {}Mb'
                                      .format(round(file.size / 1048576, 2)))

            file_ext = os.path.splitext(file.name)[1]
            valid_extensions = ('.rar', '.zip', '.7z', '.tar', '.tgz')

            if not file_ext.lower() in valid_extensions:
                raise ValidationError('Недопустимий формат файлу. Підтримуються: {}, було завантажено - {}'.
                                      format(' '.join(valid_extensions), file_ext.lower()))

            new_filename = 'c' + c_id + '-course' + cr_id + '-step' + s_id + '-' + \
                           request.user.username + '-' + rand_string + file_ext

            file.name = new_filename

            new_answer_file = AnswerFile(user=request.user, file=file, independent_work=step.independentwork)
            new_answer_file.save()

            messages.success(request, 'Файл успішно завантажено!')

        except ValidationError as ex:
            messages.error(request, ex.message)

    return redirect(step)


@login_required()
def delete_answer_file(request, c_id, cr_id, s_id, f_id):

    answer_file = get_object_or_404(AnswerFile, user=request.user, id=f_id)
    s_id = get_object_or_404(CourseStep, id=s_id)

    try:
        if answer_file:
            answer_file.delete()
            messages.success(request, 'Файл успішно видалено!')
    except:
        pass

    finally:
        return redirect(s_id)


@login_required()
def create_independent_work(request, c_id, cr_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Ви не власник цього курсу.')

    data = {
        'com': c,
        'course': this_course,
    }

    if request.method == 'POST':

        independent_work_fm = IndependentWorkForm(request.POST)

        if independent_work_fm.is_valid():

            name = independent_work_fm.cleaned_data['name']
            description = independent_work_fm.cleaned_data['description']
            text = independent_work_fm.cleaned_data['text']
            is_available = independent_work_fm.cleaned_data['is_available']

            new_step = CourseStep(name=name, description=description, course=this_course,
                                  step_type=CourseStep.INDEPENDENT_WORK, is_available=is_available)
            new_step.save()

            new_independent_work = IndependentWork(course_step=new_step, text=text)
            new_independent_work.save()

            return redirect(this_course)

        else:
            messages.error(request, independent_work_fm.errors)

    independent_work_fm = IndependentWorkForm(initial={
        'name': 'Самостійна робота №'})
    data['form'] = independent_work_fm

    return render(request, 'courser/create_independent_work.html', data)


@login_required()
def write_dictation(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)
    step = get_object_or_404(CourseStep, id=s_id, course=this_course)
    dictation = step.dictation

    if not step.is_available:
        return redirect(this_course)

    if c not in request.user.profile.communities.all():
        print('Немає доступу до диктантів спільноти.')

    data = {
        'step': step,
        'dictation': dictation,
        'com': c,
        'course': this_course,
    }

    if request.method == 'GET':

        return render(request, 'courser/write_dictation.html', data)


@login_required()
def create_dictation(request, c_id, cr_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Ви не власник цього курсу.')

    data = {
        'com': c,
        'course': this_course,
    }

    if request.method == 'POST':

        dictation_fm = DictationForm(request.POST, request.FILES)

        if dictation_fm.is_valid():
            name = dictation_fm.cleaned_data['name']
            description = dictation_fm.cleaned_data['description']
            text = dictation_fm.cleaned_data['text']
            is_available = dictation_fm.cleaned_data['is_available']
            audio = dictation_fm.cleaned_data['audio']

            try:
                rand_string = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                                      for _ in range(4))

                if not audio:
                    raise ValidationError('Виберіть аудіофайл.')

                if audio.size > 209715200:  # 200 mb limit
                    raise ValidationError('Максимальний розмір файлу 200Mb, було завантажено {}Mb'
                                          .format(round(audio.size / 1048576, 2)))

                file_ext = os.path.splitext(audio.name)[1]
                new_filename = 'c' + c_id + '-course' + cr_id + '-' + rand_string + file_ext

                audio.name = new_filename

                new_step = CourseStep(name=name, description=description, course=this_course,
                                      step_type=CourseStep.DICTATION, is_available=is_available)
                new_step.save()

                new_dictation = Dictation(course_step=new_step, text=text, audio=audio)
                new_dictation.save()

                return redirect(this_course)

            except ValidationError as ex:
                messages.error(request, ex.message)

        else:
            messages.error(request, dictation_fm.errors)

    dictation_fm = DictationForm(initial={'name': 'Диктант '})

    data['form'] = dictation_fm

    return render(request, 'courser/create_dictation.html', data)


@login_required()
def check_dictation(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    step = CourseStep.objects.get(id=s_id)
    dictation = step.dictation

    if not step.is_available:
        return HttpResponseForbidden('Перевірка не можлива, через те що диктант не доступний.')

    if c not in request.user.profile.communities.all():
        return HttpResponseForbidden('Тільки для учаників спільноти.')

    if request.method == 'GET':
        return HttpResponseForbidden('Помилка. Допустимий тільки метод POST.')

    if request.method == 'POST':

        text_solution = request.POST.get('text')

        dmp = Dmp()
        d = dmp.diff_main(text2=dictation.text, text1=text_solution)
        dmp.diff_cleanupSemantic(d)

        comparison_result_in_html = dmp.diff_prettyHtml(d)

        errors_count = comparison_result_in_html.count('background')

        new_solution = DictationSolution(dictation=dictation, author=request.user, result=text_solution,
                                         comparison_result=comparison_result_in_html, errors_count=errors_count)
        new_solution.save()

        return redirect(reverse('dictation_result', args=[c_id, cr_id, s_id, new_solution.id]))


@login_required()
def dictation_result(request, c_id, cr_id, s_id, d_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)
    step = get_object_or_404(CourseStep, id=s_id, course=this_course)
    dictation_solution = get_object_or_404(DictationSolution, id=d_id, dictation=step.dictation)

    is_show_results = dictation_solution.dictation.show_results
    is_course_admin = request.user == this_course.author

    if (not request.user == dictation_solution.author) and (not is_course_admin):
        return HttpResponseForbidden('Ви не можете переглядати цей розв\'язок')

    data = {
        'com': c,
        'solution': dictation_solution,
        'step': step,
        'course': this_course,
        'is_show_results': is_show_results,
        'is_course_admin': is_course_admin,
    }

    return render(request, 'courser/dictation_result.html', data)


@login_required()
def edit_course(request, c_id, cr_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Тільки власник курсу може його редагувати')

    steps = CourseStep.objects.filter(course=this_course).order_by('sequence_number')

    data = {
        'com': c,
        'course': this_course,
        'steps': steps,
    }

    if request.method == 'POST':

        course_fm = CourseForm(request.POST)

        if course_fm.is_valid():
            name = course_fm.cleaned_data['name']
            description = course_fm.cleaned_data['description']

            this_course.name = name
            this_course.description = description
            this_course.save()

            return redirect(this_course)
        else:
            messages.error(request, course_fm.errors)

    course_fm = CourseForm(initial={'name': this_course.name, 'description': this_course.description})
    data['form'] = course_fm

    return render(request, 'courser/course_edit.html', data)


@login_required()
def action_up_step(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)
    step = get_object_or_404(CourseStep, id=s_id)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Тільки автор курсу може його редагувати.')

    previous_step_number = step.sequence_number - 1

    if previous_step_number > 0:
        previous_step = CourseStep.objects.get(sequence_number=previous_step_number, course=this_course)

        previous_step.sequence_number = step.sequence_number
        step.sequence_number = previous_step_number

        previous_step.save()
        step.save()

    return redirect(reverse('edit_course', args=[c.id, this_course.id]))


@login_required()
def action_down_step(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)
    step = get_object_or_404(CourseStep, id=s_id)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Тільки автор курсу може його редагувати.')

    next_step_number = step.sequence_number + 1

    if next_step_number <= this_course.get_steps_count:
        next_step = CourseStep.objects.get(sequence_number=next_step_number, course=this_course)

        next_step.sequence_number = step.sequence_number
        step.sequence_number = next_step_number

        next_step.save()
        step.save()

    return redirect(reverse('edit_course', args=[c.id, this_course.id]))


@login_required()
def step_edit(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id)
    step = get_object_or_404(CourseStep, id=s_id, course=this_course)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Ви не власник цього курсу.')

    data = {
        'com': c,
        'course': this_course,
        'step': step,
    }

    if step.step_type == CourseStep.LECTURE:

        lecture = step.lecture

        if request.method == 'POST':

            lecture_edit_fm = LectureForm(request.POST)

            if lecture_edit_fm.is_valid():
                name = lecture_edit_fm.cleaned_data['name']
                description = lecture_edit_fm.cleaned_data['description']
                text = lecture_edit_fm.cleaned_data['text']
                is_available = lecture_edit_fm.cleaned_data['is_available']

                step.name = name
                step.description = description
                lecture.text = text
                step.is_available = is_available
                step.save()
                lecture.save()

                return redirect(step)

            else:
                messages.error(request, lecture_edit_fm.errors)

        initial_dict = {
            'name': step.name,
            'description': step.description,
            'text': lecture.text,
            'is_available': step.is_available,
        }

        lecture_edit_fm = LectureForm(initial=initial_dict)
        data['form'] = lecture_edit_fm

        return render(request, 'courser/lecture_edit.html', data)

    if step.step_type == CourseStep.INDEPENDENT_WORK:

        independent_work = step.independentwork

        if request.method == 'POST':

            ind_work_edit_fm = IndependentWorkForm(request.POST)

            if ind_work_edit_fm.is_valid():
                name = ind_work_edit_fm.cleaned_data['name']
                description = ind_work_edit_fm.cleaned_data['description']
                text = ind_work_edit_fm.cleaned_data['text']
                is_available = ind_work_edit_fm.cleaned_data['is_available']

                step.name = name
                step.description = description
                independent_work.text = text
                step.is_available = is_available
                step.save()
                independent_work.save()

                return redirect(step)

            else:
                messages.error(request, ind_work_edit_fm.errors)

        initial_dict = {
            'name': step.name,
            'description': step.description,
            'text': independent_work.text,
            'is_available': step.is_available,
        }

        ind_work_edit_fm = IndependentWorkForm(initial=initial_dict)
        data['form'] = ind_work_edit_fm

        return render(request, 'courser/independent_work_edit.html', data)

    if step.step_type == CourseStep.DICTATION:

        dictation = step.dictation

        if request.method == 'POST':
            dictation_fm = DictationForm(request.POST)

            if dictation_fm.is_valid():
                name = dictation_fm.cleaned_data['name']
                description = dictation_fm.cleaned_data['description']
                text = dictation_fm.cleaned_data['text']
                is_available = dictation_fm.cleaned_data['is_available']
                show_result = dictation_fm.cleaned_data['show_results']
                new_audio = request.POST.get('new_audio')

                step.name = name
                step.description = description
                step.is_available = is_available
                dictation.text = text
                dictation.show_results = show_result
                if new_audio:
                    dictation.audio = new_audio

                step.save()
                dictation.save()

            else:
                messages.error(request, dictation_fm.errors)

        initial_dict = {
            'name': step.name,
            'description': step.description,
            'text': dictation.text,
            'is_available': step.is_available,
            'show_results': dictation.show_results,
            'audio': dictation.audio,
        }

        dictation_fm = DictationForm(initial=initial_dict)
        data['form'] = dictation_fm
        data['dictation'] = dictation

        return render(request, 'courser/dictation_edit.html', data)


@login_required()
def action_delete_step(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)
    step = get_object_or_404(CourseStep, id=s_id, course=this_course)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Видаляти етапи може тільки власник курсу.')

    step.delete()

    return redirect(this_course)


@login_required()
def action_delete_course(request, c_id, cr_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Видалити курс може тільки власник!')

    if request.method == 'POST':
        this_course.delete()

        return redirect(reverse('courses', args=[c.id]))
    else:
        return HttpResponseForbidden('Помилковий запит.')


@login_required()
def review_independent_work(request, c_id, cr_id, s_id):

    c = get_object_or_404(Community, id=c_id)
    this_course = get_object_or_404(Course, id=cr_id, community=c)
    this_step = get_object_or_404(CourseStep, id=s_id, course=this_course)
    answers = AnswerFile.objects.filter(independent_work=this_step.independentwork)

    if not request.user == this_course.author:
        return HttpResponseForbidden('Перегляди прислані файли може тільки власник курсу!')

    data = {
        'com': c,
        'step': this_step,
        'course': this_course,
        'answers': answers,
    }

    return render(request, 'courser/review_independent_work.html', data)


@login_required()
def review_answer(request, a_id):

    answer = AnswerFile.objects.get(id=a_id)
    this_step = answer.independent_work.course_step
    this_course = this_step.course
    c = this_course.community

    if not answer.user == request.user and not this_step.course.author == request.user:
        return HttpResponseForbidden('Ви не маєте доступу до цієї сторінки')

    if request.method == 'GET':
        data = {
            'answer': answer,
            'com': c,
            'course': this_course,
            'step': this_step,
        }

        return render(request, 'courser/review_answer.html', data)

    if request.method == 'POST':

        if request.POST.get('rez-btn') == 'sub':

            if request.POST.get('comment-rev'):
                answer.comment = request.POST.get('comment-rev')
            answer.status = AnswerFile.CHECKED
            answer.save()
            messages.success(request, 'Робота {} зарахована.'.format(answer.user.get_full_name()))

        if request.POST['rez-btn'] == 'rew':

            if request.POST.get('comment-rev'):
                answer.comment = request.POST.get('comment-rev')
            answer.status = AnswerFile.TO_REVISION
            answer.save()
            messages.success(request, 'Робота {} відправлена на доопрацювання'.format(answer.user.get_full_name()))

        return redirect(reverse('review_independent_work', args=[c.id, this_course.id, this_step.id]))
