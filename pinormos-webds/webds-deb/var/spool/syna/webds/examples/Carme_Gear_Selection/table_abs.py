import copy
import numpy as np

from jupyter_dash import JupyterDash
from dash import dcc, html, no_update
from dash import callback_context
from dash.dash_table import DataTable
from dash.dash_table.Format import Format, Scheme, Trim
from dash.dependencies import Input, Output, State

table: object = None

app = JupyterDash()

@app.callback(
    Output('table', 'columns'),
    Output('table', 'data'),
    Output('table', 'style_data_conditional'),
    Output('table', 'hidden_columns'),
    Input('table', 'active_cell'),
    Input('sort-button', 'n_clicks'),
    Input('exclude-all-button', 'n_clicks'),
    Input('clear-exclusions-button', 'n_clicks'),
    Input('hide-xy-button', 'n_clicks'),
    Input('display-noise-button', 'n_clicks'),
    Input('hsync-freq-input', 'value'),
    State('table', 'derived_viewport_data'),
)
def _handle_input_events(cell, sort_n_clicks, exclude_all_n_clicks, clear_exclusions_n_clicks, hide_xy_n_clicks, display_noise_n_clicks, hsync_freq_value, data):
    context = callback_context.triggered[0]['prop_id'].split('.')[0]
    if context == 'sort-button':
        return table._sort_button_clicked()
    elif context == 'exclude-all-button':
        return table._exclude_all_button_clicked()
    elif context == 'clear-exclusions-button':
        return table._clear_exclusions_button_clicked()
    elif context == 'hide-xy-button':
        return table._hide_xy_button_clicked()
    elif context == 'display-noise-button':
        if (display_noise_n_clicks % 2) == 0:
            style = table._set_display_noise(False)
            return no_update, no_update, style, no_update
        else:
            style = table._set_display_noise(True)
            return no_update, no_update, style, no_update
    elif context == 'hsync-freq-input':
        try:
            if hsync_freq_value:
                table.hsync_frequency = float(hsync_freq_value)
                style = table._set_display_noise(True)
                return no_update, no_update, style, no_update
            else:
                return no_update, no_update, no_update, no_update
        except ValueError:
            return no_update, no_update, no_update, no_update
    if cell and (cell['column_id'] == 'exclude' or cell['column_id'] == 'include') and cell['row'] >= table.header_rows and cell['row'] < table.table_rows - 1:
        return table._cell_clicked(cell['column_id'], cell['row'] - table.header_rows)
    elif cell and cell['column'] >= 5 and '_max' in cell['column_id'] and cell['row'] >= 0 and cell['row'] <= 1:
        return table._cell_clicked(cell['column_id'], cell['row'])
    else:
        return no_update, no_update, no_update, no_update

@app.callback(
    Output('hide-xy-button', 'children'),
    Input('hide-xy-button', 'n_clicks')
)
def _handle_hide_xy_button(hide_xy_n_clicks):
    if (hide_xy_n_clicks % 2) == 0:
        return 'Hide X/Y'
    else:
        return 'Show X/Y'

@app.callback(
    Output('hsync-frequency', 'style'),
    Output('hsync-freq-input', 'style'),
    Input('display-noise-button', 'n_clicks')
)
def _handle_display_noise_button(display_noise_n_clicks):
    if (display_noise_n_clicks % 2) == 0:
        style = table._set_display_noise(False)
        return {'display': 'none'}, {'display': 'none'}
    else:
        style = table._set_display_noise(True)
        return {'fontFamily': 'Arial', 'fontSize': '14px'}, {}

