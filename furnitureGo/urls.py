from django.urls import path
from .views import *
app_name = "furnitureGo"
urlpatterns = [
    path("", HomeView.as_view(),name="home"),
    path("all-products/", AllProductsView.as_view(),name="allproducts"),
    path("user-login/", UserLoginView.as_view(),name="user_login"),
    path("user-register/", UserRegisterView.as_view(),name="user_register"),
    path("product/<slug:slug>/", ProductDetailView.as_view(),name="productdetails"),
    path("add-to-cart-<int:pro_id>/", AddtoCartView.as_view(),name="addtocart"),
    path("my-cart", MyCartView.as_view(),name="mycart"),
]