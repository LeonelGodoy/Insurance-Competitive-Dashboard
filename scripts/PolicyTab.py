import pandas as pd
import numpy as np
from scipy.stats import binned_statistic
from math import pi
from bokeh.transform import cumsum
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, WheelZoomTool, LabelSet
from bokeh.models.widgets import Panel, Slider, RangeSlider, Select
from bokeh.layouts import row, WidgetBox, column

companies = ['Progressive', 'Country', 'Auto_Owners',
             'StateFarm', 'USAA', 'Liberty', 'GFB']

companies_comvert = {'Prog Mountain: Total Policy Premium': 'Progressive',
                     'Country Companies (Mutual CMIC): Total Policy Premium': 'Country',
                     'Auto Owners (Auto-Owners): Total Policy Premium': 'Auto_Owners',
                     'State Farm Auto (SFM): Total Policy Premium': 'StateFarm',
                     'USAA Auto (USAA): Total Policy Premium': 'USAA',
                     'LM General Insurance Company (LM Ins Co): Total Policy Premium': 'Liberty',
                     'Farm Bureau Mutual: Total Policy Premium': 'GFB'}

policy_dictionary = {
    'Progressive': ['Progressive_Premium', 'Prog Mountain: Total Policy Premium',
                    '#79b6dc', 'solid', 'Progressive'],
    'Country': ['CMIC_Premium', 'Country Companies (Mutual CMIC): Total Policy Premium',
                '#febe0c', 'solid', 'Country'],
    'Auto_Owners': ['Allstate_Premium', 'Auto Owners (Auto-Owners): Total Policy Premium',
                    '#2f4f4f', 'solid', 'Auto Owners'],
    'StateFarm': ['SFM_Premium', 'State Farm Auto (SFM): Total Policy Premium',
                  '#5e4fa2', 'solid', 'State Farm'],
    'USAA': ['USAA_Premium', 'USAA Auto (USAA): Total Policy Premium',
             '#65c05d', 'solid', 'USAA'],
    'Liberty': ['Liberty_Premium', 'LM General Insurance Company (LM Ins Co): Total Policy Premium',
                '#ac5370', 'solid', 'Liberty'],
    'GFB': ['GFB_Premium', 'Farm Bureau Mutual: Total Policy Premium',
            '#d53e4f', 'dashed', 'Georgia Farm']}

