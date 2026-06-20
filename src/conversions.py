
import pandas as pd
import numpy as np

# ------------------------------------------------------------------------------
# 1.0. helper function to calculate CRs
# ------------------------------------------------------------------------------

def maturity_flags (table, date_column_start, date_column_end, window):
  """
  Create maturity and conversion flags for fixed-window conversion analysis
  Function changes the input table by adding new column to it

  Parameters
  ----------
  table : pandas.DataFrame
      User-level table with start date and end date
  date_column_start : str
      Start date of the conversion window
  date_column_end : str
      End date - conversion event date
  window : int
      Conversion window in days
  """

  if date_column_start not in table.columns:
    raise ValueError (f'{date_column_start} is not found')

  if date_column_end not in table.columns:
    raise ValueError (f'{date_column_end} is not found')

  if not pd.api.types.is_datetime64_any_dtype(table[date_column_start]):
    raise ValueError (f'{date_column_start} must be date type')

  if not pd.api.types.is_datetime64_any_dtype(table[date_column_end]):
    raise ValueError (f'{date_column_end} must be date type')

  # getting max date in the source
  limit_maturity_date = table[date_column_start].max()

  # cohorts maturity window
  maturity_window = limit_maturity_date - pd.Timedelta(days = window)

  # marking mature cohorts
  table[f'flag_window_{window}_days_{date_column_start[:3]}_to_{date_column_end[:3]}_maturity'] = (table[date_column_start] <= maturity_window)

  # marking mature users
  table[f'flag_window_{window}_days_{date_column_start[:3]}_to_{date_column_end[:3]}_conversion'] = ((table[date_column_start] <= maturity_window)
                                                           & (table[date_column_end] <= table[date_column_start] + pd.Timedelta(days = window)))



# ------------------------------------------------------------------------------
# 1.1. helper function to calculate CRs
# ------------------------------------------------------------------------------

def bulk_maturity_flags (tables):

  """
  Apply maturity_flags() for multiple conversion windows

  Parameters
  ----------
  tables : list of tuple
      Each tuple should contain:
      (table, date_column_start, date_column_end, window)
  """

  for table, date_column_start, date_column_end, window in tables:
    maturity_flags (table, date_column_start, date_column_end, window)


# ------------------------------------------------------------------------------
# 1.2. helper function to calculate CRs
# ------------------------------------------------------------------------------

def cr_calculation (table, list_of_group_columns, denominator_column, numerator_column, new_column_name, rounded_number = 2):

  """
  Calculate conversion rate by cohort period

  Parameters
  ----------
  table : pandas.DataFrame
      Table containing cohort date, denominator flag, and numerator flag
  list_of_group_columns : list
      Columns to group the data by
  denominator_column : str
      Column identifying eligible mature users
  numerator_column : str
      Column identifying users who converted within the selected window
  new_column_name : str
      Name of the resulting conversion-rate column

  Returns
  -------
  pandas.DataFrame
      Aggregated table with denominator, numerator, and conversion rate
  """

  if denominator_column not in table.columns:
    raise ValueError (f'{denominator_column} is not found')

  if numerator_column not in table.columns:
    raise ValueError (f'{numerator_column} is not found')

  if not (pd.api.types.is_numeric_dtype(table[denominator_column]) or pd.api.types.is_bool_dtype(table[denominator_column])):
    raise ValueError (f'{denominator_column} must be numeric or bool type')

  if not (pd.api.types.is_numeric_dtype(table[numerator_column]) or pd.api.types.is_bool_dtype(table[numerator_column])):
    raise ValueError (f'{numerator_column} must be numeric or bool type')

  if not list_of_group_columns:
    raise ValueError('list_of_group_columns cannot be empty')

  if not isinstance(list_of_group_columns, list):
    raise ValueError('list_of_group_columns must be list type')

  missing_group_columns = [col for col in list_of_group_columns if col not in table.columns]

  if missing_group_columns:
      raise ValueError(f'{missing_group_columns} is/are not found')

  new_table = (table.groupby(list_of_group_columns, as_index = False)
                      [[denominator_column, numerator_column]]
                      .sum())

  new_table[new_column_name] = np.where(new_table[denominator_column] == 0, 
                                        np.nan, 
                                        round(new_table[numerator_column] / new_table[denominator_column] * 100, rounded_number))

  return new_table
