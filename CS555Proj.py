import itertools

from pathlib import Path
from prettytable import PrettyTable
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

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
        return self.IDeath == 'NA'
        
    def get_last_name(self):
        return self.IName.split()[-1]
        
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
        for FKey in families:
            fam: Family = families[FKey]
            if(indiv.IId in fam.FChildIds):
                if(indiv.IBirth < fam.FMar):
                    print(f"ANOMALY: US02: Individual {indiv.IId} has Birth Date {indiv.IBirth} BEFORE Marriage Date {fam.FMar}")
                    output_file.write(f"ANOMALY: US02: Individual {indiv.IId} has Birth Date {indiv.IBirth} BEFORE Marriage Date {fam.FMar}\n")

# Birth before death
def run_US03(individuals: dict[Individual], output_file):
    for IKey in individuals:
        indiv: Individual = individuals[IKey]
        if(indiv.IDeath != 'NA' and indiv.IBirth > indiv.IDeath):
            print(f"ERROR: INDIVIDUAL: US03: Individual {indiv.IId} has Birth Date {indiv.IBirth} AFTER Death Date {indiv.IDeath}")
            output_file.write(f"ERROR: INDIVIDUAL: US03: Individual {indiv.IId} has Birth Date {indiv.IBirth} AFTER Death Date {indiv.IBirth}\n")

# Marriage before divorce, divorce after marriage
def run_US04(families: dict[Family], output_file):
    for FKey in families:
        fam: Family = families[FKey]
        if(fam.FDiv != 'NA' and fam.FMar > fam.FDiv):
            print(f"ERROR: FAMILY: US04: Family {fam.FId} has Marriage Date {fam.FMar} AFTER Divorce Date {fam.FDiv}")
            output_file.write(f"ERROR: FAMILY: US04: Family {fam.FId} has Marriage Date {fam.FMar} AFTER Divorce Date {fam.FDiv}\n") 
    
# Marriage before death    
def run_US05(individuals: dict[Individual], families: dict[Family], output_file):
    for IKey in individuals:
        indiv: Individual = individuals[IKey]
        if(indiv.ISpouse != 'NA'):
            for FKey in families:
                fam: Family = families[FKey]
                if(indiv.IId == fam.FHusbId or indiv.IId == fam.FWifeId):
                    if(indiv.IDeath != 'NA' and fam.FMar > indiv.IDeath):
                        print(f"ANOMALY: US05: Individual {indiv.IId} has Marriage Date {fam.FMar} AFTER Death Date {indiv.IDeath}")
                        output_file.write(f"ANOMALY: US05: Individual {indiv.IId} has Marriage Date {fam.FMar} AFTER Death Date {indiv.IDeath}\n")

# Divorce before death
def run_US06(individuals: dict[Individual], families: dict[Family], output_file):
    for FKey in families:
        fam: Family = families[FKey]
        husbDeath = individuals[fam.FHusbId].IDeath
        wifeDeath = individuals[fam.FWifeId].IDeath
        if(husbDeath != 'NA' and wifeDeath != 'NA'):
            if(fam.FDiv > husbDeath):
                print(f"ERROR: US06: Family {fam.FId} has Divorce Date {fam.FDiv} AFTER Death Date {husbDeath} of Husband")
                output_file.write(f"ERROR: US06: Family {fam.FId} has Divorce Date {fam.FDiv} AFTER Death Date {husbDeath} of Husband\n")
            elif(fam.FDiv > wifeDeath):
                print(f"ERROR: US06: Family {fam.FId} has Divorce Date {fam.FDiv} AFTER Death Date {wifeDeath} of Wife")
                output_file.write(f"ERROR: US06: Family {fam.FId} has Divorce Date {fam.FDiv} AFTER Death Date {wifeDeath} of Wife\n")

#Less than 150 years old     
def run_US07(individuals: dict[Individual], output_file):
    for IKey in individuals:
        indiv: Individual = individuals[IKey]
        plus = indiv.IBirth + timedelta(days=150*365) #approx 150yrs
        plusShift = (abs((plus - datetime.today()).days)/365)
        if(plusShift > 150): #current date < 150 years after birth birth date
            print(f"ANOMALY: US07: Individual {indiv.IId} has an age of {plusShift}")
            output_file.write(f"ANOMALY: US07: Individual {indiv.IId} has an age of {plusShift}\n")
        else: 
            if(indiv.IDeath != 'NA'):
                yrsAlive = (abs((indiv.IDeath - indiv.IBirth).days)/365)
                if(yrsAlive > 150): #death date < 150 years after birth date
                    print(f"ANOMALY: US07: Individual {indiv.IId} had an age of {yrsAlive} when alive")
                    output_file.write(f"ANOMALY: US07: Individual {indiv.IId} had an age of {yrsAlive} when alive\n")