def _tab(policy_data):
    def make_dataset_distribution(policy_data, range_start=0, range_end=1000, bin_width=20, target_column='Age Max'):
        """
        districts = list of districts we will iterate through
        range_start = start of the slider for the x-axis
        range_end = end of the slider for the x-axis
        bin_width = the amount of bins for which the data will be placed into
        """
        # Check to make sure the start is less than the end!
        assert range_start < range_end, "Start must be less than end!"

        range_extent = range_end - range_start

        # Create a histogram with specified bins and range
        arr_hist, edges = np.histogram(policy_data[target_column],
                                       bins=int(range_extent / bin_width),
                                       range=[range_start, range_end])

        # Divide the counts by the total to get a proportion and create df
        arr_df = pd.DataFrame({'proportion': arr_hist / np.sum(arr_hist),
                               'left': edges[:-1], 'right': edges[1:]})

        # Format the proportion
        arr_df['_proportion'] = ['%0.5f' % proportion for proportion in arr_df['proportion']]

        # Format the interval
        arr_df['_interval'] = ['%d to %d' % (left, right) for left,
                                                              right in zip(arr_df['left'], arr_df['right'])]

        arr_df['count'] = arr_hist

        arr_df['gfb_average_premium'] = binned_statistic(policy_data[target_column],
                                                         policy_data['Farm Bureau Mutual: Total Policy Premium'],
                                                         bins=int(range_extent / bin_width),
                                                         range=[range_start, range_end])[0]
        arr_df['progressive_average_premium'] = binned_statistic(policy_data[target_column],
                                                                 policy_data['Prog Mountain: Total Policy Premium'],
                                                                 bins=int(range_extent / bin_width),
                                                                 range=[range_start, range_end])[0]
        arr_df['country_average_premium'] = binned_statistic(policy_data[target_column],
                                                             policy_data[
                                                                 'Country Companies (Mutual CMIC): Total Policy Premium'],
                                                             bins=int(range_extent / bin_width),
                                                             range=[range_start, range_end])[0]
        arr_df['auto_owners_average_premium'] = binned_statistic(policy_data[target_column],
                                                                 policy_data[
                                                                     'Auto Owners (Auto-Owners): Total Policy Premium'],
                                                                 bins=int(range_extent / bin_width),
                                                                 range=[range_start, range_end])[0]
        arr_df['state_farm_average_premium'] = binned_statistic(policy_data[target_column],
                                                                policy_data[
                                                                    'State Farm Auto (SFM): Total Policy Premium'],
                                                                bins=int(range_extent / bin_width),
                                                                range=[range_start, range_end])[0]
        arr_df['usaa_average_premium'] = binned_statistic(policy_data[target_column],
                                                          policy_data['USAA Auto (USAA): Total Policy Premium'],
                                                          bins=int(range_extent / bin_width),
                                                          range=[range_start, range_end])[0]
        arr_df['liberty_average_premium'] = binned_statistic(policy_data[target_column],
                                                             policy_data[
                                                                 'LM General Insurance Company (LM Ins Co): Total Policy Premium'],
                                                             bins=int(range_extent / bin_width),
                                                             range=[range_start, range_end])[0]
        # Convert dataframe to column data source
        return ColumnDataSource(arr_df)

    def make_plot_distribution(src):
        # Blank plot with correct labels
        p = figure(plot_width=1200, plot_height=250, title='',
                   x_axis_label='Age Max', y_axis_label='Proportion',
                   tools="")

        p.quad(source=src, bottom=0, top='proportion',
               left='left', right='right',
               color='blue', fill_alpha=0.5,
               hover_fill_color='blue',
               hover_fill_alpha=1.0, line_color='blue')

        # Hover tool with vline mode
        hover = HoverTool(tooltips=[
            ('Policy Count', '@count'),
            ('Interval', '[@_interval)'),
            ('Proportion', '@_proportion{%0.0}')],
            mode='vline', toggleable=False)

        p.add_tools(hover)
        p.toolbar.logo = None
        return p

    def make_plot_premium(src):
        """
        Creates the graph based on the inputed source
        """
        #        sourcedataframe = pd.DataFrame.from_dict(src.data)
        # Blank plot with correct labels
        p = figure(plot_width=1200, plot_height=250, title='',
                   x_axis_label='', y_axis_label='Premium',
                   tools="pan,wheel_zoom,reset")
        #
        p.line(x='left', y='progressive_average_premium', source=src, color='#79b6dc',
               line_width=4, legend='Progressive')
        p.circle(x='left', y='progressive_average_premium', source=src, color='#79b6dc',
                 fill_color='white', size=6, legend='Progressive', name='Progressive')

        p.line(x='left', y='country_average_premium', source=src, color='#febe0c',
               line_width=4, legend='Country')
        p.circle(x='left', y='country_average_premium', source=src, color='#febe0c',
                 fill_color='white', size=6, legend='Country', name='Country')

        p.line(x='left', y='auto_owners_average_premium', source=src, color='#2f4f4f',
               line_width=4, legend='Auto Owners')
        p.circle(x='left', y='auto_owners_average_premium', source=src, color='#2f4f4f',
                 fill_color='white', size=6, legend='Auto Owners', name='Auto Owners')

        p.line(x='left', y='state_farm_average_premium', source=src, color='#5e4fa2',
               line_width=4, legend='State Farm')
        p.circle(x='left', y='state_farm_average_premium', source=src, color='#5e4fa2',
                 fill_color='white', size=6, legend='State Farm', name='State Farm')

        p.line(x='left', y='usaa_average_premium', source=src, color='#65c05d',
               line_width=4, legend='USAA')
        p.circle(x='left', y='usaa_average_premium', source=src, color='#65c05d',
                 fill_color='white', size=6, legend='USAA', name='USAA')

        p.line(x='left', y='liberty_average_premium', source=src, color='#ac5370',
               line_width=4, legend='Liberty')
        p.circle(x='left', y='liberty_average_premium', source=src, color='#ac5370',
                 fill_color='white', size=6, legend='Liberty', name='Liberty')

        p.line(x='left', y='gfb_average_premium', source=src, color='#d53e4f',
               line_width=4, legend='Georgia Farm')
        p.circle(x='left', y='gfb_average_premium', source=src, color='#d53e4f',
                 fill_color='white', size=6, legend='Georgia Farm', name='Georgia Farm')

        # Hover tool with vline mode
        p.add_tools(HoverTool(names=['Progressive'], tooltips=[
            ('Progressive Average Premium', '@progressive_average_premium{$0,}'),
            ('Interval', '[@_interval)')], mode='mouse', toggleable=False))
        p.add_tools(HoverTool(names=['Country'], tooltips=[
            ('Country Average Premium', '@country_average_premium{$0,}'),
            ('Interval', '[@_interval)')], mode='mouse', toggleable=False))
        p.add_tools(HoverTool(names=['Auto Owners'], tooltips=[
            ('Auto Owners Average Premium', '@auto_owners_average_premium{$0,}'),
            ('Interval', '[@_interval)')], mode='mouse', toggleable=False))
        p.add_tools(HoverTool(names=['State Farm'], tooltips=[
            ('State Farm Average Premium', '@state_farm_average_premium{$0,}'),
            ('Interval', '[@_interval)')], mode='mouse', toggleable=False))
        p.add_tools(HoverTool(names=['USAA'], tooltips=[
            ('USAA Average Premium', '@usaa_average_premium{$0,}'),
            ('Interval', '[@_interval)')], mode='mouse', toggleable=False))
        p.add_tools(HoverTool(names=['Liberty'], tooltips=[
            ('Liberty Average Premium', '@liberty_average_premium{$0,}'),
            ('Interval', '[@_interval)')], mode='mouse', toggleable=False))
        p.add_tools(HoverTool(names=['Georgia Farm'], tooltips=[
            ('Georgia Farm Average Premium', '@gfb_average_premium{$0,}'),
            ('Interval', '[@_interval)')], mode='mouse', toggleable=False))

        p.toolbar.logo = None

        p.legend.location = "top_right"
        p.legend.click_policy = "hide"
        p.legend.label_standoff = 10
        p.legend.background_fill_color = "white"
        p.legend.background_fill_alpha = 1
        p.legend.glyph_width = 10
        p.legend.spacing = 1
        p.legend.padding = 10
        p.legend.margin = 0
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)
        return p

    def make_dataset(companies, range_start=0, range_end=1000, target_column='Age Max'):

        subset = policy_data[(range_start <= policy_data[target_column]) & (policy_data[target_column] < range_end)]
        by_companies = {}

        # Iterate through all the districts
        for i, company_name in enumerate(companies):
            # Subset to the companies
            by_companies[company_name] = policy_dictionary[company_name]

        # Overall dataframe
        # ===========================================================================
        x_axis = []
        for i in by_companies:
            x_axis.append(by_companies[i][4])

        data = pd.DataFrame()
        data['x'] = list(x_axis)
        data['top'] = [subset[subset[by_companies[list(
            by_companies.keys())[i]][1]] != 0][by_companies[list(by_companies.keys())[i]][1]].mean()
                       for i in range(len(by_companies.keys()))]
        data['color'] = [by_companies[list(by_companies.keys())[i]][2] for i in range(len(by_companies.keys()))]
        data['text'] = data['top'].apply(lambda x: '$' + '{0:.0f}'.format(x))
        for n, company in enumerate(by_companies):
            value = data['top'][n]
            data[company] = data.apply(lambda row: (1 - (value / row['top'])), axis=1)
            # data[company] = data.apply(lambda row: "{:.0%}".format((1 - (row['top']/value))), axis=1)
            data[company + "_text"] = data.apply(lambda row: ('is more expensive than ' + company +
                                                              ' by ' +
                                                              "{:.0%}".format(row[company]))
            if
            row[company] > 0 else ('' if row[company] == 0 else
                                   'is less expensive than ' + company +
                                   ' by ' +
                                   "{:.0%}".format(row[company])), axis=1)
        # ===========================================================================
        # Convert dataframe to column data source
        return ColumnDataSource(data)

    def make_plot(src):
        # ===========================================================================
        # graphing process starts
        # ===========================================================================
        sourcedataframe = pd.DataFrame.from_dict(src.data)
        x_range = list(sourcedataframe['x'])
        p = figure(title="Average Premium", x_range=list(x_range), width=900, height=300, tools="")
        text_notation = LabelSet(x='x', y='top', text='text', text_font_size="10pt",
                                 text_color='white', text_font='Lucida Console',
                                 x_offset=-19, y_offset=-18,
                                 source=src, render_mode='canvas')
        # ===========================================================================
        # vertical bar graph to figure
        # ===========================================================================
        p.vbar(x='x', top='top', width=0.5, source=src, line_color='white', fill_color='color', legend=False,
               name='State')
        # ===========================================================================
        # graph settings
        # ===========================================================================
        p.add_layout(text_notation)
        p.add_tools(HoverTool(names=['State'], tooltips="""
            <div align="left">
                <span style="font-size: 12px; font-weight: bold;"> @x </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px; font-weight: bold;"> Premium: </span>&nbsp;
                <span style="font-size: 11px;"> @text </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px;"> @GFB_text </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px;"> @Country_text </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px;"> @Auto_Owners_text </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px;"> @Progressive_text </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px;"> @StateFarm_text </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px;"> @USAA_text </span>&nbsp;
            </div>
            <div align="left">
                <span style="font-size: 11px;"> @Liberty_text </span>&nbsp;
            </div>
                """, mode='vline', toggleable=False))
        p.title.align = "left"
        p.toolbar_location = 'right'
        p.grid.grid_line_color = None
        # ===========================================================================
        p.toolbar.logo = None
        p.y_range.start = 0
        p.yaxis.visible = False
        p.xaxis.axis_label = ""
        p.xaxis.axis_label_standoff = 10
        p.yaxis.axis_label_text_font_style = "italic"
        p.yaxis.axis_label_standoff = 10
        p.ygrid.minor_grid_line_color = 'navy'
        p.ygrid.minor_grid_line_alpha = 0.1
        # ===========================================================================
        return p

    def make_dataset_winrate(companies, range_start=0, range_end=1000, target_column='Age Max'):
        by_companies = {}

        # Iterate through all the districts
        for i, company_name in enumerate(companies):
            # Subset to the companies
            by_companies[company_name] = policy_dictionary[company_name]

        subset = policy_data[(range_start <= policy_data[target_column]) & (policy_data[target_column] < range_end)]
        subset['lowest_col'] = subset.loc[:, ['Auto Owners (Auto-Owners): Total Policy Premium',
                                              'Country Companies (Mutual CMIC): Total Policy Premium',
                                              'Farm Bureau Mutual: Total Policy Premium',
                                              'LM General Insurance Company (LM Ins Co): Total Policy Premium',
                                              'Prog Mountain: Total Policy Premium',
                                              'State Farm Auto (SFM): Total Policy Premium',
                                              'USAA Auto (USAA): Total Policy Premium']].idxmin(axis=1)
        x = subset['lowest_col'].value_counts(dropna=False)
        data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'VS'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        data['ratio'] = data['value'].apply(lambda x: '{0:.4f}'.format(x / data['value'].sum()))
        data['text'] = data['value'].apply(lambda x: '{:.0%}'.format(x / data['value'].sum()))
        data['key'] = data['VS'].apply(lambda x: companies_comvert[x])
        data['name'] = data['key'].apply(lambda x: by_companies[x][4])
        data['color'] = data['key'].apply(lambda x: by_companies[x][2])
        data['cumulative_angle'] = [(sum(data['value'][0:i + 1]) - (item / 2)) / sum(data['value']) * 2 * pi for i, item
                                    in enumerate(data['value'])]
        data['cos'] = np.cos(data['cumulative_angle']) * 0.3
        data['sin'] = np.sin(data['cumulative_angle']) * 0.3
        data['policy_count'] = policy_data.count()['Policy No']
        data['subset_count'] = subset.count()['Policy No']
        # Convert dataframe to column data source
        return ColumnDataSource(data)

    def make_plot_winrate(src):
        p = figure(plot_height=300, width=300, title="Win Rate", toolbar_location=None,
                   tools="hover,wheel_zoom", tooltips=
                   "<b>@name </b><br> Policy Count: @value </br> Volume: @ratio{%0.2f}",
                   x_range=(-0.75, 0.75), match_aspect=True)
        p.annular_wedge(x=0, y=0, inner_radius=0, outer_radius=0.5, direction="anticlock",
                        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                        line_color="white", fill_color='color', source=src)
        plabel = LabelSet(x=0, y=0, text='policy_count', level='overlay',
                          text_font_size='20pt', text_color='#808080',
                          x_units='screen', y_units='screen',
                          x_offset=5, y_offset=5, source=src, render_mode='canvas')
        slabel = LabelSet(x=0, y=25, text='subset_count', level='overlay',
                          text_font_size='20pt', text_color='#808080',
                          x_units='screen', y_units='screen',
                          x_offset=5, y_offset=5, source=src, render_mode='canvas')
        p.add_layout(plabel)
        p.add_layout(slabel)

        labels = LabelSet(x='cos', y='sin', text="text",
                          text_font_size="10pt", text_color="white", source=src, text_align='center')
        p.add_layout(labels)
        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None
        return p

    # Update function takes three default parameters
    def update(attr, old, new):
        # ===========================================================================
        new_src = make_dataset(companies,
                               range_start=range_select.value[0],
                               range_end=range_select.value[1],
                               target_column=x_axis.value)
        # Update the source
        src.data.update(new_src.data)
        # ===========================================================================
        new_src_dist = make_dataset_distribution(policy_data,
                                                 range_start=range_select.value[0],
                                                 range_end=range_select.value[1],
                                                 bin_width=binwidth_select.value,
                                                 target_column=x_axis.value)
        # Update the source
        src_dist.data.update(new_src_dist.data)
        # ===========================================================================
        new_src_win = make_dataset_winrate(companies,
                                           range_start=range_select.value[0],
                                           range_end=range_select.value[1],
                                           target_column=x_axis.value)
        # Update the source
        src_win.data.update(new_src_win.data)
        # ===========================================================================

    # Update function takes three default parameters
    def update_axis(attr, old, new):
        q.xaxis.axis_label = x_axis.value
        if (x_axis.value == 'Credit Score Max') or (x_axis.value == 'Credit Score Min'):
            range_select.value = (500, 1000)
            range_select.start = 0
            range_select.end = 1000
            range_select.step = 50

            binwidth_select.start = 10
            binwidth_select.end = 50
            binwidth_select.step = 5
            binwidth_select.value = 25
        elif (x_axis.value == 'Age Max') or (x_axis.value == 'Age Min'):
            range_select.value = (0, 120)
            range_select.start = 0
            range_select.end = 120
            range_select.step = 5

            binwidth_select.start = 1
            binwidth_select.end = 10
            binwidth_select.step = 1
            binwidth_select.value = 3
        elif (x_axis.value == 'Vehicle Newest') or (x_axis.value == 'Vehicle Oldest'):
            range_select.value = (1980, 2022)
            range_select.start = 1970
            range_select.end = 2022
            range_select.step = 2

            binwidth_select.start = 1
            binwidth_select.end = 10
            binwidth_select.step = 1
            binwidth_select.value = 3

        # ===========================================================================
        new_src = make_dataset(companies,
                               range_start=range_select.value[0],
                               range_end=range_select.value[1],
                               target_column=x_axis.value)
        # Update the source
        src.data.update(new_src.data)
        # ===========================================================================
        new_src_dist = make_dataset_distribution(policy_data,
                                                 range_start=range_select.value[0],
                                                 range_end=range_select.value[1],
                                                 bin_width=binwidth_select.value,
                                                 target_column=x_axis.value)
        # Update the source
        src_dist.data.update(new_src_dist.data)
        # ===========================================================================
        new_src_win = make_dataset_winrate(companies,
                                           range_start=range_select.value[0],
                                           range_end=range_select.value[1],
                                           target_column=x_axis.value)
        # Update the source
        src_win.data.update(new_src_win.data)
        # ===========================================================================

    target_columns = ['Age Max', 'Age Min', 'Credit Score Max', 'Credit Score Min', 'Vehicle Newest', 'Vehicle Oldest']
    # Check box tool
    x_axis = Select(title="X Axis", options=target_columns, value="Age Max")
    x_axis.on_change('value', update_axis)

    #    # Bin slider
    binwidth_select = Slider(start=2, end=10,
                             step=1, value=3,
                             title='Bin Width')
    binwidth_select.on_change('value', update)
    #
    #    # X-axis range slider
    range_select = RangeSlider(start=0, end=120, value=(0, 120),
                               step=5, title='X-axis Range')
    range_select.on_change('value', update)
    #
    #    # X-axis range slider

    src_dist = make_dataset_distribution(policy_data,
                                         range_start=range_select.value[0],
                                         range_end=range_select.value[1],
                                         bin_width=binwidth_select.value,
                                         target_column=x_axis.value)

    # Initial source
    src = make_dataset(companies,
                       range_start=range_select.value[0],
                       range_end=range_select.value[1],
                       target_column=x_axis.value)

    src_win = make_dataset_winrate(companies,
                                   range_start=range_select.value[0],
                                   range_end=range_select.value[1],
                                   target_column=x_axis.value)
    # Initial graph
    p = make_plot(src)
    q = make_plot_distribution(src_dist)
    w = make_plot_premium(src_dist)
    u = make_plot_winrate(src_win)

    q.x_range = w.x_range
    # Put controls in a single element
    controls = WidgetBox(x_axis, range_select, binwidth_select)

    # Create a row layout
    layout = row(controls, column(row(p, u), w, q))

    # Make a tab with the layout
    tab = Panel(child=layout, title='PPA - Policy Level')

    return tab
