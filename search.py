import csv

def search_csv(database_file, search_query, url):
    results = []
    with open(database_file, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if search_query.lower() in row['Title'].lower() and url.lower() in row['URL'].lower():
                results.append(row)
    return results

def main():
    database_file = ""  # Replace with your CSV file name
    search_query = input("Enter search query: ")
    url = input("Enter URL: ")

    results = search_csv(database_file, search_query, url)

    if results:
        print("Search results:")
        for result in results:
            print(f"Title: {result['Title']}")
            print(f"URL: {result['URL']}")
            print()
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
