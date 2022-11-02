from itertools import product
from pipes import Template
from django.shortcuts import render
from django.views.generic import TemplateView

from furnitureGo.models import *
# Create your views here.
class HomeView(TemplateView):
    template_name="home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_list'] = Product.objects.all().order_by("-id")
        return context

class  AllProductsView(TemplateView):
    template_name="allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context

class ProductDetailView(TemplateView):
    template_name = "productdetails.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        context['product'] = product
        product.view_count +=1
        product.save()
        return context

class UserRegisterView(TemplateView):
    template_name="user_register.html"

class UserLoginView(TemplateView):
    template_name="user_login.html"

class AddtoCartView(TemplateView):
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
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            else:
                cartproduct
            
        else:
            cart_obj = Cart.objects.create(total = 0)
            self.request.session['cart_id'] = cart_obj.id
            print("new cart")
        #check if product already exist in cart
        return context