from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render

def chatbot_response(message: str) -> str:
    if 'hello' in message.lower():
        return "Hello! How can I help you today?"
    elif 'how are you' in message.lower():
        return "I'm just a bot, but I'm doing great! How about you?"
    elif 'bye' in message.lower():
        return "Goodbye! Have a great day!"
    else:
        return "Sorry, I didn't understand that."

def chatbot_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        message = request.POST.get('message')
        response = chatbot_response(message)
        return JsonResponse({'response': response})
    return render(request, 'chatbot/chat.html')
