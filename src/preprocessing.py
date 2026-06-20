
import pandas as pd

# ------------------------------------------------------------------------------
# 1. function applying pd.to_datetime in bulk
# ------------------------------------------------------------------------------

def bulk_convert_to_datetime(columns):

    """
    Convert multiple DataFrame columns to datetime

    Parameters
    ----------
    columns : list of tuples
        Each tuple contains:
        (DataFrame, column_name)
    """

    for table, column in columns:
        table[column] = pd.to_datetime(table[column])



# ------------------------------------------------------------------------------
# 2. function checking duplicates in the columns (primary keys)
# ------------------------------------------------------------------------------

def no_duplicates (table, column, table_for_checks, table_for_result, table_name = None):

    """
    Returns a summary of duplicated values in a selected column

    Parameters:
    ---------
    table : pandas.DataFrame
        The table to check
    column : str
        Column that is expected to have only unique values
    table_for_checks : dict 
        Stores rows that failed the check 
    table_for_result : list 
        Stores the check summary 
    table_name : str, optional 
        Name used in the output message

    """
    duplicate_count = sum(table[column].duplicated())
    result = f'FAIL | {duplicate_count} {column}s of {table[column].nunique()} are duplicated in {table_name}' \
            if duplicate_count != 0 \
            else f'PASS | {duplicate_count} {column}s of {table[column].nunique()} are duplicated in {table_name}'

    if duplicate_count != 0:
      duplicate_rows = table[table[column].duplicated(keep = False)].sort_values(by = column)
      check_name = f'{table_name}_{column}_duplicates'
      table_for_checks[check_name] = duplicate_rows
      table_for_result.append(['Duplicates', result, check_name])
    else:
      table_for_result.append(['Duplicates', result, None])

    return result



# ------------------------------------------------------------------------------
# 2.1. function checking duplicates in the columns (primary keys)
# ------------------------------------------------------------------------------

def bulk_dupl_check(checks):

  """
  Runs duplicate value checks for multiple DataFrame columns

  Each tuple must contain:
      (DataFrame, column_name, table_for_checks, table_for_result, table_name)
  """

  res = []
  for table, column, table_for_checks, table_for_result, table_name in checks:
    r = no_duplicates(table, column, table_for_checks, table_for_result, table_name)
    res.append(r)
  return res



# ------------------------------------------------------------------------------
# 3. function checking referential integrity (foreign keys -> primary keys)
# ------------------------------------------------------------------------------

def referential_integrity (table1, table2, column, table1_name, table2_name, table_for_checks, table_for_result, join_direction = 'outer'):

  """
  Count identifier values that do not match between two tables

  Parameters
  ----------
  table1 : pandas.DataFrame
      Left table
  table2 : pandas.DataFrame
      Right table
  column : str
      Column used to link the tables
  table_for_checks : dict 
      Stores rows that failed the check 
  table_for_result : list 
      Stores the check summary 
  join_direction : str
      Join type: 'left' or 'outer'
  """

  if join_direction not in ('left', 'outer'):
    raise ValueError('join_direction can only be "outer" or "left"')

  t1 = pd.DataFrame(table1[column].unique()).dropna().rename(columns={0 : column + '_x'})
  t2 = pd.DataFrame(table2[column].unique()).dropna().rename(columns={0 : column + '_y'})
  union = t1.merge(t2, left_on = column + '_x', right_on = column + '_y', how = join_direction)

  if join_direction == 'outer':
    t = union[(union[column + '_x'].isna()) | (union[column + '_y'].isna())]
    x = len(t)
  elif join_direction == 'left':
    t = union[union[column + '_y'].isna()]
    x = len(t)

  result =  f'FAIL | {x} {column}s in {table1_name} & {table2_name} do not match' \
              if x != 0 \
              else f'PASS | {x} {column}s in {table1_name}, {table2_name} do not match'

  if x != 0:
    columns_referential_integrity = t
    check_name = f"{table1_name}_and_{table2_name}_{column}_referential_integrity"
    table_for_checks[check_name] = columns_referential_integrity
    table_for_result.append(['Referential integrity', result, check_name])
  else:
    table_for_result.append(['Referential integrity', result, None])

  return result


