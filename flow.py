from pocketflow import Flow
from nodes import CrawlAndExtract, AgentDecision, DraftAnswer

def create_support_bot_flow():
    """Create and return an AI support bot flow."""
    # Create nodes
    crawl_node = CrawlAndExtract(max_retries=3, wait=10)
    agent_node = AgentDecision(max_retries=3, wait=10)
    draft_answer_node = DraftAnswer(max_retries=3, wait=10)
    
    # Connect nodes with transitions
    crawl_node >> agent_node
    agent_node - "explore" >> crawl_node  # Loop back for more exploration
    agent_node - "answer" >> draft_answer_node  # Go to answer generation (includes refusals)
    
    # Create flow starting with crawl node
    return Flow(start=crawl_node)

support_bot_flow = create_support_bot_flow()