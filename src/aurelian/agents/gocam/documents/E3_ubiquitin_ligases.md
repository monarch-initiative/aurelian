# E3 ubiquitin ligases

An **E3 ubiquitin ligase** is a protein that recruits an E2 ubiquitin-conjugating enzyme loaded with ubiquitin, recognizes a protein substrate, and assists or directly catalyzes the transfer of ubiquitin from the E2 to the protein substrate.

The recognition of the protein substrate can be done by the ubiquitin protein ligase itself or through a complex composed of ubiquitin ligase-substrate adaptor and ubiquitin ligase complex scaffolds.

<https://en.wikipedia.org/wiki/Ubiquitin_ligase>

# How to annotate E3 ubiquitin ligases

## E3 ligase that promotes ubiquitination by itself

The molecular activity unit for the ubiquitin ligase is:

* **MF**: 'enables' ubiquitin protein ligase activity [GO:0061630](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0061630#term=history)
* 'has input'the substrate protein
* **BPs**:
* 'part of' ubiquitination ([GO:0016567](https://www.ebi.ac.uk/QuickGO/term/GO%3A0070936))**:** if known, the **BP** should describe the type of ubiquitination (K-48, K-63…)

ex: protein K48-linked ubiquitination [GO:0070936](https://www.ebi.ac.uk/QuickGO/term/GO%3A0070936); otherwise, use the parent protein ubiquitination GO:0016567 or protein polyubiquitination GO:0000209.

* the ubiquitination is part\_of the biological process in which the ubiquitination is involved:

e. g. : proteasome-mediated ubiquitin-dependent protein catabolic process [GO:0043161](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0043161#term=history) or children, such as: SCF-dependent proteasomal ubiquitin-dependent protein catabolic process ([GO:0031146](https://www.ebi.ac.uk/QuickGO/term/GO%3A0031146)) or ubiquitin-dependent protein catabolic process via the C-end degron rule pathway ([GO:0140627](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140627))

* and/or part of’ the BP in which the ubiquitination is involved: DNA repair, DNA damage response, lysosomal degradation, etc regulated by this mechanism (ex: negative regulation of inflammatory response, [GO:0050728](https://www.ebi.ac.uk/QuickGO/term/GO%3A0050728))
* The causal relation to the substrate molecular activity unit is: ‘indirectly negatively regulates’.

Example: [TRIM45-mediated degradation of TAB2 leading to inflammatory response inhibition (Human)](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A63f809ec00000307)

![](data:image/png;base64...)

## An E3-ligase complex with adaptors and scaffold protein(s)

####

* The molecular activity unit for the ubiquitin ligase complex scaffold, such as CUL4A and/or DDB1 is:
* **MF**: ubiquitin ligase complex scaffold activity [GO:0160072](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0160072#term=history)
* Has **input** both the ubiquitin ligase-substrate adaptor and the ubiquitin protein ligase
* **BP**: if known, the **BP** should describe the type of ubiquitination (K-48, K-63…)

ex: protein K48-linked ubiquitination [GO:0070936](https://www.ebi.ac.uk/QuickGO/term/GO%3A0070936)

if not known, use a **BP** describing the biological process in which the ubiquitination is involved in.

ex: proteasome-mediated ubiquitin-dependent protein catabolic process [GO:0043161](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0043161#term=history) or children, such as: SCF-dependent proteasomal ubiquitin-dependent protein catabolic process ([GO:0031146](https://www.ebi.ac.uk/QuickGO/term/GO%3A0031146)) or ubiquitin-dependent protein catabolic process via the C-end degron rule pathway ([GO:0140627](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140627))

‘Part of’ the BP regulated by this mechanism (ex: T cell activation, [GO:0042110](https://www.ebi.ac.uk/QuickGO/term/GO%3A0042110))

* The causal relation between the substrate molecular activity unit is: ‘directly negatively regulates’ if it leads to degradation. (to decide for the other cases)
* The causal relation to the ubiquitin ligase-substrate adaptor molecular activity unit is: ‘directly regulates’.
* The molecular activity unit for the ubiquitin ligase-substrate adaptor is:
* **MF**: ubiquitin ligase-substrate adaptor activity [GO:1990756](http://amigo.geneontology.org/amigo/term/GO%3A1990756)
* Has **input** the substrate protein
* **BP**: if known, the **BP** should describe the type of ubiquitination (K-48, K-63…)

ex: protein K48-linked ubiquitination [GO:0070936](https://www.ebi.ac.uk/QuickGO/term/GO%3A0070936)

if not known, use a **BP** describing the biological process in which the ubiquitination is involved in.

ex: proteasome-mediated ubiquitin-dependent protein catabolic process [GO:0043161](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0043161#term=history) or children, such as: SCF-dependent proteasomal ubiquitin-dependent protein catabolic process ([GO:0031146](https://www.ebi.ac.uk/QuickGO/term/GO%3A0031146)) or ubiquitin-dependent protein catabolic process via the C-end degron rule pathway ([GO:0140627](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140627))

‘Part of’ the BP regulated by this mechanism (ex: T cell activation, [GO:0042110](https://www.ebi.ac.uk/QuickGO/term/GO%3A0042110))

* The causal relation to the ubiquitin ligase molecular activity unit is: ‘directly provides input for’.
* Annotation of the ubiquitin ligase is the same as [above](#_j8u1po26cp9w)

Example: [DCAF12 controls MOV10 during T cell activation. (Human)](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A636d9ce800001192)

![](data:image/png;base64...)

#### When only substrate adaptor and substrate are known (scaffold and ligase not known)

Example: [FBXL19-mediated degradation of IL1R1 via GSK3B (Human)](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A63d320cd00001588)![](data:image/png;base64...)

* The molecular activity unit for the ubiquitin ligase-substrate adaptor is:
* **MF**: ubiquitin ligase-substrate adaptor activity [GO:1990756](http://amigo.geneontology.org/amigo/term/GO%3A1990756)
* Has **input** the substrate protein
* **BP**: if known, the **BP** should describe the type of ubiquitination (K-48, K-63…)

ex: protein K48-linked ubiquitination [GO:0070936](https://www.ebi.ac.uk/QuickGO/term/GO%3A0070936)

if not known, use a **BP** describing the biological process in which the ubiquitination is involved in.

ex: proteasome-mediated ubiquitin-dependent protein catabolic process [GO:0043161](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0043161#term=history) or children, such as: SCF-dependent proteasomal ubiquitin-dependent protein catabolic process ([GO:0031146](https://www.ebi.ac.uk/QuickGO/term/GO%3A0031146)) or ubiquitin-dependent protein catabolic process via the C-end degron rule pathway ([GO:0140627](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140627))

‘Part of’ the BP regulated by this mechanism (ex: T cell activation, [GO:0042110](https://www.ebi.ac.uk/QuickGO/term/GO%3A0042110))

* The causal relation to the substrate molecular activity unit is: ‘indirectly regulates’ since we don’t add/have information about the E3 ligase.

#### When only substrate adaptor, scaffold and substrate are known (ligase not known)

Ex: [DCAF13 supports the spindle assembly and chromosome condensation during oocyte meiotic division by targeting PTEN polyubiquitination and degradation. (Human)](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A63c0ac2b00001634)

![](data:image/png;base64...)

* The molecular activity unit for the ubiquitin ligase complex scaffold, such as CUL4A and/or DDB1 is:
* **MF**: ubiquitin ligase complex scaffold activity [GO:0160072](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0160072#term=history)
* Has **input** both the ubiquitin ligase-substrate adaptor and the ubiquitin protein ligase
* **BP**: if known, the **BP** should describe the type of ubiquitination (K-48, K-63…)

ex: protein K48-linked ubiquitination [GO:0070936](https://www.ebi.ac.uk/QuickGO/term/GO%3A0070936)

if not known, use a **BP** describing the biological process in which the ubiquitination is involved in.

ex: proteasome-mediated ubiquitin-dependent protein catabolic process [GO:0043161](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0043161#term=history) or children, such as: SCF-dependent proteasomal ubiquitin-dependent protein catabolic process ([GO:0031146](https://www.ebi.ac.uk/QuickGO/term/GO%3A0031146)) or ubiquitin-dependent protein catabolic process via the C-end degron rule pathway ([GO:0140627](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140627))

‘Part of’ the BP regulated by this mechanism (ex: T cell activation, [GO:0042110](https://www.ebi.ac.uk/QuickGO/term/GO%3A0042110))

* The causal relation to the ubiquitin ligase-substrate adaptor molecular activity unit is: ‘directly regulates’.
* The molecular activity unit for the ubiquitin ligase-substrate adaptor is:
* **MF**: ubiquitin ligase-substrate adaptor activity [GO:1990756](http://amigo.geneontology.org/amigo/term/GO%3A1990756)
* Has **input** the substrate protein
* **BP**: if known, the **BP** should describe the type of ubiquitination (K-48, K-63…)

ex: protein K48-linked ubiquitination [GO:0070936](https://www.ebi.ac.uk/QuickGO/term/GO%3A0070936)

if not known, use a **BP** describing the biological process in which the ubiquitination is involved in.

ex: proteasome-mediated ubiquitin-dependent protein catabolic process [GO:0043161](https://www.ebi.ac.uk/QuickGO/GTerm?id=GO:0043161#term=history) or children, such as: SCF-dependent proteasomal ubiquitin-dependent protein catabolic process ([GO:0031146](https://www.ebi.ac.uk/QuickGO/term/GO%3A0031146)) or ubiquitin-dependent protein catabolic process via the C-end degron rule pathway ([GO:0140627](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140627))

‘Part of’ the BP regulated by this mechanism (ex: T cell activation, [GO:0042110](https://www.ebi.ac.uk/QuickGO/term/GO%3A0042110))

* The causal relation to the substrate molecular activity unit is: ‘indirectly regulates’ since we don’t add/have information about the E3 ligase.

## Examples of larger processes in which various types of ubiquitination play a role

![](data:image/png;base64...)

Source: PMID:[27285106](https://pubmed.ncbi.nlm.nih.gov/27285106)

**Review date:**

**Reviewed by:**
