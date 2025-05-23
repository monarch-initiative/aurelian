# How to annotate complexes in GO-CAM

When complexes are involved in specific activities, several options are available in GO-CAM to represent them.

1. **The subunit that carries the molecular activity is known:**

In that case, the complex is not described and the activity(ies) is represented by the specific protein (s) carrying the activity.

Ex:

![](data:image/x-emf;base64...)

In this example, all the proteins in the E3 ligase complex have a defined and precise activity. Therefore, they are all displayed in the model. In this case, the scaffold activity is usually represented first, *activating subsequent activities from the* complex.

1. **The subunit which carries the molecular activity is not known:**

If the precise subunit carrying the activity is not known, we can use the GO accession for the complex.

Ex: Ragulator complex (GO:0071986): Ragulator is comprised of the membrane anchor subunit LAMTOR1, LAMTOR2, LAMTOR3, LAMTOR4 and LAMTOR5.

![A screenshot of a computer

Description automatically generated](data:image/png;base64...)

In this example LAMTOR1 activity is known (protein-membrane adaptor activity) but the protein that carries the guanyl-nucleotide exchange factor activity is not known, therefore we use the complex ID from GO in this situation.

1. **If the activity is shared by several proteins**

EX: Heterodimeric receptor where both activities are important for activity.
