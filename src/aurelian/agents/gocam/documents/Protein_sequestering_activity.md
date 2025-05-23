# Guidelines for annotating molecular sequestering activity

A sequestering activity is defined as the binding to a specific molecule to prevent it from interacting with other partners or to inhibit its localization to the area of the cell or complex where the target is active.

# Pathway Editor

The activity unit for a molecular sequestering activity is:

* **MF**: molecular sequestering activity ([GO:0140313)](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140313). **The most commonly used child is protein sequestering activity (**[**GO:0140311**](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140311)**).**
* **Context:**
  + The relation between the protein that act to sequester and its target is *'*has input'
  + **BP**: 'part of' negative regulation of the BP in which the target protein participates .
  + **CC**: the location where the activity occurs.
  + The causal relation between the **sequestering activity** and the activity of the protein it inhibits is 'directly negatively regulates' because there is a direct interaction between the two proteins.

**Example 1:** [**Sequestering activity of CAV1 negatively regulates TLR4 signaling**](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A645d887900001414)

![A screenshot of a computer

Description automatically generated with medium confidence](data:image/png;base64...)

**Example 2:** [**Trans-negative regulation of Sars-CoV-2 viral entry into host cell by LRRC15.**](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A63f809ec00000027)

**![](data:image/png;base64...)**

#

# Form Editor

The activity unit for sequestering activity is:

* **MF**: molecular sequestering activity ([GO:0140313](https://www.ebi.ac.uk/QuickGO/term/GO%3A0140313)) or a child
* **Context:**
  + The relation between the protein that act to sequester and its target receptor is *'*has input'
  + **BP**: negative regulation of the BP in which the regulated protein participates
  + **CC**: the location where the activity occurs.

**Example 1:** [**Sequestering activity of CAV1 negatively regulates TLR4 signaling**](http://noctua.geneontology.org/workbench/noctua-form/?model_id=gomodel%3A645d887900001414)

![](data:image/png;base64...)

# Differences between GO-CAM and standard annotation of a sequestering activity

In standard annotation (captured with the Noctua Form or Protein2GO), relations between molecular functions are not captured, so there is no relation between the sequestering activity and the activity of the protein being sequestered.

# Review information

Review date: 2023-07-25

Reviewed by: Cristina Casals, Pascale Gaudet, Patrick Masson
