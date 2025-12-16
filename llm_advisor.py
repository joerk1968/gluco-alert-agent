

# llm_advisor.py - CONTEXT-AWARE MEDICAL ADVICE GENERATOR
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS

def get_glucose_advice(glucose_level, trend="stable", context=None):
    """
    Gets AI-generated, context-aware advice for abnormal glucose.
    
    Args:
        glucose_level (float): Current glucose in mg/dL
        trend (str): 'rising', 'falling', 'stable', 'rising rapidly', 'falling rapidly'
        context (dict): Optional context with meal/exercise/time info
    
    Returns:
        str: Actionable, clinically safe advice (1-3 sentences)
    """
    if not OPENAI_API_KEY:
        return "⚠️ LLM advice unavailable: missing OpenAI key."

    try:
        # Build context string for LLM
        context_str = "Standard monitoring"
        if context:
            parts = []
            if context.get('meal'):
                parts.append(f"recent {context['meal']}")
            if context.get('exercise'):
                parts.append("post-exercise")
            if context.get('time_of_day') == 'night':
                parts.append("overnight")
            context_str = ", ".join(parts) if parts else "Standard monitoring"

        # Enhanced prompt with safety guardrails
        system_prompt = (
            "You are a diabetes care assistant providing evidence-based guidance. "
            "NEVER suggest specific insulin doses or medication changes. "
            "ALWAYS prioritize safety: for lows, focus on fast carbs; for highs, focus on hydration and rechecking. "
            "Use simple, actionable language. Max 3 sentences. Include when to seek emergency help."
        )
        
        # Context-aware prompts
        if glucose_level <= 70:  # Hypoglycemia
            user_prompt = (
                f"CRITICAL: Glucose {glucose_level:.1f} mg/dL ({trend}) during {context_str}. "
                "Patient needs immediate, clear instructions for treating low blood sugar. "
                "What should they do RIGHT NOW, and when should they recheck or seek help?"
            )
        elif glucose_level >= 180:  # Hyperglycemia  
            user_prompt = (
                f"ELEVATED: Glucose {glucose_level:.1f} mg/dL ({trend}) during {context_str}. "
                "Patient needs practical steps to address high blood sugar safely. "
                "What actions should they take, and what warning signs require immediate medical attention?"
            )
        else:  # Normal range (still provide helpful context)
            if "overnight" in context_str or context_str == "night":
                user_prompt = (
                    f"Normal overnight glucose: {glucose_level:.1f} mg/dL ({trend}). "
                    "Provide brief reassurance and guidance for nighttime monitoring."
                )
            else:
                user_prompt = (
                    f"Stable glucose: {glucose_level:.1f} mg/dL ({trend}) during {context_str}. "
                    "Provide brief positive reinforcement and general monitoring advice."
                )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Init LLM with safety settings
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENAI_API_KEY,
            max_tokens=MAX_TOKENS,
            temperature=0.2,  # Low randomness for medical safety
            top_p=0.9
        )

        # Generate advice
        chain = prompt | llm
        response = chain.invoke({})
        
        advice = response.content.strip()
        
        # Safety post-processing
        if glucose_level <= 70 and "15g" not in advice.lower():
            advice = f"🚨 URGENT: Consume 15g of fast-acting carbohydrates immediately (4 oz juice, glucose tablets, or regular soda). Wait 15 minutes, then recheck. If still ≤70 mg/dL or you feel worse, repeat treatment and call your healthcare provider."
        elif glucose_level >= 180 and any(word in advice.lower() for word in ["insulin", "dose", "units"]):
            advice = "💧 Drink 8-16 oz water and avoid carbohydrates for the next hour. Recheck glucose in 1-2 hours. If >250 mg/dL with nausea/vomiting, seek medical attention immediately."

        return advice

    except Exception as e:
        return f"⚠️ LLM error: {type(e).__name__} - {str(e)}"

# 🔬 TEST FUNCTION
if __name__ == "__main__":
    print("🧠 Testing CONTEXT-AWARE LLM advice generator...\n")
    
    # Test multiple realistic scenarios
    scenarios = [
        {"glucose": 62.4, "trend": "falling rapidly", "context": {"meal": "breakfast", "time_of_day": "day"}},
        {"glucose": 215.7, "trend": "rising", "context": {"meal": "dinner", "time_of_day": "day"}},
        {"glucose": 68.3, "trend": "falling", "context": {"time_of_day": "night"}},
        {"glucose": 142.8, "trend": "stable", "context": {"exercise": True, "time_of_day": "day"}}
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🧪 Scenario {i}:")
        print(f"   Glucose: {scenario['glucose']} mg/dL ({scenario['trend']})")
        print(f"   Context: {scenario['context']}")
        
        advice = get_glucose_advice(**scenario)
        print(f"💡 Advice:\n{advice}\n")
        print("-" * 60)
