from deeplearning_a2a.policyagent import PolicyAgent

if __name__ == "__main__":
    policy_agent = PolicyAgent()
    response = policy_agent.query(
        "How much would I pay for mental health therapy?", "./data/2026AnthemgHIPSBC.pdf"
    )
    policy_agent.display_response(response)
    