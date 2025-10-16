from django.http import HttpResponse


def home(request):
    return HttpResponse("SkillSwap is up!")
