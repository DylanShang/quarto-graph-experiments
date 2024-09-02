COPY Author FROM "Author.csv" (escape ='\\', delim =',', quote='\"', header=true);
COPY Document FROM "Document.csv" (escape ='\\', delim =',', quote='\"', header=true);
COPY Source FROM "Source.csv" (escape ='\\', delim =',', quote='\"', header=true);
COPY Category FROM "Category.csv" (escape ='\\', delim =',', quote='\"', header=true);
COPY has_source FROM "has_source.csv" (escape ='\\', delim =',', quote='\"', header=true);
COPY has_category FROM "has_category.csv" (escape ='\\', delim =',', quote='\"', header=true);
COPY authored_by FROM "authored_by.csv" (escape ='\\', delim =',', quote='\"', header=true);
