Guidelines for annotating signaling receptor
activity
Receptor activation by a ligand is represented differently in GO-CAM depending on whether
the ligand is (i) a protein (i. e., encoded by a gene) or (ii) a small molecule.

Pathway Editor
Protein ligand-activated signaling receptor
Ligand
The activity unit for a ligand of a signaling receptor is:
●

MF: a ligand 'enables' receptor ligand activity (GO:0048018) or a child

●

Context:
o
o
o

The relation between a ligand and its target receptor is 'has input'
BP 'part of' the process in which the ligand participates, usually a child of
signal transduction (GO:0007165)
CC:
▪

extracellular ligands: 'occurs in' extracellular space (GO:0005615)

▪

membrane-bound ligands: 'occurs in' plasma membrane
(GO:0005886)

o

The causal relation between the ligand activity and the receptor activity is
'directly positively regulates'.

Signaling receptor
The activity unit for a signaling receptor is:
●

MF: 'enables' signaling receptor activity (GO:0038023) or a child.

●

Context:
o
o

The input (target) of the receptor is the effector protein it regulates, for
example a molecular adaptor, captured with the 'has input' relation.
Note that the input (target) of the receptor is NOT its ligand

●

BP 'part of' the same BP/signal transduction pathway as the ligand

●

CC: transmembrane receptors: 'occurs in' plasma membrane (GO:0005886)

o

The causal relation between the MF of the receptor and the MF of its target
is 'directly positively regulates'.

Example: Insulin signaling model

Small molecule-activated signaling receptor activity
●

Since small molecules are not annotated in GO, a small molecule ligand does not
have a molecular function. Instead, the ligand and the receptor activity are linked
by the causal relation 'is small molecule activator'.

●

The receptor's function, input, and contextual relations are the same as for protein
ligand-activated receptors.

●

Note that it is also possible to annotate an inhibitory ligand using the relation 'is small
molecule inhibitor'.

●

BP and CC annotations are the same as for protein ligand-activated receptor activity.

Example: Activation of a GPCR by succinate

Special cases
Receptor with coreceptor
This is common in immune receptors. The typical sequence of events is that the ligand binds
the signaling receptor, which signals to the co-receptor to activate its downstream effector
(such as a protein kinase).

Example: IL2 signaling pathway (Human)
In this case, the receptor is activated by an information biomacromolecule (i.e. a protein).
Interleukin-2 (IL2), a cytokine, activates its receptor, interleukin-2 receptor A (IL2RA).
IL2RA directly positively regulates (activates) IL2RB, which phosphorylates and positively
regulates JAK1.
The activity unit for a signaling coreceptor is:
●

MF: coreceptor activity (GO:0015026)

●

Context:
o
o

●

The relation between the receptor and its input (target) is the signaling
coreceptor it regulates, captured with the 'has input' relation
Note that the input (target) of the coreceptor is NOT the ligand

BP 'part of' the BP in which the signaling receptor is involved, usually a child of signal
transduction (GO:0007165)

●

CC: transmembrane receptors: 'occurs in' plasma membrane (GO:0005886)
o

The causal relation between the MF of the receptor and the MF of its
coreceptor is 'directly positively regulates'.

Note:
●

cytokine activity is_a receptor ligand activity

●

interleukin-2 receptor activity is_a signaling receptor activity

Form Editor
Protein ligand-activated signaling receptor
Ligand activity
The activity unit for a ligand of a signaling receptor is:
●

MF: a ligand 'enables' receptor ligand activity (GO:0048018) or a child

●

Context:
o
o
o

The relation between a ligand and its target receptor is 'has input'
BP 'part of' the BP in which this ligand is involved (usually a child of signal
transduction (GO:0007165))
CC:
▪

extracellular ligands: 'occurs in' extracellular space (GO:0005615)

▪

membrane-bound ligands: 'occurs in' plasma membrane
(GO:0005886)

●

The causal relation between the ligand activity and the receptor activity is
'directly positively regulates'.

Example: Insulin signaling model

Signaling receptor activity
The activity unit for a signaling receptor is:

●

MF: The receptor 'enables' signaling receptor activity (GO:0038023) or a child.

●

Context:
o
o

●

The input (target) of the receptor is the effector protein it regulates, for
example a molecular adaptor, captured with the 'has input' relation
Note that the input (target) of the receptor is NOT its ligand

BP in which the signaling receptor is involved, usually a child of signal transduction
(GO:0007165)

●

CC: 'occurs in' a child of cellular anatomical entity (GO:0110165). For
transmembrane receptors, annotate to plasma membrane (GO:0005886)

Example: Insulin signaling model

o

The causal relation between the MF of the receptor and the MF of its target
is 'directly positively regulates'.

Small molecule-activated signaling receptor activity
●

In the Form, small molecules are not captured, so the MF for the receptor. Therefore,
the MF is 'enables' signaling receptor activity (GO:0038023) or a child.

●

BP and CC annotations are the same as for protein ligand-activated receptor activity.

Receptor with coreceptor
Example: IL2 signaling pathway (Human)
In this case, the receptor, interleukin-2 receptor A (IL2RA), is activated by a protein ligand,
interleukin-2 (IL2). IL2RA directly positively regulates (activates) the coreceptor IL2RB,
which phosphorylates and positively regulates JAK1.

The activity unit for a signaling coreceptor is:
●

MF: The coreceptor 'enables' coreceptor activity (GO:0015026) or a child.

●

Context:
o
o

●

The input (target) of the coreceptor is the signaling receptor it regulates,
captured with the 'has input' relation
Note that the input (target) of the coreceptor is NOT the ligand

BP 'part of' the BP in which the signaling receptor is involved, usually a child of signal
transduction (GO:0007165)

●

CC: transmembrane receptors: 'occurs in' plasma membrane (GO:0005886)

Note:
●

cytokine activity is_a receptor ligand activity

●

interleukin-2 receptor activity is_a signaling receptor activity

Differences between GO-CAM and standard annotation of a
signaling receptor and its ligand
In standard annotation (captured with the Noctua Form or Protein2GO), relations between
molecular functions are not captured, so there is no relation between the ligand activity and
the signaling receptor activity, nor is there a relation between the signaling receptor activity
and the activity of its target. Likewise for receptor activity and coreceptor activity, there is no
relation between these activities captured in standard annotations.

Review information
Review date: 2023-07-20
Reviewed by: Cristina Casals, Pascale Gaudet, Patrick Masson

