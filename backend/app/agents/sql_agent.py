from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import os

class SQLAgent:
    def __init__(self, db_uri: str):
        # Temperatura 0 é crucial para precisão em SQL
        self.llm = ChatGroq(
            model="qwen/qwen3-32b",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.db = SQLDatabase.from_uri(db_uri)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)

        # Configuração do agente especializado em banco de dados
        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type="openai-tools",
            verbose=False,
            max_iterations=5, # Aumentei um pouco para queries complexas
            max_execution_time=20,
            early_stopping_method="generate"
        )

    def run(self, question: str) -> str:
        """
        Este método será o 'coração' da sua Tool.
        Ele recebe a pergunta, gera o SQL, executa e retorna o resultado.
        """
        try:
            response = self.agent.invoke({"input": question})
            return response.get("output", str(response))
        except Exception as e:
            return f"Erro ao consultar o banco de dados: {str(e)}"