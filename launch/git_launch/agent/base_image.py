"""
Base Docker image selection agent for repository environment setup.
"""
from langchain.schema import HumanMessage

from git_launch.agent.state import AgentState, auto_catch

lang_to_candidate_images = {
    "python": [f"python:3.{v}" for v in range(6, 12)],
    "rust": [f"rust:1.7{v}" for v in range(0, 10)],
    "javascript": [f"node:1{v}" for v in range(0, 10)],
}


@auto_catch
def select_base_image(state: AgentState) -> AgentState:
    """
    Select appropriate base Docker image based on repository analysis.
    
    Uses LLM to analyze repository documentation and select the most suitable
    base image from language-specific candidate images.
    
    Args:
        state (AgentState): Current agent state with repo docs and language info
        
    Returns:
        AgentState: Updated state with selected base image
    """
    llm = state["llm"]
    logger = state["logger"]
    langauge = state["language"]
    candidate_images = lang_to_candidate_images[langauge]
    messages = [
        HumanMessage(
            content=f"""Based on related file:
{state['docs']}

Please recommend a suitable base Docker image. Consider:
1. The programming language and version requirements
2. Common system dependencies
3. Use official images when possible

Select a base image from the following candidate list:
{candidate_images}
Wrap the image name in a block like <image>ubuntu:20.04</image> to indicate your choice.
"""
        )
    ]
    base_image = None
    trials = 0
    while not base_image or trials < 5:
        trials += 1
        response = llm.invoke(messages)
        if "<think>" in response.content:
            response.content = response.content.split("</think>")[1]
        if "<image>" in response.content:
            image = response.content.split("<image>")[1].split("</image>")[0]
            if image in candidate_images:
                base_image = image
                break
            messages.append(response)
            messages.append(
                HumanMessage(
                    content=f"""The image you selected({image}) is not in the candidate list: {candidate_images}. Please select again."""
                )
            )
        else:
            messages.append(response)
            messages.append(
                HumanMessage(
                    content="""Please wrap the image name in a block like <image>ubuntu:20.04</image> to indicate your choice."""
                )
            )

    logger.info(f"Selected base image: {base_image}")
    return {
        "messages": messages,
        "base_image": base_image,
    }
