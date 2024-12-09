from django import forms
from elavateapp.models import Profile, Idea, Comment, Donation

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'tags', 'role', 'location', 'phone_number', 'website']

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'description', 'image', 'tags']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount', 'phone_number']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if not phone_number.startswith('254'):
            raise forms.ValidationError("Phone number must start with '254'.")
        return phone_number
