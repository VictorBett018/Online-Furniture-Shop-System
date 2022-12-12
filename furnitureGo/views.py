from django.views.generic import View, TemplateView ,CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import CheckoutForm, UserRegistrationForm ,UserLoginForm, AdminLoginForm
from django.urls import reverse_lazy
from furnitureGo.models import *
# Create your views here.
class EconMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj =Cart.objects.get(id = cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer=request.user.customer
                cart_obj.save()

        return super().dispatch(request, *args, **kwargs)

class HomeView(EconMixin,TemplateView):
    template_name="home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_list'] = Product.objects.all().order_by("-id")
        return context

class  AllProductsView(EconMixin,TemplateView):
    template_name="allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context

class ProductDetailView(EconMixin,TemplateView):
    template_name = "productdetails.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        context['product'] = product
        product.view_count +=1
        product.save()
        return context

class UserRegisterView(CreateView):
    template_name="user_register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("furnitureGo:home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)

        return super().form_valid(form)
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url

        else:
            return self.success_url


class UserLoginView(FormView):
    template_name="user_login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("furnitureGo:home")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pwd = form.cleaned_data.get("password")
        user = authenticate(username = uname, password = pwd)
        if user is not None and Customer.objects.filter(user=user).exists():
            login(self.request, user)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url

        else:
            return self.success_url


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("furnitureGo:home")

class AddtoCartView(EconMixin,TemplateView):
    template_name="addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        #get product id from requested cart
        product_id = self.kwargs['pro_id']
        #get product
        product_obj = Product.objects.get(id=product_id)
        #check if cart exist
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id = cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product = product_obj)
            #item already exist in the cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            #new item in the cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart = cart_obj, product = product_obj, rate = product_obj.selling_price, quantity = 1, subtotal = product_obj.selling_price
                )
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            
        else:
            cart_obj = Cart.objects.create(total = 0)
            self.request.session['cart_id'] = cart_obj.id
            print("new cart")
        #check if product already exist in cart
        return context
class MyCartView(EconMixin,TemplateView):
    template_name = "mycart.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id =self.request.session.get("cart_id",None)
        if cart_id:
            cart = Cart.objects.get(id = cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context
        
class ManageCartView(EconMixin,View):
    def get(self, request, *args, **kwargs):
        cp_id =self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id = cp_id)
        cart_obj = cp_obj.cart
     
        if action=="inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action=="dec":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action=="rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("furnitureGo:mycart")

class EmptycartView(EconMixin,View):
        def get(self, request, *args, **kwargs):
            cart_id = request.session.get("cart_id", None)
            if cart_id:
                cart = Cart.objects.get(id = cart_id)
                cart.cartproduct_set.all().delete()
                cart.total = 0
                cart.save()

            return redirect("furnitureGo:mycart")

class CheckoutView(EconMixin,CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("furnitureGo:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id =self.request.session.get("cart_id",None)
        if cart_id:
            cart_obj = Cart.objects.get(id = cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id = cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal =cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session["cart_id"]

        else:
            return redirect("furnitureGo:home")

        return super().form_valid(form)

class UserProfileView(TemplateView):

    template_name = "userprofile.html"
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        customer = self.request.user.customer
        context = super().get_context_data(**kwargs)
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer = customer)
        context['orders'] = orders
        return context
class OrderDetailView(DetailView):
    template_name = "orderdetail.html"
    model = Order
    context_object_name = "ord_obj"
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id = order_id)
            if request.user.customer != order.cart.customer:
              return redirect("/profile/") 
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

##admin pages
class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)

class AdminLoginView(AdminRequiredMixin, FormView):
    template_name = "adminpages/admin_login.html"
    form_class = AdminLoginForm
    success_url = reverse_lazy("furnitureGo:admin_home")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pwd = form.cleaned_data.get("password")
        user = authenticate(username = uname, password = pwd)
        if user is not None and Admin.objects.filter(user=user).exists():
            login(self.request, user)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
 
        return super().form_valid(form)

class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name =  "adminpages/admin_home.html"


    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status = "Order Received").order_by("-id")

        return context

class AdminOrderView(AdminRequiredMixin, DetailView):
    template_name = "adminpages/adminorderdetails.html"
    model = Order
    context_object_name = "ord_obj"


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"


    
    
