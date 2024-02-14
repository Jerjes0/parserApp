from shinywidgets import render_plotly

from shiny import reactive, render, req
from shiny.express import input, ui

import pandas as pd


## Paths to relevant files  
#
master_parser_path = 'Master_risks.csv'
users_id_path = 'users_by_id.csv'
additions_parser_path = 'additions.csv'


## Reactive values

master_parser = reactive.value(pd.DataFrame())
additions_parser = reactive.value(pd.DataFrame())
unique_users = reactive.value([])
users_options = reactive.value([])

## Lists
#

risk_cat_list = ["Extreme Heat",
                "Frost",	
                "High Humidity",	
                "Low Precipitation",	
                "Cold Stress",	
                "Low Chill Hours",	
                "Low Humidity",
                "High Precipitation",
                "Water Requirement",
                "High Humidity",
                "Killing Risk - Extreme Heat",	
                "Killing Risk - Frost",
                "Killing RiPrecipitation",	
                "Killing Risk - Humidity",	
                "High Wind Risk",	
                "Low Wind Risk"]

var_list = ["max temperature",
            "min temperature",
            "mean temperature",
            "humidity",
            "precipitation",
            "chill hours",
            "GDD",
            "wind speed",
            "solar radiation",
            "max wind speed"
            ]

risk_type_list = ["Case 1: Simple Aggregation",
                "Case 2: Days With Risk", 
                "Case 3: Threshold Aggregation", 
                "Case 4: Rolling Window"]

agg_list = ["total of variable",
            "average of variable",
            "total # of days",
            "cumulative thresholded degrees",	
            "cumulative thresholded mm",
            "cumulative thresholded % (relative humidity)","cumulative thresholded",
            "chill hours"]

comp_list = [">",
            "<",
            "=",
            ">=",
            "<="]

var_unit_list = ["°C",
                 "%",
                 "mm",
                "hours",
                "gdd",
                "km/h"]


# Add page title and sidebar
ui.page_opts(title="ClimateAi - Internal Tool", fillable=True)

with ui.sidebar(open="desktop"):
    
    ui.input_password("password",
                "Password",
                value=""
                )
    
    ui.input_selectize("user", 
                        "User", 
                        multiple=True, 
                        choices=[],
                        remove_button = True),
    
    ui.input_selectize("crops", 
                        "Crops", 
                        multiple=True, 
                        choices=[]),

    ui.input_selectize("varieties", 
                        "Varieties", 
                        multiple=True, 
                        choices=[])
    
    ui.input_action_button("select_all_users",
                      "Select All Users"),

    ui.input_action_button("clear", 
                           "Clear", 
                           class_="btn-success")