def bulk_referential_integrity (data_check):

  """
  Run referential-integrity checks for multiple table relationships

  Each tuple must contain:
  (table1, table2, column, table1_name, table2_name, table_for_checks, table_for_result, join_direction)
  """

  res = []
  for table1, table2, column, table1_name, table2_name, table_for_checks, table_for_result, join_direction in data_check:
    r = referential_integrity(table1, table2, column, table1_name, table2_name, table_for_checks, table_for_result, join_direction)
    res.append(r)
  return res



# ------------------------------------------------------------------------------
# 4. function checking date rules
# ------------------------------------------------------------------------------

def dates_logic (table1,
                 table2,
                 date_column1,
                 date_column2,
                 link_column1,
                 link_column2,
                 table_for_checks, 
                 table_for_result,
                 table_name1 = None,
                 table_name2 = None,
                 same_table = False,
                 how = '>'):

    """
    Count rows that do not follow the expected date rule.

    Parameters
    ----------
    table1 : pandas.DataFrame
        First table to check
    table2 : pandas.DataFrame or None
        Second table to join. Use None when both dates are in the same table
    date_column1 : str
        First date column
    date_column2 : str
        Second date column
    link_column1 : str
        Join column from the first table
    link_column2 : str or None
        Join column from the second table
    table_for_checks : dict 
      Stores rows that failed the check 
    table_for_result : list 
        Stores the check summary 
    table_name1 : str, optional
        First table name shown in the result
    table_name2 : str, optional
        Second table name shown in the result
    same_table : bool
        True when both date columns are in the same table
    how : str
        Comparison rule used to identify invalid rows: '>', '>=', or '!='
    """

    if not how in ('>', '>=', '!='):
      raise ValueError('Invalid operator. Allowed: >, >=, !=')

    columns_to_convert = [(table1, date_column1),
                         (table2, date_column2)]
    bulk_convert_to_datetime (columns_to_convert)


    if same_table == False:

      t = table1.merge(table2, left_on = link_column1, right_on = link_column2, how = 'left')[[date_column1, date_column2]]
      t = t.query(f"`{date_column1}` {how} `{date_column2}`")
      x = len(t)
      result = f'FAIL | {x} {date_column1}s {how} {date_column2} in {table_name1} x {table_name2}' \
                 if x != 0 \
                 else f'PASS | {x} {date_column1}s {how} {date_column2} in {table_name1} x {table_name2}'

    else:
      t = table1.query(f"`{date_column1}` {how} `{date_column2}`")
      x = len(t)
      result = f'FAIL | {x} {date_column1}s {how} {date_column2} in {table_name1}' \
            if x != 0 \
            else f'PASS | {x} {date_column1}s {how} {date_column2} in {table_name1}'

    if x != 0:
      date_columns_logic = t
      check_name = f'{date_column1}_{date_column2}_date_columns_logic'
      table_for_checks[check_name] = date_columns_logic
      table_for_result.append(['Date columns rules', result, check_name])
    else:
      table_for_result.append(['Date columns rules', result, None])

    return result

def bulk_dates_check (date_checks):

  """
  Runs dates_logic for multiple DataFrames

  Each tuple must contain:
    (table1, table2, 
    date_column1, date_column2,
    link_column1, link_column2, 
    table_for_checks, table_for_result, 
    table_name1, table_name2,
    same_table, how)
  """

  res = []
  for table1, table2, date_column1, date_column2, link_column1, link_column2, table_for_checks, table_for_result, table_name1, table_name2, selfjoin, how in date_checks:
    r =  dates_logic (table1, table2, date_column1, date_column2, link_column1, link_column2, table_for_checks, table_for_result, table_name1, table_name2, selfjoin, how)
    res.append(r)
  return res



# ---------------------------------------------------------------------------------------
# 5. function validating whether the difference between two dates matches an expected period
# ---------------------------------------------------------------------------------------

