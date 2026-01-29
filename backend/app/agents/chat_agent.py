import os
import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

class ChatAgent:
    def __init__(self, tools):
        self.llm = ChatGroq(
            model="qwen/qwen3-32b",
            temperature=0.1, # Reduzi para 0.1 para ser mais focado em fatos
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.tools_map = {tool.name: tool for tool in tools}
        self.llm_with_tools = self.llm.bind_tools(tools)
        
        # Reforcei o prompt para ele nunca responder em inglês
        self.system_prompt = """Você é um Especialista em BI.
        Sua única fonte de dados é a ferramenta 'query_database'.
        
        REGRAS CRÍTICAS:
        1. Responda SEMPRE em Português do Brasil.
        2. Se o usuário perguntar por KPIs ou dados, você DEVE usar a ferramenta 'query_database'.
        3. Nunca invente desculpas em inglês. Se algo der erro, diga 'Tive um problema ao acessar os dados' em Português.
        4. Use Markdown para tabelas."""

    def ask(self, message: str) -> str:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=message)
        ]
        
        # 1. Primeira tentativa
        response = self.llm_with_tools.invoke(messages)
        
        # 2. Se o modelo pedir ferramenta
        if response.tool_calls:
            messages.append(response)
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"].lower()
                tool_to_call = self.tools_map.get(tool_name)
                
                if tool_to_call:
                    # Garantindo que pegamos o texto da pergunta corretamente
                    query_for_sql = tool_call["args"].get("input") or tool_call["args"].get("query") or message
                    
                    # Chama o SQLAgent
                    result = tool_to_call.func(query_for_sql)
                    
                    messages.append(ToolMessage(
                        content=str(result), 
                        tool_call_id=tool_call["id"]
                    ))
            
            # 3. Resposta final humanizada
            response = self.llm_with_tools.invoke(messages)
        
        # Limpeza de tags <think>
        clean_content = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()
        return clean_content