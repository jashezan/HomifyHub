from django.urls import path
from .views import (
    OrderCreateView,
    OrderSummaryView,
    OrderHistoryView,
    OrderTrackingView,
    OrderCancelView,
    OrderInvoiceView,
    ThankYouView,
)

app_name = "orders"

urlpatterns = [
    path("checkout/", OrderCreateView.as_view(), name="checkout"),
    path("summary/<int:pk>/", OrderSummaryView.as_view(), name="order_summary"),
    path("history/", OrderHistoryView.as_view(), name="order_history"),
    path("tracking/<int:pk>/", OrderTrackingView.as_view(), name="order_tracking"),
    path("cancel/<int:pk>/", OrderCancelView.as_view(), name="order_cancel"),
    path("invoice/<int:pk>/", OrderInvoiceView.as_view(), name="invoice"),
    path("thank-you/<int:pk>/", ThankYouView.as_view(), name="thank_you"),
]
