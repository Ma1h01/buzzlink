import csv


def merge_urls(*csv_paths):
	'''
	Merge URLs from multiple CSV files into a single CSV file.
	Args:
		csv_paths: A list of paths to CSV files.
	'''
	output_csv = 'merged_urls.csv'
	urls = set()
	with open(output_csv, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerow(['url'])
		for csv_path in csv_paths:
			with open(csv_path, 'r', newline='', encoding='utf-8') as f2:
				reader = csv.reader(f2)
				next(reader)
				for row in reader:
					url = row[0]
					if url not in urls:
						urls.add(url)
						writer.writerow([url])
					else:
						print(f"Duplicate URL: {url}")
	print(f"Final CSV file length: {len(urls)}")