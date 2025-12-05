from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Skill, ExchangeRequest


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=False)
    university = forms.CharField(max_length=255, required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "university", "avatar", "password1", "password2")

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        user.full_name = self.cleaned_data.get("full_name")
        user.university = self.cleaned_data.get("university")
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            user.avatar = avatar
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    skills_can_teach = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(), required=False, widget=forms.SelectMultiple(attrs={"size": 8})
    )
    skills_to_learn = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(), required=False, widget=forms.SelectMultiple(attrs={"size": 8})
    )

    class Meta:
        model = User
        fields = ("full_name", "university", "avatar", "skills_can_teach", "skills_to_learn")

    def clean(self):
        cleaned = super().clean()
        teach = cleaned.get("skills_can_teach")
        learn = cleaned.get("skills_to_learn")
        if (not teach or teach.count() == 0) and (not learn or learn.count() == 0):
            raise forms.ValidationError("Укажите минимум 1 навык в одном из списков.")
        return cleaned


class ExchangeCreateForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(queryset=User.objects.all())
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())

    class Meta:
        model = ExchangeRequest
        fields = ("receiver", "skill")


class ExchangeSendForm(forms.ModelForm):
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    class Meta:
        model = ExchangeRequest
        fields = ("skill", "message")

