from langchain_core.documents import Document

# Note: In a real app, you would pip install pypdf, bs4, etc.
# from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, CSVLoader

def demonstrate_manual_document():
    print("--- 1. Creating a Manual Document Object ---")
    # LangChain's core data structure for RAG
    # Like a Java POJO: class Document { String page_content; Map<String, Object> metadata; }
    doc = Document(
        page_content="The refund window is 30 days from purchase date. Items must be in original condition.",
        metadata={
            "source": "policy_v2.pdf", 
            "section": "returns", 
            "year": 2024,
            "page": 1
        }
    )
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}\n")

def demonstrate_mock_pdf_loader():
    print("--- 2. Mock PDF Loader ---")
    # Real code:
    # loader = PyPDFLoader("./docs/user_manual.pdf")
    # docs = loader.load()
    
    # Mocking the output of a PyPDFLoader
    docs = [
        Document(page_content="Welcome to the User Manual. Page 1 content here.", metadata={"source": "manual.pdf", "page": 0}),
        Document(page_content="Troubleshooting: If the device won't turn on, charge it for 30 minutes.", metadata={"source": "manual.pdf", "page": 1})
    ]
    
    print(f"Loaded {len(docs)} pages.")
    for i, d in enumerate(docs):
        print(f"Page {i}: {d.page_content[:30]}... | Meta: {d.metadata}")
    print()

def demonstrate_mock_csv_loader():
    print("--- 3. Mock CSV Loader ---")
    # Real code:
    # loader = CSVLoader("./data/products.csv", metadata_columns=["product_id"])
    # docs = loader.load()
    
    # Mocking CSVLoader (Each row becomes a Document)
    docs = [
        Document(page_content="product_name: Super Widget\nprice: $19.99\ndescription: A great widget.", metadata={"row": 0, "product_id": "W123"}),
        Document(page_content="product_name: Mega Gadget\nprice: $49.99\ndescription: Our best gadget.", metadata={"row": 1, "product_id": "G456"})
    ]
    
    print("First CSV Row Document:")
    print(docs[0].page_content)
    print(f"Metadata: {docs[0].metadata}")

if __name__ == "__main__":
    demonstrate_manual_document()
    demonstrate_mock_pdf_loader()
    demonstrate_mock_csv_loader()
