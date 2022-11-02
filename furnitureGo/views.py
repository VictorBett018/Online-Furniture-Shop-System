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