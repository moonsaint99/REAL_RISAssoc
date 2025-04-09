import pandas as pd
import os
import sys


def process_phase_data(input_file):
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Print some debugging information
        print(f"Total rows in input data: {len(df)}")
        print(f"Unique stations: {df['station_id'].nunique()}")
        print(f"Unique phase types: {df['phase_type'].unique()}")

        # Validate input data
        if df.empty:
            print("Error: Input file is empty")
            return

        # Get the date from the first timestamp for the output directory
        base_time = pd.to_datetime(df['begin_time'].iloc[0])
        output_dir = base_time.strftime('%Y%m%d')

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory created: {os.path.abspath(output_dir)}")

        # Preprocess station IDs to remove duplicate periods
        df['processed_station_id'] = df['station_id'].str.replace('..', '.')

        # Group the dataframe by processed station ID
        grouped = df.groupby('processed_station_id')

        # Counter for files created
        files_created = 0

        # Process each station group
        for station_id, group in grouped:
            try:
                # Split station_id into network and station
                parts = station_id.split('.')
                if len(parts) >= 2:
                    network, station = parts[0], parts[1]
                else:
                    print(f"Skipping invalid station ID: {station_id}")
                    continue

                # Prepare output filenames for P and S phases
                p_output_filename = os.path.join(output_dir, f'{network}.{station}.P.txt')
                s_output_filename = os.path.join(output_dir, f'{network}.{station}.S.txt')

                # Process P phases
                p_phases = group[group['phase_type'] == 'P'].sort_values('phase_time')
                if not p_phases.empty:
                    with open(p_output_filename, 'w') as f:
                        for _, row in p_phases.iterrows():
                            arrival_seconds = (pd.to_datetime(row['phase_time']) - base_time).total_seconds()
                            f.write(
                                f"{arrival_seconds:.6f} {row['phase_score']:.6f} {row['phase_amplitude'] * 1000:.6f}\n")
                    print(f"Created P phase file: {p_output_filename}")
                    files_created += 1

                # Process S phases
                s_phases = group[group['phase_type'] == 'S'].sort_values('phase_time')
                if not s_phases.empty:
                    with open(s_output_filename, 'w') as f:
                        for _, row in s_phases.iterrows():
                            arrival_seconds = (pd.to_datetime(row['phase_time']) - base_time).total_seconds()
                            f.write(
                                f"{arrival_seconds:.6f} {row['phase_score']:.6f} {row['phase_amplitude'] * 1000:.6f}\n")
                    print(f"Created S phase file: {s_output_filename}")
                    files_created += 1

            except Exception as station_error:
                print(f"Error processing station {station_id}: {station_error}")

        print(f"Total files created: {files_created}")

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()


# Check if the script is being run directly
if __name__ == '__main__':
    # Use a command-line argument for the input file, or default to 'paste.txt'
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'paste.txt'
    process_phase_data(input_file)