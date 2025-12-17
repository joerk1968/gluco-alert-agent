# llm_advisor.py - FIXED LLM ADVICE GENERATOR
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS

def get_glucose_advice(glucose_level, trend="stable", context=""):
    """
    Get AI-generated advice for abnormal glucose levels
    FIXED: Properly handles string responses
    """
    if not OPENAI_API_KEY:
        return "⚠️ LLM advice unavailable: missing OpenAI API key"

    try:
        # System prompt with safety guardrails
        system_prompt = (
            "You are a diabetes care assistant. Give concise, safe, evidence-based advice. "
            "NEVER suggest insulin dosing or medication changes. "
            "For lows (≤70 mg/dL): focus on fast-acting carbs. "
            "For highs (≥180 mg/dL): focus on hydration and rechecking. "
            "Always include when to seek emergency help. "
            "Use simple language. Max 3 sentences."
        )
        
        # Context-aware user prompt
        if glucose_level <= 70:
            condition = "low blood sugar (hypoglycemia)"
            action_focus = "immediate treatment with fast-acting carbohydrates"
        else:
            condition = "high blood sugar (hyperglycemia)"
            action_focus = "hydration and monitoring"
            
        user_prompt = (
            f"Glucose reading: {glucose_level} mg/dL ({trend}) during {context}. "
            f"This indicates {condition}. "
            f"What immediate actions should the patient take for {action_focus}? "
            "Include when to seek emergency help."
        )

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Initialize LLM
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENAI_API_KEY,
            max_tokens=MAX_TOKENS,
            temperature=0.2,  # Low randomness for medical safety
        )

        # Get response
        chain = prompt | llm
        response = chain.invoke({})
        
        # ✅ CRITICAL FIX: Handle response properly as string
        if hasattr(response, 'content'):
            advice = response.content.strip()
        else:
            advice = str(response).strip()
        
        # Safety fallbacks
        if not advice or len(advice) < 10:
            if glucose_level <= 70:
                advice = "Consume 15g fast-acting carbs (4 oz juice or glucose tablets). Recheck in 15 minutes. If still low or you feel worse, call emergency services."
            else:
                advice = "Drink 16 oz water and avoid carbohydrates. Recheck in 1-2 hours. If >250 mg/dL with nausea/vomiting, seek emergency help."
        
        return advice

    except Exception as e:
        error_msg = f"⚠️ LLM error: {type(e).__name__} - {str(e)}"
        print(f"🚨 LLM Error: {error_msg}")
        return error_msg

# 🔬 Test function
if __name__ == "__main__":
    print("🧠 Testing LLM advisor...")
    advice = get_glucose_advice(65, "falling", "fasting overnight")
    print(f"💡 Advice for low glucose:\n{advice}")
    
    advice = get_glucose_advice(210, "rising", "after dinner")
    print(f"\n💡 Advice for high glucose:\n{advice}")
           
              
    

   
         
        
     
    
