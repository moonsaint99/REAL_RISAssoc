#!/usr/bin/perl -w
use Date::Calc qw(Delta_YMD);

# Ensure correct number of arguments (only 1 date)
if (@ARGV != 1) {
    die "Usage: $0 YYYY-MM-DD\n";
}

# Parse the date argument
my ($year, $month, $day) = split('-', $ARGV[0]);

# Validate the date (simple check)
if ($month < 1 || $month > 12 || $day < 1 || $day > 31) {
    die "Invalid date format. Please use YYYY-MM-DD.\n";
}

# Directory for processed files
$wa = "./wa";
if (!-e $wa) {
    `mkdir $wa`;
}

# Format date for directory names
my $dir = sprintf("%04d%02d%02d", $year, $month, $day);

# Process SAC files
my @sacs = glob "./vel/$dir/*.SAC";
if (!-e "$wa/$dir") {
    mkdir "$wa/$dir";
}

open(SAC, "|sac > jk");
foreach my $sac_file (@sacs) {
    chomp($sac_file);
    print SAC "r $sac_file\n";
    print SAC "bp c 0.05 15 n 4 p 2\n";  # Apply bandpass filter
    print SAC "transfer from vel to general n 2 f 0.8 d 0.7 m 2080\n";  # Transfer to Wood-Anderson
    print SAC "w $sac_file.wa\n";
}
print SAC "q\n";
close(SAC);

# Move processed files
`mv ./vel/$dir/*.wa $wa/$dir/`;
unlink "jk";