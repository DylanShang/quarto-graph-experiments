COPY Author FROM "Author.parquet" (escape ='\\', delim =',', quote='\"', header=false);
COPY Document FROM "Document.parquet" (escape ='\\', delim =',', quote='\"', header=false);
COPY Source FROM "Source.parquet" (escape ='\\', delim =',', quote='\"', header=false);
COPY Category FROM "Category.parquet" (escape ='\\', delim =',', quote='\"', header=false);
COPY has_source FROM "has_source.parquet" (escape ='\\', delim =',', quote='\"', header=false);
COPY has_category FROM "has_category.parquet" (escape ='\\', delim =',', quote='\"', header=false);
COPY authored_by FROM "authored_by.parquet" (escape ='\\', delim =',', quote='\"', header=false);
