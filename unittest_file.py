import itertools
import unittest

from datetime import datetime,timedelta

from CS555Proj import Individual, Family

# Birth before marriage of parents
def run_US08(individuals: dict[Individual], families: dict[Family]):
    for fam_id in families:
        family: Family = families[fam_id]
        
        for child_id in family.FChildIds:
            if child_id in individuals:
                child: Individual = individuals[child_id]
                
                # Check if child is born before the marriage of parents
                if family.FMar != "NA" and child.IBirth < family.FMar:
                    return False
                
                # Check if child is born more than 9 months after the divorce of parents
                if family.FDiv != "NA":
                    divorce_deadline = family.FDiv + timedelta(days=9*30)  # Approximate 9 months after divorce
                    if child.IBirth > divorce_deadline:
                        return False
    return True

# Birth before death of parents
def run_US09(individuals: dict[Individual], families: dict[Family]):
    for fam_id in families:
        family: Family = families[fam_id]
        if family.FHusbId != "NA" and family.FWifeId != "NA":
            husband: Individual = individuals[family.FHusbId]
            wife: Individual = individuals[family.FWifeId]
            
            for child_id in family.FChildIds:
                if child_id in individuals:
                    child: Individual = individuals[child_id]
                    
                    # Check if child is born after the mother's death
                    if wife.IDeath != "NA" and child.IBirth > wife.IDeath:
                        return False
                    
                    # Check if child is born more than 9 months after the father's death
                    if husband.IDeath != "NA":
                        father_deadline = husband.IDeath + timedelta(days=9*30)  # Approximate 9 months after death
                        if child.IBirth > father_deadline:
                            return False
    return True

# Multiple births <= 5
def run_US14(individuals: dict[Individual], families: dict[Family]):
    for key in families:
        fam: Family = families[key]

        dateCounter: dict[datetime] = {}
        for childId in fam.FChildIds:
            child: Individual = individuals[childId]
            if child.IBirth not in dateCounter.keys(): dateCounter[child.IBirth] = 1
            else: dateCounter[child.IBirth] += 1
        
        for date in dateCounter.keys():
            if dateCounter[date] > 5:
                return False
    return True

# Fewer than 15 siblings
def run_US15(families: dict[Family]):
    for key in families:
        fam: Family = families[key]
        if len(fam.FChildIds) >= 15:
            return False
    return True

# All male members of a family should have the same last name
def run_US16(individuals: dict[Individual], families: dict[Family]):
    for key in families:
        fam: Family = families[key]
        last_name = None
        
        if fam.FHusbId:
            husband = individuals[fam.FHusbId]
            last_name = husband.IName.split()[-1]

        for child_id in fam.FChildIds:
            child = individuals[child_id]
            if child.ISex == 'M' and child.IName.split()[-1] != last_name:
                return False
    return True
    
# No marriage to descendants
def run_US17(families: dict[Family]):
    key_pairs = itertools.combinations(families.keys(), 2)
    for key1, key2 in key_pairs:
        fam1: Family = families[key1]
        fam2: Family = families[key2]

        if fam1.FHusbId == fam2.FHusbId:
            if fam1.FWifeId in fam2.FChildIds: # Father marries daughter from fam2
                return False
            elif fam2.FWifeId in fam1.FChildIds: # Father marries daughter from fam1
                return False
        if fam1.FWifeId == fam2.FWifeId:
            if fam1.FHusbId in fam2.FChildIds: # Mother marries son from fam2
                return False
            elif fam2.FHusbId in fam1.FChildIds: # Mother marries son from fam1
                return False
    return True

# No marriage to siblings
def run_US18(families: dict[Family]):
    key_pairs = itertools.combinations(families.keys(), 2)
    for key1, key2 in key_pairs:
        fam1: Family = families[key1]
        fam2: Family = families[key2]

        if fam1.FHusbId in fam2.FChildIds and fam1.FWifeId in fam2.FChildIds:
            return False
            
        elif fam2.FHusbId in fam1.FChildIds and fam2.FWifeId in fam1.FChildIds:
            return False
        
    return True

