from unicodedata import category
from django.contrib import admin
from library.models import Author, Book, Publisher, Reader, Favourite, Category, Borrowing
from django import forms
import re
from easy_select2 import Select2, select2_modelform, Select2Multiple
from admin_auto_filters.filters import AutocompleteFilter


class ReaderFilter(AutocompleteFilter):
    title = 'Usuarios'
    field_name = 'user'


class ReaderAdminForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = '__all__'


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    search_fields = ('email', "user", 'name')
    list_display = ("user", 'email', 'status')
    list_filter = [ReaderFilter, 'status']
    form = ReaderAdminForm


class FavouriteFilter(AutocompleteFilter):
    title = 'Usuarios'  # display title
    field_name = 'user'


class FavouriteFilter2(AutocompleteFilter):
    title = 'Libro'  # display title
    field_name = ('book')


class FavouriteAdminForm(forms.ModelForm):
    class Meta:
        model = Favourite
        fields = '__all__'
        widgets = {
            'book': Select2(),
            'user': Select2(),
        }


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    search_fields = ("book", "user")
    list_display = ('book', 'user')
    list_filter = [FavouriteFilter, FavouriteFilter2]
    form = FavouriteAdminForm


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("book", 'name')
    form = CategoryAdminForm


class AuthorAdminForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name']
    form = AuthorAdminForm


class PublisherAdminForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = '__all__'


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ['name']
    form = PublisherAdminForm


class BookFilterCategory(AutocompleteFilter):
    title = 'Categorías'
    field_name = 'category'


class BookFilterFav(AutocompleteFilter):
    title = 'Favoritos'
    field_name = 'fav'


class BookFilterAuthor(AutocompleteFilter):
    title = 'Autor'
    field_name = 'author'


class BookFilterPublisher(AutocompleteFilter):
    title = 'Editorial'
    field_name = 'publisher'


class BookAdminForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ['fav']
        widgets = {
            'category': Select2Multiple(),
            'author': Select2(),
            'publisher': Select2()
        }

    def clean_ISBN(self):
        isbn = self.cleaned_data["ISBN"]
        if re.search('[a-zA-Z]', isbn):
            raise forms.ValidationError("solo se admiten números")
        return self.cleaned_data["ISBN"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    search_fields = ("title", "author__name", 'ISBN',)
    list_display = ("title", "author", 'ISBN', 'publisher', 'get_categories_display')
    list_filter = [BookFilterAuthor, BookFilterCategory, BookFilterFav, BookFilterPublisher]
    form = BookAdminForm

    def get_categories_display(self, obj):
        return ", ".join([category.name for category in obj.category.all()])

    get_categories_display.short_description = 'Categories'


class BorrowAdminForm(forms.ModelForm):
    class Meta:
        model = Borrowing
        fields = '__all__'
        widgets = {
            'reader': Select2(),
            'book': Select2(),
        }


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    search_fields = ("book", "reader")
    list_display = ('reader', 'book', 'date_issued', 'date_due_to_returned', 'date_returned')
    list_filter = ('date_issued', 'date_due_to_returned', 'date_returned')
    form = BorrowAdminForm


admin.site.site_title = 'Panel de administración'
admin.site.site_header = 'Panel de administración'
