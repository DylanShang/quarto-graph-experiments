from __future__ import annotations

import os
import shutil
from pathlib import Path

import kuzu
import polars as pl

#FileName,URL,FileIndex,Title,Description,Author,Categories,Date

def create_document_node_table(conn: kuzu.Connection) -> None:
    conn.execute(
        """
        CREATE NODE TABLE
            Document(
                FileIndex STRING,
                DocSite STRING,
                FileName STRING,
                URL STRING,
                Title STRING,
                Description STRING,
                Author STRING,
                Categories STRING,
                Date STRING,
                PRIMARY KEY (FileIndex)
            )
        """
    )


def create_category_node_table(conn: kuzu.Connection) -> None:
    conn.execute(
        """
        CREATE NODE TABLE
            Category(
                Category STRING,
                PRIMARY KEY (Category)
            )
        """
    )


def create_author_node_table(conn: kuzu.Connection) -> None:
    conn.execute(
        """
        CREATE NODE TABLE
            Author(
                Author STRING,
                PRIMARY KEY (Author)
            )
        """
    )


def create_source_node_table(conn: kuzu.Connection) -> None:
    conn.execute(
        """
        CREATE NODE TABLE
            Source(
                LinkURL STRING,
                PRIMARY KEY (LinkURL)
            )
        """
    )


def create_node_tables(conn: kuzu.Connection) -> None:
    create_document_node_table(conn)
    create_category_node_table(conn)
    create_author_node_table(conn)
    create_source_node_table(conn)

def create_edge_tables(conn: kuzu.Connection) -> None:
    # in format below, it seems you can add other property fields to the relationship
    # lower down, it is implementing just the relationship with no fields
    conn.execute(
        """
        CREATE REL TABLE 
            has_category(
                FROM Document TO Category
            )
        """
    )
    conn.execute("CREATE REL TABLE authored_by(FROM Document TO Author)")
    conn.execute("CREATE REL TABLE has_source(FROM Document TO Source, sourceName STRING)")
    

def main(conn: kuzu.Connection, DATA_PATH: Path) -> None:
    # Create edge table files from existing data
    # create_transaction_edge_file(conn)
    # create_merchant_edge_file(conn)
    # create_location_in_edge_file(conn)

    # Ingest nodes
    create_node_tables(conn)
    conn.execute(f"COPY Document FROM '{DATA_PATH}/core_meta-data.csv';")
    conn.execute(f"COPY Category FROM '{DATA_PATH}/unique_categories.csv';")
    conn.execute(f"COPY Author FROM '{DATA_PATH}/unique_author.csv';")
    conn.execute(f"COPY Source FROM '{DATA_PATH}/unique_source.csv';")
    print("Loaded nodes into KùzuDB")

    # Ingest edges
    create_edge_tables(conn)
    conn.execute(f"COPY has_category FROM '{DATA_PATH}/categories_meta-data.csv';")
    conn.execute(f"COPY authored_by FROM '{DATA_PATH}/author_meta-data.csv';")
    conn.execute(f"COPY has_source FROM '{DATA_PATH}/source_meta-data.csv';")
    print("Loaded edges into KùzuDB")


if __name__ == "__main__":
    DB_NAME = "data/kuzu-test"
    # Delete directory each time till we have MERGE FROM available in kuzu
    if os.path.exists(DB_NAME):
        shutil.rmtree(DB_NAME)
    # Create database
    db = kuzu.Database(f"./{DB_NAME}")
    conn = kuzu.Connection(db)

    DATA_PATH = Path("data")

    # clean_unique_files(DATA_PATH)
    main(conn, DATA_PATH)