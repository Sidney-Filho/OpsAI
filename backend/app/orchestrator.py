import os
from langchain_core.tools import Tool
from app.agents.chat_agent import ChatAgent
from app.agents.sql_agent import SQLAgent

class AIOrchestrator:
    def __init__(self):
        db_uri = os.getenv("SUPABASE_DB_URI")
        
        # 1. Instancia o executor de SQL
        self.sql_executor = SQLAgent(db_uri)
        
        # 2. Define a ferramenta de banco de dados
        # A 'description' é o que diz ao ChatAgent QUANDO usar essa ferramenta
        sql_tool = Tool(
            name="query_database",
            func=self.sql_executor.run,
            description="Útil para responder perguntas sobre dados reais, vendas, estoque e clientes. Entrada: a pergunta do usuário."
        )
        
        # 3. Inicializa o ChatAgent passando a lista de ferramentas
        self.chat_agent = ChatAgent(tools=[sql_tool])

    def handle_message(self, message: str) -> str:
        """
        O fluxo agora é automático:
        O ChatAgent recebe a mensagem -> Decide se precisa da Tool -> 
        Chama o SQLAgent -> Formata a resposta final.
        """
        return self.chat_agent.ask(message)