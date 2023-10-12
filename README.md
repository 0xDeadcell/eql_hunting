### Elasticsearch Automated EQL Hunting Visualized

#### Description
This project is a comprehensive tool designed for hunting potential security threats and anomalies within an Elasticsearch environment using Event Query Language (EQL) and visualizing the findings. It is equipped with pre-configured EQL queries to detect suspicious activities and outputs the results into various formats including CSV, Mermaid graphs, and Markdown tables for further analysis.

#### Configuration
The project uses a YAML configuration file to connect to the Elasticsearch cluster. The configuration options include the cluster's IP, port, username, password, the index to query, and other parameters. It is highly advised to modify the index before executing each query.

#### EQL Queries
Several EQL queries are included to identify potential security threats such as:
- Suspicious Linux activity after a connection
- Rundll32 execution with base64 arguments nearby network activity
- DNS queries near command executables
- Registry server (regsvr32) execution and process creation
- DLL side loading via common Microsoft programs

...and more.

These queries are highly configurable and can be adjusted to meet specific use cases or environments.

#### How It Works
The Python script reads the configuration and EQL queries from the `config.yaml` file and executes each query on the specified Elasticsearch index. The results are then processed and exported in multiple formats including CSV for data analysis, Mermaid graphs for visual representation, and Markdown tables for easy reporting.

#### Prerequisites
- Python 3.x
- Elasticsearch cluster
- Necessary Python packages as listed in `requirements.txt`

#### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/0xDeadcell/eql_hunting.git
    cd eql_hunting
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Modify the `config.yaml` file with your Elasticsearch cluster details and desired index.

#### Usage
Run the Python script to execute the EQL queries and generate the reports.
```sh
python query_elastic_eql.py
```

#### Output
The results will be saved in the `logs` directory, organized by query title. Each query's results are available as a CSV file, a Mermaid graph saved as a Markdown file, and an HTML file for easy viewing. A Markdown table is also generated for convenient reporting.

#### Note
Be cautious when using the `"*"` index in the `config.yaml` file, as it might result in extensive resource usage depending on the size of your Elasticsearch cluster.
