from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

class Document(BaseModel):
    """
    A document is a file in the documentation directory.
    """
    id: str
    title: str
    path: str
    metadata: Optional[Dict] = None

@dataclass
class DocumentationManager:
    """
    A manager for the documentation directory.
    """
    
    documents_dir: Path
    collection_name: Optional[str] = None

    def all_documents(self) -> List[Document]:
        """
        Get all available documents.
        """
        return [Document(
            id=file_path.stem,
            title=file_path.stem.replace("_", " "),
            path=str(file_path),
            metadata=None
        ) for file_path in self.documents_dir.glob("*.md")]

    def get_documents_for_prompt(self, extra_text: str = "") -> str:
        """
        Get the documents for the system prompt.

        Returns:
            A string containing the list of available GO annotation best practice documents
        """
        docs = self.all_documents()
        if not docs:
            raise AssertionError("No best practice documents are available")

        docs_text = "\n\nThe following documents are available:\n"
        docs_text += "\n".join([f"- {d.title}" for d in docs])
        docs_text += "\n\n" + extra_text
        return docs_text

    def fetch_document(self, id_or_title: str) -> Document:
        """
        Fetch a document by its ID or title.
        """
        for document in self.all_documents():
            if document.id == id_or_title or document.title == id_or_title:
                return document
        raise KeyError(f"Document with ID or title '{id_or_title}' not found")

