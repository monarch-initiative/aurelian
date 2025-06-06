"""
Query Preprocessing Agent for Intelligent Ontology Routing

This agent analyzes queries and routes them to appropriate ontologies with refined keywords,
acting as a smart preprocessing layer before the existing search_terms function.
"""

from typing import List, Dict, Tuple
from pydantic_ai import Agent


QUERY_PREPROCESSOR_SYSTEM_PROMPT = """
You are a biomedical query analysis expert. Your job is to analyze user queries and determine:

1. **Entity types** in the query (genes, diseases, phenotypes, chemicals, etc.)
2. **Best ontology** for each entity type
3. **Refined search terms** optimized for each ontology

## Ontology Mapping Rules:

**Genes/Proteins:**
- Gene symbols: BRCA1, TP53, EGFR → **HGNC**
- Protein functions, biological processes => GO terms → **GO** 

**Diseases:**
- Disease names, cancers, syndromes → **MONDO**
- Disease phenotypes, symptoms → **HP**

**Phenotypes:**
- Observable traits, abnormalities → **HP**
- Mouse phenotypes → **MP**

**Chemicals/Drugs:**
- Chemical compounds, drugs → **CHEBI**

**Anatomy:**
- Body parts, organs → **UBERON**
- Cell types → **CL**

## Output Format:
Return a JSON object with search instructions:

```json
{
  "analysis": "Brief analysis of the query",
  "searches": [
    {
      "ontology": "hgnc", 
      "query": "BRCA1",
      "entity_type": "gene",
      "confidence": 0.95,
      "reasoning": "BRCA1 is a well-known gene symbol"
    },
    {
      "ontology": "mondo",
      "query": "cancer", 
      "entity_type": "disease",
      "confidence": 0.90,
      "reasoning": "Cancer is a disease term, MONDO is the disease ontology"
    }
  ]
}
```

## Examples:

**Query:** "BRCA1 mutations in breast cancer"
→ Search HGNC for "BRCA1", Search MONDO for "breast cancer"

**Query:** "diabetes symptoms and complications" 
→ Search MONDO for "diabetes", Search HP for "diabetes symptoms"

**Query:** "aspirin chemical structure"
→ Search CHEBI for "aspirin"

Always provide the most appropriate ontology and refined search terms for optimal results.
"""

query_preprocessor_agent = Agent(
    model="openai:gpt-4o-mini",
    result_type=Dict,
    system_prompt=QUERY_PREPROCESSOR_SYSTEM_PROMPT,
    defer_model_check=True,
)


async def preprocess_query(query: str, available_ontologies: List[str]) -> List[Tuple[str, str]]:
    """
    Preprocess a query to determine optimal ontology searches.
    
    Args:
        query: User's search query
        available_ontologies: List of available ontologies
        
    Returns:
        List of (ontology_id, refined_query) tuples for searching
        
    Example:
        query = "BRCA1 causes breast cancer"
        returns = [("hgnc", "BRCA1"), ("mondo", "breast cancer")]
    """

    try:
        result = await query_preprocessor_agent.run(
            f"Analyze this biomedical query and determine the best ontology searches: '{query}'\n\n"
            f"Available ontologies: {', '.join(available_ontologies)}"
        )
        
        searches = []
        if "searches" in result.output:
            for search in result.output["searches"]:
                ontology = search.get("ontology", "").lower()
                refined_query = search.get("query", query)
                
                if ontology in [ont.lower() for ont in available_ontologies]:
                    searches.append((ontology, refined_query))
                    print(f"{ontology.upper()}: '{refined_query}'")
                else:
                    print(f"{ontology.upper()}: not available, skipping")
        
        if not searches:
            print(f" FALLBACK: Using default routing")
            default_ontologies = ["mondo", "hp", "go"]
            for ont in default_ontologies:
                if ont in [o.lower() for o in available_ontologies]:
                    searches.append((ont, query))
                    break
        
        print(f"PREPROCESSING: Generated {len(searches)} targeted searches")
        return searches
        
    except Exception as e:
        print(f"⚠PREPROCESSING: Failed ({e}), using fallback")
        return [("mondo", query)]


async def search_with_preprocessing(ctx, query: str) -> List[Dict]:
    """
    Enhanced search that preprocesses queries before calling existing search_terms.
    
    This maintains compatibility with the existing search_terms function while
    adding intelligent routing as a preprocessing step.
    """
    from .ontology_mapper_tools import search_terms
    from .ontology_mapper_config import get_config
    
    config = ctx.deps or get_config()
    available_ontologies = config.ontologies
    
    search_instructions = await preprocess_query(query, available_ontologies)
    
    # Step 2: Execute searches using existing search_terms function  
    all_results = []
    for ontology_id, refined_query in search_instructions:
        print(f"🔍 EXECUTING: search_terms('{ontology_id}', '{refined_query}')")
        try:
            results = await search_terms(ctx, ontology_id, refined_query)
            
            for result in results:
                result["preprocessed_query"] = refined_query
                result["original_query"] = query
                result["routing_method"] = "intelligent_preprocessing"
            
            all_results.extend(results)
            
        except Exception as e:
            print(f"Search failed for {ontology_id}: {e}")
            continue
    
    return all_results