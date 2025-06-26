import csv

def filter_properties(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:

            # Check flood zone (exclude if starts with 'AE')
            if row['Flood Zone'].startswith('AE'):
                continue
            
            # Check drive time (exclude if > 25 mins)
            drive_time = float(row['Drive Time (mins)'])
            if drive_time > 25:
                continue
                
            # If passed both checks, write to output
            writer.writerow(row)
                


# Usage example:
filter_properties('3_properties_w_flood.csv', '4_filtered_properties.csv')