import argparse
import os
from psutil import Process,NoSuchProcess
from search_engine_parser.core.engines.google import Search as GoogleSearch
import sys



RED = '\033[31m'
BOLD = '\033[1m'
END = '\033[0m'
CYAN = '\033[36m'

parser = argparse.ArgumentParser (prog='Rebound',description='Command-line tool that automatically searches Stack Overflow and displays results in your terminal when you get a compiler error.')
parser.add_argument('-v','--version', action='version', version='%(prog)s 2.0')
parser.add_argument("-s","--script",help="Run Script from Terminal")
parser.add_argument('-q','--query',help='Query stackoverflow with Error message ')
subparser = parser.add_subparsers(dest='command')
call = subparser.add_parser('call')
call.add_argument("-id",'--pid',required=True)
call.add_argument('-e','--err',required=True)
args = parser.parse_args()


if args.command=='call':
    if os.path.isfile(args.err):
        ProcessId= args.pid
        MonitorProcess()
    else:
        raise Exception("-e takes path to logfile Only")    
elif args.query is not None:
    search_results = search_google(args.query)
    if search_results != []:
        App(search_results) # Opens interface        
    else:
        print("\n%s%s%s" % (RED, "No Google results found.\n", END))

elif args.script is not None:
        language = get_language(args.script.lower()) # Gets the language name
        if language == '': # Unknown language
            print("\n%s%s%s" % (RED, "Sorry, Rebound doesn't support this file type.\n", END))
            sys.exit(1)
        file_path = args.script
        if language == 'java':
            file_path = [f.replace('.class', '') for f in file_path]
        output, error = execute([language] + file_path) # Compiles the file and pipes stdout
        if (output, error) == (None, None): # Invalid file
            sys.exit(1)

        error_msg = get_error_message(error, language) # Prepares error message for search
        if error_msg != None:
            language = 'java' if language == 'javac' else language # Fix language compiler command
            site = 'site:stackoverflow.com'
            query = "%s %s %s" % (language, error_msg,site)
            #search_results, captcha = search_stackoverflow(query)
            search_results = search_google(query)

            if search_results != []:
                # if captcha:
                #     print("\n%s%s%s" % (RED, "Sorry, Stack Overflow blocked our request. Try again in a minute.\n", END))
                #     return
                #elif confirm("\nDisplay Stack Overflow results?"):
                if confirm("\nDisplay Stack Overflow results?"):
                    App(search_results) # Opens interface
            else:
                print("\n%s%s%s" % (RED, "No Google results found.\n", END))
        else:
            print("\n%s%s%s" % (CYAN, "No error detected :)\n", END))

else: parser.print_help()

     




    
def execute_task(ProcessId):
  try:      
      while True:
          RunningProcess = Process(ProcessId)
  except NoSuchProcess as e:
        return
def confirm(question):
    """Prompts a given question and handles user input."""
    valid = {"yes": True, 'y': True, "ye": True,
             "no": False, 'n': False, '': True}
    prompt = " [Y/n] "

    while True:
        print(BOLD + CYAN + question + prompt + END)
        choice = input().lower()
        if choice in valid:
            return valid[choice]

        print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
def search_google(query):
    try:
      google_search = GoogleSearch()
      SearchArgs=(query,1)
      google_search.clear_cache()
      SearchDict=google_search.search(*SearchArgs)
    except Exception as e:
       sys.stdout.write("\n%s%s%s" % (RED,"Rebound was unable to fetch results. "
                                            +str(e)+"\n Try again Later.", END))
       sys.exit(1)

    return SearchDict  
def get_error_message(error, language):
    """Filters the stack trace from stderr and returns only the error message."""
    if error == '':
        return None
    elif language == "python3":
        if any(e in error for e in ["KeyboardInterrupt", "SystemExit", "GeneratorExit"]): # Non-compiler errors
            return None
        else:
            return error.split('\n')[-2].strip()
def MonitorProcess(ErrorLog,pid):
    ProcessState = execute_task(pid)
    #clear terminal  
    with open(ErrorLog,'r') as log:
        ErrorMessage = log.read()
    #ErrorMessage  = '\n \n Cant find module name scrappy \n '
    ValidError= print(RED+BOLD+ErrorMessage,file=sys.stdout) if get_error_message(ErrorMessage,'python3') is None else get_error_message(ErrorMessage,'python3') 
    #print(ValidError)
        #print to terminal and capture input while results are being fetched and cached
        # ErrorMessage = ErrMessage.split('\n')
    if ValidError is not None:
            print(RED+BOLD+ErrorMessage,file=sys.stdout)
            site = 'site:stackoverflow.com'
            query = "%s %s %s" % ('python', ValidError,site)
            search_results = search_google(query)
            if search_results != []:
                if confirm("\nDisplay Stack Overflow results?"):
                    App(search_results) # Opens interface
                    #print([i['title'] for i in search_results])
                    print([result for result in search_results]) 
            else:
                print("\n%s%s%s" % (RED, "No Google results found.\n", END))
    return 
