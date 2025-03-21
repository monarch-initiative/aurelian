# Guidelines for annotating molecular adaptor activity

A molecular adaptor activity is the binding activity of a molecule that brings together two or more molecules through a selective, non-covalent, often stoichiometric interaction, permitting those molecules to function in a coordinated way.

# Pathway Editor

The molecular activity unit for a molecular adaptor is:

* **MF**: 'enables' molecular adaptor activity ([GO:0060090](https://www.ebi.ac.uk/QuickGO/term/GO%3A0060090)) or a child
* **Context:**
  + The relation between the adaptor activity and the two (or more) molecules it brings together is 'has input'
  + **BP**: 'part of' the BP in which the adaptor participates
  + **CC**: 'occurs in' the cellular location where the activity takes place.

The relation between the adaptor and the proteins it adapts can be 'directly positively regulates' or 'provides input for', depending if the activity of the adaptor is regulatory.

**Example 1:** [**TYROBP acts as an adaptor between a receptor and a downstream effector**](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A633b013300001197)

SIGLEC1 recognizes and endocytoses virions, which leads to activation of the TYROBP molecular adaptor, which recruits PTPN11. The scaffolding activity of PTPN11 is activated by TYROBP.

![A screenshot of a computer

Description automatically generated with medium confidence](data:image/png;base64...)

**Example 2:** [**An adaptor that brings together an enzyme and its substrate**](http://noctua.geneontology.org/workbench/noctua-visual-pathway-editor/?model_id=gomodel%3A636d9ce800001192)

![](data:image/png;base64...)

In that case, the relation between the adaptor activity and the downstream activity is 'provides input for'.

## Form Editor

* **MF**: 'enables' molecular adaptor activity ([GO:0060090](https://www.ebi.ac.uk/QuickGO/term/GO%3A0060090)) or a child
* **Context:**
  + The relation between the adaptor activity and the two (or more) molecules it brings together is 'has input'
  + **BP**: 'part of' the BP in which the adaptor participates
  + **CC**: 'occurs in' the cellular location where the activity takes place.

![](data:image/png;base64...)

# Differences between GO-CAM and standard annotation of a molecular adaptor activity

In standard annotation (captured with the Noctua Form or Protein2GO), relations between molecular functions are not captured.

#

# Review information

Review date: 2023-07-20

Reviewed by: Cristina Casals, Pascale Gaudet, Patrick Masson
