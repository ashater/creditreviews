from load_news_unstructured import load_content_using_fitz_ftrst, load_unstructured_pdf_and_add_section, pdf_extract_worrkflow
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from chromadb.utils import embedding_functions
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
import json, uuid
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

#### load the json and add table content to it
cwd = os.getcwd()

workdir = os.path.join(cwd, "10_KQ")

file_name = "bank_of_america_10Q_2024_Q1.pdf"
pages_pull = 5  #### pull first 5 pages to find content

buffer = 3
verbose = True

docs, page_range, section_name, response = pdf_extract_worrkflow(workdir, file_name, 'bank of america', '2024 q1',
                                                                     pages_pull, buffer, verbose)

#### since anthropic needs money, save processed json
json.dump(docs, open(os.path.join(cwd,'pre_chroma_json', file_name.split('.')[0]+'.json'), "w+"))


table_elements = [e for e in docs if e['type'].lower() == "table"]
print(len(table_elements))

# Text
text_elements = [e for e in docs if e['type'].lower() != "table"]

#### get embeddings:
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2 ")
#### create db with meta data

vectorstore = Chroma(collection_name="bank_of_america", embedding_function=sentence_transformer_ef())

# The storage layer for the parent documents
store = InMemoryStore()
id_key = "doc_id"

# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=store,
    id_key=id_key,
)

#### todo: add llm summary option
#### add text and tables
doc_ids = [str(uuid.uuid4()) for _ in text_elements]
retriever.vectorstore.add_documents([
    Document(page_content = doc['text'], metadata = {id_key:doc_ids[idx],'section_name':doc['metadata']['section_name']}) for idx,doc in enumerate(text_elements)
])
retriever.docstore.mset(list(zip(doc_ids, text_elements)))

#### add table to DB

table_ids = [str(uuid.uuid4()) for _ in table_elements]
retriever.vectorstore.add_documents([
    Document(page_content = doc['text'], metadata = {id_key:doc_ids[idx],'section_name':doc['metadata']['section_name']}) for idx,doc in enumerate(table_elements)
])
retriever.docstore.mset(list(zip(table_ids, table_elements)))


model = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    temperature=0,
    max_tokens=2000,
    timeout=None,
    max_retries=2,
    api_key = os.environ.get("anthropic_API_KEY"),

    )

# system = "You are a financial analyst to select relevant sessions \
#               in a company's financial statement in order to perform credit risk review.\
#               The financial statements can be 10-K, 10-Q, earning call transcripts or others.\
#               Use the print_selected_sessions tool to give structured output.",

prompt_text = """Given the text. Could you help identify the table of content? \
    Please list the name of each section and the corresponding page number. \
    Below are the text: {text} """

prompt_text = """You are a financial analyst 

"""
prompt = ChatPromptTemplate.from_template(prompt_text)








