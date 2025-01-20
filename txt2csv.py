import csv

def txt_to_csv(txt_file, csv_file, column_headers):
    try:
        # Open the txt file for reading
        with open(txt_file, 'r') as txt_f:
            lines = txt_f.readlines()

        # Open the csv file for writing
        with open(csv_file, 'w', newline='') as csv_f:
            csv_writer = csv.writer(csv_f, delimiter=';')  # Using comma for CSV separation

            # Write the header line
            csv_writer.writerow(column_headers)

            # Process each line in the txt file
            for line in lines:
                # Assuming the columns in the txt file are separated by ','
                row = line.strip().split(',')  # Split by semicolon
                # Convert all elements to numbers if they are numeric
                row = [float(item) if item.replace('.', '', 1).isdigit() else item for item in row]
                csv_writer.writerow(row)

        print(f"Data has been successfully converted from {txt_file} to {csv_file} with headers.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
txt_file = 'calib_aT3_data/data_ndi/fourth_time/group1.txt'  # Replace with the path to your txt file
csv_file = 'calib_aT3_data/data_ndi/fourth_time/group1.csv'  # Output CSV file path
column_headers = ['X  [mm]', 'Y  [mm]', 'Z  [mm]', 'q0', 'q1', 'q2', 'q3']  # Replace with appropriate headers for your data

txt_to_csv(txt_file, csv_file, column_headers)