class Abs(object):
    def __init__(self, mode='jupyterlab', port=8052, width='100%', height='650px'):
        self.mode = mode
        self.port = port
        self.width = width
        self.height = height
        self.sorted = False
        self.hide_xy = False
        self.hsync_frequency = 0
        self.selected = {}
        self.excluded = []
        self.int_durs = []
        self.noise_data = []
        self.conditions = []
        self.sortedc = []
        self.columns = [
            dict(id='exclude', name='Abs Gear Selection'),
            dict(id='include', name='Abs Gear Selection'),
            dict(id='min_noise', name='Abs Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)),
            dict(id='min_gear_noise', name='Abs Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)),
            dict(id='label', name='Abs Gear Selection')
        ]
        self.data = [
            {'label': 'Select'
            },
            {'label': 'Unselect'
            },
            {'label': 'Integration Duration'
            },
            {'label': 'Frequency (kHz)'
            },
            {'label': 'Overall Max Noise'
            },
            {'label': 'Max Noise (non-excluded)'
            },
            {'exclude': 'Exclude',
             'include': 'Include',
             'min_noise': 'Min Noise',
             'min_gear_noise': 'Min Gear Noise',
             'label': 'Test Condition'
            }
        ]
        self.style_data_conditional = [
            {
                'if': {'column_id': 'label', 'row_index': 2},
                'backgroundColor': 'lightGrey'
            }
        ]
        self.hidden_columns = []
        self.header_rows = len(self.data)
        self.table_rows = None
        global table
        assert table is None, 'Attempted to instantiate more than one table. Please restart kernel.'
        table = self
        global app
        self.app = app
        self.app.layout = html.Div(
            [
                DataTable(
                    id='table',
                    columns=self.columns,
                    hidden_columns=self.hidden_columns,
                    data=self.data,
                    style_cell={
                        'textAlign': 'center',
                        'minWidth': '80px',
                        'maxWidth': '80px'
                    },
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'min_gear_noise'},
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {'column_id': 'label'},
                            'textAlign': 'right',
                            'minWidth': '230px',
                            'maxWidth': '230px'
                        }
                    ],
                    style_data_conditional=self.style_data_conditional,
                    style_header={
                        'backgroundColor': 'white'
                    },
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto'
                    },
                    css=[{"selector": ".show-hide", "rule": "display: none"}],
                    fill_width=False,
                    merge_duplicate_headers=True
                ),
                html.Div(
                    id = 'buttons-top-row',
                    children = [
                        html.Button(
                            'Sort',
                            id ='sort-button',
                            style = {
                                'width': '120px',
                                'cursor': 'pointer'
                            },
                            n_clicks = 0
                        ),
                        html.Button(
                            'Exclude All',
                            id ='exclude-all-button',
                            style = {
                                'width': '120px',
                                'cursor': 'pointer'
                            },
                            n_clicks = 0
                        ),
                        html.Button(
                            'Clear Exclusions',
                            id ='clear-exclusions-button',
                            style = {
                                'width': '120px',
                                'cursor': 'pointer'
                            },
                            n_clicks = 0
                        ),
                        html.Button(
                            children='Hide X/Y',
                            id ='hide-xy-button',
                            style = {
                                'width': '120px',
                                'cursor': 'pointer'
                            },
                            n_clicks = 0
                        )
                    ],
                    style = {
                        'marginTop': '10px',
                        'display': 'flex',
                        'flexDirection': 'row',
                        'columnGap': '20px'
                    }
                ),
                html.Div(
                    id = 'bottom-top-row',
                    children = [
                        html.Button(
                            'Display Noise Avoidance?',
                            id ='display-noise-button',
                            style = {
                                'width': '200px',
                                'cursor': 'pointer'
                            },
                            n_clicks = 0
                        ),
                        html.Div(
                            'Hsync Frequency (kHz):',
                            id ='hsync-frequency',
                            style = {
                                'display': 'none'
                            }
                        ),
                        dcc.Input(
                            id = 'hsync-freq-input',
                            type = 'text',
                            style = {
                                'display': 'none'
                            }
                        )
                    ],
                    style = {
                        'marginTop': '10px',
                        'display': 'flex',
                        'flexDirection': 'row',
                        'columnGap': '20px'
                    }
                )
            ]
        )

    def _generate_table_data(self):
        table_data = copy.deepcopy(self.data)
        for condition, condition_noise_data in enumerate(zip(*self.noise_data)):
            selected_noise_data = []
            for idx, int_dur in enumerate(self.int_durs):
                if self.selected[str(int_dur)+'_max']:
                    table_data[0][str(int_dur)+'_max'] = 'X'
                    selected_noise_data.append(condition_noise_data[2][idx])
            if len(selected_noise_data):
                table_data[condition + self.header_rows]['min_gear_noise'] = min(selected_noise_data)
            else:
                table_data[condition + self.header_rows]['min_gear_noise'] = None
        noise_data = copy.deepcopy(self.noise_data)
        for idx in range(len(self.conditions) - 1, -1, -1):
            if self.excluded[idx]:
                del noise_data[0][idx]
                del noise_data[1][idx]
                del noise_data[2][idx]
                table_data[idx + self.header_rows]['exclude'] = 'X'
        noise_array = np.array(noise_data[2])
        if len(noise_array):
            noise_array_max = noise_array.max(axis=0)
            noise_array_sum = noise_array.sum(axis=0)
        for idx, int_dur in enumerate(self.int_durs):
            if len(noise_array):
                table_data[4][str(int_dur)+'_max'] = noise_array_max[idx]
                table_data[self.table_rows -1][str(int_dur)+'_max'] = noise_array_sum[idx]
            else:
                table_data[4][str(int_dur)+'_max'] = None
                table_data[self.table_rows -1][str(int_dur)+'_max'] = None
        return table_data

    def _update_table(self):
        table_data = self._generate_table_data()
        if self.sorted:
            new_order = [0, 1, 2, 3, 4]
            group = []
            for idx, item in enumerate(self.selected):
                if self.selected[item]:
                    group.append((idx, item))
            if len(group) and table_data[self.table_rows -1][group[0][1]]:
                group.sort(key=lambda x: table_data[self.table_rows -1][x[1]])
            for item in group:
                new_order.append(item[0] * 3 + 5)
                new_order.append(item[0] * 3 + 6)
                new_order.append(item[0] * 3 + 7)
            group = []
            for idx, item in enumerate(self.selected):
                if not self.selected[item]:
                    group.append((idx, item))
            if len(group) and table_data[self.table_rows -1][group[0][1]]:
                group.sort(key=lambda x: table_data[self.table_rows -1][x[1]])
            for item in group:
                new_order.append(item[0] * 3 + 5)
                new_order.append(item[0] * 3 + 6)
                new_order.append(item[0] * 3 + 7)
            self.sortedc = [self.columns[i] for i in new_order]
            self.style_data_conditional[0] = {
                'if': {'column_id': 'label', 'row_index': self.table_rows -1},
                'backgroundColor': 'lightGrey'
            }
            return self.sortedc, table_data, self.style_data_conditional, self.hidden_columns
        else:
            self.style_data_conditional[0] = {
                'if': {'column_id': 'label', 'row_index': 2},
                'backgroundColor': 'lightGrey'
            }
            return self.columns, table_data, self.style_data_conditional, self.hidden_columns

    def _cell_clicked(self, column_id, index):
        if column_id == 'exclude':
            self.excluded[index] = True
        elif column_id == 'include':
            self.excluded[index] = False
        else:
            if index == 0 and sum(1 for v in self.selected.values() if v == True) < self.num_gears:
                self.selected[column_id] = True
            elif index == 1:
                self.selected[column_id] = False
        return self._update_table()

    def _hide_xy_button_clicked(self):
        self.hidden_columns = []
        self.hide_xy = not self.hide_xy
        if self.hide_xy:
            for column in self.columns:
                if '_abs' in column['id']:
                    self.hidden_columns.append(column['id'])
                elif '_max' in column['id']:
                    self.data[5][column['id']] = None
        else:
            for column in self.columns:
                if '_max' in column['id']:
                    self.data[5][column['id']] = 'max'
        return self._update_table()

    def _clear_exclusions_button_clicked(self):
        self.excluded = [False for _ in self.excluded]
        return self._update_table()

    def _exclude_all_button_clicked(self):
        self.excluded = [True for _ in self.excluded]
        return self._update_table()

    def _sort_button_clicked(self):
        self.sorted = not self.sorted
        return self._update_table()

    def _set_display_noise(self, enable):
        if not enable:
            for idx in range(1, len(self.style_data_conditional)):
                self.style_data_conditional[idx]['backgroundColor'] = 'transparent'
        else:
            for idx, int_dur in enumerate(self.int_durs):
                freq = self.data[3][str(int_dur)+'_max']
                hsync = self.hsync_frequency
                if (freq < hsync * 0.82) or (freq > hsync * 0.91 and freq < hsync * 1.08) or (freq > hsync * 1.3):
                    self.style_data_conditional[idx + 1]['backgroundColor'] = 'grey'
                else:
                    self.style_data_conditional[idx + 1]['backgroundColor'] = 'transparent'
        return self.style_data_conditional

    def get_selections(self):
        selections = [k for k,v in self.selected.items() if v == True]
        selections = [s[:-len('_max')] for s in selections]
        return list(map(int, selections))

    def init_table(self, tc, int_durs, conditions, noise_data, num_gears):
        self.int_durs = int_durs
        self.conditions = conditions
        self.noise_data = noise_data
        self.num_gears = num_gears
        self.table_rows = self.header_rows + len(self.conditions) + 1
        noise_array = np.array(self.noise_data[2])
        noise_array_max = noise_array.max(axis=0)
        noise_array_sum = noise_array.sum(axis=0)
        static = tc.getStaticConfig()
        istretch_dur = static['daqParams.freqTable[0].stretchDur'][0]
        reset_dur = static['resetDur'][3]
        sample_dur = 7
        other_overhead = 3
        if static['extOscEnable'] == 1:
            average_clock = 32
        else:
            average_clock = 29
        for idx, int_dur in enumerate(self.int_durs):
            self.columns.append(dict(id=str(int_dur)+'_absx', name='Abs Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)))
            self.columns.append(dict(id=str(int_dur)+'_absy', name='Abs Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)))
            self.columns.append(dict(id=str(int_dur)+'_max', name='Abs Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)))
            self.data[2][str(int_dur)+'_max'] = int_dur
            self.data[3][str(int_dur)+'_max'] = 1000 / ((istretch_dur + int_dur + reset_dur + sample_dur + other_overhead) / average_clock * 2)
            self.data[4][str(int_dur)+'_max'] = noise_array_max[idx]
            self.data[5][str(int_dur)+'_max'] = noise_array_max[idx]
            self.data[6][str(int_dur)+'_absx'] = 'AbsX'
            self.data[6][str(int_dur)+'_absy'] = 'AbsY'
            self.data[6][str(int_dur)+'_max'] = 'Max'
            self.selected[str(int_dur)+'_max'] = False
            self.style_data_conditional.append({
                'if': {'column_id': [str(int_dur)+'_absx', str(int_dur)+'_absy', str(int_dur)+'_max']},
                'backgroundColor': 'transparent'
            })
        for idx, condition_noise_data in enumerate(zip(*self.noise_data)):
            table_entry = {
                'min_noise': min(condition_noise_data[2]),
                'min_gear_noise': None,
                'label': self.conditions[idx]
            }
            for int_dur, value in zip(self.int_durs, zip(*condition_noise_data)):
                table_entry[str(int_dur)+'_absx'] = value[0]
                table_entry[str(int_dur)+'_absy'] = value[1]
                table_entry[str(int_dur)+'_max'] = value[2]
            self.data.append(table_entry)
            self.excluded.append(False)
        table_entry = {
            'label': 'Total Noise (non-excluded)'
        }
        for idx, int_dur in enumerate(self.int_durs):
            table_entry[str(int_dur)+'_max'] = noise_array_sum[idx]
        self.data.append(table_entry)

    def run(self):
        self.app.run_server(mode=self.mode, host='localhost', port=self.port, width=self.width, height=self.height)
