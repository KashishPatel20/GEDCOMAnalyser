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


individuals = {}
families = {}

# Parse data from GEDCOM file
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

indivTable = PrettyTable()
indivTable.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]

for key in sorted(individuals, key=lambda k: int(k[1:])):
    indiv: Individual = individuals[key]
    indivTable.add_row([indiv.IId, indiv.IName, indiv.IGen, indiv.IBirth.strftime("%Y-%m-%d"), indiv.get_age(), indiv.is_alive(), 
                        indiv.IDeath if indiv.IDeath == 'NA' else indiv.IDeath.strftime("%Y-%m-%d"), indiv.IChild, indiv.ISpouse])
print(indivTable)

famTable = PrettyTable()
famTable.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]

for key in sorted(families, key=lambda k: int(k[1:])):
    fam: Family = families[key]
    husb: Individual = individuals[fam.FHusbId]
    wife: Individual = individuals[fam.FWifeId]
    
    famTable.add_row([fam.FId, fam.FMar.strftime("%Y-%m-%d"), fam.FDiv if fam.FDiv == 'NA' else fam.FDiv.strftime("%Y-%m-%d"), 
                      fam.FHusbId, husb.IName, fam.FWifeId, wife.IName, fam.FChildIds])
print(famTable)