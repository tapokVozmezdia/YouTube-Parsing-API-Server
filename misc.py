api_key = 'your key'
api_url = "https://www.googleapis.com/youtube/v3"

def print_separator(thick : bool = False):
    if thick:
        print('==================================')
        return
    print('----------------------------------')

def throw_exception(code : str = 'error'):
    print_separator()
    print("ERROR\nerror code:", code)
    print_separator()
    exit(1)