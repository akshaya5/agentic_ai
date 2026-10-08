


from datetime import timedelta

from .tracking_data import DELIVERY_DATA
from orders.models import Order, RefundRequest
from django.utils import timezone


def get_order_details(order_id):
    try:
        order = Order.objects.get(id=order_id)
        return {
            "order_id": order.id,
            "product_name": order.product_name,
            "amount" : order.amount,
            "status" : order.status,
            "carrier" : order.carrier,
            "tracking_number" : order.tracking_number,
            "delivery": order.delivery,
            "created_at": order.created_at.strftime('%d %b %Y'),
            "days_since_order": (timezone.now() - order.created_at).days
        }
    except Order.DoesNotExist:
        return {"error": f"Order Number #{order_id} not found"}


def get_refund_history(user_id):
    refunds = RefundRequest.objects.filter(user_id=user_id).order_by("-created_at")
    history =[]
    print(refunds)
    print(type(refunds))
    for r in refunds:
        history.append({
            "order_id": r.order.id,
            "product": r.order.product_name,
            "reason" : r.reason,
            "status" : r.status,
            "requested_on": r.created_at.strftime('%d %b %Y')
        })

    return {
        "total_refund_requests": len(history),
        "history": history 
    }

def check_delivery_status(tracking_number, carrier):
    default_response = {
        "status": "Unknown",
        "last_location": "Tracking info unavailable",
        "last_update": "N/A",
        "estimated_delivery": "Contact carrier directly",
        "delay_reason": "No updates from carrier",
    }
    result = DELIVERY_DATA.get(tracking_number, default_response)
    result["tracking_number"] = tracking_number
    result["carrier"] = carrier
    return result

def get_customer_risk_profile(user_id):
    refund = RefundRequest.objects.filter(user_id=user_id)
    order = Order.objects.filter(user_id=user_id)

    refund_count = refund.filter(created_at__gte=timezone.now() - timedelta(days=90)).count()

    approved = refund.filter(status="approved").count()
    denied = refund.filter(status="denied").count()
    pending = refund.filter(status="pending").count()

    total_orders= order.count()
    total_refunds= refund.count()

    if total_orders > 0:
        refund_to_order_ratio = round(total_refunds/total_orders, 2)
    else: 
        refund_to_order_ratio=0

    return{
        "user_id": user_id,
        "total_orders": total_orders,
        "total_refunds_requests": total_refunds,
        "refunds_last_90_days": refund_count,
        "approved_refunds": approved,
        "denied_refunds": denied,
        "pending_refunds": pending,
        "refund_to_order_ratio": refund_to_order_ratio
    }