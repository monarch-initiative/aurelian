"""SO sequence ontology recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class SoMetadata(Dict[str, Any]):
    """Metadata dictionary for SO evaluations."""
    pass


# SO evaluation cases from CRAFT corpus - extracted from real text
homology = Case(
    name="homology",
    inputs="rubripes orthologues of MSX1, STX18, D4S234E and the predicted gene LOC118711, in addition to sequences with homology to LOXL, EVC, LOC159291, and the LDB family.",
    expected_output={'ontology_id': "SO:0000857"},
    metadata=metadata("medium", "sequence_feature_recognition")
)

consensus = Case(
    name="consensus",
    inputs="Therefore, based upon the sequence identity between these genes, we designed a consensus oligonucleotide primer, T3con2, that would be suitable for the identification of the region containing the initiator methionine of the TACC3 cDNAs from primates and rodents.",
    expected_output={'ontology_id': "SO:0000993"},
    metadata=metadata("medium", "sequence_feature_recognition")
)

paralogous = Case(
    name="paralogous",
    inputs="These loci separate two clusters of genes on human chromosome 5 that are paralogous with 4p16.",
    expected_output={'ontology_id': "SO:0000859"},
    metadata=metadata("hard", "sequence_feature_recognition")
)

orthologous = Case(
    name="orthologous",
    inputs="Comparative genomic structure of the TACC family The genomic DNA sequences corresponding to the orthologous TACC genes of human, mouse, rat, pufferfish, C.",
    expected_output={'ontology_id': "SO:0000858"},
    metadata=metadata("hard", "sequence_feature_recognition")
)

linear = Case(
    name="linear",
    inputs="Figure 2 Linear organization of gene clusters centering upon the chromosomal loci of the FGFR genes in humans.",
    expected_output={'ontology_id': "SO:0000987"},
    metadata=metadata("medium", "sequence_feature_recognition")
)

forward = Case(
    name="forward",
    inputs="XhoI intron by amplification with primers that added an external BamHI site to the 5′ end of exon 1 and ran through the Asp718 site of exon 2 (forward: GCC GGA TCC GAT CAG CAG ACC GAT TCT GG; reverse: GCC GGT ACC ACT AGG AAG GCA GAA TGC).",
    expected_output={'ontology_id': "SO:0001030"},
    metadata=metadata("easy", "sequence_feature_recognition")
)

reverse = Case(
    name="reverse",
    inputs="XhoI intron by amplification with primers that added an external BamHI site to the 5′ end of exon 1 and ran through the Asp718 site of exon 2 (forward: GCC GGA TCC GAT CAG CAG ACC GAT TCT GG; reverse: GCC GGT ACC ACT AGG AAG GCA GAA TGC).",
    expected_output={'ontology_id': "SO:0001031"},
    metadata=metadata("easy", "sequence_feature_recognition")
)

in_frame = Case(
    name="in frame",
    inputs="The transactivation domain (78 amino acid residues, corresponding to residues 413–490) of VP16 was fused in frame with the N-terminus of mouse PPARδ.",
    expected_output={'ontology_id': "SO:0001817"},
    metadata=metadata("hard", "sequence_feature_recognition")
)

mitochondrial_DNA = Case(
    name="mitochondrial DNA",
    inputs="Mitochondrial DNA was increased 2.",
    expected_output={'ontology_id': "SO:0001032"},
    metadata=metadata("easy", "sequence_feature_recognition")
)

antisense = Case(
    name="antisense",
    inputs="ERK5 has also been implicated in the development of smooth muscle, as ERK5 antisense oligonucleotides [9] or dominant negative ERK5 constructs [10] have been reported to block the differentiation of smooth muscle cells in cell culture models.",
    expected_output={'ontology_id': "SO:0000077"},
    metadata=metadata("medium", "sequence_feature_recognition")
)


def create_so_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create SO sequence ontology recognition evaluation dataset from CRAFT corpus."""
    cases = [
        homology, consensus, paralogous, orthologous, linear,
        forward, reverse, in_frame, mitochondrial_DNA, antisense
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )