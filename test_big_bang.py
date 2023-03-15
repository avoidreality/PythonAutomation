import unittest

import big_bang


class TestBig_Bang(unittest.TestCase):

        def test_step1(self):
        """This tests step 1. This will work in a Cygwin shell.""" 
            pdb1 = input("Enter PDB1 please: ")
            pdb2 = input("Enter PDB2 please: ")

            if pdb1 and pdb2:
                return_value = big_bang.step1(pdb1, pdb2)

                self.assertIsNone(return_value) #the actual test
            else:
                print("[-] Error PDB1 or PDB2 is empty.")

        def test_step2(self):
            """ Test step 2. Make sure 'None' is returned."""
            x = big_bang.step2()
            self.assertIsNone(x)




if __name__ == "__main__":
    unittest.main()



