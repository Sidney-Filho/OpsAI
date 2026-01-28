# app/ai_agent.py
"""
AI Agent System for Livestock Management
Uses LangChain to query Supabase database and answer questions
"""

from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URI from environment
def get_database_uri():
    """Get PostgreSQL connection URI for Supabase"""
    db_uri = os.getenv("SUPABASE_DB_URI")
    if not db_uri:
        # Try to construct from URL if not provided
        supabase_url = os.getenv("SUPABASE_URL", "")
        if "supabase.co" in supabase_url:
            project_id = supabase_url.split("//")[1].split(".")[0]
            print("⚠️  SUPABASE_DB_URI not found in .env")
            print(f"Add this to your .env file:")
            print(f"SUPABASE_DB_URI=postgresql://postgres:[YOUR-PASSWORD]@db.{project_id}.supabase.co:5432/postgres")
            raise ValueError("SUPABASE_DB_URI not configured")
    return db_uri

# Initialize the LLM
def initialize_llm():
    """Initialize Groq LLM"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")
    
    llm = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,  # Deterministic for data queries
        api_key=groq_api_key
    )
    return llm

# Enhanced system prompt
SYSTEM_PROMPT = """You are an AI assistant specialized in livestock management and insemination data analysis.

**YOUR ROLE:**
- Answer questions about farms, animals, bulls, protocols, and inseminations
- Query the database to provide accurate, data-driven responses
- Support both English and Portuguese languages naturally
- Be concise, clear, and professional

**DATABASE SCHEMA:**
Tables available:
1. **farms**: id, name, state, municipality, created_at
2. **animals**: id, animal_number, breed, category, farm_id, created_at
3. **bulls**: id, bull_name, bull_breed, bull_company, created_at
4. **protocols**: id, protocol_name, protocol_days, p4_implant, company, created_at
5. **inseminations**: id, animal_id, bull_id, protocol_id, inseminator, insemination_date, result, created_at

**RELATIONSHIPS:**
- animals.farm_id → farms.id
- inseminations.animal_id → animals.id
- inseminations.bull_id → bulls.id
- inseminations.protocol_id → protocols.id

**IMPORTANT RULES:**
1. ALWAYS query the database before answering - never assume or guess data
2. If asked about topics outside livestock management, politely decline:
   "I can only help with questions about farms, animals, bulls, protocols, and insemination data."
3. When calculating percentages or rates, show your work
4. If data is not available, say so clearly
5. Provide context with your answers when helpful

**EXAMPLES OF GOOD RESPONSES:**

Question: "How many farms do we have?"
Response: "We currently have 3 farms in the system."

Question: "What's the success rate of inseminations?"
Response: "Based on the data, we have 200 total inseminations. [Calculate and show breakdown by result status]"

Question: "Quantas fazendas temos?"
Response: "Atualmente temos 3 fazendas no sistema."

Always be helpful, accurate, and professional.
"""

class LivestockAgent:
    """Main AI Agent for Livestock Management queries"""
    
    def __init__(self):
        """Initialize the agent with LLM and database connection"""
        try:
            print("🔧 Initializing AI Agent...")
            
            # Initialize LLM
            self.llm = initialize_llm()
            print("✅ LLM initialized (Groq)")
            
            # Connect to database
            db_uri = get_database_uri()
            self.db = SQLDatabase.from_uri(
                db_uri,
                include_tables=['farms', 'animals', 'bulls', 'protocols', 'inseminations']
            )
            print("✅ Database connected")
            
            # Create toolkit
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            
            # Create SQL Agent
            self.agent = create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=False,  # Set to True for debugging
                agent_type="openai-tools",
                prefix=SYSTEM_PROMPT,
                max_iterations=5,
                max_execution_time=30,
                early_stopping_method="generate"
            )
            print("✅ SQL Agent created")
            
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
            raise
    
    def query(self, question: str) -> str:
        """
        Process user question and return answer
        
        Args:
            question: User's question in English or Portuguese
            
        Returns:
            Agent's response based on database data
        """
        try:
            # Quick filter for obviously off-topic questions
            off_topic_keywords = [
                "weather", "clima", "news", "notícias", "recipe", "receita",
                "movie", "filme", "game", "jogo", "politics", "política",
                "sports", "esporte", "music", "música", "celebrity", "celebridade"
            ]
            
            question_lower = question.lower()
            if any(keyword in question_lower for keyword in off_topic_keywords):
                if any(c in question for c in "áàâãéêíóôõúç"):  # Portuguese chars
                    return (
                        "Só posso ajudar com perguntas sobre fazendas, animais, touros, "
                        "protocolos e dados de inseminação. Como posso ajudar com "
                        "informações de gestão pecuária?"
                    )
                else:
                    return (
                        "I can only help with questions about farms, animals, bulls, "
                        "protocols, and insemination data. How can I assist you with "
                        "livestock management information?"
                    )
            
            # Run the agent
            response = self.agent.invoke({"input": question})
            # Extract the output from the response
            if isinstance(response, dict) and "output" in response:
                return response["output"]
            return str(response)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error in query: {error_msg}")
            
            # User-friendly error message
            if "timeout" in error_msg.lower():
                return "Sorry, the query took too long. Please try rephrasing your question."
            else:
                return f"Sorry, I encountered an error processing your question. Please try again or rephrase your question."
    
    def get_database_stats(self) -> dict:
        """Get quick statistics about the database"""
        try:
            stats = {}
            tables = ['farms', 'animals', 'bulls', 'protocols', 'inseminations']
            
            for table in tables:
                result = self.db.run(f"SELECT COUNT(*) FROM {table}")
                # Extract number from result string
                try:
                    # Handle different result formats
                    lines = result.strip().split('\n')
                    count_str = lines[-1].strip()
                    # Remove parentheses and get the number
                    if '(' in count_str and ')' in count_str:
                        count_str = count_str.strip('()')
                    count = int(count_str.split(',')[0].strip())
                    stats[table] = count
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse count for {table}: {e}")
                    stats[table] = 0
            
            return stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"error": str(e)}


# Standalone testing
if __name__ == "__main__":
    print("🤖 Initializing Livestock AI Agent for testing...")
    
    try:
        agent = LivestockAgent()
        print("✅ Agent initialized successfully!\n")
        
        # Show database stats
        print("📊 Database Statistics:")
        stats = agent.get_database_stats()
        if "error" not in stats:
            for table, count in stats.items():
                print(f"   • {table}: {count} records")
        else:
            print(f"   Error: {stats['error']}")
        
        print("\n" + "="*60)
        print("💬 Test some questions:")
        print("="*60 + "\n")
        
        # Test questions
        test_questions = [
            "How many farms do we have?",
            "Quantos touros temos no sistema?",
        ]
        
        for q in test_questions:
            print(f"Q: {q}")
            print(f"A: {agent.query(q)}\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")