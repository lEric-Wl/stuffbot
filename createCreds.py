import json
import sys

creds = {}
key = ''
'''
	Creates my api keys locally
	Takes one arg- The name of the credential file. 
	Default is creds.json
'''
try:
	arg = str(sys.argv[1]) 
except IndexError:
	print('No arguments given. File name set to creds.json')
	arg = 'creds.json'

if arg[-5:] != '.json':
    name = 'creds.json'
else:
    name = arg
	
def find_file():
    global creds, name
    
    try:
        with open(name, 'r') as saves:
            load = ''
            while load not in ('y', 'n'):
                load = input(f'{name} file found. Want to just add to it? (y/n) ').lower()

            if load == 'y':
                creds = json.load(saves)
            elif load == 'n':
                rename = ''
                while rename not in ('y', 'n'):
                    rename = input('Want to rename it to something else? (y/n) ').lower()
                
                if rename == 'y':
                    name = input('What would you like to name your credentials file? ')
                    find_file()
                    
    except FileNotFoundError:
        print(f'{name} not found, creating a new one.')

find_file()

while key != '-1':
    key = input('What is the name of the key? Type -1 if you are done. ')
    if key == '-1':
        break
    value = input('What is the value of the key? ')
    creds[key] = value
    print('\n')
    
with open(name, 'w') as save_file:
    json.dump(creds, save_file, indent=4)


