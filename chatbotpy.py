import time  
import replicate   
import os  


os.environ["REPLICATE_API_TOKEN"] = " r8_NsSc2LNahlSPo1MAPJz5VLJT2DFNByu2NJ2gd"  

salon_services = {  
    "haircut": {"price": 400, "description": "A basic haircut includes trimming and styling."},  
    "hair drying": {"price": 50, "description": "Professional blow-dry styling."},  
    "hair coloring": {"price": 150, "description": "Full coloring service, including consultation."},  
    "nail polish": {"price": 30, "description": "Application of nail polish for hands or feet."},  
    "manicure": {"price": 40, "description": "Includes nail trimming, shaping, and polish."},  
    "pedicure": {"price": 50, "description": "Foot soak, scrub, nail care, and polish."},  
    "facial": {"price": 100, "description": "Cleansing and nourishing of the facial skin."},  
    "waxing": {"price": 25, "description": "Removal of hair using waxing technique."},  
    "hair treatment": {"price": 80, "description": "Deep conditioning treatment for hair health."}  
}  
opening_hours = "We are open from 9:00 AM to 8:00 PM, Monday to Saturday. Closed on Sundays."  


services_list = "\n".join([f"- {service}: ${details['price']}" for service, details in salon_services.items()])  
 

system_prompt = f"""  
You are a Salon Assistant . You provide **short and direct answers** about salon services, prices, and opening hours.  

Here are the available services:  
{services_list}  

Salon Opening Hours:  
{opening_hours}  

Rules:     
1. If the user greets you with phrases like "hey", "hello", "hi", "good morning", "good afternoon", or "good evening", respond with "Hey! How can I assist you today?".  
2. If the user asks "What are your services?", respond with "We offer the following services: [list of services]".  
3. If asked about a service price, respond with just the price.  
   Example: "How much is a haircut?" -> "$400"  
4. If asked about opening hours, respond with the full time schedule.  
   Example: "What time do you open?" -> "We are open from 9:00 AM to 8:00 PM, Monday to Saturday. Closed on Sundays."  
5. If a user requests an explanation of any service, provide a brief description.  
   Example: "Tell me about hair coloring." -> "Full coloring service, including consultation."  
6. If the user says they need any service or asks in a general way, respond with "Okay, how can I help you?"  
7. If the question is not about these topics, say "I'm here to assist with salon services and hours."  
8. If the user's request is ambiguous and you cannot determine the service they are asking about, respond with "I'm here to assist with salon services and hours."  
"""  




    
      
def get_salon_response(user_query):  
    
    greeting_keywords = ["hey", "hello", "hi", "good morning", "good afternoon", "good evening"]  
    if any(greet in user_query.lower() for greet in greeting_keywords):  
        return "Hey! How can I assist you today?"  

  
    if "what are your services" in user_query.lower():  
        return "We offer the following services: " + ", ".join(salon_services.keys()) + "."  

     
    for service, details in salon_services.items():  
        if service in user_query.lower():  
            if "how much" in user_query.lower():  
                return f"${details['price']}"  
            if "explain" in user_query.lower() or "tell me about" in user_query.lower():  
                return f"{details['description']} Its price is ${details['price']}."  
            return f"Sure! I have the following service:\n- {service}: ${details['price']}"  

      
    if "need" in user_query.lower():  
        return "Okay, how can I help you?"  

     
    prompt = f"{system_prompt}\nUser: {user_query}\nSalon Assistant:"  

    try:  
        response = replicate.run("meta/llama-2-7b-chat", input={  
            "prompt": prompt,  
            "max_length": 100,  
            "temperature": 0  
        })  
        
        return " ".join(response).strip()  
    except Exception as e:  
        print(f"Error during response generation: {e}")  
        return "I'm sorry, I encountered an error processing your request."  
def classify_last_message_with_context(all_messages):  
    if not all_messages:  
        return "No messages to classify."  

   
    last_message = all_messages[-1]  
    print(last_message)
   
    context_history = "\n".join(all_messages[:-1]) if len(all_messages) > 1 else ""  

    prompt = f"Based on the following chat history:\n{context_history}\n\nClassify the last message:\n{last_message}\n\nOutput only the category name."  

    try:  
        response = replicate.run("meta/llama-2-7b-chat", input={  
            "prompt": prompt,  
            "max_length": 100,  
            "temperature": 0,  
        })  

      
        if isinstance(response, list):  
            classification_result = " ".join(response).strip()  
        else:  
            classification_result = response.strip()  

        return classification_result  
    except Exception as e:  
        print(f"Error during classification: {e}")  
        return "I'm sorry, I encountered an error processing the classification."  

def compare_classifications_with_llm(ai_classification, user_classification, max_retries=3, initial_delay=1):  
    """Use a separate LLM to compare classifications and score them."""  
    prompt = f"Compare the AI classification '{ai_classification}' and the user classification '{user_classification}'.\n" \
             f"Rate the similarity on a scale from 1 to 100 and explain why."  

    for attempt in range(max_retries):  
        try:  
            response = replicate.run("meta/llama-2-7b-chat", input={  
                "prompt": prompt,  
                "max_length": 150,  
                "temperature": 0,  
            })  

            
            if isinstance(response, list):  
                return " ".join(response).strip()  
            else:  
                return response.strip()    

        except Exception as e:  
            print(f"Attempt {attempt + 1} failed: {e}")  
            if attempt == max_retries - 1:  
                return "I'm sorry, I encountered an error processing the comparison."  

            wait_time = initial_delay * (2 ** attempt)  
            print(f"Waiting {wait_time} seconds before retrying...")  
            time.sleep(wait_time)  
 
def main_chat_loop():  
    user_messages = []  
    print("Salon Assistant AI: Hello! How can I assist you today?")  

    while True:  
        user_query = input("User: ")  
        
        if user_query.lower() == "end chat":  
            print("Salon Assistant AI: Thank you for chatting with us! Have a great day!")  
            ai_classification = classify_last_message_with_context(user_messages)  
            print(f"Classification by LLM model: {ai_classification}")  

              
            user_classification = input("Please enter your classification for this message: ")  

                
            comparison_result = compare_classifications_with_llm(ai_classification, user_classification)  
            print(f"Comparison Result:\n{comparison_result}")  
            break  
        
        user_messages.append(user_query)  
        response = get_salon_response(user_query)  
        print(f"Salon Assistant AI: {response}")  

if __name__ == "__main__":  
    main_chat_loop()  