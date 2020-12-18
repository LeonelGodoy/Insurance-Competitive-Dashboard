# Pandas for data management
import pandas as pd
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs, Panel
import pickle
from PolicyTab import _tab as policy_tab
from VehicleTab import _tab as vehicle_tab
from HomeTab import _tab as home_tab
import sys, os
import tkinter as tk
from tkinter.filedialog import askopenfilename


root = tk.Tk()
root.withdraw()
# location and file name
pathname = os.path.dirname(sys.argv[0])
location = os.path.abspath(pathname)
file_select_home = askopenfilename(initialdir=location+"/Data", title='Select Home Data')
homeowners_data = pd.read_csv(file_select_home, low_memory=False)
# In the future, change these to be csv imports and not pickles
file_select_vehicle = askopenfilename(initialdir=location+"/Data", title='Select Policy Data')
policy_pickle_in = open(file_select_vehicle, "rb")
file_select_policy = askopenfilename(initialdir=location+"/Data", title='Select Vehicle Data')
vehicle_pickle_in = open(file_select_policy, "rb")

policy_data = pickle.load(policy_pickle_in)
vehicle_data = pickle.load(vehicle_pickle_in).fillna(0)
# Create each of the tabs
tab1 = policy_tab(policy_data)
tab2 = vehicle_tab(vehicle_data)
tab3 = home_tab(homeowners_data)

TABS = Tabs(tabs=[tab1, tab2, tab3])

# Put the tabs in the current document for display
curdoc().add_root(TABS)