# Unique ids
def run_US22(lines: list[str]):
    individuals = {}
    families = {}

    individual = None
    family = None
    for line in lines:
        split_content = line.split()

        tag = split_content[2]
        content = split_content[1]
    
        if tag == 'INDI':
            if individual is not None: individuals[individual.IId] = individual
            id = content[1:-1]

            if id in individuals.keys(): # Duplicate individual key!
                return False
            individual = Individual(id)
        elif tag == 'FAM':
            if family is not None: families[family.FId] = family
            id = content[1:-1]

            if id in families.keys(): # Duplicate family key!
                return False
            family = Family(id)

    return True

# Unique names in families
def run_US25(individuals: dict[Individual], families: dict[Family]):
    for key in families:
        fam: Family = families[key]
        for child1_key, child2_key in itertools.combinations(fam.FChildIds, 2):
            if not child1_key == child2_key:
                child1: Individual = individuals[child1_key]
                child2: Individual = individuals[child2_key]

                if child1.IName == child2.IName and child1.IBirth.date() == child2.IBirth.date():
                    return False
    return True

# List all people in a GEDCOM file who were born in the last 30 days
def run_US35(individuals: dict[Individual]):
    recent_births = []
    now = datetime.now()

    for key in individuals:
        indiv: Individual = individuals[key]
        if (now - indiv.IBirth).days <= 30:
            recent_births.append(indiv)

    return recent_births

# Reject illegitimate dates
def run_US42(individuals: dict[Individual], families: dict[Family]):
    for IKey in individuals:
        indiv: Individual = individuals[IKey]
        try:
            datetime.strptime(indiv.IBirth)
        except Exception:
            return False
        if(indiv.IDeath != 'NA'):
            try:
                datetime.strptime(indiv.IDeath)
            except Exception:
                return False
    for FKey in families:
        fam: Family = families[FKey]
        if(fam.FMar != 'NA'):
            try:
                datetime.strptime(fam.FMar)
            except Exception:
                return False
        if(fam.FDiv != 'NA'):
            try:
                datetime.strptime(fam.FDiv)
            except Exception:
                return False
    return True


class Test_US08(unittest.TestCase):

    def test_birth_before_marriage(self):
        ind1 = Individual('I1')
        ind1.IName = "John Doe"
        ind1.IBirth = datetime.strptime("10 JAN 1980", "%d %b %Y")

        ind2 = Individual('I2')
        ind2.IName = "Jane Smith"
        ind2.IBirth = datetime.strptime("10 JAN 1980", "%d %b %Y")

        ind3 = Individual('I3')
        ind3.IName = "Johnny Doe"
        ind3.IBirth = datetime.strptime("10 JUN 1979", "%d %b %Y")

        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FMar = datetime.strptime("01 JAN 1980", "%d %b %Y")
        fam1.FChildIds = ['I3']

        individuals = {ind1.IId: ind1, ind2.IId: ind2, ind3.IId: ind3}
        families = {fam1.FId: fam1}

        self.assertFalse(run_US08(individuals, families), "Missed birth before marriage")

    def test_birth_after_divorce(self):
        ind1 = Individual('I1')
        ind1.IName = "John Doe"
        ind1.IBirth = datetime.strptime("10 JAN 1980", "%d %b %Y")

        ind2 = Individual('I2')
        ind2.IName = "Jane Smith"
        ind2.IBirth = datetime.strptime("10 JAN 1980", "%d %b %Y")

        ind3 = Individual('I3')
        ind3.IName = "Johnny Doe"
        ind3.IBirth = datetime.strptime("10 JUN 1981", "%d %b %Y")

        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FMar = datetime.strptime("01 JAN 1980", "%d %b %Y")
        fam1.FDiv = datetime.strptime("01 JAN 1980", "%d %b %Y")
        fam1.FChildIds = ['I3']

        individuals = {ind1.IId: ind1, ind2.IId: ind2, ind3.IId: ind3}
        families = {fam1.FId: fam1}

        self.assertFalse(run_US08(individuals, families), "Missed birth after divorce")