with ui.layout_columns(col_widths=[12, 12]):


    with ui.card(full_screen=True):
        with ui.card_header():
            "Risk Profiles"
            @render.data_frame
            def table():
                return render.DataGrid(parser_data(),
                                       filters=True)


    with ui.card(full_screen=True):
        with ui.card_header():
            "Risk Editor"
            with ui.layout_columns(col_widths=[2,2,2]):

                ui.input_text("account",
                              "Account",
                              value="sabi@climate.ai"
                    
                )

                ui.input_action_button("add", 
                                "Add", 
                                class_="btn-success")
                
                ui.input_action_button("clear_new", 
                                "Clear", 
                                class_="btn-success")
                
            with ui.layout_columns(col_widths=[2, 2, 2, 2, 2, 2,
                                               2, 2, 2, 2, 2, 2,
                                               2, 2, 2, 2, 2, 2]):
                ui.input_text("location", 
                        "Location",
                        "",
                        placeholder='location')
                
                ui.input_text("crop", 
                        "Crop",
                        "",
                        placeholder='crop')
            
                ui.input_text("variety", 
                        "Variety",
                        "",
                        placeholder="variety")
                
                ui.input_text("ps", 
                        "Phenological Stage",
                        "",
                        placeholder="phenological stage")
                
                ui.input_selectize("stacked", 
                        "Stacked",
                        choices=['False','True'])
                
                ui.input_selectize("stacked_logic", 
                        "Stacked Logic",
                        choices=['{}','AND', 'OR'])
                
                ui.input_selectize("risk_category", 
                        "Risk Category",
                        choices=risk_cat_list)

                ui.input_selectize("risk_type", 
                        "Risk Type",
                        choices=risk_type_list)
                
                ui.input_selectize("variable", 
                        "Variable",
                        choices=var_list)
                
                ui.input_selectize("aggregation", 
                        "Aggregation",
                        choices=agg_list)
                
                ui.input_selectize("comparator", 
                        "Comparator",
                        choices=comp_list)
                
                ui.input_numeric("threshold", 
                        "Threshold",
                        0)
                
                ui.input_selectize("var_unit", 
                        "Variable Unit",
                        choices=var_unit_list)
                
                ui.input_numeric("min_temp_recurr", 
                        "Min. Temporal Recurrence",
                        0)
                
                ui.input_text("rolling_window", 
                        "Rolling Window",
                        "{}",
                        placeholder="{}")
                
                ui.input_selectize("consecutive", 
                        "Consecutive",
                        choices=['False','True'])
                
                ui.input_selectize("yri_impact_type", 
                        "Yield Risk Index  (YRI) Type",
                        choices=['discrete', 'continuous'])
                
                # ui.input_text("yri", 
                #         "YRI",
                #         "",
                #         placeholder="0%")
                
                ui.input_text("yri_min", 
                        "YRI Minimum Recurrence (Case 2)",
                        "",
                        placeholder="0%")
                
                ui.input_text("yri_after", 
                        "YRI After Minimum Recurrence",
                        "",
                        placeholder="0%")
                
                ui.input_selectize("yri_fun_unit", 
                        "Yield Risk Index Function Unit",
                        choices=['discrete', 'continuous'])
                
                ui.input_text("max_yri", 
                        "Max YRI",
                        "",
                        placeholder="0%")
        
                ui.input_numeric("start_month", 
                        "Start Month",
                        0)
                
                ui.input_numeric("start_day", 
                        "Start Day",
                        0)
                
                ui.input_numeric("end_month", 
                        "End Month",
                        0)
                
                ui.input_numeric("end_day", 
                        "End Day",
                        0)
                

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------
@reactive.effect
def _():
     if input.password() == 'climateai00':
        ## Read files
        #
        master_parser_ = pd.read_csv(master_parser_path)
        users_id = pd.read_csv(users_id_path)

        ## Merge files to add email to master parser
        #
        master_parser_ = master_parser_.merge(users_id[['user', 'email']], on='user', how='left')

        ## Drop not needed columns
        #
        master_parser_ = master_parser_.drop(columns=['user', 'Subtitle (column editable)'])

        ## Read additions csv
        #
        additions_parser = pd.read_csv(additions_parser_path)
        master_parser_ = pd.concat([master_parser_, additions_parser], ignore_index=True)

        ## Unique options available available
        #
        unique_users_ = master_parser_.email.unique().tolist()

        users_options_= unique_users_.copy()
        users_options_.append('All')

        users_options.set(users_options_)
        unique_users.set(unique_users_)
        master_parser.set(master_parser_)

@reactive.calc
def parser_data():
    users = input.user()
    crops = input.crops()
    varieties = input.varieties()
    
    if 'All' in users:
        users = master_parser.get().email.unique().tolist()
        
    if not users and not crops and not varieties:
        return pd.DataFrame()
    if users and not crops and not varieties:
        return master_parser.get()[master_parser.get()['email'].isin(users)]
    if users and crops and not varieties:
        return master_parser.get()[master_parser.get()['Crop'].isin(crops) & 
                             master_parser.get()['email'].isin(users)]
    if users and crops and varieties:
        return master_parser.get()[master_parser.get()['Crop'].isin(crops) & 
                             master_parser.get()['email'].isin(users) & 
                             master_parser.get()['Variety'].isin(varieties)]
    else:
        return pd.DataFrame()
    
@reactive.effect
def update_user():
    global users_options
    password = input.password()

    if password == 'climateai00':
        ui.update_selectize("user", choices=users_options.get())
    else:
        ui.update_selectize("user", choices=[])
        


@reactive.effect
def update_crops():
    users = input.user()
    if users:
        if 'All' in users:
            unique_emails = master_parser.get().email.unique().tolist()
        else:
            unique_emails = users

        crops = master_parser.get()[master_parser.get()['email'].isin(unique_emails)]['Crop']
        crops = list(set(crops))
        
        ui.update_selectize("crops", choices=crops)

@reactive.effect
def update_varieties():
    users = input.user()
    crops = input.crops()
    if crops:
        if 'All' in users:
            unique_emails = master_parser.get().email.unique().tolist()
        else:
            unique_emails = users
        varieties = master_parser.get()[master_parser.get()['Crop'].isin(crops) & 
                             master_parser.get()['email'].isin(unique_emails)]['Variety']
        varieties = list(set(varieties))
        
        ui.update_selectize("varieties",
                            choices=varieties

        )

