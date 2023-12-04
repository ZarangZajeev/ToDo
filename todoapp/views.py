from django.shortcuts import render, redirect
from django.views.generic import View
from todoapp.forms import UserForm, LoginForm, TodoForm
from django.contrib.auth import authenticate,login,logout
from todoapp.models import Todos
from django.utils.decorators import method_decorator
from django.contrib import messages

def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"Invalid section")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

def owner_permission_required(fn):
    def wrapper(request,*args,**kwargs):
        id=kwargs.get("pk")
        todo_obj=Todos.objects.get(id=id)
        if todo_obj.user != request.user:
            logout(request)
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

# Create your views here.
decs=[signin_required,owner_permission_required]


class RegistrationView(View):
    def get(self,request,*args,**kwargs):
        form=UserForm()
        return render(request,"register.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Todo Account has been created")
            return redirect("signin")
        else:
            messages.error(request,"Failed to create account")
            return render(request,"register.html",{"form":form})
        
class LoginView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request, username=uname, password=pwd)
            if user_object:
                print("valid credential")
                login(request,user_object)
                messages.success(request,"Welocome")
                return redirect("index")
            else:
                messages.error(request,"Not user registerd")
                return render(request,"register.html",{"form":form})
        else:
            return render(request,"register.html",{"form":form})

@method_decorator(signin_required,name="dispatch")
class IndexView(View):
    def get(self,request,*args,**kwargs):
        form=TodoForm()
        qs=Todos.objects.filter(user=request.user)

        pending_count=Todos.objects.filter(status="todo",user=request.user).count()
        progress_count=Todos.objects.filter(status="improgress",user=request.user).count()
        finished_count=Todos.objects.filter(status="completed",user=request.user).count()
        return render(request,"index.html",{
                                            "form":form,
                                            "data":qs,
                                            "pending":pending_count,
                                            "inprogress":progress_count,
                                            "finished":finished_count,
                                            }
                    )
    def post(self,request,*args,**kwargs):
        form=TodoForm(request.POST)
        if form.is_valid():
            form.instance.user=request.user
            form.save()
            messages.success(request,"New Todo added")
            return redirect("index")
        else:
            messages.error(request,"Failed to add Todo")
            return render(request,"index.html",{"form":form})
        
@method_decorator(signin_required,name="dispatch")
class SignoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")
    
@method_decorator(decs,name="dispatch")
class TodoUpdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        if "status" in request.GET:
            value=request.GET.get("status")
            if value=="inprogress":
                Todos.objects.filter(id=id).update(status="improgress")
            elif value=="completed":
                Todos.objects.filter(id=id).update(status="completed")
        messages.success(request,"Keep Going 🤞")
        return redirect("index")
    
@method_decorator(decs,name="dispatch")
class TodoDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Todos.objects.get(id=id).delete()
        messages.success(request,"Removed your completed todo")
        return redirect("index")