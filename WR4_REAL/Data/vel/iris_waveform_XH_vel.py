import os
import sys
import obspy
from obspy import UTCDateTime, read
from obspy.clients.fdsn import Client
import concurrent.futures

def process_station(
    station_line,
    client,
    tbeg,
    tend,
    rawdata_dir,
    dirdata
):
    """
    Process data for a single station line:
    download (if needed) raw data,
    remove response, and
    write processed SAC.
    """
    stlo, stla, net, sta, chan, elev = station_line.split()

    # Construct E, N, Z channel codes from the base channel
    chane = chan[:2] + "E"
    chann = chan[:2] + "N"
    chanz = chan[:2] + "Z"
    chan_list = [chane, chann, chanz]

    for chan1 in chan_list:
        raw_filename = os.path.join(rawdata_dir, f"{net}.{sta}.{chan1}.pkl")
        raw_inventory = os.path.join(rawdata_dir, f"{net}.{sta}.{chan1}.xml")
        processed_filename = os.path.join(dirdata, f"{net}.{sta}.{chan1}.SAC")

        # Step 1: Download raw data if not cached.
        if not os.path.exists(raw_filename):
            print(f"Downloading raw data for {net}.{sta}.{chan1}")
            try:
                st = client.get_waveforms(
                    network=net,
                    station=sta,
                    channel=chan1,
                    starttime=tbeg,
                    endtime=tend,
                    location="",        # or False if you want all locations
                    attach_response=True
                )
                # Merge and interpolate
                st.merge(method=1, fill_value='interpolate')
                st.interpolate(sampling_rate=100, starttime=tbeg, method="lanczos")  # 'starttime' corrected
                st.detrend("demean")
                st.detrend("linear")

                st.write(filename=raw_filename, format="PICKLE")

            except Exception as e:
                print(f"Error downloading {net}.{sta}.{chan1}: {e}")
                continue
        else:
            print(f"Using cached raw data: {raw_filename}")

        # Step 2: Remove instrument response and write SAC
        try:
            st = read(raw_filename)
            pre_filt = [0.001, 0.002, 25, 30]
            st.remove_response(
                pre_filt=pre_filt,
                water_level=None,
                taper=True,
                taper_fraction=0.00005,
                output='VEL'
            )
            st.write(filename=processed_filename, format="SAC")
        except Exception as e:
            print(f"Error processing {net}.{sta}.{chan1}: {e}")


def main():
    """
    Main function to handle command-line arguments, set up paths,
    and parallelize over station lines.
    """
    if len(sys.argv) != 2:
        print("Usage: script.py YYYY-MM-DD")
        sys.exit(1)

    date = sys.argv[1]
    dirdata = date.replace("-", "") + '/'
    rawdata_dir = os.path.join("raw_data", dirdata)
    tb = date + "T00:00:00.00Z"

    source = "IRIS"
    stationfile = "../iris.sta"
    tsec = 86400

    # Create directories if they don't exist
    if not os.path.exists(dirdata):
        os.makedirs(dirdata)
    if not os.path.exists(rawdata_dir):
        os.makedirs(rawdata_dir)

    # Set up ObsPy client, time range
    client = Client(source)
    tbeg = UTCDateTime(tb)
    tend = tbeg + tsec

    # Read station lines
    with open(stationfile, "r") as f:
        station_lines = f.read().splitlines()

    # Parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for station_line in station_lines:
            # submit a job for each line
            futures.append(
                executor.submit(
                    process_station,
                    station_line,
                    client,
                    tbeg,
                    tend,
                    rawdata_dir,
                    dirdata
                )
            )

        # Optionally, wait for all tasks (not strictly necessary if you just want to exit)
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()