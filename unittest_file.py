import itertools
import unittest

from datetime import datetime,timedelta

from CS555Proj import Individual, Family

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


if __name__ == "__main__":
    
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

    if not run_US25(individuals, families): print("Missed duplicate siblings")

    with open("test_results.txt", "w") as f:
        runner = unittest.TextTestRunner(f)
        unittest.main(testRunner=runner)
