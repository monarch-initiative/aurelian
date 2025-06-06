"""
MCP (Model Context Protocol) server for Schema Generator Agent.
"""
import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .schema_agent import run_with_validation
from .schema_config import get_schema_config

logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("schema-generator-agent")


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available schema generator resources."""
    return [
        Resource(
            uri="schema://examples/biomedical",
            name="Biomedical Schema Examples",
            description="Example schemas for biomedical entity extraction",
            mimeType="text/plain",
        ),
        Resource(
            uri="schema://examples/chemistry", 
            name="Chemistry Schema Examples",
            description="Example schemas for chemistry entity extraction",
            mimeType="text/plain",
        ),
        Resource(
            uri="schema://examples/general",
            name="General Domain Examples", 
            description="Example schemas for various domains",
            mimeType="text/plain",
        ),
        Resource(
            uri="schema://templates/linkml",
            name="LinkML Schema Template",
            description="Base LinkML schema template structure",
            mimeType="application/x-yaml",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read schema generator resources."""
    if uri == "schema://examples/biomedical":
        return """
        Biomedical Schema Examples:
        
        • "genes, diseases, and phenotypes from clinical text"
        • "drug names, dosages, and side effects from medical literature"  
        • "protein-protein interactions with confidence scores"
        • "clinical symptoms and their severity levels"
        • "biomarkers and their associated conditions"
        • "molecular pathways and regulatory mechanisms"
        """
    
    elif uri == "schema://examples/chemistry":
        return """
        Chemistry Schema Examples:
        
        • "chemical reactions with yields and conditions"
        • "catalysts, solvents, and reaction temperatures"
        • "molecular structures and properties"
        • "synthesis pathways and intermediates"
        • "analytical methods and measurement results"
        • "chemical safety data and hazard classifications"
        """
    
    elif uri == "schema://examples/general":
        return """
        General Domain Schema Examples:
        
        Real Estate:
        • "houses, prices, and neighborhood features"
        • "property types, square footage, and amenities"
        
        Business:
        • "companies, products, and market segments"
        • "financial metrics and performance indicators"
        
        Academic:
        • "research topics, methodologies, and findings"
        • "authors, institutions, and publication venues"
        
        Legal:
        • "legal cases, outcomes, and precedents"
        • "contracts, parties, and terms"
        """
    
    elif uri == "schema://templates/linkml":
        return """
        id: https://w3id.org/ontogpt/example_schema
        name: example_schema
        description: Example LinkML schema for entity extraction
        prefixes:
          linkml: https://w3id.org/linkml/
          schema: http://schema.org/
          rdfs: http://www.w3.org/2000/01/rdf-schema#
        imports:
          - linkml:types
        classes:
          NamedEntity:
            abstract: true
            description: A generic grouping for any identifiable entity
            slots: [id, label]
            class_uri: schema:Thing
          ExampleEntity:
            is_a: NamedEntity
            description: An example entity type
            id_prefixes: [EXAMPLE]
            annotations:
              annotators: sqlite:obo:example
        slots:
          id:
            identifier: true
            slot_uri: schema:identifier
            range: uriorcurie
            description: A unique identifier for a thing
          label:
            slot_uri: rdfs:label
            description: A human-readable name for a thing
        """
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available schema generator tools."""
    return [
        Tool(
            name="generate_schema",
            description="Generate and validate a LinkML schema for entity extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of what to extract (e.g., 'genes and diseases from biomedical text')",
                    },
                    "domain": {
                        "type": "string", 
                        "enum": ["biomedical", "chemistry", "business", "academic", "legal", "general"],
                        "description": "Domain context for the schema",
                        "default": "general"
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "moderate", "complex"],
                        "description": "Schema complexity level", 
                        "default": "moderate"
                    }
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="validate_schema",
            description="Validate a LinkML schema for correctness",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_yaml": {
                        "type": "string",
                        "description": "LinkML schema in YAML format to validate",
                    }
                },
                "required": ["schema_yaml"],
            },
        ),
        Tool(
            name="list_examples",
            description="List example schema descriptions for different domains",
            inputSchema={
                "type": "object", 
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["biomedical", "chemistry", "business", "academic", "legal", "all"],
                        "description": "Domain to get examples for",
                        "default": "all"
                    }
                },
            },
        ),
        Tool(
            name="explain_schema", 
            description="Explain the components and structure of a LinkML schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_yaml": {
                        "type": "string",
                        "description": "LinkML schema in YAML format to explain",
                    }
                },
                "required": ["schema_yaml"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls for schema generation."""
    
    if name == "generate_schema":
        description = arguments.get("description", "")
        domain = arguments.get("domain", "general") 
        complexity = arguments.get("complexity", "moderate")
        
        if not description:
            return [TextContent(type="text", text="❌ Error: Description is required")]
        
        try:
            # Add domain and complexity context to description
            enhanced_description = f"{description} (domain: {domain}, complexity: {complexity})"
            
            deps = get_schema_config()
            schema_yaml = await run_with_validation(enhanced_description, deps)
            
            if "validation failed" in schema_yaml.lower() or "error" in schema_yaml.lower():
                return [TextContent(type="text", text=f"❌ {schema_yaml}")]
            
            return [TextContent(
                type="text", 
                text=f"✅ Schema generated and validated successfully!\n\n```yaml\n{schema_yaml}\n```"
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error generating schema: {str(e)}")]
    
    elif name == "validate_schema":
        schema_yaml = arguments.get("schema_yaml", "")
        
        if not schema_yaml:
            return [TextContent(type="text", text="❌ Error: Schema YAML is required")]
        
        try:
            # Use LinkML validation
            from aurelian.agents.linkml.linkml_tools import validate_then_save_schema
            from aurelian.agents.linkml.linkml_config import get_config as get_linkml_config
            
            class MockContext:
                def __init__(self, deps):
                    self.deps = deps
            
            linkml_deps = get_linkml_config()
            ctx = MockContext(linkml_deps)
            
            result = await validate_then_save_schema(ctx, schema_yaml, None)
            
            if result.valid:
                messages = "\n".join(result.info_messages or [])
                return [TextContent(type="text", text=f"✅ Schema is valid!\n{messages}")]
            else:
                return [TextContent(type="text", text="❌ Schema validation failed")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Validation error: {str(e)}")]
    
    elif name == "list_examples":
        domain = arguments.get("domain", "all")
        
        examples = {
            "biomedical": [
                "genes, diseases, and phenotypes from clinical text",
                "drug names, dosages, and side effects from medical literature", 
                "protein-protein interactions with confidence scores",
                "clinical symptoms and their severity levels"
            ],
            "chemistry": [
                "chemical reactions with yields and conditions",
                "catalysts, solvents, and reaction temperatures",
                "molecular structures and properties", 
                "synthesis pathways and intermediates"
            ],
            "business": [
                "companies, products, and market segments",
                "financial metrics and performance indicators",
                "partnerships and competitive relationships",
                "customer feedback and sentiment analysis"
            ],
            "academic": [
                "research topics, methodologies, and findings", 
                "authors, institutions, and publication venues",
                "citations and academic relationships",
                "grant funding and research outcomes"
            ],
            "legal": [
                "legal cases, outcomes, and precedents",
                "contracts, parties, and terms",
                "regulations and compliance requirements",
                "intellectual property and patents"
            ]
        }
        
        if domain == "all":
            result = "📚 Schema Examples by Domain:\n\n"
            for d, exs in examples.items():
                result += f"🔬 {d.title()}:\n"
                for ex in exs:
                    result += f"   • {ex}\n"
                result += "\n"
        else:
            exs = examples.get(domain, [])
            result = f"📚 {domain.title()} Schema Examples:\n\n"
            for ex in exs:
                result += f"• {ex}\n"
        
        result += "\n💡 Usage: Use these descriptions with the generate_schema tool"
        return [TextContent(type="text", text=result)]
    
    elif name == "explain_schema":
        schema_yaml = arguments.get("schema_yaml", "")
        
        if not schema_yaml:
            return [TextContent(type="text", text="❌ Error: Schema YAML is required")]
        
        try:
            import yaml
            schema_dict = yaml.safe_load(schema_yaml)
            
            explanation = "📋 LinkML Schema Explanation:\n\n"
            
            # Basic info
            explanation += f"**Name:** {schema_dict.get('name', 'N/A')}\n"
            explanation += f"**Description:** {schema_dict.get('description', 'N/A')}\n\n"
            
            # Classes
            classes = schema_dict.get('classes', {})
            explanation += f"**Classes ({len(classes)}):**\n"
            for class_name, class_def in classes.items():
                explanation += f"• **{class_name}**: {class_def.get('description', 'No description')}\n"
                if 'is_a' in class_def:
                    explanation += f"  - Inherits from: {class_def['is_a']}\n"
                if 'id_prefixes' in class_def:
                    explanation += f"  - Ontology prefixes: {class_def['id_prefixes']}\n"
            
            # Slots  
            slots = schema_dict.get('slots', {})
            explanation += f"\n**Slots ({len(slots)}):**\n"
            for slot_name, slot_def in slots.items():
                explanation += f"• **{slot_name}**: {slot_def.get('description', 'No description')}\n"
                if 'range' in slot_def:
                    explanation += f"  - Type: {slot_def['range']}\n"
            
            # Prefixes
            prefixes = schema_dict.get('prefixes', {})
            explanation += f"\n**Prefixes ({len(prefixes)}):**\n"
            for prefix, uri in prefixes.items():
                explanation += f"• {prefix}: {uri}\n"
            
            return [TextContent(type="text", text=explanation)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error parsing schema: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]


async def main():
    """Run the Schema Generator MCP server."""
    # Use stdin/stdout for communication
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="schema-generator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())