# llm_advisor.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS

def get_glucose_advice(glucose_level, trend="stable", context=""):
    """
    Gets AI-generated advice for abnormal glucose.
    
    Args:
        glucose_level (int): Current glucose in mg/dL
        trend (str): 'rising', 'falling', or 'stable'
        context (str): Optional (e.g., "just ate", "fasting", "post-exercise")
    
    Returns:
        str: Actionable advice (1–3 sentences)
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
            temperature=0.3  # deterministic but not rigid
        )

        # Chain & invoke
        chain = prompt | llm
        response = chain.invoke({})

        return response.content.strip()

    except Exception as e:
        return f"⚠️ LLM error: {type(e).__name__}"

# 🔬 Test
if __name__ == "__main__":
    print("🧠 Testing LLM advisor (low glucose)...")
    advice = get_glucose_advice(glucose_level=62, trend="falling", context="fasting")
    print(f"💡 Advice:\n{advice}")