class Test_US09(unittest.TestCase):

    def test_birth_after_father_death(self):
        ind1 = Individual('I1')
        ind1.IName = "John Doe"
        ind1.IDeath = datetime.strptime("10 JAN 1980", "%d %b %Y")

        ind2 = Individual('I2')
        ind2.IName = "Jane Smith"

        ind3 = Individual('I3')
        ind3.IName = "Johnny Doe"
        ind3.IBirth = datetime.strptime("10 JUN 1981", "%d %b %Y")

        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FChildIds = ['I3']

        individuals = {ind1.IId: ind1, ind2.IId: ind2, ind3.IId: ind3}
        families = {fam1.FId: fam1}

        self.assertFalse(run_US09(individuals, families), "Missed birth after father's death")

    def test_birth_after_mother_death(self):
        ind1 = Individual('I1')
        ind1.IName = "John Doe"

        ind2 = Individual('I2')
        ind2.IName = "Jane Smith"
        ind2.IDeath = datetime.strptime("10 JAN 1980", "%d %b %Y")

        ind3 = Individual('I3')
        ind3.IName = "Johnny Doe"
        ind3.IBirth = datetime.strptime("10 JUN 1980", "%d %b %Y")

        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FChildIds = ['I3']

        individuals = {ind1.IId: ind1, ind2.IId: ind2, ind3.IId: ind3}
        families = {fam1.FId: fam1}

        self.assertFalse(run_US09(individuals, families), "Missed birth after mother's death")

