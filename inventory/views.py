from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.utils import timezone
from datetime import date
import csv
import pandas as pd

from .models import Product, Customer, LeaveApplication, Attendance, UploadedFile, Employee
from .forms import ProductForm, CustomerForm, LeaveApplicationForm, UploadedFileForm


# --- Auth Views ---

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def signup_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created. Please log in.')
        return redirect('login')
    return render(request, 'signup.html', {'form': form})


# --- Dashboard ---

@login_required
def dashboard(request):
    today = date.today()
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        employee = None

    attendance = Attendance.objects.filter(employee=employee, date=today).first() if employee else None
    today_status = attendance.status if attendance else "Absent"

    return render(request, 'dashboard.html', {
        'today_status': today_status,
        'employee': employee
    })


# --- Product Views ---

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product created successfully.')
        return redirect('product_list')
    return render(request, 'product_form.html', {'form': form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('product_list')
    return render(request, 'product_form.html', {'form': form})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})


# --- Customer Views ---

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Customer created successfully.')
        return redirect('customer_list')
    return render(request, 'customer_form.html', {'form': form})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Customer updated successfully.')
        return redirect('customer_list')
    return render(request, 'customer_form.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')
    return render(request, 'customer_confirm_delete.html', {'customer': customer})


# --- Leave Application ---

@login_required
def apply_leave(request):
    form = LeaveApplicationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        leave = form.save(commit=False)
        leave.employee = request.user
        leave.save()
        messages.success(request, 'Leave application submitted successfully.')
        return redirect('view_leaves')
    return render(request, 'leave_application.html', {'form': form})


@login_required
def view_leaves(request):
    leaves = LeaveApplication.objects.filter(employee=request.user).order_by('-start_date')
    return render(request, 'view_leaves.html', {'leaves': leaves})


# --- Attendance ---

@login_required
def punch_in_view(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('dashboard')

    today = date.today()

    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)
    # Only update check_in if not already set
    if attendance.check_in is None:
        attendance.check_in = timezone.now().time()
        attendance.status = 'Present'
        attendance.save()

    return redirect('dashboard')


@login_required
def punch_out_view(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('dashboard')

    today = date.today()

    # Try to get attendance record, or create if not exists (but this time avoid duplicate)
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)

    # Only update check_out if not already set
    if attendance.check_out is None:
        attendance.check_out = timezone.now().time()
        attendance.save()

    return redirect('dashboard')

@login_required
def attendance_history(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('dashboard')

    records = Attendance.objects.filter(employee=employee).order_by('-date')
    return render(request, 'attendance_history.html', {'attendance_list': records})


# --- File Upload ---

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.save()
            try:
                if uploaded.file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded.file)
                else:
                    df = pd.read_csv(uploaded.file)
                for _, row in df.iterrows():
                    Product.objects.create(
                        name=row.get('name', 'Unnamed'),
                        price=row.get('price', 0),
                        quantity=row.get('quantity', 0)
                    )
                messages.success(request, 'File processed and products added.')
            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
            return redirect('product_list')
    else:
        form = UploadedFileForm()
    return render(request, 'upload_file.html', {'form': form})


# --- Export Products CSV ---

@login_required
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Price', 'Quantity'])
    for product in Product.objects.all():
        writer.writerow([product.name, product.price, product.quantity])
    return response
