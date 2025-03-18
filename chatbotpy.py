import time  
import replicate   
import os  
import re  

os.environ["REPLICATE_API_TOKEN"] = "r8_NBscZArVdjzaKtqvyvnrJyJ1N1tLFEa3wNGa2"  

salon_services = {  
    "haircut": 400,  
    "hair drying": 50,  
    "hair coloring": 150,  
    "nail polish": 30  
}  

opening_hours = "We are open from 9:00 AM to 8:00 PM, Monday to Saturday. Closed on Sundays."  

classification_keywords = {  
    "haircut": [r"\b(haircut|cut hair|trim)\w*\b"],  
    "hair drying": [r"\b(dry|blow dry)\w*\b"],  
    "hair coloring": [r"\b(color|dye|highlight)\w*\b"],  
    "nail polish": [r"\b(nail|manicure|polish)\w*\b"],  
    "time": [r"\b(open|close|hours|when)\b"]  
}  

services_list = "\n".join([f"- {service}: ${price}" for service, price in salon_services.items()])  

system_prompt = f"""  
You are a Salon Assistant . You provide **short and direct answers** about salon services, prices, and opening hours.  

Here are the available services:  
{services_list}  

Salon Opening Hours:  
{opening_hours}  

Rules:  
1. If asked about a service, respond with just the price.  
   Example: "How much is a haircut?" -> "$400"  
2. If asked about opening hours, respond with the full time schedule.  
   Example: "What time do you open?" -> "We are open from 9:00 AM to 8:00 PM, Monday to Saturday. Closed on Sundays."  
3. If the question is not about these topics, say "I'm here to assist with salon services and hours."  
4. If the user's request is ambiguous and you cannot determine the service they are asking about, respond with "I'm here to assist with salon services and hours."  
"""  

def classify_message(user_input):  
    user_input_lower = user_input.lower()  
    for category, keywords in classification_keywords.items():  
        for keyword_pattern in keywords:  
            if re.search(keyword_pattern, user_input_lower):  
                return category  
    return "other"  


def get_salon_response(user_query, max_retries=3, initial_delay=1):  
    prompt = f"{system_prompt}\nCustomer: {user_query}\nSalon Assistant:"  

    for attempt in range(max_retries):  
        try:  
            response = replicate.run("meta/llama-2-7b-chat", input={  
                "prompt": prompt,  
                "max_length": 100,  
                "temperature": 0  
            }, timeout=120)  

            if isinstance(response, list):  
                response_text = " ".join(response).strip()  
            else:  
                response_text = str(response).strip()  

            return response_text  

        except Exception as e:  
            print(f"Attempt {attempt+1} failed: {e}")  
            if attempt == max_retries - 1:  
                print("Max retries reached.  Returning error message.")  
                return "I'm sorry, I encountered an error processing your request."  

            wait_time = initial_delay * (2 ** attempt)  
            print(f"Waiting {wait_time} seconds before retrying...")  
            time.sleep(wait_time)  

    return "I'm sorry, I encountered an error processing your request."  

def analyze_last_message(user_messages):  
    
    if len(user_messages) < 1:  
        print("Not enough messages to analyze.")  
        return None, None  

    last_message = user_messages[-1]  
    classification = classify_message(last_message)  

    return last_message, classification  


  
def main_chat_loop():  
    user_messages = []  
    ai_responses = []  
    print("Salon Assistant AI: Hello! How can I assist you today?")  

    while True:  
        user_query = input("User: ")  

        if user_query.lower() == "end chat":  
            print("Salon Assistant AI: Thank you for chatting with us! Have a great day!")  

              
            last_message, classification = analyze_last_message(user_messages)  
            if last_message:  
                print(f"\nClassification of User Message:")  
                print(f"Message: {last_message}")  
                print(f"Classification: {classification}")  
            break  

        user_messages.append(user_query)  

        response = get_salon_response(user_query)  
        ai_responses.append(response)  
        print(f"Salon Assistant AI: {response}")  


if __name__ == "__main__":  
    main_chat_loop()  