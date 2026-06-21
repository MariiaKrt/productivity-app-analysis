
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ---------------------------------------------------------------------------------------------
# 1. function analyzing numeric columns: validating expected ranges, and visualizing distributions
# ---------------------------------------------------------------------------------------------

def exp_range(column_name, table_name, table, column, table_for_checks, table_for_result, allowable_min_incl = 0, allowable_max_excl = 1, bins_size = 1, result = 'both'):

  """
    Summarize the distribution of a numeric column and check whether
    its values fall within an expected range.

    Parameters
    ----------
    column_name : str
        Readable name displayed in chart titles
    table_name : str
        Readable name displayed in chart titles
    table : pandas.DataFrame
        Table containing the column to analyze
    column : str
        Numeric column to analyze
    allowable_min_incl : int or float, optional
        Minimum allowed value, inclusive
    allowable_max_excl : int or float, optional
        Maximum allowed value, exclusive
    bins_size : int, optional
        Width of histogram bins
    """

  if allowable_min_incl >= allowable_max_excl:
    return 'Min allowable value should be smaller then max allowable value'

  if column not in table.columns:
    raise ValueError(f'{column} is not found')

  if table[column].dropna().empty:
    raise ValueError(f'{column} contains no valid values')

  if bins_size <= 0:
    return 'Bin size should be positive'

  if not pd.api.types.is_numeric_dtype(table[column]):
    return 'Column should be numeric'

  null_values = sum(table[column].isna())
  null_values_share = sum(table[column].isna()) / len(table[column])
  values = table[column].dropna()
  min_value = float(values.min())
  max_value = float(values.max())
  mean = float(round(values.mean(), 4))
  median = values.median()
  min_check = min_value >= allowable_min_incl
  max_check = max_value < allowable_max_excl
  q25 = float(np.quantile(values, 0.25))
  q75 = float(np.quantile(values, 0.75))
  iqr = q75 - q25
  skewness = round(float(stats.skew(values, bias = False)),4)

  stat_result =  {
      'Null values & share:' : [null_values, round(null_values_share * 100,1)],
      'Allowed range:' : [allowable_min_incl, allowable_max_excl],
      'Actual column range:' : [min_value, max_value],
      'Minimum check passed:' : min_check,
      'Maximum check passed:' : max_check,
      'Mean:' : f"{mean:.4f}",
      'Median:' : f"{median:.4f}",
      '25th percentile:' : f"{q25:.4f}",
      '75th percentile:' : f"{q75:.4f}",
      'IQR:' : f"{iqr:.4f}",
      'Skewness:' : f"{skewness:.4f}"
    }

  stat_result = pd.DataFrame([stat_result]).T
  stat_result.columns = ['Values']

  if (min_check != True) | (max_check != True):
    column_limit_values = values[(values < allowable_min_incl) | (values >= allowable_max_excl)]
    check_name = f"{table_name}_{column_name}_column_limit_values"
    table_for_checks[check_name] = column_limit_values
    table_for_result.append(('Min/Max limits',
                       f'FAIL | Minimum limit rule is {min_check}, Maximum limit rule is {max_check} for {column_name}'\
                        if ((min_check != True) | (max_check != True)) \
                        else f'PASS | Minimum limit rule is {min_check}, Maximum limit rule is {max_check} for {column_name}',
                        check_name))
  else:
    table_for_result.append(('Min/Max limits',
                  f'FAIL | Minimum limit rule is {min_check}, Maximum limit rule is {max_check} for {column_name}'\
                  if ((min_check != True) | (max_check != True)) \
                  else f'PASS | Minimum limit rule is {min_check}, Maximum limit rule is {max_check} for {column_name}',
                  None))

  if result == 'table':
    return stat_result

  elif result in ('both', 'viz'):
    fig, ax = plt.subplots(1,2, figsize = (18,5))

    values[(values >= allowable_min_incl) & (values < allowable_max_excl)].hist(bins = range(int(min_value), int(max_value) + bins_size, bins_size), color = '#5EE8C3', grid = False, ax = ax[0], label = 'Within limits')
    values[(values < allowable_min_incl) | (values >= allowable_max_excl)].hist(bins = range(int(min_value), int(max_value) + bins_size, bins_size), color = '#ED829F', grid = False, ax = ax[0], label = 'Outside limits')
    ax[0].set_title(f'{column_name.capitalize()} histogram: absolute values and limits')
    ax[0].axvline(allowable_min_incl, color = 'black')
    ax[0].axvline(allowable_max_excl, color = 'black', label = 'Limits')
    ax[0].legend(loc = 'upper left', bbox_to_anchor=(0.2, -0.1), ncol=4)

    table[column].hist(bins = range(int(min_value), int(max_value) + bins_size, bins_size), color = '#82D4ED', grid = False, ax = ax[1])
    ax[1].set_title(f'{column_name.capitalize()} histogram: absolute values and stats')
    ax[1].axvline(mean, linestyle = 'dashed', color = '#29B6E0', label = 'Mean')
    ax[1].axvline(median, linestyle = 'dashed', color = '#D182ED', label = 'Median')
    ax[1].axvline(q25, linestyle = 'dotted', color = '#D3D3D3')
    ax[1].axvline(q75, linestyle = 'dotted', color = '#D3D3D3', label = 'IQR')
    ax[1].axvspan(q25, q75, alpha = 0.2, color = '#D3D3D3', zorder = 0)
    ax[1].legend(loc = 'upper left', bbox_to_anchor=(0.2, -0.1), ncol=4)

  if result == 'both':
    return stat_result, fig
  elif result == 'viz':
    return fig


