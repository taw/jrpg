#!/usr/bin/perl -w

for(@ARGV) {
    my $outfn = $_;
    $outfn =~ s/\.jpe?g$/.png/ or die "$_ not a JPEG ?";

    `identify -format "%w %h" "$_"` =~ /(\d+) (\d+)/;
    my ($x, $y) = ($1, $2);
    die "Image $_ of $x x $y too small" if $x < 320 or $y < 320;
    my $m = $x < $y ? $x : $y;
    system qq[convert -crop "${m}x${m}+0+0" "$_" tmp.png];
    system qq[convert -resize "320x320!" "tmp.png" "bg-$outfn"];
}
