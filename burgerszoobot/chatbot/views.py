from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render

from chatbot.services.chatbot_service import handle_chatbot_interaction 
from chatbot.services.llm_instructions import INSTRUCTIONS_CHATBOT


def chatbot_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user_input = request.POST.get('message')
        chat_history_enabled = request.POST.get('chat_history_enabled') == "true"
        retrieval_method = request.POST.get('retrieval_method')
        if not retrieval_method:
            raise ValueError("No retrieval method found in POST request.")

        if chat_history_enabled:
            if 'chat_history' not in request.session:
                request.session['chat_history'] = [{"role": "system", "content": INSTRUCTIONS_CHATBOT}]

            request.session['chat_history'].append({"role": "user", "content": user_input})
            chat_history = request.session['chat_history']
        else:
            chat_history = [
                {"role": "system", "content": INSTRUCTIONS_CHATBOT},
                {"role": "user", "content": user_input}
            ]

        response = handle_chatbot_interaction(chat_history=chat_history, retrieval_method=retrieval_method)
        
        if chat_history_enabled:
            request.session['chat_history'].append({"role": "assistant", "content": response})
            request.session.modified = True
        
        return JsonResponse({'response': response})
    
    return render(request, 'chatbot/chat.html')
