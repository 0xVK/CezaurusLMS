from django.db import models
from django.contrib.auth.models import User
from communities.models import Community
from django.shortcuts import reverse
import os
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db.models import F
import datetime


class Course(models.Model):

    name = models.CharField(max_length=40)
    description = models.CharField(max_length=80, null=True, blank=True)
    community = models.ForeignKey(Community, null=True, blank=True)
    author = models.ForeignKey(User)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return 'Курс {}, з групи {} ({} {} ({}))'.format(self.name, self.community,
                                                         self.author.first_name, self.author.last_name,
                                                         self.author.username)

    def get_absolute_url(self):
        return reverse('course', args=[self.community.id, self.id])

    @property
    def get_steps_count(self):
        return self.get_steps.all().count()

    def delete(self, *args, **kwargs):
        steps = CourseStep.objects.filter(course=self)
        for step in steps:
            step.delete()
        super(Course, self).delete(*args, **kwargs)


class CourseStep(models.Model):

    LECTURE = 'L'
    DICTATION = 'D'
    TEST = 'T'
    INDEPENDENT_WORK = 'I'

    COURSE_STEP_TYPES = (
        (LECTURE, 'Лекція'),
        (DICTATION, 'Диктант'),
        (TEST, 'Тест'),
        (INDEPENDENT_WORK, 'Самостійна робота'))

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=600, null=True, blank=True)
    course = models.ForeignKey(Course, related_name='get_steps', on_delete=models.CASCADE)
    step_type = models.CharField(choices=COURSE_STEP_TYPES, max_length=1)
    is_available = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True, blank=True)
    stop_time = models.DateTimeField(null=True, blank=True)
    sequence_number = models.IntegerField(default=1)

    def __str__(self):
        return 'Крок: {} - {} ({})'.format(self.name, self.course.name, self.step_type)

    def get_absolute_url(self):
        return reverse('course_step', args=[self.course.community.id, self.course.id, self.id])

    def delete(self, *args, **kwargs):

        if self.step_type == CourseStep.INDEPENDENT_WORK:
            self.independentwork.delete()

        elif self.step_type == CourseStep.DICTATION:
            self.dictation.delete()

        super(CourseStep, self).delete(*args, **kwargs)


class Lecture(models.Model):

    course_step = models.OneToOneField(CourseStep, on_delete=models.CASCADE)
    text = models.TextField(max_length=15000)

    def __str__(self):
        return 'Лекція: {}, курс: {}'.format(self.course_step.name, self.course_step.course.name)

    # def get_text_as_markdown(self):
    #     return markdown.markdown(self.description, safe_mode='escape')


class IndependentWork(models. Model):

    course_step = models.OneToOneField(CourseStep)
    text = models.TextField(max_length=15000)

    def __str__(self):
        return 'Самостійна робота: {}, курс: {}'.format(self.course_step.name, self.course_step.course.name)

    def delete(self, *args, **kwargs):
        answers = AnswerFile.objects.filter(independent_work=self)
        for answer in answers:
            answer.delete()
        super(IndependentWork, self).delete(*args, **kwargs)


class AnswerFile(models.Model):

    CHECKED = 'C'  # перевірено
    TO_REVISION = 'R'  # відправлено на доопрацювання
    WAIT = 'W'  # очікує перевірки

    STATUS_TYPES = (
        (CHECKED, 'Перевірено'),
        (TO_REVISION, 'Відправлено на доопрацювання'),
        (WAIT, 'Очікує перевірки'),
    )

    independent_work = models.ForeignKey(IndependentWork)
    user = models.ForeignKey(User)
    file = models.FileField(upload_to='answers')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_TYPES, default=WAIT, max_length=3)
    comment = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return 'Відповідь до: {}, завантажив: ({})'.format(self.independent_work.course_step.name,
                                                           self.user.get_full_name())

    def delete(self, *args, **kwargs):
        try:
            os.remove(self.file.path)
        except:
            pass

        super(AnswerFile, self).delete(*args, **kwargs)


class Dictation(models.Model):

    text = models.TextField(max_length=15000)
    course_step = models.OneToOneField(CourseStep)
    audio = models.FileField(upload_to='dictations', null=True, blank=True)
    show_results = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):

        try:
            os.remove(self.audio.path)
        except:
            pass

        super(Dictation, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Диктант: {} ,курс: {}'.format(self.course_step.name, self.course_step.course.name)


class DictationSolution(models.Model):

    dictation = models.ForeignKey(Dictation)
    author = models.ForeignKey(User)
    result = models.TextField(max_length=15000)
    comparison_result = models.TextField(max_length=15000)
    time = models.DateTimeField(auto_now_add=True)
    errors_count = models.IntegerField(default=0)

    def __str__(self):
        return 'Диктант: {} ,розв\'язок {} {}, курс: {}'.format(self.dictation.course_step.name,
                                                                self.author.first_name,
                                                                self.author.last_name,
                                                                self.dictation.course_step.course.name)


@receiver(post_save, sender=CourseStep)
def set_sequence_number(sender, instance, created, **kwargs):
    if created:
        instance.sequence_number = instance.course.get_steps_count
        instance.save()


@receiver(pre_delete, sender=CourseStep)
def recount_sequence_number(sender, instance, using, **kwargs):
    deleted_step_number = instance.sequence_number
    CourseStep.objects.filter(sequence_number__gt=deleted_step_number).update(sequence_number=F('sequence_number')-1)

