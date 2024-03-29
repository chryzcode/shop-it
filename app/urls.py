from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "app"


urlpatterns = [
    path("", views.home_page, name="base"),
    path("create-product/", views.create_product, name="create_product"),
    path("edit/product/<slug>", views.edit_product, name="edit_product"),
    path("delete/product/<slug>", views.delete_product, name="delete_product"),
    path("add-wishlist/<slug>", views.add_wishlist, name="add_wishlist"),
    path("remove-wishlist/<slug>", views.remove_wishlist, name="remove_wishlist"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wallet/", views.store_wallet, name="store_wallet"),
    path(
        "products/",
        views.a_store_all_products,
        name="store_products",
    ),
    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
    path(
        "store/<slugified_store_name>/category/<slug:slug>/products/",
        views.store_category_products,
        name="store_category_products",
    ),
    path(
        "store/<slugified_store_name>/collections",
        views.all_store_products,
        name="all_store_products",
    ),
    path("store/", views.store_admin, name="store_admin"),
    path("store/<slugified_store_name>/", views.store, name="store"),
    path("categories/", views.all_category, name="all_category"),
    path("create-category/", views.add_category, name="create_category"),
    path("edit-category/<slug:slug>/", views.edit_category, name="edit_category"),
    path("delete-category/<slug:slug>/", views.delete_category, name="delete_category"),
    path("discount-products/", views.discount_products, name="discount_products"),
    path("coupon/", views.all_coupons, name="all_coupons"),
    path("create-coupon/", views.create_coupon, name="create_coupon"),
    path("delete-coupon/<str:pk>/", views.delete_coupon, name="delete_coupon"),
    path("customers/", views.all_customers, name="all_customers"),
    path("orders/", views.store_orders, name="store_orders"),
    path("unpaid-orders/", views.unpaid_store_orders, name="unpaid_store_orders"),
    path("order/<uuid:pk>/", views.store_order_detail, name="store_order_detail"),
    path("<slugified_store_name>/review/", views.store_review, name="store_review"),
    path(
        "<slugified_store_name>/create/review/product/<slug:slug>/",
        views.product_store_review,
        name="product_store_review",
    ),
    path("reviews/", views.store_review_list, name="store_review_list"),
    path("review/<str:pk>/", views.store_review_detail, name="store_review_detail"),
    path(
        "yearly/subscriptions/",
        views.yearly_subscription_plans,
        name="yearly_subscription_plans",
    ),
    path(
        "monthly/subscriptions/",
        views.monthly_subscription_plans,
        name="monthly_subscription_plans",
    ),
    path(
        "transanction-history/", views.transanction_history, name="transanction_history"
    ),
    path("store-staff/", views.store_staff_page, name="store_staff_page"),
    path("shipping/", views.shipping_method_list, name="shipping_method_list"),
    path(
        "notification/mark-as-read/<str:id>/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
    path(
        "customer/detail/<str:pk>/",
        views.store_customers_details,
        name="store_customers_details",
    ),
    path(
        "store/<slugified_store_name>/product/<slug:slug>/reviews/",
        views.product_review_list,
        name="product_review_list",
    ),
    path("company/reviews/", views.company_review, name="company_review"),
    path("company/team/", views.company_team, name="company_team"),
    path("get-state/<iso2>/", views.get_state, name="get_state"),
    path("get-city/<iso2>/", views.get_state, name="get_city"),
    path("notifications/", views.notification_page, name="notification_page"),
    path("newsletter/", views.newsletter_page, name="newsletter_page"),
    path("generate/newsletter/", views.generate_store_newsletter, name="generate_store_newsletter"),
    path("draft/newsletter/", views.draft_newsletter, name="draft_newsletter"),
    path("publish/newsletter/", views.publish_newsletter, name="publish_newsletter"),
    path("publish/draft/newsletter/<str:pk>", views.publish_draft_newsletter, name="publish_draft_newsletter"),
    path("delete/newsletter/<str:pk>/", views.delete_draft_newsletter, name="delete_draft_newsletter"),
    path("edit/draft/newsletter/<str:pk>/", views.edit_draft_newsletter, name="edit_draft_newsletter"),
    path("unsubscribe-newsletter/<slugified_store_name>/", views.unsubscribe_newsletter, name="unsubscribe_newsletter"),
    path("resubscribe-newsletter/<slugified_store_name>/", views.resubscribe_newsletter, name="resubscribe_newsletter"),
    path(
        "create/shipping-method/", views.add_shipping_method, name="add_shipping_method"
    ),
    path(
        "edit/shipping-method/<str:pk>",
        views.edit_shipping_method,
        name="edit_shipping_method",
    ),
    path(
        "delete/shipping-method/<str:pk>",
        views.delete_shipping_method,
        name="delete_shipping_method",
    ),
    path("shipping-company/", views.shipping_company_list, name="shipping_company_list"),
    path("add/shipping-company/", views.add_shipping_company, name="add_shipping_company"),
    path("edit/shipping-company/<str:pk>", views.edit_shipping_company, name="edit_shipping_company"),
    path("delete/shipping-company/<str:pk>", views.delete_shipping_company, name="delete_shipping_company"),
    path("faqs/", TemplateView.as_view(template_name='faqs.html'), name="faqs" ),
    path("terms/", TemplateView.as_view(template_name='terms.html'), name="terms" ),
    path("privacy-policy/", TemplateView.as_view(template_name='privacy-policy.html'), name="privacy_policy" ),
    
]