# Birth before marriage of parents and not more than 9 months after divorce
def run_US08(individuals: dict[str, Individual], families: dict[str, Family], output_file):
    for fam_id in families:
        family = families[fam_id]
        
        for child_id in family.FChildIds:
            if child_id in individuals:
                child = individuals[child_id]
                
                # Check if child is born before the marriage of parents
                if family.FMar != "NA" and child.IBirth < family.FMar:
                    print(f"ERROR: FAMILY: US08: Child {child.IId} ({child.IBirth}) born before parents' marriage ({family.FMar})")
                    output_file.write(f"ERROR: FAMILY: US08: Child {child.IId} ({child.IBirth}) born before parents' marriage ({family.FMar})\n")
                
                # Check if child is born more than 9 months after the divorce of parents
                if family.FDiv != "NA":
                    divorce_deadline = family.FDiv + timedelta(days=9*30)  # Approximate 9 months after divorce
                    if child.IBirth > divorce_deadline:
                        print(f"ERROR: FAMILY: US08: Child {child.IId} ({child.IBirth}) born more than 9 months after parents' divorce ({family.FDiv})")
                        output_file.write(f"ERROR: FAMILY: US08: Child {child.IId} ({child.IBirth}) born more than 9 months after parents' divorce ({family.FDiv})\n")

# Birth before death of parents
def run_US09(individuals: dict[str, Individual], families: dict[str, Family], output_file):
    for fam_id in families:
        family = families[fam_id]
        if family.FHusbId != "NA" and family.FWifeId != "NA":
            husband = individuals[family.FHusbId]
            wife = individuals[family.FWifeId]
            
            for child_id in family.FChildIds:
                if child_id in individuals:
                    child = individuals[child_id]
                    
                    # Check if child is born after the mother's death
                    if wife.IDeath != "NA" and child.IBirth > wife.IDeath:
                        print(f"ERROR: FAMILY: US09: Child {child.IId} ({child.IBirth}) born after mother's ({wife.IId}) death ({wife.IDeath})")
                        output_file.write(f"ERROR: FAMILY: US09: Child {child.IId} ({child.IBirth}) born after mother's ({wife.IId}) death ({wife.IDeath})\n")
                    
                    # Check if child is born more than 9 months after the father's death
                    if husband.IDeath != "NA":
                        father_deadline = husband.IDeath + timedelta(days=9*30)  # Approximate 9 months after death
                        if child.IBirth > father_deadline:
                            print(f"ERROR: FAMILY: US09: Child {child.IId} ({child.IBirth}) born more than 9 months after father's ({husband.IId}) death ({husband.IDeath})")
                            output_file.write(f"ERROR: FAMILY: US09: Child {child.IId} ({child.IBirth}) born more than 9 months after father's ({husband.IId}) death ({husband.IDeath})\n")

# Marriage after 14
def run_US10(individuals: dict[Individual], families: dict[Family], output_file):
    for key in families:
        fam: Family = families[key]
        husb: Individual = individuals[fam.FHusbId]
        wife: Individual = individuals[fam.FWifeId]

        # Check husband age
        husb_age = fam.FMar.year - husb.IBirth.year
        if fam.FMar.month < husb.IBirth.month: husb_age -= 1  # Birth month had not yet come
        elif fam.FMar.month == husb.IBirth.month and fam.FMar.day < husb.IBirth.day: husb_age -= 1  # Bith day has not yet come

        if husb_age < 14:
            print(f"ANOMALY: US10: Individual {fam.FHusbId} was less than 14 years old when married")
            output_file.write(f"ANOMALY: US10: Individual {fam.FHusbId} was less than 14 years old when married\n")

        # Check wife age
        wife_age = fam.FMar.year - wife.IBirth.year
        if fam.FMar.month < wife.IBirth.month: wife_age -= 1  # Birth month had not yet come
        elif fam.FMar.month == wife.IBirth.month and fam.FMar.day < wife.IBirth.day: wife_age -= 1  # Bith day has not yet come

        if wife_age < 14:
            print(f"ANOMALY: US10: Individual {fam.FWifeId} was less than 14 years old when married")
            output_file.write(f"ANOMALY: US10: Individual {fam.FWifeId} was less than 14 years old when married\n")