def difference_period (table, table_name, column_start, column_end, expected_value, unit, table_for_checks, table_for_result, nullable_end = False):

  """
  Count rows where the difference between two dates does not match the expected period

  Parameters
  ----------
  table : pandas.DataFrame
    Table containing the date columns
  table_name : str
    Table name
  column_start : str
    Column containing the start date
  column_end : str
    Column containing the end date
  expected_value : int
    Expected number of days, months, or years between the dates
  unit : str
    Unit used for comparison: 'day', 'month', 'year'
  table_for_checks : dict 
    Stores rows that failed the check 
  table_for_result : list 
      Stores the check summary 
  nullable_end : bool, optional
    If True, rows with missing end dates are excluded from the check
  """

  if not isinstance(expected_value, int):
    raise ValueError('expected_values should be of int type')

  if unit not in ('day', 'month', 'year'):
    raise ValueError('unit can only contain "day", "month", or "year"')

  columns_to_convert = [(table, column_start),
                        (table, column_end)]

  bulk_convert_to_datetime (columns_to_convert)

  if nullable_end:
    table = table[[column_start, column_end]].dropna()

  if unit == 'day':
    t = table[(table[column_end] - table[column_start]).dt.days.astype(int) != expected_value]
    x = len(t)

  if unit in ('month', 'year'):
    t = table[table[column_start] + pd.DateOffset(**{f'{unit}s' : expected_value}) != table[column_end]]
    x = len(t)

  result = f'FAIL | {x} rows where difference between {column_start} and {column_end} is not {expected_value} {unit}(s)' \
          if x != 0 \
          else f'PASS | {x} rows where difference between {column_start} and {column_end} is not {expected_value} {unit}(s)'

  if x != 0:
    check_name = f"{table_name}_{column_start}_{column_end}_expected_period"
    table_for_checks[check_name] = t
    table_for_result.append(['Expected period', result, check_name])
  else:
    table_for_result.append(['Expected period', result, None])

  return result

def bulk_periods_check (data_check):

  """
  Runs difference_period for multiple DataFrames

  Each tuple must contain:
    (table, column_start, column_end, constant, unit, table_for_checks, table_for_result, nullable)
  """

  res = []
  for table, trials_name, column_start, column_end, constant, unit, table_for_checks, table_for_result, nullable_end in data_check:
    r =  difference_period (table, trials_name, column_start, column_end, constant, unit, table_for_checks, table_for_result, nullable_end)
    res.append(r)
  return res


# ------------------------------------------------------------------------------
# 6.0. helper function for cutting dates to month or week
# ------------------------------------------------------------------------------

def date_to_month_week (table,
                   column,
                   period_type = 'Month',
                   new_column_name = None,
                   period_start = True):


  """
  Create a monthly or weekly period column from a datetime column

  Parameters
  ----------
  table : pandas.DataFrame
      DataFrame containing the source date column
  column : str
      Datetime column
  period_type : str, default 'Month'
      Period granularity. Must be either 'Month or 'Week'
  new_column_name : str
      Name of the new period column
  period_start : bool, default True
      If True, returns the start of the period
      If False, returns the end of the period
  """

  if column not in table.columns:
    raise ValueError (f'{column} is not found')

  if not pd.api.types.is_datetime64_any_dtype(table[column]):
    raise ValueError (f'{column} must be of date type')

  if period_start not in (True, False):
    raise ValueError ('period_start must be True or False')

  if period_type not in ('Month', 'Week'):
    raise ValueError ('period_type must be "Month" or "Week"')

  if period_start:
    if period_type == 'Month':
      table[new_column_name] = table[column].dt.to_period("M").dt.to_timestamp()
    elif period_type == 'Week':
      table[new_column_name] = table[column] - pd.to_timedelta(table[column].dt.weekday.astype('int'), unit = 'D')

  elif period_start == False:
    if period_type == 'Month':
      table[new_column_name] = table[column].dt.to_period("M").dt.to_timestamp(how = 'end')
    elif period_type == 'Week':
      table[new_column_name] = table[column] + pd.to_timedelta(6 - table[column].dt.weekday.astype('int'), unit = 'D')


# ------------------------------------------------------------------------------
# 6.1. helper function for cutting dates to month or week
# ------------------------------------------------------------------------------

def bulk_date_to_month_week (tables):
  """
  Apply date_to_month_week() to multiple DataFrames and date columns

  Parameters
  ----------
  tables : list of tuple
      Each tuple should contain:
      (table, column, period_type, new_column_name, period_start)
  """
  for table, column, period_type, new_column_name, period_start in tables:
    date_to_month_week(table, column, period_type, new_column_name, period_start)

