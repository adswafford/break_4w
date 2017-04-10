from unittest import TestCase, main

import pandas as pd
import numpy as np
# import numpy.testing as npt
import pandas.util.testing as pdt

from break4w.categorical import Categorical


class CategoricalTest(TestCase):

    def setUp(self):

        self.map_ = pd.DataFrame([['2', '4', '4'],
                                  ['False', 'True', 'True'],
                                  ['Striker', 'D-man', 'D-man']],
                                 index=['years_on_team',
                                        'team_captain', 'position'],
                                 columns=['Bitty', 'Ransom', 'Holster'],
                                 ).T
        self.name = 'position'
        self.description = 'Where the player can normally be found on the ice'
        self.dtype = str
        self.order = ["Striker", "D-man", "Goalie"]
        self.extremes = ["Striker", "Goalie"]

        self.c = Categorical(
            name=self.name,
            description=self.description,
            dtype=self.dtype,
            order=self.order,
            extremes=self.extremes,
            )

    def test_categorical_init(self):
        test = Categorical(self.name,
                           self.description,
                           self.dtype,
                           self.order)

        self.assertEqual(self.order, test.order)
        self.assertEqual(test.extremes, self.extremes)
        self.assertEqual(test.type, 'Categorical')
        self.assertEqual(test.frequency_cutoff, None)

    def test_update_order(self):

        # Checks that the log is empty
        self.assertEqual(self.c.log, [])

        # Sets up a function to adjust the data
        def remap_(x):
            if x in {"D-man", "Goalie"}:
                return "Defense"
            elif x in {"Striker"}:
                return "Offense"
            else:
                return "Not on the team!"

        # # updates the data
        self.c._update_order(remap_)

        # Checks the updated order
        self.assertEqual(self.c.order, ["Offense", "Defense"])
        self.assertEqual(self.c.extremes, ["Offense", 'Defense'])

    def test_analysis_drop_infrequent(self):
        self.assertTrue(set(self.map_[self.c.name].unique()),
                        {'Striker', 'D-man'})
        self.c.frequency_cutoff = 1
        self.c.analysis_drop_infrequent(self.map_)
        self.assertEqual(set(self.map_[self.c.name].unique()),
                         {'D-man', np.nan})

    def test_analysis_remove_ambigious(self):
        # Checks the current map status
        self.assertEqual(set(self.map_[self.c.name].unique()),
                         {'Striker', 'D-man'})

        # Sets up the data to handle drop ambigious values
        self.c.ambiguous_values = {"D-man"}
        self.c.analyis_remove_ambiguious(self.map_)

        # Checks the remapping
        self.assertEqual(set(self.map_[self.c.name].unique()),
                         {'Striker', np.nan})

    def test_analysis_convert_to_numeric(self):
        self.assertEqual(self.c.order, ["Striker", "D-man", "Goalie"])
        self.c.analysis_convert_to_numeric(self.map_)
        self.assertEqual(self.c.order, [0, 1, 2])
        pdt.assert_series_equal(self.map_['position'],
                                pd.Series(data=[0, 1, 1],
                                          index=['Bitty', 'Ransom', 'Holster'],
                                          name='position',
                                          )
                                )
        self.assertEqual(self.c.log[0]['transformation'],
                         'Striker >>> 0 | D-man >>> 1 | Goalie >>> 2')

    def test_analysis_label_order(self):
        self.assertEqual(self.c.order, ["Striker", "D-man", "Goalie"])
        self.c.analysis_label_order(self.map_)
        self.assertEqual(self.c.order,
                         ["(0) Striker", "(1) D-man", "(2) Goalie"]
                         )
        pdt.assert_series_equal(self.map_['position'],
                                pd.Series(data=["(0) Striker", "(1) D-man",
                                                "(1) D-man"],
                                          index=['Bitty', 'Ransom', 'Holster'],
                                          name='position',
                                          )
                                )
        self.assertEqual(self.c.log[0]['transformation'],
                         'Striker >>> (0) Striker | D-man >>> (1) D-man |'
                         ' Goalie >>> (2) Goalie')

    def test_analysis_remap_null(self):
        self.c.missing = ['Striker']
        self.assertEqual(self.c.order, ["Striker", "D-man", "Goalie"])
        self.c.analysis_remap_null(self.map_)
        self.assertEqual(self.c.order, ['D-man', 'Goalie'])
        pdt.assert_series_equal(self.map_['position'],
                                pd.Series([np.nan, 'D-man', 'D-man'],
                                          index=['Bitty', 'Ransom', 'Holster'],
                                          name='position'))

    def test_validate_map_pass(self):
        self.c.validate_map(self.map_)

    def test_validate_map_fail(self):
        self.c.name = 'years_on_team'
        with self.assertRaises(ValueError):
            self.c.validate_map(self.map_)

if __name__ == '__main__':
    main()