# Parents not too old
def run_US12(individuals: dict[Individual], families: dict[Family], output_file):
    for key in families:
        fam: Family = families[key]

        if len(fam.FChildIds) == 0: continue

        # Get parent birthdays
        father_birthday = individuals[fam.FHusbId].IBirth
        mother_birthday = individuals[fam.FWifeId].IBirth
        
        # Get youngest child's birthday
        youngest_child_birhday = max([individuals[childId].IBirth for childId in fam.FChildIds])

        # Check father age
        if relativedelta(youngest_child_birhday, father_birthday).years >= 80:
            print(f"ANOMALY: US12: Individual {fam.FHusbId} had a child when he was 80 years or older")
            output_file.write(f"ANOMALY: US12: Individual {fam.FHusbId} had a child when he was 80 years or older\n")

        # Check mother age
        if relativedelta(youngest_child_birhday, mother_birthday).years >= 60:
            print(f"ANOMALY: US12: Individual {fam.FWifeId} had a child when she was 60 years or older")
            output_file.write(f"ANOMALY: US12: Individual {fam.FWifeId} had a child when she was 60 years or older\n")

# Multiple births <= 5
def run_US14(individuals: dict[Individual], families: dict[Family], output_file):
    for key in families:
        fam: Family = families[key]

        dateCounter: dict[datetime] = {}
        for childId in fam.FChildIds:
            child: Individual = individuals[childId]
            if child.IBirth not in dateCounter.keys(): dateCounter[child.IBirth] = 1
            else: dateCounter[child.IBirth] += 1
        
        for date in dateCounter.keys():
            if dateCounter[date] > 5:
                dateStr = date.strftime("%Y-%m-%d")
                print(f"ANOMALY: US14: Family {fam.FId} has more than 5 children born on date {dateStr}")
                output_file.write(f"ANOMALY: US14: Family {fam.FId} has more than 5 children born on date {dateStr}\n")

# Fewer than 15 siblings
def run_US15(families: dict[Family], output_file):
    for key in families:
        fam: Family = families[key]
        if len(fam.FChildIds) >= 15:
            print(f"ANOMALY: FAMILY: US15: Family {key} has 15 or more children")
            output_file.write(f"ANOMALY: FAMILY: US15: Family {key} has 15 or more children")
            
# Male last names
def run_US16(individuals: dict[str, Individual], families: dict[str, Family], output_file):
    for fam_id in families:
        family = families[fam_id]
        male_last_names = set()
        
        if family.FHusbId in individuals:
            husband = individuals[family.FHusbId]
            if husband.IGen == 'M':
                male_last_names.add(husband.get_last_name())
        
        for child_id in family.FChildIds:
            if child_id in individuals:
                child = individuals[child_id]
                if child.IGen == 'M':
                    male_last_names.add(child.get_last_name())
        
        if len(male_last_names) > 1:
            print(f"ERROR: FAMILY: US16: Male members of family {fam_id} have different last names: {male_last_names}")
            output_file.write(f"ERROR: FAMILY: US16: Male members of family {fam_id} have different last names: {male_last_names}\n")

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

# Correct gender for role
def run_US21(individuals: dict[Individual], families: dict[Family], output_file):
    for key in families:
        fam: Family = families[key]
        husb: Individual = individuals[fam.FHusbId]
        wife: Individual = individuals[fam.FWifeId]
        
        # Check husband gender
        if not husb.IGen == 'M':
            print(f"ERROR: US21: Individual {fam.FHusbId} had the wrong gender")
            output_file.write(f"ERROR: US21: Individual {fam.FHusbId} had the wrong gender\n")

        # Check wife gender
        if not wife.IGen == 'F':
            print(f"ERROR: US21: Individual {fam.FWifeId} had the wrong gender")
            output_file.write(f"ERROR: US21: Individual {fam.FWifeId} had the wrong gender\n")

# Unique names in families
def run_US25(individuals: dict[Individual], families: dict[Family], output_file):
    for key in families:
        fam: Family = families[key]
        for child1_key, child2_key in itertools.combinations(fam.FChildIds, 2):
            if not child1_key == child2_key:
                child1: Individual = individuals[child1_key]
                child2: Individual = individuals[child2_key]

                if child1.IName == child2.IName and child1.IBirth.date() == child2.IBirth.date():
                    print(f"ERROR: FAMILY: US25: Individuals {child1_key} and {child2_key} from the same family share a name \"{child1.IName}\" and birthday")
                    output_file.write(f"ERROR: FAMILY: US25: Individuals {child1_key} and {child2_key} from the same family share a name \"{child1.IName}\" and birthday")

