from core.base_agent import BaseAgent
from typing import Dict, Any
import os
import magic
import mimetypes
import pandas as pd
from langchain.chains import LLMChain
from langchain.document_loaders import (
    TextLoader,
    CSVLoader,
    JSONLoader
)
from langchain.embeddings import HuggingFaceEmbeddings

class FileAnalyzerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory
        )
        self.supported_formats = {
            'text/plain': self._analyze_text,
            'text/csv': self._analyze_csv,
            'application/json': self._analyze_json
        }
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def process(self, prompt: str, context: Dict[str, Any] = None) -> str:
        try:
            # Extract file path using LLM
            file_info = self.chain.run(
                input=prompt,
                action="extract_file_info"
            )
            file_path = self._extract_file_path(prompt)
            
            if not file_path:
                return "Please provide a valid file path to analyze."
            
            # Detect file type
            mime_type = magic.from_file(file_path, mime=True)
            
            # Get relevant analysis context
            relevant_analyses = self.get_relevant_context(prompt)
            
            # Analyze file
            if mime_type in self.supported_formats:
                analysis = self.supported_formats[mime_type](file_path)
                
                # Generate insights using LLM
                insights = self.chain.run(
                    input=analysis,
                    context=relevant_analyses,
                    action="generate_insights"
                )
                
                # Save analysis to memory
                self.save_to_memory(
                    prompt,
                    f"File Analysis for {file_path}:\n{analysis}\n\nInsights:\n{insights}"
                )
                
                return self._format_response(analysis, insights)
            else:
                return f"File type {mime_type} is not supported for analysis."
            
        except Exception as e:
            self.logger.error(f"File analysis failed: {str(e)}")
            return f"Failed to analyze file: {str(e)}"

    def _analyze_text(self, file_path: str) -> str:
        try:
            # Use LangChain's TextLoader
            loader = TextLoader(file_path)
            documents = loader.load()
            
            # Get text content
            content = documents[0].page_content
            
            # Basic analysis
            analysis = "Text File Analysis:\n\n"
            analysis += f"Character count: {len(content)}\n"
            analysis += f"Word count: {len(content.split())}\n"
            analysis += f"Line count: {len(content.splitlines())}\n"
            
            # Generate embeddings for content chunks
            chunks = self._chunk_text(content)
            embeddings = [self.embeddings.embed_query(chunk) for chunk in chunks]
            
            # Add semantic analysis
            analysis += "\nSemantic Analysis:\n"
            analysis += self._analyze_embeddings(embeddings)
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Text analysis failed: {str(e)}")

    def _analyze_csv(self, file_path: str) -> str:
        try:
            # Use LangChain's CSVLoader
            loader = CSVLoader(file_path)
            documents = loader.load()
            
            # Convert to pandas for analysis
            df = pd.read_csv(file_path)
            
            analysis = "CSV File Analysis:\n\n"
            analysis += f"Total rows: {len(df)}\n"
            analysis += f"Total columns: {len(df.columns)}\n"
            analysis += "\nColumn Summary:\n"
            
            for column in df.columns:
                analysis += f"\n{column}:\n"
                analysis += f"- Type: {df[column].dtype}\n"
                analysis += f"- Non-null count: {df[column].count()}\n"
                analysis += f"- Unique values: {df[column].nunique()}\n"
                
                # Add statistical analysis for numeric columns
                if pd.api.types.is_numeric_dtype(df[column]):
                    analysis += f"- Mean: {df[column].mean():.2f}\n"
                    analysis += f"- Std: {df[column].std():.2f}\n"
                    analysis += f"- Min: {df[column].min()}\n"
                    analysis += f"- Max: {df[column].max()}\n"
            
            return analysis
            
        except Exception as e:
            raise Exception(f"CSV analysis failed: {str(e)}")

    def _analyze_json(self, file_path: str) -> str:
        try:
            # Use LangChain's JSONLoader
            loader = JSONLoader(
                file_path,
                jq_schema='.[]',
                text_content=False
            )
            documents = loader.load()
            
            with open(file_path, 'r') as f:
                data = pd.read_json(f)
            
            analysis = "JSON File Analysis:\n\n"
            analysis += f"Number of records: {len(data)}\n"
            analysis += f"Structure depth: {self._get_json_depth(data)}\n"
            analysis += "\nKey Statistics:\n"
            
            for key in data.keys():
                analysis += f"- {key}: {type(data[key]).__name__}\n"
                if isinstance(data[key], pd.Series):
                    analysis += f"  - Unique values: {data[key].nunique()}\n"
            
            return analysis
            
        except Exception as e:
            raise Exception(f"JSON analysis failed: {str(e)}")

    def _format_response(self, analysis: str, insights: str) -> str:
        return f"""File Analysis Results:

{analysis}

Key Insights:
{insights}

Note: This analysis was performed using LangChain and various specialized tools."""

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> list:
        """Split text into chunks for embedding analysis"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_size += len(word) + 1
            if current_size > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def _analyze_embeddings(self, embeddings: list) -> str:
        """Analyze text embeddings for semantic patterns"""
        # This could be expanded with clustering or similarity analysis
        return f"Number of semantic chunks analyzed: {len(embeddings)}\n"