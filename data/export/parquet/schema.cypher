CREATE NODE TABLE Author (Author STRING, PRIMARY KEY(Author));
CREATE NODE TABLE Document (FileIndex STRING,DocSite STRING,FileName STRING,URL STRING,Title STRING,Description STRING,Author STRING,Categories STRING,Date STRING, PRIMARY KEY(FileIndex));
CREATE NODE TABLE Source (LinkURL STRING, PRIMARY KEY(LinkURL));
CREATE NODE TABLE Category (Category STRING, PRIMARY KEY(Category));
CREATE REL TABLE has_source (FROM Document TO Source, sourceName STRING,MANY_MANY);
CREATE REL TABLE has_category (FROM Document TO Category, MANY_MANY);
CREATE REL TABLE authored_by (FROM Document TO Author, MANY_MANY);
