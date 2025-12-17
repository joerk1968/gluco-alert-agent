# llm_advisor.py - REAL LLM ADVICE WITH ROBUST ERROR HANDLING
import time
import traceback
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS

class LLMAdvisor:
    def __init__(self):
        self.last_request_time = 0
        self.request_cooldown = 1.0  # seconds between requests
        self.max_retries = 3
        self.retry_delay = 2.0  # seconds
        
    def _get_llm_instance(self):
        """Create LLM instance with proper configuration"""
        if not OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key")
            
        return ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENAI_API_KEY,
            max_tokens=MAX_TOKENS,
            temperature=0.2,  # Low randomness for medical safety
            timeout=30.0,
            max_retries=2
        )
    
    def _create_prompt(self, glucose_level, trend, context):
        """Create context-aware prompt with safety guardrails"""
        # Determine condition type
        if glucose_level <= 70:
            condition = "low blood sugar (hypoglycemia)"
            action_focus = "immediate treatment with fast-acting carbohydrates"
        else:
            condition = "high blood sugar (hyperglycemia)"
            action_focus = "hydration and monitoring"
        
        # System prompt with strict safety rules
        system_prompt = (
            "You are a diabetes care assistant providing evidence-based guidance. "
            "NEVER suggest insulin dosing, medication changes, or specific medical procedures. "
            "ALWAYS include when to seek emergency help. "
            "For lows (≤70 mg/dL): recommend 15g fast-acting carbs, recheck in 15 minutes. "
            "For highs (≥180 mg/dL): recommend hydration, light activity, recheck in 1-2 hours. "
            "Use simple, actionable language. Max 3 sentences."
        )
        
        # User prompt with full context
        user_prompt = (
            f"Glucose reading: {glucose_level} mg/dL ({trend}) during {context}. "
            f"This indicates {condition}. "
            f"Provide immediate actions for {action_focus}. "
            "Include when to seek emergency help."
        )
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
    
    def _extract_advice(self, response):
        """Safely extract advice from LLM response"""
        try:
            # Handle different response formats
            if hasattr(response, 'content'):
                return str(response.content).strip()
            elif isinstance(response, dict) and 'content' in response:
                return str(response['content']).strip()
            elif isinstance(response, str):
                return response.strip()
            else:
                return str(response).strip()
        except Exception as e:
            print(f"⚠️ Error extracting advice: {str(e)}")
            return None
    
    def _get_safety_fallback(self, glucose_level, error_context=""):
        """Safety fallback advice when LLM fails"""
        base_advice = (
            "This is a safety message. Please consult your healthcare provider "
            "for personalized guidance. In emergencies, call emergency services."
        )
        
        if glucose_level <= 70:
            return (
                f"🚨 CRITICAL LOW GLUCOSE ({glucose_level} mg/dL)\n"
                "Immediately consume 15g fast-acting carbohydrates (4 oz juice, glucose tablets, or regular soda).\n"
                "Wait 15 minutes, then recheck blood sugar.\n"
                "If still ≤70 mg/dL or you feel confused/weak, call emergency services immediately.\n"
                f"{base_advice}"
            )
        else:
            return (
                f"🚨 HIGH GLUCOSE ({glucose_level} mg/dL)\n"
                "Drink 8-16 oz water and avoid carbohydrates for 1-2 hours.\n"
                "Consider light activity like walking if you feel well enough.\n"
                "Recheck blood sugar in 1-2 hours. If >250 mg/dL with nausea/vomiting, seek emergency care.\n"
                f"{base_advice}"
            )
    
    def get_advice(self, glucose_level, trend="stable", context="automated monitoring"):
        """Get real LLM advice with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Rate limiting
            elapsed = time.time() - self.last_request_time
            if elapsed < self.request_cooldown:
                time.sleep(self.request_cooldown - elapsed)
            
            # Create LLM instance
            llm = self._get_llm_instance()
            
            # Create prompt
            prompt = self._create_prompt(glucose_level, trend, context)
            
            # Get response with retry logic
            for attempt in range(self.max_retries):
                try:
                    print(f"🧠 LLM Request (attempt {attempt+1}/{self.max_retries})")
                    chain = prompt | llm
                    response = chain.invoke({})
                    
                    # Extract advice
                    advice = self._extract_advice(response)
                    
                    if advice and len(advice) > 20:  # Minimum meaningful length
                        self.last_request_time = time.time()
                        print(f"✅ LLM Response received in {time.time()-start_time:.2f}s")
                        return advice
                    else:
                        print(f"⚠️ LLM returned short/empty response: '{advice}'")
                
                except Exception as e:
                    error_type = type(e).__name__
                    print(f"❌ LLM attempt {attempt+1} failed: {error_type} - {str(e)[:100]}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
            
            # If all retries fail, use safety fallback
            print("❌ All LLM attempts failed - using safety fallback")
            return self._get_safety_fallback(glucose_level, "LLM failure")
            
        except ValueError as e:
            # Missing API key or configuration error
            print(f"❌ Configuration error: {str(e)}")
            return self._get_safety_fallback(glucose_level, "configuration error")
            
        except Exception as e:
            # Unexpected errors
            error_details = traceback.format_exc()
            print(f"🚨 Unexpected error in LLM advisor: {str(e)}")
            print(f"   Details: {error_details[:200]}...")
            return self._get_safety_fallback(glucose_level, "system error")

# Global instance
llm_advisor = LLMAdvisor()

def get_glucose_advice(glucose_level, trend="stable", context=""):
    """Public interface for getting glucose advice"""
    return llm_advisor.get_advice(glucose_level, trend, context)

# 🔬 Test function
if __name__ == "__main__":
    print("🧠 Testing REAL LLM advisor with error handling...")
    
    # Test low glucose scenario
    advice = get_glucose_advice(65, "falling", "fasting overnight")
    print(f"\n💡 Advice for LOW glucose (65 mg/dL):\n{'-'*50}\n{advice}\n{'-'*50}")
    
    # Test high glucose scenario
    advice = get_glucose_advice(210, "rising", "after dinner")
    print(f"\n💡 Advice for HIGH glucose (210 mg/dL):\n{'-'*50}\n{advice}\n{'-'*50}")
    
    print("\n✅ LLM advisor test complete")
           
    
           
              
    

   
         
        
     
    
