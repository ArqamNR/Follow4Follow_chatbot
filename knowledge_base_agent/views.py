from django.http import HttpResponse
from django.shortcuts import render
from knowledge_base_agent.knowlege_base_chatbot import KnowlegdeBase
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# --- Main execution loop ---
# This part remains similar to the original snippet, but uses the new Orchestrator class
knowledge_base_agent = KnowlegdeBase()


agent_creation_success = knowledge_base_agent.initialize()

def home(request):
    return render(request, 'index.html')

import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def get_user_input(request):
    if request.method == "POST":
        try:
            mem = knowledge_base_agent.memory_for_agent
            

            data = json.loads(request.body.decode("utf-8"))
            user_input = data.get("message", "")

            if agent_creation_success:
                bot_response = knowledge_base_agent.chat_with_agent(user_input)
            else:
                bot_response = "Agent not ready."

            # Prepare chat history
            chat_history = []
            for msg in mem.chat_memory.messages:
                chat_history.append({
                    "type": msg.__class__.__name__,
                    "content": msg.content
                })

            # Define save directory and file path
            history_dir = "chat_histories"
            history_file_path = os.path.join(history_dir, "chat_history.json")

            # Create directory if it doesn't exist
            os.makedirs(history_dir, exist_ok=True)

            # Save chat history to file
            with open(history_file_path, "w", encoding="utf-8") as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=4)
            total_tokens_used = knowledge_base_agent.knowledge_base_total_tokens
            input_tokens = knowledge_base_agent.knowledge_base_input_tokens
            output_tokens = knowledge_base_agent.knowledge_base_output_tokens
            return JsonResponse({"response": bot_response, 
                                 "tokens": total_tokens_used,
                                 "input_tokens":input_tokens,
                                 "output_tokens":output_tokens})

        except Exception as e:
            print(f"Exception: {e}")
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)
 