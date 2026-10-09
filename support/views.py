from django.shortcuts import render, get_object_or_404
import json
from django.http import JsonResponse, StreamingHttpResponse
import time
from .agents import run_support_agent
from .event_queue import subscribe, unsubscribe, publish
from .models import Message, Conversation, AgentLog
from orders.models import Order
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

def chat(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        if not user_message:
            return JsonResponse({"error":"empty message"}, status=400)

        order = get_object_or_404(Order, id=id, user =  request.user)
        conversation, created = Conversation.objects.get_or_create(user = request.user, order=order)
        Message.objects.create(conversation=conversation,role='user',content = user_message)
        event = {"type": "user_message", "message": user_message, "name": request.user.first_name}
        publish(conversation.id, event)
        #send user message and conversation to LLM
        reply = run_support_agent(user_message, conversation.id, order.id, request.user.id)
        #store the LLM reply
        Message.objects.create(conversation=conversation,role='assistant',content = reply)
        return JsonResponse({"reply": reply})

@staff_member_required
def dashboard(request):
    conversations = Conversation.objects.all().order_by("-created_at")
    context={
        "conversations": conversations
    }
    return render(request, "dashboard.html", context)

def conversation_detail(request, pk):
    conversation_detail = get_object_or_404(Conversation, id=pk)
    messages = conversation_detail.messages.order_by("created_at")
    logs = conversation_detail.agentlogs.order_by("created_at")
    print("Conv===>", conversation_detail)
    print("Message==>", messages)
    print("logs==>", logs)
    context = {
        "conversation_detail": conversation_detail,
        "messages": messages,
        "logs": logs
    }

    return render(request, "conversation_detail.html", context)


def conversation_stream(request, conversation_id):
    def event_stream(conversation_id):
        q= subscribe(conversation_id)
        try:
            while True:
                event = q.get()

                yield f"data: {json.dumps(event)}\n\n"
        finally:
            unsubscribe(conversation_id,q)
    response = StreamingHttpResponse(event_stream(conversation_id), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response