@reactive.effect
@reactive.event(input.select_all_users)
def select_all_users():
    ui.update_selectize("user",
                        choices=unique_users.get() + ['All'],
                        selected='All'
    )

@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("total_bill", value=bill_rng)
    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])

@reactive.effect
@reactive.event(input.clear)
def clear_all():
    ui.update_selectize("user", 
                        choices=unique_users.get()),
    
    ui.update_selectize("crops", 
                        choices=[]),

    ui.update_selectize("varieties", 
                        choices=[])

@reactive.effect
@reactive.event(input.add)
def _():
        new_row = {'Location': input.location(),
                'Crop': input.crop(),
                'Variety': input.variety(),
               'Phenological Stage': input.ps(),
               'Stacked': input.stacked(),
               'Stacked Logic': input.stacked_logic(),
               'Risk Category': input.risk_category(),
               'Risk Type (Internal use for parser development only)': input.risk_type(),
               'Variable': input.variable(),
               'Aggregation': input.aggregation(),
               'Comparator': input.comparator(),
               'Threshold': input.threshold(),
               'user': input.account(),
                'email': input.account(),
                'Variable Unit': input.var_unit(),
                'Minimum Temporal Recurrence': input.min_temp_recurr(),
                'Rolling Window': input.rolling_window(),
                'Consecutive': input.consecutive(),
                'Yield Impact Type': input.yri_impact_type(),
                'Yield Impact (Minimum Recurrence Met/No Recurrence)': input.yri_min(),
                'Yield Impact After Minimum Recurrence (Only valid for case 2)': input.yri_after(),
                'Yield Impact Function Unit': input.yri_fun_unit(),
                'Max Yield Impact': input.max_yri(),
                'Start Month': input.start_month(),
                'Start Day': input.start_day(),
                'End Month': input.end_month(),
                'End Day': input.end_day()
                }
        new_row_df = pd.DataFrame([new_row])

        additions_parser_ = pd.concat([additions_parser.get(), new_row_df], ignore_index=True)
        additions_parser_.to_csv(additions_parser_path, index=False)
        master_parser.set(pd.concat([master_parser.get(), additions_parser_], ignore_index=True))

        if input.account() not in unique_users.get():
                unique_users.set(unique_users.get().append(input.account()))

        if input.account() not in users_options.get():
                users_options.set(users_options.get().append(input.account()))



@reactive.effect
@reactive.event(input.clear_new)
def _():

        ui.update_text("account", 
                        value="sabi@climate.ai")
        
        ui.update_text("location", 
                        value="",
                        placeholder='location')
                
        ui.update_text("crop", 
                value="",
                placeholder='crop')
            
        ui.update_text("variety", 
                value="",
                placeholder="variety")
        
        ui.update_text("ps", 
                value="",
                placeholder="phenological stage")
        
        ui.update_selectize("stacked", 
                choices=['False','True'])
        
        ui.update_selectize("stacked_logic", 
                choices=['{}','AND', 'OR'])
        
        ui.update_selectize("risk_category", 
                choices=risk_cat_list)

        ui.update_selectize("risk_type", 
                choices=risk_type_list)
        
        ui.update_selectize("variable", 
                choices=var_list)
        
        ui.update_selectize("aggregation", 
                choices=agg_list)
        
        ui.update_selectize("comparator", 
                choices=comp_list)
        
        ui.update_numeric("threshold", 
                value=0)
        
        ui.update_selectize("var_unit", 
                choices=var_unit_list)
        
        ui.update_numeric("min_temp_recurr", 
                value=0)
        
        ui.update_text("rolling_window", 
                value="",
                placeholder="{}")
        
        ui.update_selectize("consecutive", 
                choices=['False','True', ])
        
        ui.update_selectize("yri_impact_type", 
                choices=['discrete', 'continuous'])
        
        # ui.input_text("yri", 
        #         "YRI",
        #         "",
        #         placeholder="0%")
        
        ui.update_text("yri_min", 
                value="",
                placeholder="0%")
        
        ui.update_text("yri_after", 
                value="",
                placeholder="0%")
        
        ui.update_selectize("yri_fun_unit", 
                choices=['discrete', 'continuous'])
        
        ui.update_text("max_yri", 
                value="",
                placeholder="0%")

        ui.update_numeric("start_month", 
                value=0)
        
        ui.update_numeric("start_day", 
                value=0)
        
        ui.update_numeric("end_month", 
                value=0)
        
        ui.update_numeric("end_day", 
                value=0)


                






