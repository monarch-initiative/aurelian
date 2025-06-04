"""Tools for the Knowledge Agent."""

from typing import List, Tuple

from oaklib import get_adapter


async def search_ontology_with_oak(term: str, ontology: str, n: int = 10, verbose: bool = False) -> List[Tuple[str, str]]:
    """
    Search an OBO ontology for a term.

    Note that search should take into account synonyms, but synonyms may be incomplete,
    so if you cannot find a concept of interest, try searching using related or synonymous
    terms.

    If you are searching for a composite term, try searching on the sub-terms to get a sense
    of the terminology used in the ontology.

    Args:
        term: The term to search for.
        ontology: The ontology ID to search
        n: The maximum number of results to return.
        verbose: Whether to print debug information.

    Returns:
        A list of tuples, each containing an ontology ID and a label.
    """
    adapter = get_adapter("ols:" + ontology)
    results = adapter.basic_search(term)
    if n:
        results = list(results)[:n]  # Limit the number of results if n is specified
    labels = list(adapter.labels(results))
    if verbose:
        print(f"## TOOL USE: Searched for '{term}' in '{ontology}' ontology")
        print(f"## RESULTS: {labels}")
    return labels
