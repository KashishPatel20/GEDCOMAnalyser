import itertools

from pathlib import Path
from prettytable import PrettyTable
from datetime import datetime

class Individual:
    def __init__(self, id: str):
        self.IId: str = id
        self.IName: str = "NA"
        self.IGen: str = "NA"
        self.IBirth: datetime = None
        self.IDeath: datetime = "NA"
        self.IChild: str = "NA"
        self.ISpouse: str = "NA"

    def is_alive(self) -> bool:
        return (self.IDeath is not None)
    
    def get_age(self) -> int:
        if self.is_alive(): enddate = datetime.now()
        else: enddate = self.IDeath

        age = enddate.year - self.IBirth.year
        if enddate.month < self.IBirth.month: age -= 1  # Birth month had not yet come
        elif enddate.month == self.IBirth.month and enddate.day < self.IBirth.day: age -= 1  # Bith day has not yet come

        return age

class Family:
    def __init__(self, id: str):
        self.FId: str = id
        self.FMar: datetime = "NA"
        self.FDiv: datetime = "NA"
        self.FHusbId: str = "NA"
        self.FWifeId: str = "NA"
        self.FChildIds = []

# No marriage to descendants
def run_US17(families: dict[Family], output_file):
    key_pairs = itertools.combinations(families.keys(), 2)
    for key1, key2 in key_pairs:
        fam1: Family = families[key1]
        fam2: Family = families[key2]

        if fam1.FHusbId == fam2.FHusbId:
            if fam1.FWifeId in fam2.FChildIds:
                print(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married daughter {fam1.FWifeId}")
                output_file.write(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married daughter {fam1.FWifeId}\n")
            elif fam2.FWifeId in fam1.FChildIds:
                print(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married daughter {fam2.FWifeId}")
                output_file.write(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married daughter {fam2.FWifeId}\n")
        if fam1.FWifeId == fam2.FWifeId:
            if fam1.FHusbId in fam2.FChildIds:
                print(f"ERROR: FAMILY: US17: Individual {fam1.FWifeId} married son {fam1.FHusbId}")
                output_file.write(f"ERROR: FAMILY: US17: Individual {fam1.FWifeId} married son {fam1.FHusbId}\n")
            elif fam2.FHusbId in fam1.FChildIds:
                print(f"ERROR: FAMILY: US17: Individual {fam1.FWifeId} married son {fam2.FHusbId}")
                output_file.write(f"ERROR: FAMILY: US17: Individual {fam1.FWifeId} married son {fam2.FHusbId}\n")

# No marriage to siblings
def run_US18(families: dict[Family], output_file):
    key_pairs = itertools.combinations(families.keys(), 2)
    for key1, key2 in key_pairs:
        fam1: Family = families[key1]
        fam2: Family = families[key2]

        if fam1.FHusbId in fam2.FChildIds and fam1.FWifeId in fam2.FChildIds:
            print(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married sister {fam1.FWifeId}")
            output_file.write(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married sister {fam1.FWifeId}\n")
            
        elif fam2.FHusbId in fam1.FChildIds and fam2.FWifeId in fam1.FChildIds:
            print(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married sister {fam1.FWifeId}")
            output_file.write(f"ERROR: FAMILY: US17: Individual {fam1.FHusbId} married sister {fam1.FWifeId}\n")
            
# Dates before current date
def run_US01(individuals: dict[Individual], families: dict[Family], output_file):
    today = datetime.now()
    for IKey in individuals:
        indiv: Individual = individuals[IKey] 
        if(indiv.IBirth > today):
            print(f"ERROR: INDIVIDUAL: US01: Individual {indiv.IId} has Birth Date {indiv.IBirth} AFTER Current Date {today}")
            output_file.write(f"ERROR: INDIVIDUAL: US01: Individual {indiv.IId} has Birth Date {indiv.IBirth} AFTER Current Date {today}\n")
        if(indiv.IDeath != 'NA' and indiv.IDeath > today):
            print(f"ERROR: INDIVIDUAL: US01: Individual {indiv.IId} has Death Date {indiv.IDeath} AFTER Current Date {today}")
            output_file.write(f"ERROR: INDIVIDUAL: US01: Individual {indiv.IId} has Death Date {indiv.IDeath} AFTER Current Date {today}\n")
            
    for FKey in families:
        fam: Family = families[FKey]
        if (fam.FMar != 'NA' and fam.FMar > today):
            print(f"ERROR: FAMILY: US01: Family {fam.FId} has Marriage Date {fam.FMar} AFTER Current Date {today}")
            output_file.write(f"ERROR: FAMILY: US01: Family {fam.FId} has Marriage Date {fam.FMar} AFTER Current Date {today}\n")
        if (fam.FDiv != 'NA' and fam.FDiv > today):
            print(f"ERROR: FAMILY: US01: Family {fam.FId} has Divorce Date {fam.FMar} AFTER Current Date {today}")
            output_file.write(f"ERROR: FAMILY: US01: Family {fam.FId} has Divorce Date {fam.FMar} AFTER Current Date {today}\n")

# Birth before marriage
def run_US02(individuals: dict[Individual], families: dict[Family], output_file):
    for IKey in individuals:
        indiv: Individual = individuals[IKey]
        if(indiv.ISpouse != 'NA'):
            for FKey in families:
                fam: Family = families[FKey]
                if(indiv.IId == fam.FHusbId or indiv.IId == fam.FWifeId):
                    if(indiv.IBirth > fam.FMar):
                        print(f"ERROR: US02: Individual {indiv.IId} has Birth Date {indiv.IBirth} AFTER Marriage Date {fam.FMar}")
                        output_file.write(f"ERROR: US02: Individual {indiv.IId} has Birth Date {indiv.IBirth} AFTER Marriage Date {fam.FMar}\n")


# Add completed user stories here to implement into the main running code
def run_all_user_stories(individuals: dict[Individual], families: dict[Family], output_file):
    run_US01(individuals, families, output_file)
    run_US02(individuals, families, output_file)
    run_US17(families, output_file)
    run_US18(families, output_file)


HANDLED_TAGS = ['INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE']
SPECIAL_TAGS = ['INDI', 'FAM']

# Parse out the tag and content from each line
def parse_line(line: str):
    split_content = line.split()

    if len(split_content) >= 3 and split_content[2] in SPECIAL_TAGS:  # Special line for INDI or FAM
        tag = split_content[2]
        content = split_content[1]
    elif len(split_content) >= 2 and split_content[1] in HANDLED_TAGS:  # Regular accepted line tag
        tag = split_content[1]
        content = ' '.join(split_content[2:])
    else: return None  # Line tag is not accepted

    return (tag, content)

# Parse data from GEDCOM file
def parse_GEDCOM():
    individuals = {}
    families = {}

    path = Path(__file__).with_name('babelman_GEDCOM.ged')
    with path.open('r') as file:
        individual = None
        family = None

        lines = file.readlines()
        index = 0
        while index < len(lines):
            line = lines[index].rstrip()
            
            data = parse_line(line)
            if data is None: 
                index += 1
                continue

            tag, content = data

            # Handle each accepted tag
            if tag == 'INDI':
                if individual is not None: individuals[individual.IId] = individual
                id = content[1:-1]
                individual = Individual(id)
            elif tag == 'FAM':
                if family is not None: families[family.FId] = family
                id = content[1:-1]
                family = Family(id)
            elif tag == 'NAME':
                individual.IName = content
            elif tag == 'SEX':
                individual.IGen = content
            elif tag == 'BIRT':
                index += 1
                line = lines[index].rstrip()
                data = parse_line(line)
                if data is None or not data[0] == 'DATE':
                    index += 1
                    continue
                date = datetime.strptime(data[1], "%d %b %Y")
                individual.IBirth = date
            elif tag == 'DEAT':
                index += 1
                line = lines[index].rstrip()
                data = parse_line(line)
                if data is None or not data[0] == 'DATE':
                    index += 1
                    continue
                date = datetime.strptime(data[1], "%d %b %Y")
                individual.IDeath = date
            elif tag == 'FAMC':
                id = content[1:-1]
                individual.IChild = id
            elif tag == 'FAMS':
                id = content[1:-1]
                individual.ISpouse = id
            elif tag == 'MARR':
                index += 1
                line = lines[index].rstrip()
                data = parse_line(line)
                if data is None or not data[0] == 'DATE':
                    index += 1
                    continue
                date = datetime.strptime(data[1], "%d %b %Y")
                family.FMar = date
            elif tag == 'DIV':
                index += 1
                line = lines[index].rstrip()
                data = parse_line(line)
                if data is None or not data[0] == 'DATE':
                    index += 1
                    continue
                date = datetime.strptime(data[1], "%d %b %Y")
                family.FDiv = date
            elif tag == 'HUSB':
                id = content[1:-1]
                family.FHusbId = id
            elif tag == 'WIFE':
                id = content[1:-1]
                family.FWifeId = id
            elif tag == 'CHIL':
                id = content[1:-1]
                family.FChildIds.append(id)

            index += 1

    with open('output_GEDCOM.ged','w') as output_file:
        indivTable = PrettyTable()
        indivTable.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]

        for key in sorted(individuals, key=lambda k: int(k[1:])):
            indiv: Individual = individuals[key]
            indivTable.add_row([indiv.IId, indiv.IName, indiv.IGen, indiv.IBirth.strftime("%Y-%m-%d"), indiv.get_age(), indiv.is_alive(), 
                                indiv.IDeath if indiv.IDeath == 'NA' else indiv.IDeath.strftime("%Y-%m-%d"), indiv.IChild, indiv.ISpouse])
        print(indivTable)
        output_file.write(str(indivTable)+'\n')

        famTable = PrettyTable()
        famTable.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]

        for key in sorted(families, key=lambda k: int(k[1:])):
            fam: Family = families[key]
            husb: Individual = individuals[fam.FHusbId]
            wife: Individual = individuals[fam.FWifeId]
            
            famTable.add_row([fam.FId, fam.FMar.strftime("%Y-%m-%d"), fam.FDiv if fam.FDiv == 'NA' else fam.FDiv.strftime("%Y-%m-%d"), 
                            fam.FHusbId, husb.IName, fam.FWifeId, wife.IName, fam.FChildIds])
        print(famTable)
        output_file.write(str(famTable)+'\n')

        run_all_user_stories(individuals, families, output_file)


parse_GEDCOM()