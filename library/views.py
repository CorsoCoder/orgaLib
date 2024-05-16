#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta
from PyPDF2 import PdfFileReader
from django.conf import settings
import os
import re
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView

from .forms import BookForm, SearchForm, LoginForm, RegisterForm, ResetPasswordForm
from .models import Book, Category, Reader, User, Favourite, Borrowing, Author, Publisher
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import AuthenticationForm



def check_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        state = False
        print(state)
    else:
        state = True
        print(state)


#! -----------------------error-----------------------

#si la pagina no se encuentra se procede a devolver un error404
#docs:
#The default 404 view will pass two variables to the template: request_path, which is the URL that resulted in the error, and exception,
#which is a useful representation of the exception that triggered the view (e.g. containing any message passed to a specific Http404 instance).
def page_not_found_view(request, exception=None):
    context = {
        'searchForm': SearchForm(),
    }
    return render(request, 'error/404.html',context)





#! -----------------------category-----------------------

@method_decorator(staff_member_required, name='dispatch')
class AddCategoryView(CreateView):
    model = Category
    template_name = 'categories/add_category.html'
    fields = '__all__'

@method_decorator(staff_member_required, name='dispatch')
class AddAuthorView(CreateView):
    model = Author
    template_name = 'categories/add_category.html'
    fields = '__all__'

@method_decorator(staff_member_required, name='dispatch')
class AddPublisherView(CreateView):
    model = Publisher
    template_name = 'categories/add_category.html'
    fields = '__all__'


def categoriesList(request):
    categories = Category.objects.all().annotate(book_count=Count('book'))


    context={'categories': categories,}
    return render(request,'categories/categories_list.html',context)


def categoryView(request, cats):
    page = request.GET.get('page', 1)
    current_path = request.get_full_path()
    category_books = Book.objects.filter(category__name=cats)
    paginator = Paginator(category_books, 5)

    try:
        category_books = paginator.page(page)
    except PageNotAnInteger:
        category_books = paginator.page(1)
    except EmptyPage:
        category_books = paginator.page(paginator.num_pages)

    context = {
        'category_books':category_books,
        'current_path': current_path,
        'searchForm': SearchForm(),
        'cats':cats,
    }
    return render(request, 'categories/categories.html',context)





#! -----------------------loan-----------------------

@login_required
def borrow(request, id, action):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')

    if action == 'return_book':
        if not id:
            return HttpResponse('El id del libro no se ha encontrado, por favor comuníqueselo al administrador')

        borrowing = get_object_or_404(Borrowing, pk=id)
        borrowing.date_returned = date.today()
        borrowing.save()

        reader = Reader.objects.get(user=request.user)
        reader.max_borrowing += 1
        reader.save()

        book = borrowing.book
        book.quantity += 1
        book.save()

        borrowing_list = Borrowing.objects.filter(reader=reader, date_returned__isnull=True)

        context = {
            'state': 'return_success',
            'borrowing': borrowing_list,
        }
        return render(request, 'loan/prestados.html', context)

    elif action == 'renew_book':
        if not id:
            return HttpResponse('No se ha encontrado el ID del libro')

        borrowing = get_object_or_404(Borrowing, pk=id)
        if (borrowing.date_due_to_returned - borrowing.date_issued) < timedelta(days=60):
            borrowing.date_due_to_returned += timedelta(days=30)
            borrowing.save()

        reader = Reader.objects.get(user=request.user)
        borrowing_list = Borrowing.objects.filter(reader=reader, date_returned__isnull=True)

        context = {
            'state': 'renew_success',
            'borrowing': borrowing_list,
        }
        return render(request, 'loan/prestados.html', context)

    elif action == 'borrow':
        reader = Reader.objects.get(user=request.user)
        if reader.max_borrowing > 0:
            reader.max_borrowing -= 1
            reader.save()

            book = get_object_or_404(Book, pk=id)
            book.quantity -= 1
            book.save()

            issued = date.today()
            due_to_returned = issued + timedelta(days=30)
            borrowing = Borrowing.objects.create(
                reader=reader,
                book=book,
                date_issued=issued,
                date_due_to_returned=due_to_returned
            )

            borrowing_list = Borrowing.objects.filter(reader=reader, date_returned__isnull=True)

            context = {
                'state': 'borrow_success',
                'borrowing': borrowing_list
            }
            return render(request, 'loan/prestados.html', context)
        else:
            return render(request, 'loan/prestados.html', {'state': 'upper_limit'})


def borrowed_books(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    id = request.user.id

    try:
        reader = Reader.objects.get(user_id=id)
    except Reader.DoesNotExist:
        return HttpResponse('No se encuentra al usuario')
    borrowing = Borrowing.objects.filter(reader=reader).exclude(date_returned__isnull=False)

    context = {
        'reader': reader,
        'borrowing': borrowing,
    }
    return render(request, 'loan/prestados.html', context)





#! -----------------------CRUD-----------------------


def book_detail(request, id):
    try:
        book = get_object_or_404(Book, id=id)
    except Book.DoesNotExist:
        return HttpResponse('No se ha encontrado el libro')

    reader = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pass
        else:
            reader = get_object_or_404(Reader, user=request.user)

    fav = None
    if reader:
        fav = Favourite.objects.filter(book=book, user=request.user).exists()

    context = {
        'reader': reader,
        'book': book,
        'fav': fav
    }
    return render(request, 'CRUD/book_detail.html', context)

@staff_member_required
def update_view(request, id):
    try:
        book = get_object_or_404(Book, pk=id)
    except:
        return HttpResponse('No existe un libro con ese ID.')

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            return HttpResponseRedirect('/book/detail/' + str(book.id))
    else:
        form = BookForm(instance=book)

    context = {
        'form': form
    }
    return render(request, 'CRUD/update_view.html', context)


@staff_member_required
def delete_view(request, id):
    context = {}

    if not id:
        return HttpResponse('No existe un ID')

    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return HttpResponse('No existe un libro con este ID')

    obj = get_object_or_404(Book, pk=id)
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/")

    return render(request, "CRUD/delete_view.html", context)




@staff_member_required
def create_view(request):
    if not request.user.is_superuser and not request.user.groups.filter(permissions__codename='create_book').exists():
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            
            if 'pdf' not in request.FILES:
                placeholder_path = os.path.join(settings.MEDIA_ROOT, 'book_covers/placeholder.jpg')
                
                book.cover.save('placeholder.jpg', open(placeholder_path, 'rb'), save=False)
            
            book.save()
            return HttpResponseRedirect('/book/detail/' + str(book.id))
    else:
        form = BookForm()

    context = {
        'form': form
    }
    return render(request, "CRUD/create_view.html", context)


#! -----------------------generic-----------------------

def book_search(request):
    search_by = request.GET.get('search_by', 'Book_name')
    keyword = request.GET.get('keyword', '')

    if keyword == 'all':
        books = Book.objects.all()
    else:
        if search_by == 'Book_name':
            books = Book.objects.filter(title__icontains=keyword)
        elif search_by == 'ISBN':
            books = Book.objects.filter(ISBN__icontains=keyword)
        elif search_by == 'author':
            books = Book.objects.filter(author__icontains=keyword)
        elif search_by == 'publisher':
            books = Book.objects.filter(publisher__icontains=keyword)

    paginator = Paginator(books, 5)
    page = request.GET.get('page')

    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    current_path = request.get_full_path().split('&page')[0]

    context = {
        'books': books,
        'search_by': search_by,
        'keyword': keyword,
        'current_path': current_path,
        'searchForm': SearchForm(),
    }
    return render(request, 'generic/search.html', context)

def about(request):
    context = {
        'searchForm': SearchForm()
    }
    return render(request, "generic/about.html", context)

def index(request):
    reader = None
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            try:
                reader = Reader.objects.get(user=request.user)
            except Reader.DoesNotExist:
                pass
    context = {
        'reader': reader,
        'searchForm': SearchForm(),
    }
    return render(request, 'generic/index.html', context)




#! -----------------------account-----------------------


@ensure_csrf_cookie
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('profile'))
    
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('profile'))
                else:
                    messages.error(request, 'Tu cuenta está inhabilitada.')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'loginForm': form})



