
from langsmith import Client
from dotenv import load_dotenv

load_dotenv(override=True)

client = Client()
client.update_run(run_id="77d5f23a-19d7-4b9e-bc7b-ed10dd8f09d2", status="aborted")
