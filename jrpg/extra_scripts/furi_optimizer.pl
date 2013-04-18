#!/usr/bin/perl -w -C
# Merged into demons_kanji_preprocess.pl

use utf8;

# Only compound-common hatsuon is relevant
our %common_kanji_hatsuon;

open F, "common_kanji_hatsuon" or die "Can't open common_kanji_hatsuon file: $!";
for(<F>)
{
    chomp;
    my ($kj,@ho) = split /\s+/, $_;
    push @{$common_kanji_hatsuon{$kj}}, @ho;
}
close F;


while (defined ($line = <>)) {
    $line =~ s/\[([^\|\]]{2,})\|(.*?)\]/furi_optimize($1,$2)/eg;
    print $line;
}

sub furi_optimize {
    my ($kanji, $furi) = @_;
    my $res = "";
    my $res2 = "";

    # Operations at the beginning
    LOOP_START: while(1) {
        last if $kanji eq "";
        my $ks = substr $kanji,0,1;
        my $kr = substr $kanji,1;
        if($ks eq "～" or $ks eq "~") {
            $kanji = $kr;
            $res  .= "{$ks}";
            next;
        }
        if($ks eq substr $furi,0,1) {
            $res  .= $ks;
            $kanji = $kr;
            $furi  = substr $furi,1;
            next;
        }
        # The next operation makes sense only for simplifying multikanji furigana
        # If the furigana is for a single kanji already, don't run it
        last if $kr eq "";
        for my $hatsuon(@{$common_kanji_hatsuon{$ks}}) {
            if($hatsuon eq substr $furi, 0, length($hatsuon)) {
                $res  .= "[$ks|$hatsuon]";
                $kanji = $kr;
                $furi  = substr $furi, length($hatsuon);
                next LOOP_START;
            }
        }
        last;
    }
    # Operations at the end
    LOOP_END: while(1) {
        last if $kanji eq "";
        my $ke = substr $kanji,-1;
        my $kr = substr $kanji,0,-1;
        if($ke eq "～" or $ke eq "~") {
            $kanji = $kr;
            $res2 = "{$ke}".$res2;
            next;
        }
        if($ke eq substr $furi,-1) {
            $res2  = $ke.$res2;
            $kanji = $kr;
            $furi  = substr $furi,0,-1;
            next;
        }
        # The next operation makes sense only for simplifying multikanji furigana
        # If the furigana is for a single kanji already, don't run it
        last if $kr eq "";
        for my $hatsuon(@{$common_kanji_hatsuon{$ke}}) {
            if($hatsuon eq substr $furi, -length($hatsuon)) {
                $res2  = "[$ke|$hatsuon]" . $res2;
                $kanji = $kr;
                $furi  = substr $furi, 0, -length($hatsuon);
                next LOOP_END;
            }
        }
        last;
    };
    # If only one of them is nonempty, it's a bug
    return "$res$res2" if $kanji eq "" and $furi eq "";
    return ($res."[$kanji|$furi]$res2") if $kanji ne "" and $furi ne "";
    die("Only one of (kanji|furigana) is nonempty - $res"."[$kanji|$furi]$res2)");
}
