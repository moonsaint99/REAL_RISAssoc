import obspy
from obspy.clients.fdsn.mass_downloader import RectangularDomain, Restrictions, MassDownloader

domain = RectangularDomain(
    minlatitude=-90,
    maxlatitude=-70,
    minlongitude=0,
    maxlongitude=180
)

restrictions = Restrictions(
    starttime=obspy.UTCDateTime(2014,11,28),
    endtime=obspy.UTCDateTime(2016,11,1),
    chunklength_in_sec=86400,
    network="XH",station='DR05,DR06,DR07,DR08,DR09,DR10,DR11,DR12,DR13,DR14,DR15,RS04,RS05',
    channel='HH*',
    location="",
    reject_channels_with_gaps=False,
)

mdl = MassDownloader(providers='IRIS')
mdl.download(domain, restrictions, mseed_storage="waveforms",
             stationxml_storage="stations")