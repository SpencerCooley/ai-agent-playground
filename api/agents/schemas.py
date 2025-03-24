from pydantic import BaseModel, Field
from typing import List, Union, Optional

class TextExplanation(BaseModel):
    content: str = Field(description="A textual explanation of the answer")

class Chart3DData(BaseModel):
    x: List[float] = Field(description="X-axis values")
    y: List[float] = Field(description="Y-axis values")
    z: List[float] = Field(description="Z-axis values")
    chart_type: str = Field(default="3d_surface", description="Suggested chart type")

class CodeSnippet(BaseModel):
    language: str = Field(description="Programming language, e.g., 'javascript'")
    code: str = Field(description="Executable code snippet")

# Registry of available response modules
RESPONSE_MODULES = {
    "text_explanation": TextExplanation,
    "chart_3d": Chart3DData,
    "code_snippet": CodeSnippet
}

class DynamicResponse(BaseModel):
    components: List[Union[TextExplanation, Chart3DData, CodeSnippet]] = Field(
        description="Ordered list of response components"
    )