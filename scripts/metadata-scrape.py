import os
import csv
import yaml
import re
import json
import pandas as pd

def find_qmd_and_ipynb_files(directory):
    """
    Recursively searches a directory and its subdirectories for files with .qmd or .ipynb extensions,
    excluding files named 'index.qmd'.
    
    Args:
        directory (str): The path to the directory to search.
        
    Returns:
        list: A list of full file paths for the matching files.
    """
    file_paths = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".qmd") and file != "index.qmd" or file.endswith(".ipynb"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    
    return file_paths

def extract_yaml_from_ipynb(file_path):
    """
    Extracts the YAML metadata from a Jupyter Notebook (.ipynb) file, excluding the '---' lines.
    
    Args:
        file_path (str): The full file path of the Jupyter Notebook file.
        
    Returns:
        dict: The YAML metadata as a dictionary, or None if not found.
    """
    with open(file_path, 'r') as file:
        notebook = json.load(file)
        
    for cell in notebook['cells']:
        if cell['cell_type'] == 'raw' and '---' in cell['source']:
            yaml_source = [line for line in cell['source'] if line.strip() != '---']
            yaml_source = ''.join(yaml_source)
            yaml_contents = yaml.safe_load(yaml_source)
            return yaml_contents
    
    return None

def generate_csv(file_paths):
    """
    Extracts relevant fields from the YAML contents of each file and writes them to a CSV file.
    
    Args:
        file_paths (list): A list of full file paths for the files to process.
    """
    
    doc_site = "graph"
    # arrays for core meta-data
    csv_rows = []
    analect_csv_rows = []
    
    # arrays for classic quarto metadata
    # for relationships
    category_csv_rows = []
    author_csv_rows = []
    source_csv_rows = []
    # for nodes: this approach is required for achieving uniqueness
    unique_categories = set()
    unique_authors = set()
    unique_sources = set()


    # Add the header row for core and rship datasets
    csv_rows.append(['FileIndex', 'DocSite', 'FileName', 'URL', 'Title', 'Description', 'Author', 'Categories', 'Date'])
    analect_csv_rows.append(['FileIndex', 'Project', 'DocSite', 'URL', 'Title', 'Date', 'ProjSynopsis', 'UseCase', 'Industry', 'DeployTarget', 'AppSet', 'BackstageTemplate', 'BackstageDocs', 'Workflow', 'FeaturePipe', 'TrainPipe', 'InferencePipe', 'LLM', 'Embedding', 'Registry', 'EndPoints', 'IaC', 'AppCode', 'Config', 'ObjectStore', 'DB', 'DataCentric', 'DataSource', 'Observe'])
    category_csv_rows.append(['FileIndex', 'Category']) # Used as Rship Table Kuzu: FROM, TO are first 2 columns
    author_csv_rows.append(['FileIndex', 'Author']) # Used as Rship Table Kuzu: FROM, TO are first 2 columns
    source_csv_rows.append(['FileIndex', 'LinkURL', 'LinkName']) # Used as Rship Table Kuzu: FROM, TO are first 2 columns
    
    for file_path in file_paths:
        if file_path.endswith(".qmd"):
            with open(file_path, 'r') as stream:
                contents = stream.read()

            delim = re.compile(r'^---$', re.MULTILINE)
            splits = re.split(delim, contents)
            yaml_preamble = splits[1].strip() if len(splits) > 2 else ""
            rest_of_post = splits[2] if len(splits) > 2 else contents

            yaml_contents = yaml.safe_load(yaml_preamble) if yaml_preamble else None
        elif file_path.endswith(".ipynb"):
            yaml_contents = extract_yaml_from_ipynb(file_path)
        else:
            continue
        
        if yaml_contents:
        # Extract relevant fields from the YAML contents
            file_name = os.path.basename(file_path)
            file_name_without_ext, _ = os.path.splitext(file_name)
            file_ext_without_dot = os.path.splitext(file_name)[1][1:]
            file_index = f"graph_{os.path.dirname(file_path).split('/')[-1]}_{file_name_without_ext}_{file_ext_without_dot}"
            url_fixed = os.path.dirname(file_path).replace('../', '')
            url_fixed = url_fixed.replace(' ', '%20')
            url = f"https://analect.github.io/quarto-graph-experiments/{url_fixed}/{file_name_without_ext}.html"
            title = yaml_contents.get('title', '')
            description = yaml_contents.get('description', '').replace('\n', ' ')
            # Extract source links from the description
            source_links = re.findall(r'\[(.*?)\]\((.*?)\)', description)
            author = yaml_contents.get('author', [])
            if isinstance(author, list):
                author_str = ', '.join(author)
            else:
                author_str = author
            categories = yaml_contents.get('categories', [])
            categories_str = ', '.join(categories)
            date = yaml_contents.get('date', '')

            
            # CORE QUARTO META-DATA FILES
            # append core_meta-data
            csv_rows.append([file_index, doc_site, file_name, url, title, description, author_str, categories_str, date])

            # FOR CATEGORY UNIQUE (FOR NODES) AND UNWOUND (FOR RSHIPS)
            # append categories_meta-data
            for category in categories:
                unique_categories.add(category)
                category_csv_rows.append([file_index, category])
                
            # FOR AUTHOR UNIQUE (FOR NODES) AND UNWOUND (FOR RSHIPS)
            # append author_meta-data
            if isinstance(author, list):
                for author_item in author:
                    unique_authors.add(author_item)
                    author_csv_rows.append([file_index, author_item])
                    # author_unique.add((author_item)) #for kuzu unique author
            else:
                author_csv_rows.append([file_index, author_str])
                unique_authors.add(author_str) #for kuzu unique author

            # FOR SOURCE UNIQUE (FOR NODES) AND UNWOUND (FOR RSHIPS)
            # Add the source link rows to the source_csv_rows
            for link_name, link_url in source_links:
                unique_sources.add(link_url) #for kuzu unique source
                # unique_sources.add((link_url, link_name)) #for kuzu unique source
                source_csv_rows.append([file_index, link_url, link_name])


    
    # Write the core_meta-data CSV file
    if not os.path.exists(f'{DATA_PATH}/core_meta-data.csv'):
        try:
            with open(f'{DATA_PATH}/core_meta-data.csv', 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_rows)
        except FileExistsError:
        # The file was created by another process after the existence check
            pass
    else:
        with open(f'{DATA_PATH}/core_meta-data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_rows)

    # Write the categories_meta-data CSV file
    if not os.path.exists(f'{DATA_PATH}/categories_meta-data.csv'):
        try:
            with open(f'{DATA_PATH}/categories_meta-data.csv', 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(category_csv_rows)
        except FileExistsError:
        # The file was created by another process after the existence check
            pass
    else:
        with open(f'{DATA_PATH}/categories_meta-data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(category_csv_rows)
    
    # Write the author_meta-data CSV file
    if not os.path.exists(f'{DATA_PATH}/author_meta-data.csv'):
        try:
            with open(f'{DATA_PATH}/author_meta-data.csv', 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(author_csv_rows)
        except FileExistsError:
        # The file was created by another process after the existence check
            pass
    else:
        with open(f'{DATA_PATH}/author_meta-data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(author_csv_rows)
    
    # Write the source_meta-data CSV file
    if not os.path.exists(f'{DATA_PATH}/source_meta-data.csv'):
        try:
            with open(f'{DATA_PATH}/source_meta-data.csv', 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(source_csv_rows)
        except FileExistsError:
        # The file was created by another process after the existence check
            pass
    else:
        with open(f'{DATA_PATH}/source_meta-data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(source_csv_rows)

    # Write the unique values to separate CSV files
    if not os.path.exists(f'{DATA_PATH}/unique_categories.csv'):
        try:
            with open(f'{DATA_PATH}/unique_categories.csv', 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Category'])
                for category in unique_categories:
                    writer.writerow([category])
        except FileExistsError:
        # The file was created by another process after the existence check
            pass
    else:
        with open(f'{DATA_PATH}/unique_categories.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Category'])
            for category in unique_categories:
                writer.writerow([category])


    # Write the unique values to separate CSV files
    if not os.path.exists(f'{DATA_PATH}/unique_author.csv'):
        try:
            with open(f'{DATA_PATH}/unique_author.csv', 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Author'])
                for author in unique_authors:
                    if author:
                        writer.writerow([author])
        except FileExistsError:
        # The file was created by another process after the existence check
            pass
    else:
        with open(f'{DATA_PATH}/unique_author.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Author'])
            for author in unique_authors:
                if author:
                    writer.writerow([author])


    # Write the unique values to separate CSV files
    if not os.path.exists(f'{DATA_PATH}/unique_source.csv'):
        try:
            with open(f'{DATA_PATH}/unique_source.csv', 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['LinkURL'])
                for source in unique_sources:
                    writer.writerow([source])
        except FileExistsError:
        # The file was created by another process after the existence check
            pass
    else:
        with open(f'{DATA_PATH}/unique_source.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['LinkURL'])
            for source in unique_sources:
                writer.writerow([source])

    
# Usage
DATA_PATH = "./data"
directory_to_search = "docs"
all_qmd_and_ipynb_files = find_qmd_and_ipynb_files(directory_to_search)
generate_csv(all_qmd_and_ipynb_files)
