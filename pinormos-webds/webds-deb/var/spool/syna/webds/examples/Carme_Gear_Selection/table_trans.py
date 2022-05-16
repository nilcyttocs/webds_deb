import copy
import numpy as np

from jupyter_dash import JupyterDash
from dash import html, no_update
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
    Input('table', 'active_cell'),
    Input('sort-button', 'n_clicks'),
    Input('exclude-all-button', 'n_clicks'),
    Input('clear-exclusions-button', 'n_clicks'),
    State('table', 'derived_viewport_data'),
)
def _cell_button_clicked(cell, sort_n_clicks, exclude_all_n_clicks, clear_exclusions_n_clicks, data):
    context = callback_context.triggered[0]['prop_id'].split('.')[0]
    if context == 'sort-button':
        return table._sort_button_clicked()
    elif context == 'exclude-all-button':
        return table._exclude_all_button_clicked()
    elif context == 'clear-exclusions-button':
        return table._clear_exclusions_button_clicked()
    if cell and (cell['column_id'] == 'exclude' or cell['column_id'] == 'include') and cell['row'] >= table.header_rows and cell['row'] < table.table_rows - 1:
        return table._cell_clicked(cell['column_id'], cell['row'] - table.header_rows)
    elif cell and cell['column'] >= 5 and cell['row'] >= 0 and cell['row'] <= 1:
        return table._cell_clicked(cell['column_id'], cell['row'])
    else:
        return no_update, no_update, no_update

class Trans(object):
    def __init__(self, mode='jupyterlab', port=8051, width='100%', height='650px'):
        self.mode = mode
        self.port = port
        self.width = width
        self.height = height
        self.sorted = False
        self.selected = {}
        self.excluded = []
        self.int_durs = []
        self.noise_data = []
        self.conditions = []
        self.sortedc = []
        self.columns = [
            dict(id='exclude', name='Transcap Gear Selection'),
            dict(id='include', name='Transcap Gear Selection'),
            dict(id='min_noise', name='Transcap Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)),
            dict(id='min_gear_noise', name='Transcap Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)),
            dict(id='label', name='Transcap Gear Selection')
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
                    id = 'buttons',
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
        for condition, condition_noise_data in enumerate(self.noise_data):
            selected_noise_data = []
            for idx, int_dur in enumerate(self.int_durs):
                if self.selected[str(int_dur)]:
                    table_data[0][str(int_dur)] = 'X'
                    selected_noise_data.append(condition_noise_data[idx])
            if len(selected_noise_data):
                table_data[condition + self.header_rows]['min_gear_noise'] = min(selected_noise_data)
            else:
                table_data[condition + self.header_rows]['min_gear_noise'] = None
        noise_data = copy.deepcopy(self.noise_data)
        for idx in range(len(self.conditions) - 1, -1, -1):
            if self.excluded[idx]:
                del noise_data[idx]
                table_data[idx + self.header_rows]['exclude'] = 'X'
        noise_array = np.array(noise_data)
        if len(noise_array):
            noise_array_max = noise_array.max(axis=0)
            noise_array_sum = noise_array.sum(axis=0)
        for idx, int_dur in enumerate(self.int_durs):
            if len(noise_array):
                table_data[4][str(int_dur)] = noise_array_max[idx]
                table_data[self.table_rows -1][str(int_dur)] = noise_array_sum[idx]
            else:
                table_data[4][str(int_dur)] = None
                table_data[self.table_rows -1][str(int_dur)] = None
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
                new_order.append(item[0] + 5)
            group = []
            for idx, item in enumerate(self.selected):
                if not self.selected[item]:
                    group.append((idx, item))
            if len(group) and table_data[self.table_rows -1][group[0][1]]:
                group.sort(key=lambda x: table_data[self.table_rows -1][x[1]])
            for item in group:
                new_order.append(item[0] + 5)
            self.sortedc = [self.columns[i] for i in new_order]
            self.style_data_conditional[0] = {
                'if': {'column_id': 'label', 'row_index': self.table_rows -1},
                'backgroundColor': 'lightGrey'
            }
            return self.sortedc, table_data, self.style_data_conditional
        else:
            self.style_data_conditional[0] = {
                'if': {'column_id': 'label', 'row_index': 2},
                'backgroundColor': 'lightGrey'
            }
            return self.columns, table_data, self.style_data_conditional

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

    def _clear_exclusions_button_clicked(self):
        self.excluded = [False for _ in self.excluded]
        return self._update_table()

    def _exclude_all_button_clicked(self):
        self.excluded = [True for _ in self.excluded]
        return self._update_table()

    def _sort_button_clicked(self):
        self.sorted = not self.sorted
        return self._update_table()

    def get_selections(self):
        selections = [k for k,v in self.selected.items() if v == True]
        return list(map(int, selections))

    def init_table(self, tc, int_durs, conditions, noise_data, num_gears):
        self.int_durs = int_durs
        self.conditions = conditions
        self.noise_data = noise_data
        self.num_gears = num_gears
        self.table_rows = self.header_rows + len(self.conditions) + 1
        noise_array = np.array(self.noise_data)
        noise_array_max = noise_array.max(axis=0)
        noise_array_sum = noise_array.sum(axis=0)
        static = tc.getStaticConfig()
        istretch_dur = static['daqParams.freqTable[0].stretchDur'][0]
        reset_dur = static['resetDur'][2]
        sample_dur = 7
        other_overhead = 3
        if static['extOscEnable'] == 1:
            average_clock = 32
        else:
            average_clock = 29
        for idx, int_dur in enumerate(self.int_durs):
            self.columns.append(dict(id=str(int_dur), name='Transcap Gear Selection', type='numeric', format=Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)))
            self.data[2][str(int_dur)] = int_dur
            self.data[3][str(int_dur)] = 1000 / ((istretch_dur + int_dur + reset_dur + sample_dur + other_overhead) / average_clock * 2)
            self.data[4][str(int_dur)] = noise_array_max[idx]
            self.data[5][str(int_dur)] = noise_array_max[idx]
            self.selected[str(int_dur)] = False
        for idx, condition_noise_data in enumerate(self.noise_data):
            table_entry = {
                'min_noise': min(condition_noise_data),
                'min_gear_noise': None,
                'label': self.conditions[idx]
            }
            for int_dur, value in zip(self.int_durs, condition_noise_data):
                table_entry[str(int_dur)] = value
            self.data.append(table_entry)
            self.excluded.append(False)
        table_entry = {
            'label': 'Total Noise (non-excluded)'
        }
        for idx, int_dur in enumerate(self.int_durs):
            table_entry[str(int_dur)] = noise_array_sum[idx]
        self.data.append(table_entry)

    def run(self):
        self.app.run_server(mode=self.mode, host='localhost', port=self.port, width=self.width, height=self.height)
