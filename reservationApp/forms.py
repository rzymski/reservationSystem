from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile


class CreateUserForm(UserCreationForm):
    # username = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nick'}))
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adres email'}))
    first_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imie'}))
    last_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko'}))
    # password1 = forms.CharField(label="", max_length=50, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Hasło'}))
    # password2 = forms.CharField(label="", max_length=50, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Powtórz hasło'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Nick'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-gray-950 dark:text-gray-50"><small>Wymagane pole. Maksymalnie 150 znaków. Dozwolone tylko litery, cyfry i @/./+/-/_.</small></span>'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Hasło'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-gray-950 dark:text-gray-50 small"><li>Hasło nie może być podobne do innych personalnych informacji.</li><li>Hasło musi składać się z conajmniej 8 znaków.</li><li>Hasło nie może być powszechnie używane.</li><li>Hasło nie może składać się tylko z cyfr.</li></ul>'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Potwierdź hasło'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-gray-950 dark:text-gray-50"><small>Takie same hasło jak wcześniej w celu weryfikacji.</small></span>'


# class UpdateProfileForm(forms.ModelForm):
#     age = forms.IntegerField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wiek'}))
#     sex = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Płeć'}))
#     description = forms.CharField(label="", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opis'}))
#     profileImage = forms.ImageField(label="Zdjęcie profilowe")
#
#     class Meta:
#         model = UserProfile
#         fields = ['age', 'sex', 'description', 'profileImage']


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(label="", max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nick'}))
    email = forms.EmailField(label="", required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adres email'}))
    first_name = forms.CharField(label="", max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imie'}))
    last_name = forms.CharField(label="", max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UpdateProfileForm(forms.ModelForm):
    age = forms.IntegerField(required=False, label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wiek'}))
    sex = forms.CharField(required=False, label="", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Płeć'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Opis', 'rows': 5}))
    # profileImage = forms.ImageField(required=False, label="")

    class Meta:
        model = UserProfile
        fields = ['age', 'sex', 'description', 'profileImage']
