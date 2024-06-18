import itertools
import unittest

from datetime import datetime

from CS555Proj import Individual, Family


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

if __name__ == "__main__":
    with open("test_results.txt", "w") as f:
        runner = unittest.TextTestRunner(f)
        unittest.main(testRunner=runner)