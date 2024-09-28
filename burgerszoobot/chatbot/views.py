from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render

from chatbot.services.chatbot_service import handle_chatbot_interaction 
from chatbot.services.llm_instructions import INSTRUCTIONS_CHATBOT


def chatbot_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user_input = request.POST.get('message')

        if 'chat_history' not in request.session:
            instructions = INSTRUCTIONS_CHATBOT
            request.session['chat_history'] = [{"role": "system", "content": instructions}]

        request.session['chat_history'].append({"role": "user", "content": user_input})

        response = handle_chatbot_interaction(request.session['chat_history'])
        
        request.session['chat_history'].append({"role": "assistant", "content": response})
        request.session.modified = True
        
        return JsonResponse({'response': response})
    
    return render(request, 'chatbot/chat.html')
