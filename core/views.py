from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import Skill, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import SkillForm


def home(request):
    return render(request, 'home.html')


def skill_list(request):
    # Ensure legacy skills without slug get populated
    for sk in Skill.objects.filter(slug__isnull=True):
        sk.save()
    for sk in Skill.objects.filter(slug=""):
        sk.save()
    form = SkillForm()
    if request.user.is_authenticated:
        skills_teach = request.user.skills_can_teach.all()
        skills_learn = request.user.skills_to_learn.all()
        context = { 'skills_teach': skills_teach, 'skills_learn': skills_learn, 'form': form }
    else:
        # For guests show all skills as catalog
        skills = Skill.objects.all()
        context = { 'skills': skills, 'form': form }
    return render(request, 'skills/list.html', context)


def skill_detail(request, slug: str):
    from django.shortcuts import get_object_or_404
    skill = get_object_or_404(Skill, slug=slug)
    can_teach_count = User.objects.filter(skills_can_teach=skill).count()
    to_learn_count = User.objects.filter(skills_to_learn=skill).count()
    return render(request, 'skills/detail.html', {
        'skill': skill,
        'can_teach_count': can_teach_count,
        'to_learn_count': to_learn_count,
    })


@login_required
def skill_add(request):
    if request.method == 'POST':
        form = SkillForm(request.POST, request.FILES)
        if form.is_valid():
            # create or get by name
            skill, _created = Skill.objects.get_or_create(name=form.cleaned_data['name'], defaults={
                'description': form.cleaned_data.get('description', ''),
                'photo': form.cleaned_data.get('photo'),
                'experience_years': form.cleaned_data.get('experience_years'),
            })
            # if existed, update optional fields if provided
            if not _created:
                updated = False
                for field in ['description', 'photo', 'experience_years']:
                    val = form.cleaned_data.get(field)
                    if val:
                        setattr(skill, field, val)
                        updated = True
                if updated:
                    skill.save()
            # assign to current user per flags
            if form.cleaned_data.get('assign_to_teach'):
                request.user.skills_can_teach.add(skill)
            if form.cleaned_data.get('assign_to_learn'):
                request.user.skills_to_learn.add(skill)
            return redirect('skill_list')
    return redirect('skill_list')
