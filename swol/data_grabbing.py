import pandas as pd
from datetime import datetime
# consolodate data

class WorkoutData():
    """
    class for pulling and formatting data from xls
    """

    def __init__(self, data_path=None, drop_on='Rep', fill_on='Type'):
        """
        Parameters
        ----------
        data_path: str
            path to xls file to be processed
            defaults to '../data/workout_log.xls'
        drop_on: str
            column title string on which null values will be dropped
            defaults to 'Rep'
        fill_on: str
            column title string on which values will be interpolated
            the structure of the document has missing values between
            sets of exercises. This fills between missing values.
            deaults to 'Type'
        """

        if not data_path:
            self.data_path = '../data/workout_log.xls'
        else:
            self.data_path = data_path

        self.drop_on=drop_on
        self.fill_on = fill_on
        self.drop_routine = ['LEGS']

        self.rename_routine = {
            'Dumbbell deadlift':'Squats',
            'Free Squats':'Squats',
            'Bench pull / row': 'Rows',
            'Squat-Rows' : 'Rows'
        }


    def get_xls_data(self, data_path):
        """
        access xls data and parse into sheets
        """

        xls = pd.ExcelFile(data_path)
        self.sheet_names = xls.sheet_names

        sheet_dict = {}
        for sheet_name in xls.sheet_names:
            sheet_dict[sheet_name] = xls.parse(sheet_name)

        return sheet_dict


    def aggregate_sheets(self, sheet_dict):
        """
        Combine multiple sheets in an xls book into a single dataframe.
        Includes some basic preprocessing of column names and
        NA removal.
        """
        agg_df = pd.DataFrame()
        for key, val in sheet_dict.items():
            date = key.split(' ')[0]
            val = self.clean_sheet(val, self.drop_on, self.fill_on)
            val['Date'] = datetime.strptime(date,'%Y-%m-%d')
            agg_df = agg_df.append(val)

        agg_df.set_index('Date',inplace=True)

        agg_df = agg_df.rename(axis=1, mapper={agg_df.columns[4]:'Notes',
                                                 agg_df.columns[5]:'Notes2'})

        return agg_df


    def clean_sheet(self, sheet, drop_on=None, fill_on=None,
                    convert_numeric=['Weight','Rep']
                    ):
        """
        Drop null values and interpolate string entries between rows

        Parameters
        ----------
        sheet: pandas.DataFrame
            dataframe subset from xls workbook
        drop_on: str
            column title string on which null values will be dropped
            defaults to 'Rep'
        fill_on: str
            column title string on which values will be interpolated
            the structure of the document has missing values between
            sets of exercises. This fills between missing values.
            deaults to 'Type'
        convert_numeric: list(str)
            column titles to convert to numeric
            coerces strings to NaN and fills with 0s


        Returns
        -------
        sheet : pandas.DataFrame
            cleaned dataframe
        """
        # drop empty sets
        if drop_on:
            sheet = sheet[~sheet[drop_on].isna()]

        # interpolate NaNs
        if fill_on:
            sheet[fill_on].interpolate(method="pad", inplace=True)

        # convert to numeric
        for col in convert_numeric:
            sheet[col] = sheet[col].apply(
                                          pd.to_numeric,
                                          errors='coerce').fillna(0)


        return sheet

    def clean_routines(self, df, drop_routine=None, rename_routine=None):
        """
        consolodate naming conventions of different rountines

        Parameters
        ----------
        df : pandas.DataFrame
            agg_df export from aggregate_sheets
        drop_routine : list(str)
            list of routines to drop from 'Type'
        rename_routine : dict
            dict of routines to rename in format {old_name:new_name}

        Returns
        -------
        df
        """
        if drop_routine:
            for routine in drop_routine:
                df = df[~(df['Type'] == routine)]

        if rename_routine:
            for key, val in rename_routine.items():
                df.Type.replace(key, val, inplace=True)

        return df


    def get_data(self):
        """
        Master function for pulling and preprocessing data

        Returns aggregated dataframe

        """
        sheet_dict = self.get_xls_data(self.data_path)
        self.agg_df = self.aggregate_sheets(sheet_dict)
        self.agg_df = self.clean_routines(df=self.agg_df,
                                     drop_routine=self.drop_routine,
                                     rename_routine=self.rename_routine)

        return self.agg_df
