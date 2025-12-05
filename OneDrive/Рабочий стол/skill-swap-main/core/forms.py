from django import forms
from accounts.models import Skill


class SkillForm(forms.ModelForm):
    assign_to_teach = forms.BooleanField(required=False, initial=True, label="Добавить в 'Могу преподавать'")
    assign_to_learn = forms.BooleanField(required=False, label="Добавить в 'Хочу изучить'")
    class Meta:
        model = Skill
        fields = ("name", "description", "photo", "experience_years")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например: Линейная алгебра"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Краткое описание навыка"}),
            "experience_years": forms.NumberInput(attrs={"min": 0, "placeholder": "Стаж в годах (необязательно)"}),
        }


