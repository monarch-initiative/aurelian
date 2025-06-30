"""UBERON anatomy recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class UberonMetadata(Dict[str, Any]):
    """Metadata dictionary for UBERON evaluations."""
    pass


# UBERON evaluation cases from CRAFT corpus - manually curated
striatum = Case(
    name="striatum",
    inputs="The striatum plays a pivotal role in modulating motor activity and higher cognitive function.",
    expected_output={'ontology_id': "UBERON:0002435"},
    metadata=metadata("easy", "anatomy_recognition")
)

brain = Case(
    name="brain",
    inputs="Brain weight and striatal volume correlate strongly in all strains of mice examined.",
    expected_output={'ontology_id': "UBERON:0000955"},
    metadata=metadata("easy", "anatomy_recognition")
)

central_nervous_system = Case(
    name="central_nervous_system", 
    inputs="From a technical point of view the mouse striatum has several advantages that make it an excellent target for complex trait analysis of the mammalian CNS.",
    expected_output={'ontology_id': "UBERON:0001017"},
    metadata=metadata("medium", "anatomy_recognition")
)

head = Case(
    name="head",
    inputs="The neural crest cells migrate extensively throughout the developing embryo, particularly in the head region.",
    expected_output={'ontology_id': "UBERON:0000033"},
    metadata=metadata("easy", "anatomy_recognition")
)

wing = Case(
    name="wing",
    inputs="During wing development, the expression of signaling molecules is tightly regulated.",
    expected_output={'ontology_id': "UBERON:0000023"},
    metadata=metadata("easy", "anatomy_recognition")
)

pituitary_gland = Case(
    name="pituitary_gland",
    inputs="The pituitary gland secretes hormones that regulate various physiological processes.",
    expected_output={'ontology_id': "UBERON:0000007"},
    metadata=metadata("easy", "anatomy_recognition")
)

peripheral_nervous_system = Case(
    name="peripheral_nervous_system",
    inputs="Neurons of the peripheral nervous system regenerate more readily than those in the central nervous system.",
    expected_output={'ontology_id': "UBERON:0000010"},
    metadata=metadata("medium", "anatomy_recognition")
)

lymph_node = Case(
    name="lymph_node",
    inputs="Immune cells aggregate in the lymph node where they encounter antigens.",
    expected_output={'ontology_id': "UBERON:0000029"},
    metadata=metadata("easy", "anatomy_recognition")
)

tendon = Case(
    name="tendon",
    inputs="The tendon connects muscle to bone and transmits force during movement.",
    expected_output={'ontology_id': "UBERON:0000043"},
    metadata=metadata("easy", "anatomy_recognition")
)

organ = Case(
    name="organ",
    inputs="Each organ has a specific function and is composed of multiple tissue types.",
    expected_output={'ontology_id': "UBERON:0000062"},
    metadata=metadata("easy", "anatomy_recognition")
)

blood_vessel = Case(
    name="blood_vessel",
    inputs="The blood vessel network transports nutrients and oxygen throughout the body.",
    expected_output={'ontology_id': "UBERON:0001981"},
    metadata=metadata("easy", "anatomy_recognition")
)

heart = Case(
    name="heart",
    inputs="The heart pumps blood throughout the circulatory system in vertebrates.",
    expected_output={'ontology_id': "UBERON:0000948"},
    metadata=metadata("easy", "anatomy_recognition")
)

kidney = Case(
    name="kidney",
    inputs="The kidney filters waste products from the blood and produces urine.",
    expected_output={'ontology_id': "UBERON:0002113"},
    metadata=metadata("easy", "anatomy_recognition")
)

liver = Case(
    name="liver",
    inputs="The liver performs numerous metabolic functions including detoxification.",
    expected_output={'ontology_id': "UBERON:0002107"},
    metadata=metadata("easy", "anatomy_recognition")
)

lung = Case(
    name="lung",
    inputs="The lung is the primary organ of gas exchange in air-breathing vertebrates.",
    expected_output={'ontology_id': "UBERON:0002048"},
    metadata=metadata("easy", "anatomy_recognition")
)

skeletal_muscle = Case(
    name="skeletal_muscle",
    inputs="Skeletal muscle tissue is responsible for voluntary movement in vertebrates.",
    expected_output={'ontology_id': "UBERON:0001134"},
    metadata=metadata("medium", "anatomy_recognition")
)

bone = Case(
    name="bone",
    inputs="Bone tissue provides structural support and protection for internal organs.",
    expected_output={'ontology_id': "UBERON:0002481"},
    metadata=metadata("easy", "anatomy_recognition")
)

skin = Case(
    name="skin",
    inputs="The skin forms a barrier between the organism and its environment.",
    expected_output={'ontology_id': "UBERON:0002097"},
    metadata=metadata("easy", "anatomy_recognition")
)

eye = Case(
    name="eye",
    inputs="The eye is the primary organ of vision in most vertebrates.",
    expected_output={'ontology_id': "UBERON:0000970"},
    metadata=metadata("easy", "anatomy_recognition")
)

spinal_cord = Case(
    name="spinal_cord",
    inputs="The spinal cord transmits neural signals between the brain and peripheral nervous system.",
    expected_output={'ontology_id': "UBERON:0002240"},
    metadata=metadata("medium", "anatomy_recognition")
)

stomach = Case(
    name="stomach",
    inputs="The stomach secretes acid and enzymes to begin protein digestion.",
    expected_output={'ontology_id': "UBERON:0000945"},
    metadata=metadata("easy", "anatomy_recognition")
)

intestine = Case(
    name="intestine",
    inputs="The intestine is responsible for nutrient absorption and waste processing.",
    expected_output={'ontology_id': "UBERON:0000160"},
    metadata=metadata("easy", "anatomy_recognition")
)

pancreas = Case(
    name="pancreas",
    inputs="The pancreas produces digestive enzymes and hormones like insulin.",
    expected_output={'ontology_id': "UBERON:0001264"},
    metadata=metadata("easy", "anatomy_recognition")
)

thyroid_gland = Case(
    name="thyroid_gland",
    inputs="The thyroid gland regulates metabolism through hormone secretion.",
    expected_output={'ontology_id': "UBERON:0002046"},
    metadata=metadata("easy", "anatomy_recognition")
)

adrenal_gland = Case(
    name="adrenal_gland",
    inputs="The adrenal gland produces stress hormones like cortisol and adrenaline.",
    expected_output={'ontology_id': "UBERON:0002369"},
    metadata=metadata("easy", "anatomy_recognition")
)

cerebellum = Case(
    name="cerebellum",
    inputs="The cerebellum coordinates movement and maintains balance.",
    expected_output={'ontology_id': "UBERON:0002037"},
    metadata=metadata("medium", "anatomy_recognition")
)

cerebral_cortex = Case(
    name="cerebral_cortex",
    inputs="The cerebral cortex is involved in higher-order brain functions.",
    expected_output={'ontology_id': "UBERON:0000956"},
    metadata=metadata("medium", "anatomy_recognition")
)

hippocampus = Case(
    name="hippocampus", 
    inputs="The hippocampus plays important roles in memory formation and spatial navigation.",
    expected_output={'ontology_id': "UBERON:0002421"},
    metadata=metadata("medium", "anatomy_recognition")
)

spleen = Case(
    name="spleen",
    inputs="The spleen filters blood and plays a role in immune function.",
    expected_output={'ontology_id': "UBERON:0002106"},
    metadata=metadata("easy", "anatomy_recognition")
)

ureter = Case(
    name="ureter",
    inputs="The ureter transports urine from the kidney to the bladder.",
    expected_output={'ontology_id': "UBERON:0000056"},
    metadata=metadata("medium", "anatomy_recognition")
)

bladder = Case(
    name="bladder",
    inputs="The bladder stores urine before it is expelled from the body.",
    expected_output={'ontology_id': "UBERON:0001255"},
    metadata=metadata("easy", "anatomy_recognition")
)

uterus = Case(
    name="uterus",
    inputs="The uterus houses and nourishes the developing fetus during pregnancy.",
    expected_output={'ontology_id': "UBERON:0000995"},
    metadata=metadata("easy", "anatomy_recognition")
)

ovary = Case(
    name="ovary",
    inputs="The ovary produces eggs and female sex hormones.",
    expected_output={'ontology_id': "UBERON:0000992"},
    metadata=metadata("easy", "anatomy_recognition")
)

testis = Case(
    name="testis",
    inputs="The testis produces sperm and male sex hormones.",
    expected_output={'ontology_id': "UBERON:0000473"},
    metadata=metadata("easy", "anatomy_recognition")
)

mammary_gland = Case(
    name="mammary_gland",
    inputs="The mammary gland produces milk for nourishing offspring in mammals.",
    expected_output={'ontology_id': "UBERON:0001911"},
    metadata=metadata("easy", "anatomy_recognition")
)

tooth = Case(
    name="tooth",
    inputs="The tooth structure is adapted for cutting and grinding food.",
    expected_output={'ontology_id': "UBERON:0001091"},
    metadata=metadata("easy", "anatomy_recognition")
)

tongue = Case(
    name="tongue",
    inputs="The tongue contains taste buds and assists in food manipulation.",
    expected_output={'ontology_id': "UBERON:0001723"},
    metadata=metadata("easy", "anatomy_recognition")
)

ear = Case(
    name="ear",
    inputs="The ear detects sound waves and maintains balance.",
    expected_output={'ontology_id': "UBERON:0001690"},
    metadata=metadata("easy", "anatomy_recognition")
)

nose = Case(
    name="nose",
    inputs="The nose is the primary organ for detecting airborne chemicals.",
    expected_output={'ontology_id': "UBERON:0000004"},
    metadata=metadata("easy", "anatomy_recognition")
)

limb = Case(
    name="limb",
    inputs="Each limb contains multiple joints that allow for complex movement.",
    expected_output={'ontology_id': "UBERON:0002101"},
    metadata=metadata("easy", "anatomy_recognition")
)

forelimb = Case(
    name="forelimb",
    inputs="The forelimb structure varies considerably among different vertebrate species.",
    expected_output={'ontology_id': "UBERON:0002102"},
    metadata=metadata("medium", "anatomy_recognition")
)

hindlimb = Case(
    name="hindlimb",
    inputs="The hindlimb is specialized for locomotion in terrestrial vertebrates.",
    expected_output={'ontology_id': "UBERON:0002103"},
    metadata=metadata("medium", "anatomy_recognition")
)

tail = Case(
    name="tail",
    inputs="The tail serves various functions including balance and communication.",
    expected_output={'ontology_id': "UBERON:0002415"},
    metadata=metadata("easy", "anatomy_recognition")
)

vertebral_column = Case(
    name="vertebral_column",
    inputs="The vertebral column protects the spinal cord and provides structural support.",
    expected_output={'ontology_id': "UBERON:0001130"},
    metadata=metadata("medium", "anatomy_recognition")
)

rib = Case(
    name="rib",
    inputs="The rib cage protects vital organs in the thoracic cavity.",
    expected_output={'ontology_id': "UBERON:0002228"},
    metadata=metadata("easy", "anatomy_recognition")
)

skull = Case(
    name="skull",
    inputs="The skull protects the brain and houses the sensory organs.",
    expected_output={'ontology_id': "UBERON:0003129"},
    metadata=metadata("easy", "anatomy_recognition")
)

jaw = Case(
    name="jaw",
    inputs="The jaw provides mechanical advantage for food processing.",
    expected_output={'ontology_id': "UBERON:0004742"},
    metadata=metadata("easy", "anatomy_recognition")
)

cartilage = Case(
    name="cartilage",
    inputs="Cartilage provides flexible support in joints and other structures.",
    expected_output={'ontology_id': "UBERON:0002418"},
    metadata=metadata("medium", "anatomy_recognition")
)

joint = Case(
    name="joint",
    inputs="The joint allows movement between connected bones.",
    expected_output={'ontology_id': "UBERON:0000982"},
    metadata=metadata("easy", "anatomy_recognition")
)

blood = Case(
    name="blood",
    inputs="Blood transports oxygen, nutrients, and waste products throughout the body.",
    expected_output={'ontology_id': "UBERON:0000178"},
    metadata=metadata("easy", "anatomy_recognition")
)

lymph = Case(
    name="lymph",
    inputs="Lymph fluid returns proteins and excess fluid to the bloodstream.",
    expected_output={'ontology_id': "UBERON:0002391"},
    metadata=metadata("medium", "anatomy_recognition")
)

nerve = Case(
    name="nerve",
    inputs="The nerve bundle transmits electrical signals between different body regions.",
    expected_output={'ontology_id': "UBERON:0001021"},
    metadata=metadata("medium", "anatomy_recognition")
)

ganglion = Case(
    name="ganglion",
    inputs="The ganglion contains clusters of nerve cell bodies outside the central nervous system.",
    expected_output={'ontology_id': "UBERON:0000045"},
    metadata=metadata("hard", "anatomy_recognition")
)

# Additional anatomical structures
artery = Case(
    name="artery",
    inputs="The artery carries oxygenated blood away from the heart to body tissues.",
    expected_output={'ontology_id': "UBERON:0001637"},
    metadata=metadata("easy", "anatomy_recognition")
)

vein = Case(
    name="vein",
    inputs="The vein returns deoxygenated blood from tissues back to the heart.",
    expected_output={'ontology_id': "UBERON:0001638"},
    metadata=metadata("easy", "anatomy_recognition")
)

capillary = Case(
    name="capillary",
    inputs="Gas and nutrient exchange occurs across the thin walls of capillaries.",
    expected_output={'ontology_id': "UBERON:0001982"},
    metadata=metadata("medium", "anatomy_recognition")
)

trachea = Case(
    name="trachea",
    inputs="The trachea conducts air from the larynx to the bronchi.",
    expected_output={'ontology_id': "UBERON:0003126"},
    metadata=metadata("easy", "anatomy_recognition")
)

bronchus = Case(
    name="bronchus",
    inputs="Each bronchus branches from the trachea to deliver air to a lung.",
    expected_output={'ontology_id': "UBERON:0002185"},
    metadata=metadata("medium", "anatomy_recognition")
)

alveolus = Case(
    name="alveolus",
    inputs="Gas exchange between air and blood occurs in the alveolus.",
    expected_output={'ontology_id': "UBERON:0003215"},
    metadata=metadata("medium", "anatomy_recognition")
)

esophagus = Case(
    name="esophagus",
    inputs="The esophagus transports food from the pharynx to the stomach.",
    expected_output={'ontology_id': "UBERON:0001043"},
    metadata=metadata("easy", "anatomy_recognition")
)

pharynx = Case(
    name="pharynx",
    inputs="The pharynx serves as a passageway for both digestive and respiratory systems.",
    expected_output={'ontology_id': "UBERON:0001729"},
    metadata=metadata("medium", "anatomy_recognition")
)

larynx = Case(
    name="larynx",
    inputs="The larynx contains the vocal cords and regulates airflow to the lungs.",
    expected_output={'ontology_id': "UBERON:0001737"},
    metadata=metadata("medium", "anatomy_recognition")
)

diaphragm = Case(
    name="diaphragm",
    inputs="The diaphragm is the primary muscle of respiration in mammals.",
    expected_output={'ontology_id': "UBERON:0001103"},
    metadata=metadata("medium", "anatomy_recognition")
)

appendix = Case(
    name="appendix",
    inputs="The appendix is a small pouch connected to the large intestine.",
    expected_output={'ontology_id': "UBERON:0001154"},
    metadata=metadata("easy", "anatomy_recognition")
)

gallbladder = Case(
    name="gallbladder",
    inputs="The gallbladder stores and concentrates bile produced by the liver.",
    expected_output={'ontology_id': "UBERON:0002110"},
    metadata=metadata("easy", "anatomy_recognition")
)

bile_duct = Case(
    name="bile_duct",
    inputs="The bile duct transports bile from the liver to the small intestine.",
    expected_output={'ontology_id': "UBERON:0002394"},
    metadata=metadata("medium", "anatomy_recognition")
)

salivary_gland = Case(
    name="salivary_gland",
    inputs="The salivary gland produces saliva to aid in digestion and oral hygiene.",
    expected_output={'ontology_id': "UBERON:0001044"},
    metadata=metadata("easy", "anatomy_recognition")
)

thymus = Case(
    name="thymus",
    inputs="The thymus is where T lymphocytes mature during development.",
    expected_output={'ontology_id': "UBERON:0002370"},
    metadata=metadata("medium", "anatomy_recognition")
)

bone_marrow = Case(
    name="bone_marrow",
    inputs="Bone marrow is the primary site of blood cell production in adults.",
    expected_output={'ontology_id': "UBERON:0002371"},
    metadata=metadata("medium", "anatomy_recognition")
)

# Tissue types
epithelium = Case(
    name="epithelium",
    inputs="Epithelium forms protective barriers and secretory surfaces throughout the body.",
    expected_output={'ontology_id': "UBERON:0000483"},
    metadata=metadata("medium", "anatomy_recognition")
)

connective_tissue = Case(
    name="connective_tissue",
    inputs="Connective tissue provides structural support and connects different body parts.",
    expected_output={'ontology_id': "UBERON:0002384"},
    metadata=metadata("medium", "anatomy_recognition")
)

muscle_tissue = Case(
    name="muscle_tissue",
    inputs="Muscle tissue generates force and produces movement through contraction.",
    expected_output={'ontology_id': "UBERON:0002385"},
    metadata=metadata("easy", "anatomy_recognition")
)

nervous_tissue = Case(
    name="nervous_tissue",
    inputs="Nervous tissue processes and transmits information throughout the body.",
    expected_output={'ontology_id': "UBERON:0003714"},
    metadata=metadata("medium", "anatomy_recognition")
)

# Body cavities and regions
thoracic_cavity = Case(
    name="thoracic_cavity",
    inputs="The thoracic cavity houses the heart, lungs, and other vital structures.",
    expected_output={'ontology_id': "UBERON:0002224"},
    metadata=metadata("medium", "anatomy_recognition")
)

abdominal_cavity = Case(
    name="abdominal_cavity",
    inputs="The abdominal cavity contains most of the digestive organs.",
    expected_output={'ontology_id': "UBERON:0000464"},
    metadata=metadata("medium", "anatomy_recognition")
)

pelvic_cavity = Case(
    name="pelvic_cavity",
    inputs="The pelvic cavity contains reproductive and excretory organs.",
    expected_output={'ontology_id': "UBERON:0002355"},
    metadata=metadata("medium", "anatomy_recognition")
)

thorax = Case(
    name="thorax",
    inputs="The thorax includes the chest wall and the organs it contains.",
    expected_output={'ontology_id': "UBERON:0000915"},
    metadata=metadata("easy", "anatomy_recognition")
)

abdomen = Case(
    name="abdomen",
    inputs="The abdomen contains digestive organs between the thorax and pelvis.",
    expected_output={'ontology_id': "UBERON:0000916"},
    metadata=metadata("easy", "anatomy_recognition")
)

pelvis = Case(
    name="pelvis",
    inputs="The pelvis forms the lower part of the trunk in vertebrates.",
    expected_output={'ontology_id': "UBERON:0002355"},
    metadata=metadata("easy", "anatomy_recognition")
)

neck = Case(
    name="neck",
    inputs="The neck connects the head to the torso and contains vital structures.",
    expected_output={'ontology_id': "UBERON:0000974"},
    metadata=metadata("easy", "anatomy_recognition")
)

back = Case(
    name="back",
    inputs="The back provides structural support for the entire vertebrate body.",
    expected_output={'ontology_id': "UBERON:0001137"},
    metadata=metadata("easy", "anatomy_recognition")
)

trunk = Case(
    name="trunk",
    inputs="The trunk contains most of the body's vital organs and systems.",
    expected_output={'ontology_id': "UBERON:0002100"},
    metadata=metadata("easy", "anatomy_recognition")
)

# Embryonic structures
neural_tube = Case(
    name="neural_tube",
    inputs="The neural tube gives rise to the central nervous system during development.",
    expected_output={'ontology_id': "UBERON:0001049"},
    metadata=metadata("hard", "anatomy_recognition")
)

notochord = Case(
    name="notochord",
    inputs="The notochord provides structural support in early vertebrate development.",
    expected_output={'ontology_id': "UBERON:0002328"},
    metadata=metadata("hard", "anatomy_recognition")
)

neural_crest = Case(
    name="neural_crest",
    inputs="Neural crest cells migrate extensively and form diverse structures.",
    expected_output={'ontology_id': "UBERON:0002342"},
    metadata=metadata("hard", "anatomy_recognition")
)

somite = Case(
    name="somite",
    inputs="Somites give rise to vertebrae, ribs, and skeletal muscle.",
    expected_output={'ontology_id': "UBERON:0002329"},
    metadata=metadata("hard", "anatomy_recognition")
)

# Sense organs and specialized structures
retina = Case(
    name="retina",
    inputs="The retina contains photoreceptors that detect light and initiate vision.",
    expected_output={'ontology_id': "UBERON:0000966"},
    metadata=metadata("medium", "anatomy_recognition")
)

cornea = Case(
    name="cornea",
    inputs="The cornea is the transparent front layer of the eye.",
    expected_output={'ontology_id': "UBERON:0000964"},
    metadata=metadata("medium", "anatomy_recognition")
)

lens = Case(
    name="lens",
    inputs="The lens focuses light onto the retina for clear vision.",
    expected_output={'ontology_id': "UBERON:0000965"},
    metadata=metadata("medium", "anatomy_recognition")
)

iris = Case(
    name="iris",
    inputs="The iris controls the amount of light entering the eye.",
    expected_output={'ontology_id': "UBERON:0001015"},
    metadata=metadata("medium", "anatomy_recognition")
)

cochlea = Case(
    name="cochlea",
    inputs="The cochlea converts sound vibrations into neural signals.",
    expected_output={'ontology_id': "UBERON:0001844"},
    metadata=metadata("hard", "anatomy_recognition")
)

semicircular_canal = Case(
    name="semicircular_canal",
    inputs="The semicircular canals detect rotational movements of the head.",
    expected_output={'ontology_id': "UBERON:0001840"},
    metadata=metadata("hard", "anatomy_recognition")
)

# Glands and secretory structures
sebaceous_gland = Case(
    name="sebaceous_gland",
    inputs="Sebaceous glands secrete oils that lubricate skin and hair.",
    expected_output={'ontology_id': "UBERON:0001820"},
    metadata=metadata("medium", "anatomy_recognition")
)

sweat_gland = Case(
    name="sweat_gland",
    inputs="Sweat glands help regulate body temperature through evaporation.",
    expected_output={'ontology_id': "UBERON:0001820"},
    metadata=metadata("medium", "anatomy_recognition")
)

hair_follicle = Case(
    name="hair_follicle",
    inputs="The hair follicle produces and anchors each strand of hair.",
    expected_output={'ontology_id': "UBERON:0002073"},
    metadata=metadata("medium", "anatomy_recognition")
)

feather_follicle = Case(
    name="feather_follicle",
    inputs="The feather follicle produces the complex branched structure of feathers.",
    expected_output={'ontology_id': "UBERON:0010698"},
    metadata=metadata("hard", "anatomy_recognition")
)

# Vascular and lymphatic system
lymphatic_vessel = Case(
    name="lymphatic_vessel",
    inputs="Lymphatic vessels transport lymph fluid throughout the body.",
    expected_output={'ontology_id': "UBERON:0001473"},
    metadata=metadata("medium", "anatomy_recognition")
)

aorta = Case(
    name="aorta",
    inputs="The aorta is the main artery that carries blood from the heart.",
    expected_output={'ontology_id': "UBERON:0000947"},
    metadata=metadata("medium", "anatomy_recognition")
)

ventricle = Case(
    name="ventricle",
    inputs="The heart ventricle pumps blood out to the body or lungs.",
    expected_output={'ontology_id': "UBERON:0002082"},
    metadata=metadata("medium", "anatomy_recognition")
)

atrium = Case(
    name="atrium",
    inputs="The heart atrium receives blood returning from circulation.",
    expected_output={'ontology_id': "UBERON:0002081"},
    metadata=metadata("medium", "anatomy_recognition")
)

valve = Case(
    name="valve",
    inputs="Heart valves prevent backflow of blood during circulation.",
    expected_output={'ontology_id': "UBERON:0003978"},
    metadata=metadata("medium", "anatomy_recognition")
)


def create_uberon_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create UBERON anatomy recognition evaluation dataset from CRAFT corpus."""
    cases = [
        striatum, brain, central_nervous_system, head, wing, 
        pituitary_gland, peripheral_nervous_system, lymph_node, tendon, organ
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )