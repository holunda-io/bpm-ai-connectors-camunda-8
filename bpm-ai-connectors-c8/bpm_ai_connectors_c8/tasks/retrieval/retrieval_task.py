from bpm_ai.retrieval.retrieval import retrieve_llm
from bpm_ai_core.llm.common.llm import LLM
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task
from bpm_ai_connectors_c8.models import remote_model

retrieval_router = ZeebeTaskRouter()


@ai_task(retrieval_router, "retrieval", 2)
async def retrieval(
    llm: LLM,
    index: dict,
    query: str,
    input_json: dict | None = None,
    output_schema: dict | None = None,
):
    """
    Retrieve relevant documents and synthesize an answer using an LLM.
    
    Args:
        llm: LLM instance to use for answer synthesis
        index: Dict mapping index names to lists of URLs/file paths
        query: User's question to answer
        input_json: Optional user provided context information
        output_schema: Optional schema for structured JSON output

    Returns:
        Dict containing the synthesized answer
    """
    return await retrieve_llm(
        llm=llm,
        index=index,
        query=query,
        retrieval=remote_model("ByaldiDocumentRetrieval"),  # non-configurable right now
        crawler=remote_model("PlaywrightWebCrawler"),  # non-configurable right now
        input_data=input_json,
        output_schema=output_schema
    )
