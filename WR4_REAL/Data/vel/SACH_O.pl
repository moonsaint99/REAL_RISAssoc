#!/usr/bin/env perl
use warnings;

# Ensure that the correct number of arguments are passed
if (@ARGV != 1) {
    die "Usage: $0 YYYY-MM-DD\n";
}

# Parse the input date
my ($year, $month, $day) = split('-', $ARGV[0]);

# Validate the date (simple check)
if ($month < 1 || $month > 12 || $day < 1 || $day > 31) {
    die "Invalid date format. Please use YYYY-MM-DD.\n";
}

# Directory names based on the date provided
my $dir1 = sprintf("%04d%02d%02d", $year, $month, $day);
my $dir2 = $dir1;  # In this case, dir1 and dir2 are the same

# Julian day calculation (day of the year) (this may need to be different on Mac vs GNU)
my $date_input = "$year-$month-$day";
my $jday = `date -j -f "%Y-%m-%d" "$date_input" "+%j"`; # Get Julian day (1-366)
chomp($jday);

# Time variables
my $hour = "00";
my $min = "00";
my $sec0 = "00";
my $msec = "00";

# Fetch the list of SAC files
my @sac = glob "$dir1//*";

# Process the SAC files
open(SAC, "|sac> jk");
for (my $i = 0; $i < @sac; $i++) {
    chomp($sac[$i]);
    my ($jk, $name) = split("//", $sac[$i]);
    print SAC "r $sac[$i]\n";
    print SAC "ch o gmt $year $jday $hour $min $sec0 $msec\n";
    print SAC "evaluate to tmp 0 - &1,o\n";
    print SAC "ch allt %tmp% iztype io\n";
    print SAC "ch o 0\n";
    print SAC "w $dir2/$name\n";
}
print SAC "q\n";
close(SAC);

# Re-run SAC commands for final processing
open(SAC, "|sac > jk");
print SAC "r $dir2/*\n";
print SAC "w over\nq\n";
close(SAC);
unlink "jk";