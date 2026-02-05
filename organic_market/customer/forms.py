from django import forms
from django.contrib.auth import get_user_model
from .models import CustomerProfile

User = get_user_model()


class CustomerProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and not self.initial.get('email'):
            self.initial['email'] = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            return email
        existing = User.objects.filter(email__iexact=email)
        if self.user:
            existing = existing.exclude(pk=self.user.pk)
        if existing.exists():
            raise forms.ValidationError('Email already exists')
        return email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if self.user:
            self.user.email = self.cleaned_data.get('email', self.user.email)
            if commit:
                self.user.save()
        return profile
