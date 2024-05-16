from django.forms import ModelForm, PasswordInput
from django import forms
from .models import Book, Reader, Category
from easy_select2 import Select2, Select2Multiple
from django.core.validators import FileExtensionValidator

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        label=u'Usuario: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'username',
            'id': 'id_username',
        })
    )
    password = forms.CharField(
        label=u'Contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'password',
            'id': 'id_password',
        }),
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        label=u'Nombre de usuario: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'username',
            'id': 'id_username',
        }),
    )
    name = forms.CharField(
        label=u'Nombre: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'name',
            'id': 'id_name',
        }),
    )
    password = forms.CharField(
        label=u'Contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'password',
            'id': 'id_password',
        }),
    )
    re_password = forms.CharField(
        label=u'Repetir contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 're_password',
            'id': 'id_re_password',
        }),
    )
    email = forms.EmailField(
        label=u'E-mail: ',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'name': 'email',
            'id': 'id_email',
        }),
        required=False,
    )

    photo = forms.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg'])],
        label=u'Avatar: ',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'name': 'photo',
            'id': 'id_photo',
        }),
        required=False,
    )

class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(
        label=u'Contraseña actual: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'old_password',
            'id': 'id_old',
        }),
    )
    new_password = forms.CharField(
        label=u'Contraseña nueva: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'new_password',
            'id': 'id_new',
        }),
    )
    repeat_password = forms.CharField(
        label=u'Repetir contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'repeat_password',
            'id': 'id_repeat',
        }),
    )

class SearchForm(forms.Form):
    CHOICES = [
        ('ISBN', 'ISBN'),
        ('Book_name', 'Nombre'),
        ('author', 'Autor'),
        ('publisher', 'Editorial')
    ]

    search_by = forms.ChoiceField(
        label='',
        choices=CHOICES,
        widget=forms.RadioSelect(),
        initial='Book_name',
    )

    keyword = forms.CharField(
        label='',
        max_length=32,
        widget=forms.TextInput(attrs={
            'class': 'form-control input-lg',
            'placeholder': 'Buscador',
            'name': 'keyword',
        })
    )
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'pdf', 'category', 'author', 'publisher', 'description','cover',]
        widgets = {
            'category': Select2Multiple(attrs={'class': 'select2', 'required': 'True'}),
            'author': Select2(attrs={'class': 'select2'}),
            'publisher': Select2(attrs={'class': 'select2'}),
            'description': forms.Textarea(attrs={'rows': '10', 'cols': '70'}),
        }

class ReaderForm(ModelForm):
    class Meta:
        model = Reader
        fields = '__all__'

