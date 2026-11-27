"""Stage 1: load, split, embed the corpus, and hand back a retriever.

YOUR CODE GOES HERE. `build_retriever` raises NotImplementedError.

You did all of this in the Session 4 notebook (`Agentic_RAG_From_Scratch.ipynb`,
Task 4). Two differences here:
  - `api.py` calls this exactly once, in the FastAPI lifespan, and holds the retriever for
    the life of the process — never once per request (Week 1's CLI re-embedded every run).
  - Qdrant is **on disk**, not `:memory:`. It memory-maps its files, so the collection
    survives restarts — you embed once, ever, and later boots load from disk for free.
"""

from pathlib import Path
import os

from langchain_core.retrievers import BaseRetriever 
from langchain_core.vectorstores import VectorStoreRetriever


from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
QDRANT_PATH = Path(__file__).resolve().parent.parent / "qdrant_storage_dp"  # on-disk, gitignored

# gpt-5.4-mini: newest-gen, strong tool-calling, fast + cheap for repeated runs.
# (gpt-5.6-luna/terra are reasoning-only and can't tool-call over chat completions.)
CHAT_MODEL = os.environ.get("LLM_MODEL")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")


def build_retriever(corpus_path: Path, k: int = 3) -> VectorStoreRetriever:
    

    """Load the corpus, split it, embed it into Qdrant, and return a retriever.
    
        Args:
            corpus_path: the .txt file to index.
            k: how many chunks the retriever returns per query.
    
        Returns:
            A LangChain retriever (`vector_store.as_retriever(...)`) ready to `.invoke(query)`.
    
        The moves, all from Session 4 Task 4 (now on disk):
          1. `TextLoader(corpus_path).load()` -> Documents.
          2. `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)` -> chunks.
          3. `OpenAIEmbeddings(model=EMBEDDING_MODEL)`, and an on-disk client:
                 client = QdrantClient(path=str(QDRANT_PATH))
             Create the collection only if it's missing (`client.collection_exists(name)`), build a
             `QdrantVectorStore`, and `.add_documents(chunks)` ONLY when the collection is empty
             (`client.count(name).count == 0`) — otherwise reuse what's already on disk.
          4. `vector_store.as_retriever(search_kwargs={"k": k})`.
    
        Two things persistence forces you to get right:
          - Idempotency: don't re-create or re-embed an index that already exists, or you pay to
            embed every boot (and `create_collection` throws on a collision). Guard both.
          - `chunk_id`: the chunk's position in the split list is the only id you have. Stamp it
            into metadata (`chunk.metadata["chunk_id"] = i`) BEFORE adding — it's what makes
            `Source.chunk_id` mean anything, and once on disk you can't add it retroactively.
    
        Note: on-disk Qdrant locks its folder to one client, so one server owns it at a time.
        Delete `qdrant_storage_dp/` if you change the corpus, chunking, or embedding model.
        Hosted/shared instead? Run a Qdrant server and swap the client for
        `QdrantClient(url="http://localhost:6333")` — that's the multi-process production path.
        """

#TextLoader allows us to chunk the text into smaller pieces, which is important for embedding and retrieval. The RecursiveCharacterTextSplitter splits the text into chunks of a specified size with some overlap to ensure context is preserved. The OpenAIEmbeddings model is used to generate embeddings for the text chunks, which are then stored in a Qdrant vector store for efficient retrieval. The retriever allows us to query the vector store and retrieve relevant chunks based on the query.

    loader = TextLoader(corpus_path , encoding="utf-8")
    document = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, length_function=len)
    chunks = text_splitter.split_documents(document) 
    #Assign a chunk id for tracking
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i  

#Create an instance of the OpenAIEmbeddings model using the specified embedding model and API key. 
# The embedding dimension is determined by embedding a test query and measuring the length of the resulting vector.

    from langchain_openai import OpenAIEmbeddings
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams

    embedding_model = OpenAIEmbeddings(model=os.environ["EMBEDDING_MODEL"],api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["LLM_API_BASE"])
    

# On-disk Qdrant: vectors persist to memory-mapped files, so they survive a kernel
# restart. Embed once; later runs load from disk instead of paying to re-embed.

    #QDRANT_PATH = "qdrant_storage_dp"  
    collection_name = "wellness_knowledge"

#below _prev_client is used to check if there is an existing Qdrant client in the global namespace. If there is, it closes that client before creating a new one. 
# This ensures that only one client is active at a time, which is important because Qdrant locks its storage folder to a single client. After closing any previous client, a new QdrantClient is created with the specified path to the on-disk storage.
    _prev_client = globals().get("_qdrant_client_dp")
    if _prev_client is not None:
        _prev_client.close()  # close any previous client before creating a new one
    qdrant_client = QdrantClient(path=str(QDRANT_PATH))
    globals()["_qdrant_client_dp"]= qdrant_client #client tracking

#below code checks if the specified collection exists in the Qdrant client. 
# If it does not exist, it creates a new collection with the specified name and vector configuration (size and distance metric). This ensures that the collection is only created if it doesn't already exist, preventing errors from attempting to create a collection that already exists.
    if not qdrant_client.collection_exists(collection_name):
      embedding_dim = len(embedding_model.embed_query("test"))
      qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
  )
    else:
      embedding_dim = qdrant_client.get_collection(collection_name).config.params.vectors.size

  #below code creates a QdrantVectorStore INSTANCE using the Qdrant client,
  # collection name, and embedding function. It then checks if the collection is empty (i.e., has no documents). 
  # If it is empty, it adds the chunks to the collection and prints a message indicating how many chunks were added. 
  # If the collection already has documents, it prints a message indicating how many chunks are already present and skips the embedding process. 
  # Finally, it creates a retriever from the vector store with a specified number of results to return per query.
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embedding_model
    )

    if qdrant_client.count(collection_name).count == 0:
      vector_store.add_documents(chunks) 
      print(f"Added {len(chunks)} chunks to Qdrant collection '{collection_name}'")
    else:
      print(f"Qdrant collection '{collection_name}' already has {qdrant_client.count(collection_name).count} chunks; skipping embedding.")

    print(f"Retriever ready (dim={embedding_dim}, path={QDRANT_PATH}).")
    return vector_store.as_retriever(search_kwargs={"k": k})
    
