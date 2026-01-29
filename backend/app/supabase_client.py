import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Validate credentials
if not supabase_url or not supabase_key:
    raise ValueError(
        "Missing Supabase credentials. "
        "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file"
    )

# Create and export Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Optional: Test connection on import
try:
    # Simple health check
    supabase.table("farms").select("id").limit(1).execute()
    print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not verify Supabase connection: {e}")