# List deceased
def run_US29(individuals: dict[Individual], output_file):
    deceasedTable = PrettyTable()
    deceasedTable.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Death"]
    for key in individuals:
        indiv: Individual = individuals[key]
        if not indiv.is_alive():
            deceasedTable.add_row([indiv.IId, indiv.IName, indiv.IGen, indiv.IBirth.strftime("%Y-%m-%d"), indiv.get_age(), indiv.IDeath.strftime("%Y-%m-%d")])

    print("\nUS29: Deceased List")
    print(deceasedTable)
    output_file.write("US29: Deceased List\n")
    output_file.write(str(deceasedTable)+'\n')

# List living married
def run_US30(individuals: dict[Individual], output_file):
    livingMarried = PrettyTable()
    livingMarried.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Child", "Spouse"]
    for key in individuals:
        indiv: Individual = individuals[key]
        if indiv.is_alive() and indiv.ISpouse != "NA":
            livingMarried.add_row([indiv.IId, indiv.IName, indiv.IGen, indiv.IBirth.strftime("%Y-%m-%d"), indiv.get_age(), indiv.IChild, indiv.ISpouse])
    
    print("\nUS30: Living Married List")
    print(livingMarried)
    output_file.write("US30: Living Married List\n")
    output_file.write(str(livingMarried)+'\n')

# List living single
def run_US31(individuals: dict[Individual], output_file):
    livingSingle = PrettyTable()
    livingSingle.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Child", "Spouse"]
    for key in individuals:
        indiv: Individual = individuals[key]
        if indiv.is_alive() and indiv.ISpouse == "NA" and indiv.get_age() > 30:
            livingSingle.add_row([indiv.IId, indiv.IName, indiv.IGen, indiv.IBirth.strftime("%Y-%m-%d"), indiv.get_age(), indiv.IChild, indiv.ISpouse])
    
    print("\nUS31: Living Single List")
    print(livingSingle)
    output_file.write("US31: Living Single List\n")
    output_file.write(str(livingSingle)+'\n')

# List recent births
def run_US35(individuals: dict[str, Individual], output_file):
    print("\nUS35: Recent Births")
    output_file.write("\nUS35: Recent Births\n")
    
    today = datetime.now()
    recent_births = []

    for indiv_id in individuals:
        individual = individuals[indiv_id]
        if individual.IBirth and (today - individual.IBirth).days <= 30:
            recent_births.append(individual)

    if recent_births:
        print("Recent Births (last 30 days):")
        output_file.write("Recent Births (last 30 days):\n")
        for person in recent_births:
            print(f"ID: {person.IId}, Name: {person.IName}, Birth Date: {person.IBirth}")
            output_file.write(f"ID: {person.IId}, Name: {person.IName}, Birth Date: {person.IBirth}\n")
    else:
        print("No recent births in the last 30 days.")
        output_file.write("No recent births in the last 30 days.\n")

# List recent deaths
def run_US36(individuals: dict[str, Individual], output_file):
    print("\nUS36: Recent Deaths")
    output_file.write("\nUS36: Recent Deaths\n")
    today = datetime.now()
    recent_deaths = []

    for indiv_id in individuals:
        individual = individuals[indiv_id]
        if individual.IDeath != 'NA' and (today - individual.IDeath).days <= 30:
            recent_deaths.append(individual)

    if recent_deaths:
        print("Recent Deaths (last 30 days):")
        output_file.write("Recent Deaths (last 30 days):\n")
        for person in recent_deaths:
            print(f"ID: {person.IId}, Name: {person.IName}, Death Date: {person.IDeath}")
            output_file.write(f"ID: {person.IId}, Name: {person.IName}, Death Date: {person.IDeath}\n")
    else:
        print("No recent deaths in the last 30 days.")
        output_file.write("No recent deaths in the last 30 days.\n")

# List upcoming birthdays
def run_US38(individuals: dict[str, Individual], output_file):
    print("\nUS38: Upcoming Birthdays")
    output_file.write("\nUS38: Upcoming Birthdays\n")
    today = datetime.now()
    upcoming_birthdays = []

    for indiv_id in individuals:
        individual = individuals[indiv_id]
        if individual.IBirth:
            if individual.IBirth.month == today.month:
                if individual.IBirth.day >= today.day and individual.IBirth.day <= today.day + 30:
                    upcoming_birthdays.append(individual)
            elif individual.IBirth.month == today.month + 1:
                if individual.IBirth.day <= today.day + 30 - 31:
                    upcoming_birthdays.append(individual)

    if upcoming_birthdays:
        print("Upcoming Birthdays (next 30 days):")
        output_file.write("Upcoming Birthdays (next 30 days):\n")
        for person in upcoming_birthdays:
            print(f"ID: {person.IId}, Name: {person.IName}, Birth Date: {person.IBirth}")
            output_file.write(f"ID: {person.IId}, Name: {person.IName}, Birth Date: {person.IBirth}\n")
    else:
        print("No upcoming birthdays in the next 30 days.")
        output_file.write("No upcoming birthdays in the next 30 days.\n")

