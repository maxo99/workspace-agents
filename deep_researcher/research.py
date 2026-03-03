from deep_researcher.flow import DeepResearchFlow


async def run_deep_research(prompt):
    """Run the deep research flow and return the result."""
    try:
        flow = DeepResearchFlow()
        flow.state.query = prompt
        payload: dict = await flow.kickoff_async()
        return str(payload.get("result", "No result returned"))
    except Exception as e:
        return f"An error occurred: {e}"
