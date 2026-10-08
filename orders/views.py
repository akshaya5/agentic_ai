from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from support.models import Conversation
from .models import Order, RefundRequest

# Create your views here.

@login_required
def get_orders_list(request):
    orders = Order.objects.filter(user=request.user)
    context = {
        "orders": orders
    }

    return render(request,'orders_list.html', context )

def get_order_detail(request, pk):
    order = get_object_or_404(Order, id=pk, user =request.user)
    refunds = RefundRequest.objects.filter(order=order)
    try:
        conversation = Conversation.objects.get(user = request.user, order=order)
        previous_messages = conversation.messages.order_by("created_at")
    except Conversation.DoesNotExist:
        conversation=None
        previous_messages=[]

    context = {
        "order": order,
        "refunds": refunds,
        "conversation": conversation,
        "previous_messages":previous_messages
    }

    return render(request, 'order_detail.html', context)