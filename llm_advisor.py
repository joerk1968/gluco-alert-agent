# llm_advisor.py - FIXED FOR STRING RESPONSES
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS
import json

def get_glucose_advice(glucose_level, trend="stable", context=""):
    """
    Gets AI-generated advice for abnormal glucose.
    FIXED: Handles string responses properly.
    """
    if not OPENAI_API_KEY:
        return "⚠️ LLM advice unavailable: missing OpenAI key."

    try:
        # Define prompt
        system_prompt = (
            "You are a diabetes care assistant. Give concise, safe, evidence-based advice. "
            "Never suggest insulin dosing. Focus on: carbs, hydration, rechecking, when to seek help. "
            "Use simple language. Max 3 sentences."
        )
        
        user_prompt = (
            f"Glucose: {glucose_level} mg/dL ({'low' if glucose_level <= 70 else 'high' if glucose_level >= 180 else 'normal'}), "
            f"trend: {trend}. Context: '{context}'. What should the patient do now?"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Init LLM
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENAI_API_KEY,
            max_tokens=MAX_TOKENS,
            temperature=0.3
        )

        # Chain & invoke
        chain = prompt | llm
        response = chain.invoke({})
        
        # ✅ CRITICAL FIX: Handle both string and message responses
        if hasattr(response, 'content'):
            advice = response.content.strip()
        elif isinstance(response, str):
            advice = response.strip()
        else:
            # Try to extract content from various response formats
            try:
                response_dict = json.loads(str(response))
                advice = response_dict.get('content', str(response))
            except:
                advice = str(response)
        
        # Safety fallback
        if not advice or len(advice) < 10:
            if glucose_level <= 70:
                advice = "Consume 15g fast-acting carbs (e.g., juice). Recheck in 15 minutes. If still low, repeat and contact provider."
            elif glucose_level >= 180:
                advice = "Hydrate well and consider light activity. Recheck in 1-2 hours. If persistently high, contact your healthcare provider."
            else:
                advice = "Glucose is in normal range. Continue regular monitoring and stay hydrated."
        
        return advice

    except Exception as e:
        error_msg = f"⚠️ LLM error: {type(e).__name__} - {str(e)}"
        print(f"🚨 LLM Error: {error_msg}")
        return error_msg

# 🔬 Test
if __name__ == "__main__":
    print("🧠 Testing LLM advisor (low glucose)...")
    advice = get_glucose_advice(glucose_level=62, trend="falling", context="fasting")
    print(f"💡 Advice:\n{advice}")


   
         
        
     
    