def user_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')

    registerForm = RegisterForm()
    state = None

    if request.method == 'POST':
        registerForm = RegisterForm(request.POST, request.FILES)
        password = request.POST.get('password', '')
        repeat_password = request.POST.get('re_password', '')
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')
        name = request.POST.get('name', '')
        photo = request.FILES.get('photo', '')

        if User.objects.filter(username=username):
            state = 'user_exist'
        elif not photo.name[-3:].lower() in ['jpg','png','jpeg','gif']:
            state = "wrong_extension"
        elif password == '':
            state = 'empty_password'
        elif repeat_password == '':
            state = 'empty_repeat_password'
        elif password != repeat_password:
            state = 'repeat_error'
        elif email == '':
            state = 'empty_email'
        elif check_email(email) == False:
            state = 'wrong_email'
        else:
            new_user = User.objects.create(username=username)
            new_user.set_password(password)
            new_user.save()

            new_reader = Reader.objects.create(user=new_user, name=name, email=email)

            if photo:
                image = Image.open(photo)
                image = image.convert("RGB")
                image.thumbnail((100, 100))  
                thumbnail_io = BytesIO()
                image.save(thumbnail_io, format='JPEG')  
                thumbnail_file = InMemoryUploadedFile(thumbnail_io, None, photo.name, 'image/jpeg', thumbnail_io.tell(), None)
                new_reader.photo.save(photo.name, thumbnail_file, save=False)

            new_reader.save()
            state = 'success'

            auth.login(request, new_user)

            return HttpResponseRedirect('/profile')

    context = {
        'state': state,
        'registerForm': registerForm,
    }
    return render(request, 'registration/register.html', context)

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def set_password(request):
    user = request.user
    state = None

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            print("1")

            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, '¡Tu contraseña ha sido cambiada con éxito!')
            return redirect('profile') 

        else:
            state = 'password_error'
            
    else:
        form = PasswordChangeForm(user)

    context = {
        'state': state,
        'resetPasswordForm': form,
    }
    return render(request, 'registration/set_password.html', context)


@login_required
def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')



def profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')

    reader = None
    if not request.user.is_superuser:
        try:
            reader = Reader.objects.get(user=request.user)
        except Reader.DoesNotExist:
            pass

    borrowing = None
    if reader:
        borrowing = Borrowing.objects.filter(reader=reader).exclude(date_returned__isnull=False)

    context = {
        'state': request.GET.get('state', None),
        'reader': reader,
        'borrowing': borrowing,
    }
    return render(request, 'registration/profile.html', context)






#! -----------------------favourite-----------------------
def fav_view(request):
    if request.user.is_authenticated:
        user = request.user
        favs = Favourite.objects.filter(user=user)
        return render(request, "favourite/favourite.html", {"favs": favs})
    return redirect("user_login")


def add_to_fav(request, id):
    if request.user.is_authenticated:
        book = Book.objects.filter(pk=id).first()
        fav = Favourite()
        fav.user = request.user
        fav.book = book
        fav.save()
        return redirect("favourite")
    return redirect("user_login")


@login_required
def remove_fav(request, id):
    if request.user.is_authenticated:
        book = Book.objects.filter(pk=id).first()
        fav = Favourite.objects.filter(user=request.user, book=book)
        fav.delete()
        return redirect("favourite")
    return redirect("user_login")