class Test_US14(unittest.TestCase):

    def test_less_than_5_children_born_on_same_day(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3']

        child1 = Individual('I1')
        child1.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child2 = Individual('I2')
        child2.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child3 = Individual('I3')
        child3.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        individuals = {child1.IId: child1, child2.IId: child2, child3.IId: child3}
        families = {fam1.FId: fam1}
        self.assertTrue(run_US14(individuals, families), "Identified multiple births when there were not more than 5")

    def test_more_than_5_children_born_on_different_days(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3', 'I4', 'I5', 'I6']

        child1 = Individual('I1')
        child1.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child2 = Individual('I2')
        child2.IBirth = datetime.strptime("12 OCT 2003", "%d %b %Y")

        child3 = Individual('I3')
        child3.IBirth = datetime.strptime("13 OCT 2004", "%d %b %Y")

        child4 = Individual('I4')
        child4.IBirth = datetime.strptime("14 OCT 2005", "%d %b %Y")

        child5 = Individual('I5')
        child5.IBirth = datetime.strptime("15 OCT 2006", "%d %b %Y")

        child6 = Individual('I6')
        child6.IBirth = datetime.strptime("16 OCT 2007", "%d %b %Y")

        individuals = {child1.IId: child1, child2.IId: child2, child3.IId: child3, child4.IId: child4, child5.IId: child5, child6.IId: child6}
        families = {fam1.FId: fam1}
        self.assertTrue(run_US14(individuals, families), "Identified multiple births when there were not more than 5 on the same day")

    def test_more_than_5_children_born_on_same_day(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3', 'I4', 'I5', 'I6']

        child1 = Individual('I1')
        child1.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child2 = Individual('I2')
        child2.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child3 = Individual('I3')
        child3.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child4 = Individual('I4')
        child4.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child5 = Individual('I5')
        child5.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        child6 = Individual('I6')
        child6.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        individuals = {child1.IId: child1, child2.IId: child2, child3.IId: child3, child4.IId: child4, child5.IId: child5, child6.IId: child6}
        families = {fam1.FId: fam1}
        self.assertFalse(run_US14(individuals, families), "Missed multiple births")

class Test_US15(unittest.TestCase):

    def test_less_than_15_siblings(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3']

        families = {fam1.FId: fam1}
        self.assertTrue(run_US15(families), "Identified too many siblings when there were less than 15")

    def test_15_siblings(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3']

        fam2 = Family('F2')
        fam2.FChildIds = ['I1', 'I2', 'I3', 'I4', 'I5',
                          'I6', 'I7', 'I8', 'I9', 'I10',
                          'I11', 'I12', 'I13', 'I14', 'I15']

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US15(families), "Did not identify that there were 15 siblings")

    def test_more_than_15_siblings(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3', 'I4', 'I5',
                          'I6', 'I7', 'I8', 'I9', 'I10',
                          'I11', 'I12', 'I13', 'I14', 'I15',
                          'I16', 'I17', 'I18', 'I19', 'I20']
        
        fam2 = Family('F2')
        fam2.FChildIds = ['I1', 'I2', 'I3']

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US15(families), "Did not identify that there were more than 15 siblings")

class Test_US16(unittest.TestCase):

    def test_same_last_name(self):
        ind1 = Individual('I1')
        ind1.IName = "John Doe"
        ind1.ISex = 'M'
        ind2 = Individual('I2')
        ind2.IName = "Jane Doe"
        ind2.ISex = 'F'
        ind3 = Individual('I3')
        ind3.IName = "Johnny Doe"
        ind3.ISex = 'M'

        fam1 = Family('F1')
        fam1.FHusbId = ind1.IId
        fam1.FWifeId = ind2.IId
        fam1.FChildIds = [ind3.IId]

        individuals = {ind1.IId: ind1, ind2.IId: ind2, ind3.IId: ind3}
        families = {fam1.FId: fam1}

        self.assertTrue(run_US16(individuals, families), "Identified different last names when they were the same")

    def test_different_last_name(self):
        ind1 = Individual('I1')
        ind1.IName = "John Doe"
        ind1.ISex = 'M'
        ind2 = Individual('I2')
        ind2.IName = "Jane Doe"
        ind2.ISex = 'F'
        ind3 = Individual('I3')
        ind3.IName = "Johnny Smith"
        ind3.ISex = 'M'

        fam1 = Family('F1')
        fam1.FHusbId = ind1.IId
        fam1.FWifeId = ind2.IId
        fam1.FChildIds = [ind3.IId]

        individuals = {ind1.IId: ind1, ind2.IId: ind2, ind3.IId: ind3}
        families = {fam1.FId: fam1}

        self.assertFalse(run_US16(individuals, families), "Did not identify different last names for male family members")

class Test_US17(unittest.TestCase):

    def test_no_descendant_marriage(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FChildIds = ['I3']

        fam2 = Family('F2')
        fam2.FHusbId = 'I3'
        fam2.FWifeId = 'I4'

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertTrue(run_US17(families), "Identified descendant marriage when there was none")

    def test_husb_marr_fam1_child(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FChildIds = ['I3']

        fam2 = Family('F2')
        fam2.FHusbId = 'I1'
        fam2.FWifeId = 'I3'

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US17(families), "Missed descendant marriage: Father marries daughter")

    def test_husb_marr_fam2_child(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'

        fam2 = Family('F2')
        fam2.FHusbId = 'I1'
        fam2.FWifeId = 'I3'
        fam2.FChildIds = ['I2']

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US17(families), "Missed descendant marriage: Father marries daughter")

    def test_wife_marr_fam1_child(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FChildIds = ['I3']

        fam2 = Family('F2')
        fam2.FHusbId = 'I3'
        fam2.FWifeId = 'I2'

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US17(families), "Missed descendant marriage: Mother marries son")

    def test_wife_marr_fam2_child(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'

        fam2 = Family('F2')
        fam2.FHusbId = 'I3'
        fam2.FWifeId = 'I2'
        fam2.FChildIds = ['I1']

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US17(families), "Missed descendant marriage: Mother marries son")

class Test_US18(unittest.TestCase):

    def test_no_sibling_marriage(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FChildIds = ['I3']

        fam2 = Family('F2')
        fam2.FHusbId = 'I3'
        fam2.FWifeId = 'I4'
        fam2.FChildIds = ['I5']

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertTrue(run_US18(families), "Identified sibling marriage when there was none")

    def test_siblings_in_fam1(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'
        fam1.FChildIds = ['I3', 'I4']

        fam2 = Family('F2')
        fam2.FHusbId = 'I3'
        fam2.FWifeId = 'I4'

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US18(families), "Missed marriage between siblings from family 1")

    def test_siblings_in_fam2(self):
        fam1 = Family('F1')
        fam1.FHusbId = 'I1'
        fam1.FWifeId = 'I2'

        fam2 = Family('F2')
        fam2.FHusbId = 'I3'
        fam2.FWifeId = 'I4'
        fam2.FChildIds = ['I1', 'I2']

        families = {fam1.FId: fam1, fam2.FId: fam2}
        self.assertFalse(run_US18(families), "Missed marriage between siblings from family 2")

class Test_US22(unittest.TestCase):

    def test_no_duplicates(self):
        lines = ["0 @I1@ INDI",
                 "0 @I2@ INDI",
                 "0 @I3@ INDI",
                 "0 @F1@ FAM",
                 "0 @F2@ FAM",
                 "0 @F3@ FAM",]

        self.assertTrue(run_US22(lines), "Identified duplicate id when there was none")

    def test_duplicate_individual_id(self):
        lines = ["0 @I1@ INDI",
                 "0 @I2@ INDI",
                 "0 @I1@ INDI",
                 "0 @F1@ FAM",
                 "0 @F2@ FAM",
                 "0 @F3@ FAM",]

        self.assertFalse(run_US22(lines), "Missed duplicate individual id")

    def test_duplicate_family_id(self):
        lines = ["0 @I1@ INDI",
                 "0 @I2@ INDI",
                 "0 @I3@ INDI",
                 "0 @F1@ FAM",
                 "0 @F2@ FAM",
                 "0 @F2@ FAM",]

        self.assertFalse(run_US22(lines), "Missed duplicate family id")

class Test_US25(unittest.TestCase):

    def test_no_duplicate_names(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3']

        families = {fam1.FId: fam1}

        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'
        indiv1.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        indiv2 = Individual('I2')
        indiv2.IName = 'Andrew Abelman'
        indiv2.IBirth = datetime.strptime("13 NOV 2008", "%d %b %Y")

        indiv3 = Individual('I3')
        indiv3.IName = 'Fredric Abelman'
        indiv3.IBirth = datetime.strptime("22 DEC 1972", "%d %b %Y")

        individuals = {indiv1.IId: indiv1, indiv2.IId: indiv2, indiv3.IId: indiv3}

        self.assertTrue(run_US25(individuals, families), "Identified duplicate siblings when there were none")

    def test_duplicate_names_but_not_birth(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3']

        families = {fam1.FId: fam1}

        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'
        indiv1.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        indiv2 = Individual('I2')
        indiv2.IName = 'Bradley Abelman'
        indiv2.IBirth = datetime.strptime("13 NOV 2008", "%d %b %Y")

        indiv3 = Individual('I3')
        indiv3.IName = 'Fredric Abelman'
        indiv3.IBirth = datetime.strptime("22 DEC 1972", "%d %b %Y")

        individuals = {indiv1.IId: indiv1, indiv2.IId: indiv2, indiv3.IId: indiv3}

        self.assertTrue(run_US25(individuals, families), "Identified duplicate siblings when there was no duplicate birthday")

    def test_duplicate_birth_but_not_names(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3']

        families = {fam1.FId: fam1}

        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'
        indiv1.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        indiv2 = Individual('I2')
        indiv2.IName = 'Andrew Abelman'
        indiv2.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        indiv3 = Individual('I3')
        indiv3.IName = 'Fredric Abelman'
        indiv3.IBirth = datetime.strptime("22 DEC 1972", "%d %b %Y")

        individuals = {indiv1.IId: indiv1, indiv2.IId: indiv2, indiv3.IId: indiv3}

        self.assertTrue(run_US25(individuals, families), "Identified duplicate siblings when there were no duplicate name")

    def test_duplicate_names_and_birth(self):
        fam1 = Family('F1')
        fam1.FChildIds = ['I1', 'I2', 'I3']

        families = {fam1.FId: fam1}

        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'
        indiv1.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        indiv2 = Individual('I2')
        indiv2.IName = 'Bradley Abelman'
        indiv2.IBirth = datetime.strptime("11 OCT 2002", "%d %b %Y")

        indiv3 = Individual('I3')
        indiv3.IName = 'Fredric Abeman'
        indiv3.IBirth = datetime.strptime("22 DEC 1972", "%d %b %Y")

        individuals = {indiv1.IId: indiv1, indiv2.IId: indiv2, indiv3.IId: indiv3}

        self.assertFalse(run_US25(individuals, families), "Missed duplicate siblings")

class Test_US35(unittest.TestCase):

    def test_recent_births(self):
        now = datetime.now()
        ind1 = Individual('I1')
        ind1.IName = "John Doe"
        ind1.IBirth = now - timedelta(days=10)
        ind2 = Individual('I2')
        ind2.IName = "Jane Doe"
        ind2.IBirth = now - timedelta(days=40)
        ind3 = Individual('I3')
        ind3.IName = "Johnny Doe"
        ind3.IBirth = now - timedelta(days=20)
        
        individuals = {ind1.IId: ind1, ind2.IId: ind2, ind3.IId: ind3}

        recent_births = run_US35(individuals)
        self.assertEqual(len(recent_births), 2, "Identified incorrect number of recent births")
        self.assertIn(ind1, recent_births, "Missed a recent birth")
        self.assertIn(ind3, recent_births, "Missed a recent birth")
        self.assertNotIn(ind2, recent_births, "Included a non-recent birth")

class Test_US42(unittest.TestCase):

    def test_invalid_birth_date(self):        
        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'
        indiv1.IBirth = "32 OCT 2002"

        individuals = {indiv1.IId: indiv1}

        fam = Family('F1')
        fam.FHusbId = 'I1'
        fam.FWifeId = 'I2'

        families = {fam.FId: fam}

        self.assertFalse(run_US42(individuals, families), "Illegitimate birth date")

    def test_invalid_death_date(self):
        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'
        indiv1.IDeath = "32 OCT 2002"

        individuals = {indiv1.IId: indiv1}

        fam = Family('F1')
        fam.FHusbId = 'I1'
        fam.FWifeId = 'I2'

        families = {fam.FId: fam}

        self.assertFalse(run_US42(individuals, families), "Illegitimate death date")

    def test_invalid_mar_date(self):
        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'

        individuals = {indiv1.IId: indiv1}

        fam = Family('F1')
        fam.FHusbId = 'I1'
        fam.FWifeId = 'I2'
        fam.FMar = "32 OCT 2002"

        families = {fam.FId: fam}

        self.assertFalse(run_US42(individuals, families), "Illegitimate marriage date")

    def test_invalid_div_date(self):
        indiv1 = Individual('I1')
        indiv1.IName = 'Bradley Abelman'

        individuals = {indiv1.IId: indiv1}

        fam = Family('F1')
        fam.FHusbId = 'I1'
        fam.FWifeId = 'I2'
        fam.FDiv = "32 OCT 2002"

        families = {fam.FId: fam}

        self.assertFalse(run_US42(individuals, families), "Illegitimate divorce date")


if __name__ == "__main__":
    with open("test_results.txt", "w") as f:
        runner = unittest.TextTestRunner(f)
        unittest.main(testRunner=runner)
