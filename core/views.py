from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import Skill, User


def home(request):
    return render(request, 'home.html')


def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'skills/list.html', { 'skills': skills })


def skill_detail(request, slug: str):
    skill = Skill.objects.get(slug=slug)
    can_teach_count = User.objects.filter(skills_can_teach=skill).count()
    to_learn_count = User.objects.filter(skills_to_learn=skill).count()
    return render(request, 'skills/detail.html', {
        'skill': skill,
        'can_teach_count': can_teach_count,
        'to_learn_count': to_learn_count,
    })
