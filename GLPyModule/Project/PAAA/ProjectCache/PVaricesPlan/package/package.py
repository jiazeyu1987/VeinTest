import configparser

config = configparser.ConfigParser()
config.read("..\..\settings.ini")
config.set('PAAA', 'current_project_selector_project_name', 'PVaricesPlan')
with open('..\..\settings.ini', 'w') as configfile:
    config.write(configfile)
 