# ------------------------------------------------------------------------------
# 2. helper function for creating bar or linechart
# ------------------------------------------------------------------------------

def line_chart_formatting (table,
                           x,
                           y,
                           chart_type = 'line',
                           title = None,
                           main_color = '#70CFFF',
                           span = False,
                           span_period = 'Year',
                           span_color = '#EAEBF0',
                           data_labels = True,
                           label = None,
                           min_y = 0,
                           ax = None
                           ):

  """
  Plot a formatted line or bar chart for monthly product metrics

  Parameters
  ----------
  table : pandas.DataFrame
      DataFrame containing x and y columns
  x : str
      Datetime column for the x-axis
  y : str
      Numeric metric column for the y-axis
  chart_type : str, default "line"
      Chart type. Must be either 'line' or 'bar'
  title : str, optional
      Chart title
  main_color : str, default "#70CFFF"
      Main chart color
  span : bool, default False
      If True, adds background shading by year or month
  span_period : str, default "Year"
      Background shading period. Must be either 'Year' or 'Month'
  span_color : str, default "#EAEBF0"
      Color used for chart spines and background shading
  data_labels : bool, default True
      If True, adds value labels to each point or bar
  label : str, optional
      Legend label
  ax : matplotlib.axes.Axes, optional
      Existing matplotlib axis. If None, a new chart is created
  """

  if x not in table.columns:
    raise ValueError (f'{x} is not found')

  if y not in table.columns:
    raise ValueError (f'{y} is not found')

  if not pd.api.types.is_datetime64_any_dtype(table[x]):
    raise ValueError (f'{x} must be date type')

  if not pd.api.types.is_numeric_dtype(table[y]):
    raise ValueError (f'{y} must be numeric type')

  if span and span_period not in ('Year', 'Month'):
    raise ValueError ('span_period must be "Year" or "Month"')

  if chart_type not in ('line', 'bar'):
    raise ValueError ('chart_type must be "line" or "bar"')

  if ax is None:
    _, ax = plt.subplots(figsize=(10, 5))

  if chart_type == 'line':
    ax.plot(table[x], table[y], color = main_color, label = label)
  if chart_type == 'bar':
    ax.bar(table[x], table[y], width = 20, color = main_color, label = label)

  min_limit = table[x].min().to_period('M').to_timestamp()
  max_limit = table[x].max().to_period('M').to_timestamp(how = 'end')

  ax.set_xlim(min_limit, max_limit)

  ax.set_ylim(bottom = min_y)

  if title != None:
    ax.set_title(title)

  ax.spines["top"].set_color(span_color)
  ax.spines["bottom"].set_color(span_color)
  ax.spines["left"].set_color(span_color)
  ax.spines["right"].set_color(span_color)

  if span == True:
    for n in pd.date_range(start = min_limit, end = max_limit, freq = ('2YS' if span_period == 'Year' else 'MS')):
      ax.axvspan(n, n + (pd.DateOffset(years = 1) if span_period == 'Year' else pd.DateOffset(months = 1)), color = span_color, alpha = 0.4, zorder = 0)

  if data_labels == True:
    for k, z in zip(table[x], table[y]):
      ax.annotate(z, (k, z), fontsize = 9)

  