#Reject illegitimate dates            
def run_US42(individuals: dict[Individual], families: dict[Family], output_file):
    for IKey in individuals:
        indiv: Individual = individuals[IKey]
        try:
            datetime.date(indiv.IBirth)
        except Exception:
            print(f"ANOMALY: US42: Individual {indiv.IId} had an invalid date of {indiv.IBirth} for Birth Date")
            output_file.write(f"ANOMALY: US42: Individual {indiv.IId} had an invalid date of {indiv.IBirth} for Birth Date\n")
        if(indiv.IDeath != 'NA'):
            try:
                datetime.date(indiv.IDeath)
            except Exception:
                print(f"ANOMALY: US42: Individual {indiv.IId} had an invalid date of {indiv.IDeath} for Death Date")
                output_file.write(f"ANOMALY: US42: Individual {indiv.IId} had an invalid date of {indiv.IDeath} for Death Date\n")
    for FKey in families:
        fam: Family = families[FKey]
        if(fam.FMar != 'NA'):
            try:
                datetime.date(fam.FMar)
            except Exception:
                print(f"ANOMALY: US42: Family {fam.FId} had an invalid date of {fam.FMar} for Marriage Date")
                output_file.write(f"ANOMALY: US42: Family {fam.FId} had an invalid date of {fam.FMar} for Marriage Date\n")
        if(fam.FDiv != 'NA'):
            try:
                datetime.date(fam.FDiv)
            except Exception:
                print(f"ANOMALY: US42: Family {fam.FId} had an invalid date of {fam.FDiv} for Divorce Date")
                output_file.write(f"ANOMALY: US42: Family {fam.FId} had an invalid date of {fam.FDiv} for Divorce Date\n")

# Add completed user stories here to implement into the main running code
def run_all_user_stories(individuals: dict[Individual], families: dict[Family], output_file):
    run_US01(individuals, families, output_file)
    run_US02(individuals, families, output_file)
    run_US03(individuals, output_file)
    run_US04(families, output_file)
    run_US05(individuals, families, output_file)
    run_US06(individuals, families, output_file)
    run_US07(individuals, output_file)
    run_US08(individuals, families, output_file)
    run_US09(individuals, families, output_file)
    run_US10(individuals, families, output_file)
    run_US12(individuals, families, output_file)
    run_US14(individuals, families, output_file)
    run_US15(families, output_file)
    run_US16(individuals, families, output_file)
    run_US17(families, output_file)
    run_US18(families, output_file)
    run_US21(individuals, families, output_file)
    run_US25(individuals, families, output_file)
    run_US29(individuals, output_file)
    run_US30(individuals, output_file)
    run_US31(individuals, output_file)
    run_US35(individuals, output_file)
    run_US36(individuals, output_file)
    run_US38(individuals, output_file)
    run_US42(individuals, families, output_file)


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

    with open('output_GEDCOM.txt','w') as output_file:
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

                    if id in individuals.keys(): # US22 Check unique tags
                        print(f"ERROR: INDIVIDUAL: US22: Id {id} is not unique!  Used for multiple individuals!")
                        output_file.write(f"ERROR: INDIVIDUAL: US22: Id {id} is not unique!  Used for multiple individuals!")
                    individual = Individual(id)
                elif tag == 'FAM':
                    if family is not None: families[family.FId] = family
                    id = content[1:-1]

                    if id in families.keys(): # US22 Check unique tags
                        print(f"ERROR: FAMILY: US22: Id {id} is not unique!  Used for multiple families!")
                        output_file.write(f"ERROR: FAMILY: US22: Id {id} is not unique!  Used for multiple families!")
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
        output_file.write(str(indivTable)+'\n\n')

        famTable = PrettyTable()
        famTable.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]

        for key in sorted(families, key=lambda k: int(k[1:])):
            fam: Family = families[key]
            husb: Individual = individuals[fam.FHusbId]
            wife: Individual = individuals[fam.FWifeId]
            
            famTable.add_row([fam.FId, fam.FMar.strftime("%Y-%m-%d"), fam.FDiv if fam.FDiv == 'NA' else fam.FDiv.strftime("%Y-%m-%d"), 
                            fam.FHusbId, husb.IName, fam.FWifeId, wife.IName, fam.FChildIds])
        print(famTable)
        output_file.write(str(famTable)+'\n\n')

        run_all_user_stories(individuals, families, output_file)

if __name__ == '__main__':
    parse_GEDCOM()
