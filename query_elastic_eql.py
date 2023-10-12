import os
import re
import requests
import yaml
import pandas as pd
import string
import traceback
import markdown
import random
import textwrap
import html


from mdtable import MDTable
from elasticsearch import Elasticsearch
from datetime import datetime


SCRIPT_DIRECTORY = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(SCRIPT_DIRECTORY, "config.yaml")


def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

config = load_config(CONFIG_PATH)

# authenticate to the elasticsearch api
es = Elasticsearch(
    f"https://{config['elasticsearch']['ip']}:{config['elasticsearch']['port']}",
    basic_auth=(config['elasticsearch']['user'], config['elasticsearch']['pass']),
    verify_certs=config['elasticsearch']['verify_certs'],
    ssl_show_warn=config['elasticsearch']['ssl_show_warn'],
    request_timeout=config['elasticsearch']['request_timeout'],
)


eql_queries = config['eql_queries']

for query_details in eql_queries:
    title = list(query_details.keys())[0].replace(' ', "_")
    query = list(query_details.values())[0]
    if not (title and query):
        continue
    try:
        range_filter = config['elasticsearch']['search_filter'].get('range', {}).get('@timestamp', '')
        print(f"[+] Querying <{range_filter}> for [{title.upper().replace('_', ' ')}]: {query}")
        response = es.eql.search(
            index=config['elasticsearch']['index'],
            wait_for_completion_timeout=config['elasticsearch']['completion_timeout'],
            filter=config['elasticsearch']['search_filter'],
            query=query,
            size=config['elasticsearch']['query_size']
        )

        # list to hold all events
        all_events = []


        HITS = int(response.get('hits', {}).get('total', {}).get('value', 0))
        print(f"[*] TOTAL HITS: {HITS}")
        # Return the sequences hit's if a sequence key exists, other the plain hits for the normal query
        _hits = response.get("hits", {})


        # create the directory if it doesn't already exist
        try:
            os.mkdir(os.path.join(SCRIPT_DIRECTORY, 'logs'))
        except Exception as e:
            # Directory already exists
            if e is not FileExistsError and "file" not in str(e).lower():
                print(f"[!] {str(e)}")
                traceback.print_exc()
            
        # create the directory
        directory = f"{SCRIPT_DIRECTORY}/logs/{title}"
        try:
            os.mkdir(directory)
        except Exception as e:
            pass

        if not _hits:
            print(f"[*] Skipping due to {HITS} hits...")
            continue


        # check if _hits contains a sequence
        sequences = _hits.get("sequences",response)


        # {"hits": {"events": [{"_source": data_i_want}]
        # OR
        # {"hits": {"sequences": [{"events": [{"_source": data_i_want}]}]}}
        
        response_hits = response.get("hits", {})
        sequences = response_hits.get("sequences", None)

        if sequences is None:
            # If there are no sequences, consider the events directly under hits
            sequences = [response_hits]

        for sequence in sequences:
            for event in sequence.get("events", []):
                _event = event.get("_source", {})
                # Extract the @timestamp
                timestamp = _event.get("@timestamp", "")
                # Extract the UtcTime using regex
                try:
                    utc_time_match = re.search(r"UtcTime: (.*)\n", _event.get("event", {}).get("ingested", _event.get("event", {})), re.DOTALL)
                    utc_time = utc_time_match.group(1) if utc_time_match else ""
                except Exception as e:
                    utc_time = ""
                # Add the timestamps to the record
                record = _event
                record["@timestamp"] = timestamp
                record["UtcTime"] = utc_time
                all_events.append(record)

        # convert list of events to DataFrame
        df = pd.DataFrame(all_events)
        if df.empty or HITS is None:
            print(f"Skipping due to {HITS} hits...")
            continue

        # to get just the process names
        process_names = df['process'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)

        # if you want to see the whole process info in a DataFrame
        process_info = df['process'].apply(pd.Series)

        #print(process_info)

        # Add the @timestamp and UtcTime to the DataFrame
        process_info["@timestamp"] = df["@timestamp"]
        process_info["UtcTime"] = df["UtcTime"]


        # get current date and time
        now = datetime.now()

        # format date and time as strings
        date_str = now.strftime("%y%m%d")
        time_str = now.strftime("%H%M%S")

        # create the filename
        filename = f"{directory}/eql_query_log_{date_str}_{time_str}"

        # write the DataFrame to a .log file
        process_info.replace('`', '~')
        process_info["NOTES"] = ""
        process_info.to_csv(filename+'.csv', sep='`', index=False)
        print(f"CSV Pandas Dataframe Output: {filename+'.csv'}")


        # Generate Mermaid graph
        mermaid_graph = "```mermaid\nflowchart LR\n"


        for index, row in process_info.iterrows():
            # if "parent" not in row
            # Sanitize the input by replacing problematic characters with their entity codes
            parent = str(row.get('parent', '')).replace("'", "").replace('"', "“")
            process_name = str(row.get('name', '')).replace("-", "#45;").replace(">", "#62;").replace("|", "#124;").replace("\n", "#10;").replace("{", "#123;").replace("}", "#125;").replace(":", "#58;").replace("'", "#39;").replace('"', "#34;")
            command_line = str(row.get('command_line', '')).replace("-", "#45;").replace(">", "#62;").replace("|", "#124;").replace("\n", "#10;").replace("{", "#123;").replace("}", "#125;").replace(":", "#58;").replace("'", "#39;").replace('"', "#34;")
            
            # Break long lines into multiple lines of 60 characters each
            if len(parent) > 60:
                parent = "`" + "\n".join(textwrap.wrap(parent, 60)) + "`"
            if len(process_name) > 60:
                process_name = "`" + "\n".join(textwrap.wrap(process_name, 60)) + "`"
            if len(command_line) > 60:
                command_line = "`" + "\n".join(textwrap.wrap(command_line, 60)) + "`"
            
            # RANDOM ASCII NAME, SO THERE ISN'T OVERLAP
            mermaid_graph += f"{get_random_string(10)}[\"PARENT: {parent}\"] -->|\"CMD_LINE: {command_line}\"| {get_random_string(10)}[\"PROC_NAME: {process_name}\"]\n\n"

        mermaid_graph += "```\n"

        # Save the Mermaid graph to a .md file
        with open(str(directory+f"/mermaid_output_{date_str}{time_str}"+".md"), 'w') as f:
            f.write(mermaid_graph)

        # Render the Markdown file with the Mermaid graph
        html = markdown.markdown(mermaid_graph, extensions=['md_mermaid'])

        # Save the rendered HTML to a file
        with open(str(filename+".html"), 'w') as f:
            f.write('''<html><head><title>Mermaid Diagram</title><script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script><script>mermaid.initialize({ startOnLoad: true, securityLevel: 'loose'}});</script></head><body>"''' + html  + '''</body></html>''')
        

        markdown = MDTable(filepath=str(filename+'.csv'), delimiter="`")
        markdown_string_table = markdown.get_table()
        markdown.save_table(os.path.join(directory, 'table.md'))


    except Exception as e:
        print(e)
        traceback.print_exc()
