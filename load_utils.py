import re
import pandas as pd
import numpy as np

def clean_data(mod, recode=True, replace_nan=0):
    ados_items = [i for i in mod.columns if i.startswith('ADOS')]
    ados_items += [i for i in mod.columns if re.search('^[A-E][0-9]', i) is not None]
    if np.all(mod['Modul '] == 4):
        ados_items.remove('B13')  # this item was removed as it was not part of ADOS 1
    
    # 1 entry is '0 = Logisch nicht beurteilbar (z.B. Sprachauffälligkeiten bei nicht sprechenden Probanden)', set to 0
    mod[ados_items] = mod[ados_items].mask(mod == '0 = Logisch nicht beurteilbar (z.B. Sprachauffälligkeiten bei nicht sprechenden Probanden)', 0)
    mod[ados_items] = mod[ados_items].mask(mod == '8 = Logisch nicht beurteilbar (z.B. Sprachauffälligkeiten bei nicht sprechenden Probanden)', 0)
    if recode:
        # recode 3 as 2
        mod[ados_items] = mod[ados_items].mask(mod == 3, 2)
    if replace_nan is not None:
        mod_clean = np.isnan(mod[ados_items].astype(float)).sum(axis=1) < 5
        s = 'Old N: {};'.format(len(mod))
        pd.set_option('mode.chained_assignment',None)
        mod = mod[mod_clean]
        s+= ' After deletion of Subjects with n_nan >= 5: {}'.format(len(mod))
        mod = mod.fillna(replace_nan)
        print(s)
        
    # replace 7 and 8 with 0
    mod[ados_items] = mod[ados_items].mask(mod == 8, 0)
    mod[ados_items] = mod[ados_items].mask(mod == 7, 0)

    return mod, ados_items


def load_data(module=1, recode=True, replace_nan=0):
    try:
        mod = pd.read_excel('ADOS_IQ_real_data.xlsx', sheet_name=f'Modul {module}', index_col=0,
                            na_values='nc')
    except FileNotFoundError:
        print('Real Data not found, running on Sample Data...')
        mod = pd.read_excel('ADOS_IQ_sample_data.xlsx', sheet_name=f'Modul {module}', index_col=0,
                            na_values='nc')
    mod, ados_items = clean_data(mod, recode, replace_nan)

    return_items = ados_items + ['IQ Level ', 'ASD', 'F70 ', 'sex', 'Modul ', 'age', '1_IQ_Gesamt']

    return mod[return_items]