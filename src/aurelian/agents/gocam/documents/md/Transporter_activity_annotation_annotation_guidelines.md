Guidelines for annotating transporter activity
Pathway Editor
The activity unit for a transmembrane transporter is:
● MF: 'enables' a child of transmembrane transporter activity GO:0022857
● Context:
○ The movement of the small molecule substrate is represented by:
■ small molecule (ChEBI) + ‘input of’ + the start location of the small
molecule, captured with the relation 'located in'
■ the transporter activity + ‘has output’ the small molecule (ChEBI) + the
end location of the small molecule, captured with the relation 'located in'
○ BP 'part of' the BP in which this transporter activity participates
○ CC 'occurs in' a child of membrane (GO:0016020), e. g.: lysosomal membrane
(GO:0005765).

Example: SLC17A9 transports ATP to the lysosomal lumen

Form Editor
The activity unit for a transmembrane transporter is:
● MF: a child of transmembrane transporter activity GO:0022857
● Context: The movement of the small molecule substrate is represented by:
○ 'has input’ the small molecule (ChEBI)
○ BP 'part of' the BP in which this transporter activity participates
○ CC 'occurs in' a child of membrane (GO:0016020), e. g.: lysosomal membrane
(GO:0005765)

Example: SLC17A9 transports ATP to the lysosomal lumen

Differences between GO-CAM and standard
annotation of a transmembrane transporter activity
In standard annotation (captured with the Noctua Form or Protein2GO), the localization of the
molecule is not captured; neither is the output of the transporter, since that output relates to the
localization of the molecule transported.

Review information
Review date: 2023-07-20
Reviewed by:Cristina Casals, Pascale Gaudet, Patrick Masson

