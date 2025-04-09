#!/usr/bin/env python

import os
import glob
from obspy import read, UTCDateTime
import matplotlib.pyplot as plt

def parse_phase_file(phase_file):
    """
    Parses a phase_sel.txt-like file and returns a list of event dictionaries.

    Each dictionary has:
        - 'event_time': an ObsPy UTCDateTime object
        - 'stations': a list of station codes for that event
    """
    events = []
    with open(phase_file, 'r') as f:
        lines = f.readlines()

    current_event = None

    # Helper function to finalize an event in the list
    def finalize_event(ev):
        if ev is not None:
            if 'event_time' in ev:
                # Ensure we have a stations list, even if empty
                if 'stations' not in ev:
                    ev['stations'] = []
                events.append(ev)

    for line in lines:
        parts = line.split()
        # We’ll detect a new event line by checking that the first
        # token is an integer and has at least 5 numeric columns for date/time
        try:
            # If this conversion fails, it's not an event line
            _ = int(parts[0])
            # If we got here, it’s likely an event line
            # Finalize any previously open event
            finalize_event(current_event)

            # Start a new event
            current_event = {}

            # Example line (first 5 columns):
            # 1   2014 11 30 13:05:05.117
            # Indices: 0 -> 1, 1 -> 2014, 2 -> 11, 3 -> 30, 4 -> 13:05:05.117
            year  = int(parts[1])
            month = int(parts[2])
            day   = int(parts[3])

            # The time is in parts[4] = 'HH:MM:SS.sss'
            hh, mm, ss = parts[4].split(':')
            hh = int(hh)
            mm = int(mm)
            ss = float(ss)

            # Create UTCDateTime
            current_event['event_time'] = UTCDateTime(year, month, day, hh, mm, ss)
            current_event['stations'] = []

        except ValueError:
            # If it's not an event line, it might be a station line
            # Typically: "XH     DR09     P   47111.2300  ..."
            # The station code might appear in a fixed position, e.g. parts[1]
            if current_event is not None and len(parts) > 1:
                # e.g., network = parts[0], station=parts[1]
                # We'll store station code as network.station, or just station
                station_code = parts[1].strip()
                if station_code not in current_event['stations']:
                    current_event['stations'].append(station_code)

    # Don’t forget to finalize the last event if file ends
    finalize_event(current_event)
    return events

def plot_event_waveforms(event_time, stations, base_dir='.', time_before=10, time_after=30):
    """
    For the given event time and set of station codes, read the daily folder
    (named YYYYMMDD) and load all relevant SAC files for that day. Then trim
    to event_time +/- the specified window and plot.

    Parameters
    ----------
    event_time : UTCDateTime
        The origin time of the event.
    stations : list of str
        List of station codes to read. (e.g. [DR10, DR09, ...])
    base_dir : str
        Directory that contains the daily subfolders (YYYYMMDD).
    time_before : float
        Seconds before the event time to include in the plot.
    time_after : float
        Seconds after the event time to include in the plot.
    """

    # Determine the folder name from the event date
    day_folder = event_time.strftime("%Y%m%d")
    full_path_to_day = os.path.join(base_dir, 'vel/'+day_folder)

    # If you want to plot only those stations found in the picks:
    # You might loop over each station and each component (HHE, HHN, HHZ).
    # If you want to get absolutely everything, you could use a wildcard 'XH.*.HH?.SAC'.
    st = None
    components = ["HHE", "HHN", "HHZ"]
    for station in stations:
        for comp in components:
            pattern = f"XH.{station}.{comp}.SAC"
            sac_files = glob.glob(os.path.join(full_path_to_day, pattern))
            for sacf in sac_files:
                try:
                    # Read the file
                    stream_tmp = read(sacf)
                    # Combine
                    if st is None:
                        st = stream_tmp
                    else:
                        st += stream_tmp
                except Exception as e:
                    print(f"Could not read {sacf}: {e}")

    # If no data found, just return
    if not st:
        print(f"No data found for event on {event_time} in folder {full_path_to_day}")
        return

    # Merge or fix any overlaps/gaps
    st.merge(method=1, fill_value='interpolate')

    # Trim the waveforms
    start_time = event_time - time_before
    end_time = event_time + time_after
    st.trim(start_time, end_time)

    # after you have your Stream 'st' trimmed:
    st.sort(['station'])

    # Optionally filter or normalize:
    # st.filter("bandpass", freqmin=1.0, freqmax=20.0)
    # st.normalize(global_max=True)

    # Plot:
    st.plot(
        type='relative',
        color_per_channel=True,
        equal_scale=False,
        size=(1000, 800),
        linewidth=0.8,
        reftime=event_time
    )

def main():
    phase_file = "../REAL/cat_output_jan23/phase_sel.txt"  # path to your phase selection file
    events = parse_phase_file(phase_file)

    # Loop over each event in the file
    for i, ev in enumerate(events, 1):
        event_time = ev['event_time']
        stations   = ev['stations']

        print(f"Processing event #{i} at {event_time.isoformat()} with stations {stations}")

        # Adjust base_dir if your daily subfolders are not in the current working directory
        plot_event_waveforms(event_time, stations, base_dir='.')

if __name__ == "__main__":
    main()