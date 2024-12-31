from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render

from .services.chatbot_service import handle_chatbot_interaction 
from .services.llm_instructions import INSTRUCTIONS_CHATBOT
from .services.rag import RAGSettings


def chatbot_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user_input = request.POST.get('message')
        chat_history_enabled = request.POST.get('chat_history_enabled') == "true"
        rag_settings = RAGSettings(
            rag=request.POST.get('use_rag') == "true",
            retrieval_top_n=int(request.POST.get('retrieval_top_n', '5')),
            classification=request.POST.get('use_classification') == "true",
            rephrasing=request.POST.get('use_rephrasing') == "true",
            reranking=request.POST.get('use_reranking') == "true",
            reranking_top_n=int(request.POST.get('reranking_top_n', '5')),
            repacking=request.POST.get('use_repacking') == "true"
        )

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

        response = handle_chatbot_interaction(chat_history=chat_history, rag_settings=rag_settings)
        
        if chat_history_enabled:
            request.session['chat_history'].append({"role": "assistant", "content": response})
            request.session.modified = True
        
        return JsonResponse({'response': response})
    
    if request.method == 'GET':
        request.session.clear()
    return render(request, 'chatbot/chat.html')
