# agents/agent.py
from pydantic import BaseModel, ValidationError
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
from .schemas import RESPONSE_MODULES, DynamicResponse

class AdaptiveConversationalAgent(BaseModel):
    api_key: str
    model: str
    llm: ChatOpenAI = None
    available_modules: dict = RESPONSE_MODULES
    max_retries: int = 3 

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = ChatOpenAI(api_key=self.api_key, model=self.model)

        # Chain 1: Analyze the prompt
        self.analyze_prompt = PromptTemplate(
            input_variables=["prompt"],
            template="""
            Analyze the question and decide what response components would benefit the user.
            Return a JSON list of module names from: {modules}.
            Order them logically.

            Examples:
            - "Explain exponential growth" -> ["text_explanation", "simple_chart"]
            - "Show a 3D plot with JS code" -> ["chart_3d", "code_snippet"]

            Question: {prompt}
            """.format(modules=list(self.available_modules.keys()))
        )
        self.analyze_chain = LLMChain(llm=self.llm, prompt=self.analyze_prompt, output_key="component_names")

        # Chain 2: Generate structured response (PydanticAI-style)
        self.generate_prompt = PromptTemplate(
            input_variables=["prompt", "component_name", "context", "schema"],
            template="""
            Generate content for '{component_name}' based on this question: {prompt}.
            Previous context: {context}
            Return JSON matching this schema:
            {schema}

            Ensure all fields are present and correctly typed as per the schema.
            """
        )
        self.generate_chain = LLMChain(llm=self.llm, prompt=self.generate_prompt)

    async def _generate_component(self, name: str, prompt: str, context: str) -> BaseModel:
        """Generate a component, with try-except as a safety net."""
        schema = self.available_modules[name].schema_json()
        for attempt in range(self.max_retries):
            try:
                result = await self.generate_chain.acall({
                    "prompt": prompt,
                    "component_name": name,
                    "context": context,
                    "schema": schema
                })
                raw_output = json.loads(result["text"])
                return self.available_modules[name](**raw_output)
            except (json.JSONDecodeError, ValidationError) as e:
                if attempt == self.max_retries - 1:
                    # Log this in production, but raise for now
                    raise Exception(f"Failed to generate {name} after {self.max_retries} attempts: {str(e)}")
                continue

    async def run(self, prompt: str) -> DynamicResponse:
        """Run the agent, trusting PydanticAI-style structuring with a fallback."""
        # Step 1: Analyze with LangChain
        analysis_result = await self.analyze_chain.acall({"question": prompt})
        component_names = json.loads(analysis_result["component_names"])

        # Step 2 & 3: Generate components, relying on LLM structuring
        components = []
        context = ""
        for name in component_names:
            if name not in self.available_modules:
                continue
            component = await self._generate_component(name, question, context)
            components.append(component)
            context += f"{name}: {component.json()}\n"

        return DynamicResponse(components=components)

# Test
if __name__ == "__main__":
    import asyncio
    agent = AdaptiveConversationalAgent(api_key="your_openai_api_key", model="gpt-4")
    question = "Can you explain what exponential growth is in 3D and show me how to calculate it in JavaScript?"
    response = asyncio.run(agent.run(prompt))
    for component in response.components:
        print(f"\nComponent Type: {component.__class__.__name__}")
        print(component.json(indent=2))