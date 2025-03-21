Receptor activation by a ligand is represented differently in GO-CAM
depending on whether the ligand is (i) a protein (i. e., encoded by a
gene) or (ii) a small molecule. 

Pathway Editor
==============

Protein ligand-activated signaling receptor
-------------------------------------------

### Ligand

The activity unit for a [ligand of a signaling receptor]{.underline} is:

-   **MF**: a ligand \'[enables]{.underline}\' receptor ligand activity
    > ([[GO:0048018]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0048018))
    > or a child

-   **Context:**

    -   The relation between a ligand and its target receptor is
        > *\'*[has input\']{.underline}

    -   **BP** \'[part of\']{.underline} the process in which the ligand
        > participates, usually a child of signal transduction
        > ([[GO:0007165]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0007165))

    -   **CC:**

        -   extracellular ligands: \'[occurs in]{.underline}\'
            > extracellular space
            > ([[GO:0005615]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

        -   membrane-bound ligands: \'[occurs in]{.underline}\' plasma
            > membrane
            > ([[GO:0005886]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

    -   The causal relation between the **ligand activity** and the
        > **receptor activity** is\
        > \'[directly positively regulates]{.underline}\'.

### Signaling receptor

The activity unit for a [signaling receptor]{.underline} is:

-   **MF:** \'[enables]{.underline}\' signaling receptor activity
    > ([[GO:0038023]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0038023)*)*
    > or a child*.* 

-   **Context:**

    -   The input (target) of the receptor is the **effector protein it
        > regulates**, for example a molecular adaptor, captured with
        > the *\'*[has input\']{.underline} relation.

    -   **Note that the input (target) of the receptor is NOT its
        > ligand**

-   **BP** \'[part of\']{.underline} the same BP/signal transduction
    > pathway as the ligand

-   **CC:** transmembrane receptors: \'[occurs in]{.underline}\' plasma
    > membrane
    > ([[GO:0005886]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

    -   The causal relation between the MF of the **receptor** and the
        > MF of its **target** is \'[directly positively
        > regulates\']{.underline}*.*

**Example: [[Insulin signaling
model]{.underline}](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A6482692800000931)**

![](media/image5.png){width="6.267716535433071in"
height="1.3888888888888888in"}

 

Small molecule-activated signaling receptor activity
----------------------------------------------------

-   Since small molecules are not annotated in GO, a small molecule
    > ligand does not have a molecular function. Instead, the **ligand**
    > and the **receptor activity** are linked by the causal relation
    > \'[is small molecule activator\']{.underline}*.*

-   The receptor\'s function, input, and contextual relations are the
    > same as for protein ligand-activated receptors. 

-   Note that it is also possible to annotate an inhibitory ligand using
    > the relation \'[is small molecule inhibitor\']{.underline}*.*

-   BP and CC annotations are the same as for protein ligand-activated
    > receptor activity.

**Example: [[Activation of a GPCR by
succinate]{.underline}](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A648d0dc100000022)**

![](media/image1.png){width="5.526042213473316in"
height="2.5371741032370956in"}

 

Special cases
-------------

### 

### Receptor with coreceptor 

This is common in immune receptors. The typical sequence of events is
that the ligand binds the signaling receptor, which signals to the
co-receptor to activate its downstream effector (such as a protein
kinase).

**Example: [[IL2 signaling pathway
(Human)]{.underline}](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel:6205c24300001663)**

In this case, the receptor is activated by an information
biomacromolecule (i.e. a protein). Interleukin-2
([[IL2]{.underline}](https://www.uniprot.org/uniprot/P60568)), a
cytokine, activates its receptor, interleukin-2 receptor A
([[IL2RA]{.underline}](https://www.uniprot.org/uniprot/P01589)). 

IL2RA directly positively regulates (activates)
[[IL2RB]{.underline}](https://www.uniprot.org/uniprot/P14784), which
phosphorylates and positively regulates
[[JAK1]{.underline}](https://www.uniprot.org/uniprotkb/P23458).

The activity unit for a [signaling coreceptor]{.underline} is:

-   **MF:** coreceptor activity
    > ([[GO:0015026]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0015026)*)*

-   **Context:**

    -   The relation between the receptor and its input (target) is the
        > **signaling coreceptor** it regulates, captured with the
        > *\'*[has input]{.underline}\' relation

    -   **Note that the input (target) of the coreceptor is NOT the
        > ligand**

-   **BP** \'[part of]{.underline}\' the BP in which the signaling
    > receptor is involved, usually a child of signal transduction
    > ([[GO:0007165]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0007165))

-   **CC:** transmembrane receptors: \'[occurs in]{.underline}\' plasma
    > membrane
    > ([[GO:0005886]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

    -   The causal relation between the MF of the **receptor** and the
        > MF of its **coreceptor** is \'[directly positively
        > regulates]{.underline}\'*.*

![Diagram Description automatically generated with medium
confidence](media/image2.png){width="3.3854166666666665in"
height="1.1354166666666667in"}

Note: 

-   cytokine activity is\_a receptor ligand activity

-   interleukin-2 receptor activity is\_a signaling receptor activity

### 

### 

 

Form Editor
===========

Protein ligand-activated signaling receptor
-------------------------------------------

### Ligand activity

The activity unit for a [ligand of a signaling receptor]{.underline} is:

-   **MF**: a ligand \'[enables]{.underline}\' receptor ligand activity
    > ([[GO:0048018]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0048018))
    > or a child

-   **Context:**

    -   The relation between a ligand and its target receptor is
        > *\'*[has input\']{.underline}

    -   **BP** \'[part of]{.underline}\' the BP in which this ligand is
        > involved (usually a child of signal transduction
        > ([[GO:0007165]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0007165)))

    -   **CC:**

        -   extracellular ligands: \'[occurs in]{.underline}\'
            > extracellular space
            > ([[GO:0005615]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

        -   membrane-bound ligands: \'[occurs in]{.underline}\' plasma
            > membrane
            > ([[GO:0005886]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

-   The causal relation between the ***ligand* *activity*** and the
    > ***receptor activity*** is\
    > \'[directly positively regulates]{.underline}\'.

**Example: [[Insulin signaling
model]{.underline}](http://noctua.geneontology.org/workbench/noctua-form/?model_id=gomodel%3A6482692800000931)**

![](media/image3.png){width="6.267716535433071in"
height="2.736111111111111in"}

### Signaling receptor activity

The activity unit for a [signaling receptor]{.underline} is:

-   **MF:** The receptor \'[enables]{.underline}\' signaling receptor
    > activity
    > ([[GO:0038023]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0038023)*)*
    > or a child*.* 

-   **Context:**

    -   The input (target) of the receptor is the **effector protein it
        > regulates**, for example a molecular adaptor, captured with
        > the *\'*[has input\']{.underline} relation

    -   **Note that the input (target) of the receptor is NOT its
        > ligand**

-   **BP** in which the signaling receptor is involved, usually a child
    > of signal transduction
    > ([[GO:0007165]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0007165))

-   **CC:** \'[occurs in]{.underline}\' a child of cellular anatomical
    > entity (GO:0110165). For transmembrane receptors, annotate to
    > plasma membrane
    > ([[GO:0005886]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

**Example: [[Insulin signaling
model]{.underline}](http://noctua.geneontology.org/workbench/noctua-form/?model_id=gomodel%3A6482692800000931)**

![](media/image7.png){width="6.267716535433071in" height="3.125in"}

-   The causal relation between the MF of the **receptor** and the MF of
    > its **target** is \'[directly positively
    > regulates\']{.underline}*.*

 

Small molecule-activated signaling receptor activity
----------------------------------------------------

-   In the Form, small molecules are not captured, so the MF for the
    > receptor. Therefore, the MF is \'[enables]{.underline}\' signaling
    > receptor activity
    > ([[GO:0038023]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0038023)*)*
    > or a child*.* 

-   BP and CC annotations are the same as for protein ligand-activated
    > receptor activity.

![](media/image4.png){width="6.267716535433071in"
height="2.7916666666666665in"}

Receptor with coreceptor 
-------------------------

### 

**Example: [[IL2 signaling pathway
(Human)]{.underline}](http://noctua.geneontology.org/workbench/noctua-form/?model_id=gomodel%3A6205c24300001663)**

In this case, the receptor, interleukin-2 receptor A
([[IL2RA]{.underline}](https://www.uniprot.org/uniprot/P01589)), is
activated by a protein ligand, interleukin-2
([[IL2]{.underline}](https://www.uniprot.org/uniprot/P60568)). IL2RA
directly positively regulates (activates) the coreceptor
[[IL2RB]{.underline}](https://www.uniprot.org/uniprot/P14784), which
phosphorylates and positively regulates
[[JAK1]{.underline}](https://www.uniprot.org/uniprotkb/P23458).

The activity unit for a [signaling coreceptor]{.underline} is:

-   **MF:** The coreceptor \'[enables]{.underline}\' coreceptor activity
    > ([[GO:0015026]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0015026)*)*
    > or a child*.* 

-   **Context:**

    -   The input (target) of the coreceptor is the **signaling
        > receptor** it regulates, captured with the *\'*[has
        > input]{.underline}\' relation

    -   **Note that the input (target) of the coreceptor is NOT the
        > ligand**

-   **BP** \'[part of]{.underline}\' the BP in which the signaling
    > receptor is involved, usually a child of signal transduction
    > ([[GO:0007165]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0007165))

-   **CC:** transmembrane receptors: \'[occurs in]{.underline}\' plasma
    > membrane
    > ([[GO:0005886]{.underline}](https://www.ebi.ac.uk/QuickGO/term/GO:0005886))

![](media/image6.png){width="6.267716535433071in"
height="2.3194444444444446in"}

Note: 

-   cytokine activity is\_a receptor ligand activity

-   interleukin-2 receptor activity is\_a signaling receptor activity

 

Differences between GO-CAM and standard annotation of a signaling receptor and its ligand
-----------------------------------------------------------------------------------------

In standard annotation (captured with the Noctua Form or Protein2GO),
relations between molecular functions are not captured, so there is no
relation between the ligand activity and the signaling receptor
activity, nor is there a relation between the signaling receptor
activity and the activity of its target. Likewise for receptor activity
and coreceptor activity, there is no relation between these activities
captured in standard annotations.

Review information
==================

Review date: 2023-07-20

Reviewed by: Cristina Casals, Pascale Gaudet, Patrick Masson
