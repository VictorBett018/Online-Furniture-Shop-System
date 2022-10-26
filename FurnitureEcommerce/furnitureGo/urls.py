from django.urls import path
from .views import *
app_name = "furnitureGo"
urlpatterns = [
    path("", HomeView.as_view(),name="home"),
    path("all-products/", AllProductsView.as_view(),name="allproducts"),
    path("product/<slug:slug>/", ProductDetailView.as_view(),name="productdetails")
]