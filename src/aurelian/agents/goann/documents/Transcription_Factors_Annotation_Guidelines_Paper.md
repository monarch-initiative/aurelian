Contents lists available at ScienceDirect

BBA - Gene Regulatory Mechanisms

journal homepage: www.elsevier.com/locate/bbagrm

Gene Ontology representation for transcription factor functions

Pascale Gaudet a, *, Colin Logie b, Ruth C. Lovering c, Martin Kuiper d, Astrid Lægreid e,
Paul D. Thomas f
a Swiss-Prot group, SIB Swiss Institute of Bioinformatics, 1 Rue Michel-Servet, 1211 Gen`eve, Switzerland
b Molecular Biology Department, Faculty of Science, Radboud University, PO box 9101, 6500HB Nijmegen, the Netherlands
c Functional Gene Annotation, Preclinical and Fundamental Science, UCL Institute of Cardiovascular Science, University College London, London, UK
d Department of Biology, Norwegian University of Science and Technology, Trondheim, Norway
e Department of Clinical and Molecular Medicine, Norwegian University of Science and Technology, Trondheim, Norway
f Division of Bioinformatics, Department of Preventive Medicine, University of Southern California, Los Angeles, CA, USA

A R T I C L E  I N F O

A B S T R A C T

Keywords:
Transcription
Gene Ontology
Biological databases
Biocuration

Transcription plays a central role in defining the identity and functionalities of cells, as well as in their responses
to changes in the cellular environment. The Gene Ontology (GO) provides a rigorously defined set of concepts
that describe the functions of gene products. A GO annotation is a statement about the function of a particular
gene product, represented as an association between a gene product and the biological concept a GO term de-
fines. Critically, each GO annotation is based on traceable scientific evidence. Here, we describe the different GO
terms that are associated with proteins involved in transcription and its regulation, focusing on the standard of
evidence  required  to  support  these  associations.  This  article  is  intended  to  help  users  of  GO  annotations  un-
derstand how to interpret the annotations and can contribute to the consistency of GO annotations. We distin-
guish between three classes of activities involved in transcription or directly regulating it - general transcription
factors, DNA-binding transcription factors, and transcription co-regulators.

1. Introduction

The  Gene  Ontology  (GO)  develops  a  computational  model  of  bio-
logical systems, ranging from the molecular to the organism level, across
all species in the tree of life. GO aims to provide a comprehensive rep-
resentation of the current scientific knowledge about the functions of
gene products, namely, proteins and non-coding RNA molecules [1,2].
GO is organized in three aspects. GO Molecular Functions (MF) describe
activities that occur at the molecular level, such as “DNA binding tran-
scription  factor  activity”  or  “histone  deacetylase  activity”.  Biological
Processes (BP) represent the larger processes or ‘biological programs’
accomplished by multiple molecular activities. Examples of broad bio-
logical  process  terms  are  “transcription”  or  “signal  transduction”.
Cellular Components (CC) are  the cellular structures in which a  gene
product  performs  a  function,  either  cellular  compartments  (e.g.,  “nu-
cleus”  or “chromatin”), or stable macromolecular complexes of which
they are parts (e.g., “RNA polymerase II”). Together, annotations of a
gene to terms from each of those aspects describe what specific function
a gene product plays in a process and where this activity occurs in the

cell. Ideally every gene product should have an annotation from each of
the three aspects of GO.

The specific genes expressed in a given cell define the identity and
functionalities of that cell. Regulation of transcription is highly complex
and leads to differential gene expression in specific cells or under spe-
cific  conditions.  In  human  cells,  it  has  been  estimated  that  several
thousand  proteins  participate  in  gene  expression  and  its  regulation,
directly  or  indirectly  [3]  (Velthuijs  et  al.  BBAGRM-D-21-00020  this
issue).  This  includes  the  general  transcription  machinery,  the  factors
that make the chromatin more or less accessible, specific DNA-binding
transcription factors, and the signaling molecules that regulate the ac-
tivity  of  all  those  proteins.  This  complexity  is  difficult  to  accurately
represent in ontological form. Tripathi et al. [4] redesigned that part of
the  ontology  in  2013  to  define  precise  molecular  functions  for  the
various proteins involved in transcription and its regulation. Nearly 10
years  after  its  implementation,  we  had  to  acknowledge  that  this
framework  was  too  complex  and  difficult  to  navigate,  leading  to
inconsistent annotations and thus poorly serving the user community.
The  work  described  here  was  also  motivated  by  the  https://www.gr

* Corresponding author.

E-mail address: pascale.gaudet@sib.swiss (P. Gaudet).

https://doi.org/10.1016/j.bbagrm.2021.194752
Received 6 January 2021; Received in revised form 24 August 2021; Accepted 25 August 2021

BBA-GeneRegulatoryMechanisms1864(2021)194752Availableonline28August20211874-9399/©2021TheAuthor(s).PublishedbyElsevierB.V.ThisisanopenaccessarticleundertheCCBYlicense(http://creativecommons.org/licenses/by/4.0/).P. Gaudet et al.

Fig. 1. Transcription regulator activity branches of the Gene Ontology. (a) Graphical representation of the placement of the parent terms for transcription regulator
molecular functions. Black headers correspond to MF and cyan headers to BP terms. (b) Transcription regulators are dbTF and coTFs. The general transcription
initiation factors play a direct role in transcription. Top-level terms of each branch are highlighted in blue.

eekc.org/  GREEKC  consortium,  whose  goals  include  curation  tools
development,  reengineering  of  ontologies,  development  of  curation
guidelines and text mining tools, developing platforms to analyze and
render  the  molecular  logic  of  transcription  regulatory  networks  for
which  a  robust  infrastructure  is  needed.  Therefore,  we  thoroughly
reviewed  the  Gene  Ontology  representation  of  molecular  activities
relevant to transcription, with a simpler and more pragmatic approach,
more aligned with available experimental data.

We  have  revised  the  GO  MF  terms  representing  the  activities  of
proteins involved in transcription, with the input from domain experts.
In addition to RNA polymerase, we defined three different types of ac-
tivities that take place on the DNA to mediate or regulate transcription:
general transcription factors (GTFs), DNA-binding transcription factors
(dbTFs), and transcription coregulators (coTFs).

Here we present the annotation approach recommended by the GO
consortium  [5],  applied  to  the  recent  refactoring  of  the  transcription

domain of GO. This approach aims to 1) help biocurators – annotation
producers - interpret published data and correctly assign the MFs terms
for GTF, dbTF, or coTF to a protein, and 2) help users understand how
the  data  is  generated  and  how  to  interpret  them.  The  annotation  of
factors  involved  in  transcription  and  its  regulation  is  challenging  for
multiple  reasons.  Contrary  to  other  molecular  functions,  for  example
enzymes, where one protein or a well-defined complex catalyses a pre-
cise  reaction,  the  measurable  output  of  transcription  activities  is  the
result of multiple nearly simultaneous activities of GTF, dbTF, coTF, as
well  as  RNA  polymerase,  hence,  individual  activities  can  be  hard  to
distinguish  experimentally.  Moreover,  these  factors  often  form  large
complexes, such that the level of resolution of the experimental setup is
essential to determine the precise activity of any given protein. Older
experimental methods often did not provide enough details, leading to
inaccurate classifications of certain proteins. In addition, researchers use
“transcription factor” loosely, at times meaning GTF, dbTF, or coTF. This

BBA-GeneRegulatoryMechanisms1864(2021)1947522P. Gaudet et al.

Fig. 2. DNA binding branch of the Gene Ontology. This part of the Molecular Function (MF) ontology describes DNA binding. (a) Graphical representation of the
placement of the terms describing sequence-specific promoter binding. (b) Hierarchical view of the sequence-specific transcription regulatory region binding terms.

complicates the annotation process and necessitates solid expertise for
correct interpretation of the data. The experimental data itself is difficult
to parse for unambiguous assignment of a function to a protein: typi-
cally, a single experiment is insufficient for accurately determining the
function of these proteins, thus, interpretation of experimental results
that investigate dbTFs must rely on pre-existing knowledge. Also, many
proteins presumed to function as dbTFs have never been experimentally
demonstrated to bind DNA, but their role is indirectly inferred by the
presence  of  known  specific  DNA-binding  domains  and  in  some  cases,
evidence of an effect on the transcription of putative direct target genes.
To add to the complexity, the presence of a DNA-binding domain in a
protein does not always imply that the protein functions as a dbTF [6].

2. GO description of molecular functions relevant for
transcription

We  distinguish  between  three  types  of  activities  involved  in  tran-
scription  or  directly  regulating  it:  general  transcription  factors
(GO:0140223),  DNA-binding  transcription  factors  (GO:0003700),  and
transcription co-regulators (GO:0003712). The general transcription
initiation factor activity term and its descendants describe the activ-
ities of general transcription initiation factors for RNA polymerase I, II
and III, which play a direct role in the biological process of transcription
at the core promoter (Sant et al., BBAGRM-D-21-00014 this issue). In
contrast,  the  GO:0140110  transcription  regulator  activity  branch
describes the activities of transcription regulators: dbTF and coTFs, that

BBA-GeneRegulatoryMechanisms1864(2021)1947523P. Gaudet et al.

act  at  any  type  of  cis-regulatory  module  (Fig.  1).  DNA-binding  tran-
scription factors are adaptors that bind chromatin at specific genomic
addresses to coordinately regulate the expression of genes sets. This is
encoded in the ontology via links between the DNA-binding transcrip-
tion  factor activity  term  and  its  descendants  and  to  their  counterpart
branch of the MF ontology describing DNA binding. The GO:0000976
transcription regulatory region sequence-specific DNA-binding sub-tree
of GO includes terms describing specific regulatory regions, such as the
core promoter (including the TATA box and the transcription start site),
cis-regulatory  regions  (bound  by  dbTFs),  and  specific  types  of  cis-
regulatory  motifs  (such  as  E-box  and  N-box).  An  overview  of  the  GO
structure for DNA binding activities is shown in Fig. 2. The definitions
and placement of GO terms in the ontology can be viewed in the AmiGO
[7,8];  http://amigo.geneontology.org/amigo,  and  QuickGO  [9];
https://www.ebi.ac.uk/QuickGO/ browsers.

3. Strategy for annotating transcription-associated activities

GO terms are associated with gene products based on two general
approaches: from experimental data and from sequence inferences [10].
The GO database has a total of 8 million annotations, about 7% of which
are to human gene products. For human, there are >915,000 annota-
tions derived from experimental data (GO release 2020-10-10 obtained
from  http://amigo.geneontology.org).  Sequence  inference  methods
provide more than 106,000 annotations for human proteins based on
phylogenetic relationships (65,000 annotations) [11]; protein domains
(6730  annotations)  [12];  and  Ensembl  orthology  predictions  (35,000
annotations)  [13].  The  next  sections  describe  the  annotation  of  the
different types of proteins involved in transcription and its regulation.

3.1. Transcription activity annotations supported by experimental data2.

The following annotation approach follows the recommendations of
the GO consortium. First and foremost, it is necessary to use as much
information as possible, rather than annotating articles individually and
out of the wider context. When extracting information, a gene-by-gene
or  pathway-by-pathway  approach  is  considered  best  practice  [5].
Reviewing a range of articles ensures that the annotations closely reflect
the current state of knowledge. Ideally, the corpus of annotations for a
gene product should be based on multiple observations from different
articles by independent research groups. Five steps used to determine
whether  a  gene  can  be  annotated  as  a  transcriptional  regulator  are
outlined  in  Fig.  3.  Appendix  1  provides  examples  of  each  of  those
different activities.

1.  Identify the starting hypothesis: are the authors characterizing
a  transcription  regulator?  Scientific  models  are  built  by  adding
new  data  to  the  existing  corpus  of  evidence.  New  data  can  either
support  or  contradict  existing  models.  The  Introduction  section  of
research articles can be used to understand what prior knowledge the
article builds on, and which aspect of the existing model or what new
model the authors are assessing. The hypothesis tested by the authors
is essential to choose a GO term, with the caveat that inconsistent
terminology  has  been  used  in  transcription  research  articles  and
therefore may not always be aligned with the GO term categories.
2.  Determine whether knowledge from specific protein domains or
characterized orthologs support the hypothesis. The presence of
specific domains and the existence of well-characterized orthologs
can provide useful support for interpreting experimental data. Note
that this data should be used with caution. For instance, ARID-, AT
hook-, and some HMG-, GATA-, zinc finger domain-containing pro-
teins and proteins binding structural features such as the DNA minor
groove rarely bind DNA in a sequence-specific manner; some of them
merely function to increase the avidity or stability of a transcription
factor complex and its associated co-factors and do not - in their own
capacity - provide the specific genomic address to guide transcription

Fig.  3. Five  steps  to  transcription  activity  annotation.  The  five  key  steps  to
associating a transcription MF term with a protein starts with identifying the
starting hypothesis, to confirm that the authors are characterizing a GTF, dbTF
or  coTF.  Secondly,  considering  whether  the  knowledge  from  specific  protein
domains or characterized orthologs support the hypothesis. Thirdly, checking
whether existing annotations from GO, UniProt and Model Organism databases
are  consistent  with  the  hypothesis.  Fourthly,  reviewing  other  published
experimental  data  to  ensure  no  contradictory  findings  have  been  reported.
Finally, creating new GO annotations, if the experimental results are consistent
with the identified hypothesis.

to specified target genes. Such proteins are not considered dbTFs in
GO.

To support the association of a gene with a GO term from homolo-
gous sequences from other species, only closely related orthologs whose
function have been unambiguously characterized can be used if those are
consistent with the experimental data presented in the article.

-  GTFs  function  as  the  molecular  machine  that  assembles  with  the
RNA polymerase at the promoter to form the pre-initiation complex
(PIC).  GTFs  have  been  characterized  in  several  organisms,  from
archaea  to  yeast  and  mammalian  cells  [14,15],  and  therefore
orthology should provide strong support for the decision to associate
these proteins with a child specific for RNA polymerase I, II or III of
the  MF  term  “GO:0140223  general  transcription  initiation  factor
activity”. In addition, the naming of GTFs is well established across
human and model organism nomenclature groups and can be used to
help guide these decisions. Thus, for human GTFs the HUGO Gene
Nomenclature Committee (HGNC, www.genenames.org) provide the
gene symbol TAF#, for TATA-box binding protein associated factors,
and GTF2#s and GTF3#s, for general transcription factor II and III
subunits respectively.

- dbTFs are specific double-stranded DNA-binding transcription fac-
tors that provide genomic addresses and respond to the conditions
under which specific genes are expressed. Central to dbTF function is
their  binding  to  specific  double-stranded  DNA  sequences  that  are
often named transcription factor binding sites (TFBS). Gene products
associated with the GO term “GO:0003700 DNA-binding transcrip-
tion factor activity”  have the ability to bind DNA and this binding
regulates the expression of a specific set of target genes. The direct
target gene(s) can also be included in the annotation using the “has
input  relation”.  A  human  dbTF  catalog  developed  by  the  GREEKC
project  (  [6];  also  accessible  from  https://www.ebi.ac.uk/Qui
ckGO/targetset/dbTF)  may  be  consulted  to  check  whether  a  spe-
cific human protein is annotated to dbTF function with experimental
or phylogenetic evidence. When considering proteins that belong to
families of well characterized transcription factors, such as those that
contain  bHLH,  bZIP,  homeobox,  ETS,  Forkhead,  etc.  domains  and
proteins  with  a  one-to-one  ortholog  already  demonstrated  to  be  a

BBA-GeneRegulatoryMechanisms1864(2021)1947524P. Gaudet et al.

dbTF, then weaker evidence of DNA binding, such as ChIP experi-
ments is sufficient. In contrast, special care must be taken to annotate
proteins  bearing  domains  that  are  not  exclusively  found  in  tran-
scription factors, such as RING, MYND and PhD zinc fingers. Simi-
larly, for proteins with enzymatic activity: while there are rare cases
of dbTFs with enzymatic activities, such as ENO1, dbTF and enzy-
matic activity are usually mutually exclusive. For proteins not in the
dbTF  catalog,  clear  experimental  or  phylogenetic  evidence  of
sequence-specific DNA binding and gene transcription regulation via
cognate DNA motifs located in gene-associated cis-regulatory mod-
ules is required for the protein to be classified with high confidence
as a dbTF.

- coTFs: Transcription coregulators (also known as transcription co-
factors; GO:0003712) represent a group of different functions that
take place at cis-regulatory regions to make transcription of specific
gene sets either more (coactivators) or less (corepressors) efficient.
Coregulators  can  modify  chromatin  structure  through  covalent
modification  of  histones,  ATP-dependent  chromatin  remodelling,
and  modulate  dbTF  interactions  with  other  transcription  cor-
egulators. We classify the Mediator Complex, which bridges dbTFs
and  the  RNA  polymerase,  as  a  transcription  coactivator  [16–18].
Many coTFs have enzymatic activity and normally exert their func-
tion independent of high affinity binding to specific DNA sequences.
CoTFs  that  do  bind  DNA  typically  recognize  very  short  DNA  se-
quences  that  are  not  sufficiently  unique  in  the  genome  to  enable
regulation of a limited set of genes in a discrete environmental or
developmental stage. One example of this is CPF1, that binds the CpG
dinucleotide and helps most CpG islands gain epigenomic marking
[19–21].

It  is  important  to  keep  in  mind  that  DNA  binding  proteins  that
regulate transcription are not necessarily dbTFs. Key points that help
distinguish between the three activities discussed above are that (i)
dbTFs bind DNA in a sequence-specific manner, and regulate precise
sets of genes; (ii) coTFs usually do not directly bind DNA, and when
they  do  they  don't  exhibit  strong  sequence-specificity;  (iii)  coTFs
often  have  catalytic  activities  (such  as  histone  methyltransferase,
protein kinase, or ubiquitin ligase), which is highly unusual in dbTFs;
(iv) GTFs are required for core promoter activity and are considered
to act at each promoter to promote transcription initiation [14,22],
although the exact subunit composition at individual promoters may
vary.

3. Confirm  that  existing  annotations  are  consistent  with  the  hy-
pothesis. New annotations need to be consistent with existing an-
notations, unless the existing annotations are believed to be wrong or
out of date. Annotations made to a term as well as a more specific
descendant reflect differences in granularity of annotation, and are
not generally considered inconsistent. When the new annotation uses
a term in a different branch than existing annotations, a review of the
evidence supporting the existing annotations is undertaken and, if
necessary, annotations that appear to be incorrect are disputed (see
section “Ensuring a coherent set of annotations”).

4.  Check  that  other  published  experimental  results  do  not
contradict the hypothesis. The application of the gene-by-gene or
pathway-by-pathway annotation approach ensures that results from
other research articles are taken into account and that all annotations
are  in  line  with  the  current  state  of  knowledge.  Again,  if  in-
consistencies  are  noticed,  great  care  is  taken  to  confirm  correct
interpretation  of the data, this is  particularly important if there is
evidence for multiple, distinct transcription activity functions.
5.  Validate that the experimental results are consistent with the
hypothesis.  If  the  results  presented  in  the  curated  article  are
consistent  with  the  hypothesis  presented  by  the  authors,  then  the
appropriate transcription activity GO term(s) are associated with the
gene product.

Proteins that are  involved  in  transcription and  its  regulation  have
historically  been  studied  through  small-scale,  focused  experimental
approaches. For some examples of the small-scale experiments that do
provide evidence for DNA binding transcription factor activity the bio-
curator  can  use  Tables  3  and  4  of  Tripathi  et  al.  [4]  and  in  Santos-
Zavaleta  et  al.  [23].  Recent  advances  in  high-throughput  methodolo-
gies now provide robust data that, when interpreted with sufficient care,
support the assignment of a function role to many proteins, including
transcription  regulators.  This  includes  HT-SELEX  [24,25],  Protein
Binding Microarrays [26], ChIP [27], one- and two-hybrid experiments
[28,29]. For these experiments, the data quality and the false positive
rate  must  be  evaluated  before  annotations  are  created.  For  example,
human HT-SELEX data will have more false positives if native dbTFs are
assayed  in  nuclear  extracts  or  over-expressed  in  eukaryotic  cells,
compared with heterologous proteins purified from prokaryotic cells, as
the latter reduces the probability of indirect interactions with endoge-
nous factors. For high-throughput transcription data, only articles with
low rates of false positives, are curated. Those various techniques pro-
vide  multiple  independent  lines  of  evidence,  strengthening  the  confi-
dence  in  the  annotation  when  they  converge  on  a  single  motif  or
molecular  function.  The  GO  recommendations  on  curation  of  high-
throughput experimental data should be applied when such data is an-
notated [30].

3.2. Annotations based on non-experimental evidence

There are only about 500 human dbTFs for which there is experi-
mental evidence satisfying the criteria presented here. Across all areas of
biology several reliable methods infer protein function from available
experimental data. Indeed, there are approximately 1000 human pro-
teins annotated as dbTFs by non-experimental methods (Lovering et al.
same BBA issue, prepublication available at [6]). Phylogenetic annota-
tions  are  assigned  by  a  group  of  biocurators  with  expertise  in  evolu-
tionary  biology,  and  require  experimental  evidence  for  at  least  one
member  of  a  clade  of  evolutionarily  related  proteins  [11].  The  GO
knowledgebase also contains GO terms assigned by automated pipelines
based  on  protein  domain  (InterPro2GO)  and  orthology  (Ensembl).
InterPro2GO [12] is based primarily on local (partial) homology: pro-
tein domains are mapped to specific GO terms, and any protein with one
of  these  domains  will  be  annotated  to  the  appropriate  GO  term(s).
Ensembl Compara [13] generates groups of one-to-one orthologs among
closely related species and propagates all experimental annotations to
each members of the group. While manual annotations based on these
methods are allowed, the GO consortium recommends using the auto-
mated pipelines that are maintained centrally and ensure a consistent
annotation corpus across all annotated species.

4. Ensuring a coherent set of annotations

During the process of annotation other relevant annotations associ-
ated with the gene are reviewed. If there are conflicting annotations, the
supporting data should be reassessed to determine whether the anno-
tations  are  inconsistent  with  the  data,  in  which  case  the  annotations
must be fixed [5].

In cases where the primary data is conflicting across different articles
(for example a protein is sometimes described as a transcription factor,
and sometimes as a coregulator), then the literature will be reviewed
carefully to decide whether the annotation is incorrect (bad choice of
term, wrong protein annotated), whether the knowledge has evolved, if
the protein plays multiple roles under different conditions (i.e., acts as a
DNA-binding transcription factor in certain contexts and as a cofactor in
others). If no activity has yet been established, no MF annotation will be
made.

Note  that  individual  DNA-binding  transcription  factors  can  act  as
both activators or repressors dependent on the context, hence associa-
tion of both activator and repressor terms with a single protein is not

BBA-GeneRegulatoryMechanisms1864(2021)1947525P. Gaudet et al.

Fig. 4. Representation of biological context of dbTF activity. The level of cyclin-dependent kinase inhibitor p21 (CDKN1A) is regulated by the transcription factor
p53 (TP53) upon DNA damage, signaling cell cycle arrest to the cell (http://noctua.berkeleybop.org/editor/graph/gomodel:5fa76ad400000000).

considered inconsistent. The specific conditions under which this hap-
pens, such as relevant signaling pathways, cell type, as well as specific
target genes, etc., may be further specified through additional context
details ([31]; see an example of a GO-CAM model in Fig. 4).

5. Pitfalls in annotating transcription regulators

During the review of dbTF GO annotations [6], in which over 3000
GO  annotations  were  reviewed,  a  variety  of  common  errors  in  data
interpretation  were  identified.  One  of  the  most  common  errors  was
caused  by  the  difficulty  in  distinguishing  a  dbTF  from  a  coTF,  as  the
evidence for those two functions can be quite similar. To prevent this
error, biocurators ensure that the protein has a sequence-specific dou-
ble-stranded DNA-binding domain and conduct an exhaustive review of
the  literature,  including  articles  associated  with  the  protein's  close
orthologs. Furthermore, the literature supporting the dbTF activity of a
protein that also has evidence for another function, in particular, RNA
binding, will be carefully checked before assigning a dbTF activity. The
work on the human dbTF catalog added a GO ‘DNA-binding transcrip-
tion factor activity’ annotation to 583 proteins, and removed erronous
assignments for 256 proteins (Lovering et al. BBAGRM-D-20-00141 this
issue).

Transcription  regulators  most  often  act  as  members  of  complexes,
some of which also contain proteins with other activities. In some cases,
only some subunits of a complex interact with DNA: for instance, while
the RFX complex contains three members: RFX5, RFXAP and RFXANK,
only  RFX5  binds  DNA  directly.  But  the  DNA-binding  ability  of  the
complex is facilitated by all three subunits so RFXAP and RFXANK are
not coTFs [32]. In this case, RFXAP and RFXANK are annotated using the
“contributes to” qualifier, to indicate that they participate in, but are not
directly responsible for the activity.

Another  activity  that  can  easily  be  confused  for  a  coTF  is  a  dbTF
inhibitor. These proteins interact with a dbTF, but not at the DNA, to
prevent  the  dbTF  from  reaching  its  target  genes.  Well  characterized
examples  are  the  I-SMADs,  SMAD6  and  SMAD7  [33],  that  act  by
competing  with  active  SMADs  at  receptors,  thus  blocking  further
intracellular signaling, and should be annotated to “GO:0140416 tran-
scription regulator inhibitor activity”.

It must be noted that these approaches to avoid errors in dbTF ac-
tivity assignment are not unequivocal, as some proteins do have multiple
functions. For example, the glucocorticoid receptor (NR3C1), which is a

canonical dbTF, has recently been shown to bind double-stranded RNA
motifs  [34];  ATF2  (activating  transcription  factor  2)  and  CLOCK  are
dbTFs that have been reported to also exhibit histone acetyltransferase
activity  [35–38];  some  dbTFs,  such  as  NFIB  (nuclear  factor  I  B),  also
function as dbTF inhibitors [39]. Finally, general and sequence-specific
effects can be difficult to separate, as has been established for the MYC
dbTF [40].

6. Conclusion

The  annotation  approach  presented  here  is  designed  to  help  bio-
curators annotate factors involved in transcription and its regulation, as
well as for users of GO annotations to understand their meaning and the
evidence behind them. This work complements the redesign of this part
of  the  GO  to  significantly  simplify  the  ontology  structure.  The  new
ontology structure and the present standards were applied to the review
of human proteins associated with GO terms describing dbTF activity
[6].  We  anticipate  that  adoption  of  this  annotation  approach  by  all
groups  who  produce  GO  associations  will  increase  annotation  consis-
tency across all species, for transcription and also more widely across all
areas represented by GO.

Declaration of competing interest

The authors declare that they have no known competing financial
interests or personal relationships that could have appeared to influence
the work reported in this paper.

Acknowledgements

We  thank  many  GREEKC  and  GO  consortium  members  for  useful
discussions that led to the development of these guidelines, in particular
Marcio L. Acencio, Helen Attrill, and Valerie Wood.

Funding sources

The  GO  Consortium  is  funded  by  the  National  Human  Genome
Research  Institute  (US  National  Institutes  of  Health),  grant  number
HG002273. RCL has been supported by Alzheimer's Research UK grant
(ARUK-NAS2017A-1)  and  the  National  Institute  for  Health  Research
University  College  London  Hospitals  Biomedical  Research  Centre.

BBA-GeneRegulatoryMechanisms1864(2021)1947526P. Gaudet et al.

GREEKC is supported by the COST Action grant CA15205.

Appendices. Supplementary data

Supplementary data to this article can be found online at https://doi.

org/10.1016/j.bbagrm.2021.194752.

References

[1] M. Ashburner, C.A. Ball, J.A. Blake, D. Botstein, H. Butler, J.M. Cherry, et al., Gene
ontology: tool for the unification of biology, Gene Ontol. Consort. Nat Genet. 25 (1)
(2000 May) 25–29.

[2] The Gene Ontology Consortium, The Gene Ontology Resource: 20 years and still

GOing strong, Nucleic Acids Res. 47 (D1) (2019) D330–D338, 08.

[3] R. Tupler, G. Perini, M.R. Green, Expressing the human genome, Nature. 409

(6822) (2001 Feb 15) 832–833.

[4] S. Tripathi, K.R. Christie, R. Balakrishnan, R. Huntley, D.P. Hill, L. Thommesen, et
al., Gene Ontology annotation of sequence-specific DNA binding transcription
factors: setting the stage for a large-scale curation effort, Database J. Biol.
Databases Curation 2013 (2013), bat062.

[5] S. Poux, P. Gaudet, Best practices in manual annotation with the Gene Ontology,

Methods Mol. Biol. Clifton NJ 1446 (2017) 41–54.

[6] Lovering R.C., Gaudet P., Acencio M.L., Ignatchenko A., Jolma A., Fornes O., et al.,

BBAGRM-D-20-00141 this issue.

[7] Gene Ontology Consortium, Gene Ontology Consortium: going forward, Nucleic

Acids Res. 43 (Database issue) (2015 Jan) D1049–D1056.

[8] S. Carbon, A. Ireland, C.J. Mungall, S. Shu, B. Marshall, S. Lewis, et al., AmiGO:

online access to ontology and annotation data, Bioinforma Oxf. Engl. 25 (2) (2009
Jan 15) 288–289.

[9] D. Binns, E. Dimmer, R. Huntley, D. Barrell, C. O’Donovan, R. Apweiler, QuickGO:
a web-based tool for Gene Ontology searching, Bioinforma Oxf Engl. 25 (22) (2009
Nov 15) 3045–3046.

ˇ
Skunca, J.C. Hu, C. Dessimoz, Primer on the Gene Ontology, Methods
[10] P. Gaudet, N.

Mol. Biol. Clifton NJ 1446 (2017) 25–37.

[11] P. Gaudet, M.S. Livstone, S.E. Lewis, P.D. Thomas, Phylogenetic-based propagation
of functional annotations within the Gene Ontology consortium, Brief. Bioinform.
12 (5) (2011 Sep) 449–462.

[12] A. Mitchell, H.-Y. Chang, L. Daugherty, M. Fraser, S. Hunter, R. Lopez, et al., The
InterPro protein families database: the classification resource after 15 years,
Nucleic Acids Res. 43 (Database issue) (2015 Jan) D213–D221.

[13] F. Cunningham, P. Achuthan, W. Akanni, J. Allen, M.R. Amode, I.M. Armean, et al.,

Ensembl 2019, Nucleic Acids Res. 47 (D1) (2019) D745–D751, 08.

[14] S. Sainsbury, C. Bernecky, P. Cramer, Structural basis of transcription initiation by
RNA polymerase II, Nat. Rev. Mol. Cell Biol. 16 (3) (2015 Mar) 129–143.
[15] M.J.E. Koster, B. Snel, H.T.M. Timmers, Genesis of chromatin and transcription
dynamics in the origin of species, Cell. 161 (4) (2015 May 7) 724–736.

[16] K.M. Andr´e, E.H. Sipos, J. Soutourina, Mediator roles going beyond transcription,

Trends Genet TIG. 37 (3) (2020 Sep 10) 224–234.

[17] T. Eychenne, M. Werner, J. Soutourina, Toward understanding of the mechanisms
of mediator function in vivo: focus on the preinitiation complex assembly,
Transcription. 8 (5) (2017) 328–342.

[18] J. Yin, G. Wang, The mediator complex: a master coordinator of transcription and
cell lineage development, Dev. Camb. Engl. 141 (5) (2014 Mar) 977–987.
[19] J.P. Thomson, P.J. Skene, J. Selfridge, T. Clouaire, J. Guy, S. Webb, et al., CpG
islands influence chromatin structure via the CpG-binding protein Cfp1, Nature.
464 (7291) (2010 Apr 15) 1082–1086.

[20] J. Lipski, X. Zhang, B. Kruszewska, R. Kanjhan, Morphological study of long axonal

projections of ventral medullary inspiratory neurons in the rat, Brain Res. 640
(1–2) (1994 Mar 21) 171–184.

[21] H.K. Long, N.P. Blackledge, R.J. Klose, ZF-CxxC domain-containing proteins, CpG

islands and the chromatin connection, Biochem. Soc. Trans. 41 (3) (2013 Jun)
727–740.

[22] P. Cramer, Organization and regulation of gene transcription, Nature. 573 (7772)

(2019) 45–54.

[23] A. Santos-Zavaleta, H. Salgado, S. Gama-Castro, M. S´anchez-P´erez, L. G´omez-

Romero, D. Ledezma-Tejeida, et al., RegulonDB v 10.5: tackling challenges to unify
classic and high throughput knowledge of gene regulation in E. coli K-12, Nucleic
Acids Res. 47 (D1) (2019) D212–D220, 08.

[24] A.D. Ellington, J.W. Szostak, In vitro selection of RNA molecules that bind specific

ligands, Nature. 346 (6287) (1990 Aug 30) 818–822.

[25] C. Tuerk, L. Gold, Systematic evolution of ligands by exponential enrichment: RNA
ligands to bacteriophage T4 DNA polymerase, Science. 249 (4968) (1990 Aug 3)
505–510.

[26] K.K. Andrilenas, A. Penvose, T. Siggers, Using protein-binding microarrays to study

transcription factor specificity: homologs, isoforms and complexes, Brief Funct.
Genom. 14 (1) (2015 Jan) 17–29.

[27] T.H. Kim, J. Dekker, ChIP-seq, Cold Spring Harb. Protoc. 2018 (5) (2018), 01.
[28] J.A. Sewell, J.I. Fuxman Bass, Options and considerations when using a yeast one-

hybrid system, Methods Mol. Biol. Clifton NJ. 1794 (2018) 119–130.

[29] A. Paiano, A. Margiotta, M. De Luca, C. Bucci, Yeast two-hybrid assay to identify

interacting proteins, Curr. Protoc. Protein Sci. 95 (1) (2019), e70.

[30] H. Attrill, P. Gaudet, R.P. Huntley, R.C. Lovering, S.R. Engel, S. Poux, et al.,

Annotation of gene product function from high-throughput studies using the Gene
Ontology, Database J. Biol. Databases Curation. 2019 (2019), 01.

[31] P.D. Thomas, D.P. Hill, H. Mi, D. Osumi-Sutherland, K. Van Auken, S. Carbon, et
al., Gene Ontology Causal Activity Modeling (GO-CAM) moves beyond GO
annotations to structured descriptions of biological functions and systems, Nat.
Genet. 51 (10) (2019) 1429–1433.

[32] K. Masternak, E. Barras, M. Zufferey, B. Conrad, G. Corthals, R. Aebersold, et al.,
A gene encoding a novel RFX-associated transactivator is mutated in the majority
of MHC class II deficiency patients, Nat. Genet. 20 (3) (1998 Nov) 273–277.

[33] K. Miyazawa, K. Miyazono, Regulation of TGF-β family signaling by inhibitory

smads, Cold Spring Harb. Perspect. Biol. 9 (3) (2017 Mar 1).

[34] N.V. Parsonnet, N.C. Lammer, Z.E. Holmes, R.T. Batey, D.S. Wuttke, The

glucocorticoid receptor DNA-binding domain recognizes RNA hairpin structures
with high affinity, Nucleic Acids Res. 47 (15) (2019 05) 8180–8192.

[35] H. Kawasaki, L. Schiltz, R. Chiu, K. Itakura, K. Taira, Y. Nakatani, et al., ATF-2 has
intrinsic histone acetyltransferase activity which is modulated by phosphorylation,
Nature. 405 (6783) (2000 May 11) 195–200.

[36] J. Hirayama, S. Sahar, B. Grimaldi, T. Tamaru, K. Takamatsu, Y. Nakahata, et al.,

CLOCK-mediated acetylation of BMAL1 controls circadian function, Nature. 450
(7172) (2007 Dec 13) 1086–1090.

[37] B. Grimaldi, Y. Nakahata, S. Sahar, M. Kaluzova, D. Gauthier, K. Pham, et al.,

Chromatin remodeling and circadian control: master regulator CLOCK is an
enzyme, Cold Spring Harb. Symp. Quant. Biol. 72 (2007) 105–112.

[38] Z. Wang, Y. Wu, L. Li, X.-D. Su, Intermolecular recognition revealed by the complex
structure of human CLOCK-BMAL1 basic helix-loop-helix domains with E-box
DNA, Cell Res. 23 (2) (2013 Feb) 213–224.

[39] Y. Liu, H.U. Bernard, D. Apt, NFI-B3, a novel transcriptional repressor of the

nuclear factor I family, is generated by alternative RNA processing, J. Biol. Chem.
272 (16) (1997 Apr 18) 10739–10745.

[40] Z. Nie, C. Guo, S.K. Das, C.C. Chow, E. Batchelor, S.S. Simons, et al., Dissecting

transcriptional amplification by MYC, eLife 9 (2020), 27.

BBA-GeneRegulatoryMechanisms1864(2021)1947527