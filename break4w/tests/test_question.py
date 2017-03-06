from unittest import TestCase, main

import pandas as pd
import numpy as np
import numpy.testing as npt

from break4w.question import Question


class QuestionTest(TestCase):

    def setUp(self):
        self.name = 'player_name'
        self.description = 'Samwell Hockey Players'
        self.dtype = str

        self.map_ = pd.DataFrame([['Bitty', 'Ransom', 'Holster'],
                                  ['2', '4', '4'],
                                  ['False', 'True', 'True']],
                                 index=['player_name', 'years_on_team',
                                        'team_captain']).T
        self.q = Question(name=self.name,
                          description=self.description,
                          dtype=self.dtype,
                          free_response=True,
                          )

    def test_init_default(self):
        self.assertEqual(self.name, self.q.name)
        self.assertEqual(self.description, self.q.description)
        self.assertEqual(self.dtype, self.q.dtype)
        self.assertEqual('Player Name', self.q.clean_name)
        self.assertEqual('Question', self.q.type)
        self.assertTrue(self.q.free_response)
        self.assertFalse(self.q.mimarks)
        self.assertFalse(self.q.ontology)
        self.assertFalse(self.q.ebi_required)
        self.assertFalse(self.q.qiita_required)
        self.assertEqual(self.q.missing, None)

    def test_init_error_name(self):
        with self.assertRaises(TypeError):
            self.q = Question(name=1,
                              description=self.description,
                              dtype=self.dtype,
                              )

    def test_init_error_description(self):
        with self.assertRaises(TypeError):
            self.q = Question(name=self.name,
                              description=self.dtype,
                              dtype=self.dtype,
                              )

    def test_init_error_dtype(self):
        with self.assertRaises(TypeError):
            self.q = Question(name=self.name,
                              description=self.description,
                              dtype=self.description,
                              )

    def test_init_error_clean_name(self):
        with self.assertRaises(TypeError):
            self.q = Question(name=self.name,
                              description=self.description,
                              dtype=self.dtype,
                              clean_name=self.dtype
                              )

    def test_check_map_pass(self):
        self.q.check_map(self.map_)

    def test_check_map_error(self):
        self.map_.rename(columns={'player_name': 'question'}, inplace=True)
        with self.assertRaises(ValueError):
            self.q.check_map(self.map_)

    def test_remap_dtype_bool_str(self):
        q = Question(name='team_captain',
                     description='who is has the C or AC',
                     dtype=bool
                     )
        self.assertTrue(
            self.map_['team_captain'].apply(lambda x: isinstance(x, str)).all()
            )
        q.remap_dtype(self.map_)
        npt.assert_array_equal(np.array([False, True, True]),
                               self.map_['team_captain'].values)

    def test_remap_dtype_bool(self):
        self.map_['team_captain'] = self.map_['team_captain'] == 'True'
        npt.assert_array_equal(np.array([False, True, True]),
                               self.map_['team_captain'].values)
        q = Question(name='team_captain',
                     description='who is has the C or AC',
                     dtype=bool
                     )
        q.remap_dtype(self.map_)
        npt.assert_array_equal(np.array([False, True, True]),
                               self.map_['team_captain'].values)

    def test_remap_dtype_bool_int(self):
        self.map_['team_captain'] = \
            (self.map_['team_captain'] == 'True').astype(int)
        npt.assert_array_equal(np.array([0, 1, 1]),
                               self.map_['team_captain'].values)
        q = Question(name='team_captain',
                     description='who is has the C or AC',
                     dtype=bool
                     )
        q.remap_dtype(self.map_)
        npt.assert_array_equal(np.array([False, True, True]),
                               self.map_['team_captain'].values)

    def test_remap_dtype_int(self):
        q = Question(name='years_on_team',
                     description=('The number of years a player has played '
                                  'hockey for Samwell'),
                     dtype=float)
        q.remap_dtype(self.map_)
        npt.assert_array_equal(np.array([2, 4, 4]),
                               self.map_['years_on_team'].values)

if __name__ == '__main__':
    main()