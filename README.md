# OpsAI

## Project Description
GadoAI is an AI assistant for managing operations and KPIs in a corporate system. Users can ask questions in natural language about operations, costs, and KPIs. The system uses LangChain + Groq LLM to interpret queries, execute SQL against the database, and return precise, data-driven responses.

Originally focused on livestock management, the project has been adapted to a broader corporate operations and KPIs theme, keeping all AI query and analysis logic intact.

## Features

- KPI Queries: Total operations, total cost, average cost, completed, failed, and in-progress operations.
- Natural Language Chat: Ask short or medium-length questions about system data.
- Off-topic Filtering: The AI responds only to questions relevant to operations/KPIs.
- Interactive Frontend: Built with React + TailwindCSS for easy interaction.
- Consistency Verification: Answers match real database data.

## Project Structure

```
backend/
│
├── app/
│ ├── core/ # Configuration and logging
│ ├── db/ # Database scripts and connection
│ ├── services/ # SQL & LLM services
│ ├── api/ # FastAPI endpoints
│ ├── prompts/ # LLM prompts and examples
│ └── utils/ # Helper functions
│
├── scripts/ # Seed and auxiliary scripts
├── tests/ # Unit tests
├── .env # Environment variables
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```

## Technologies

- Python 3.12+
- FastAPI → backend and API
- PostgreSQL / Supabase → database
- LangChain + Groq → language model for SQL queries
- React / TailwindCSS → frontend chat interface

## Installation & Setup

Clone the repository:

```
git clone <REPO_URL>
cd backend
```

Install Python dependencies:

```
pip install -r requirements.txt
```

Configure environment variables in .env:

```
SUPABASE_DB_URI=<Your database URI>
GROQ_API_KEY=<Your Groq API key>
```

Start the API:

```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open the React frontend and start chatting with the AI assistant.

## Example Questions

"What is the total cost of operations?"
"How many operations have been completed?"
"How many operations are in progress?"
"What is the average cost per operation?"

## Contributing

Contributions are welcome!

If you want to test or improve the AI responses, feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License.
