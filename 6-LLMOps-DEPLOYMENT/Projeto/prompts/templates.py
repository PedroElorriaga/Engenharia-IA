from langchain_core.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_template(
    """You are a helpful Pedrinhos Company assistant that provides information based on this 3 documents chunk:

    {documents}
    """
)
