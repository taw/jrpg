#!/usr/bin/perl -w -C

use utf8;
use strict;

#####################################################################
# Aux functions                                                     #
#####################################################################

sub max
{
    my $res = shift;
    for(@_) {
        $res = $_ if $_ > $res;
    }
    return $res;
}

#####################################################################
# common_kanji_hatsuon                                              #
#####################################################################

# Only compound-common hatsuon is relevant
our %common_kanji_hatsuon;

open F, "data/common_kanji_hatsuon" or die "Can't open data/common_kanji_hatsuon file: $!";
for(<F>)
{
    chomp;
    my ($kj,@ho) = split /\s+/, $_;
    push @{$common_kanji_hatsuon{$kj}}, @ho;
}
close F;

#####################################################################
# kanji_learning_order                                              #
#####################################################################

our %DIFF;
open DIFF, "kanji_learning_order" or die "Can't open kanji_learning_order file: $!";
for(<DIFF>) {
    /^(\d+) (.)/ or die "Format error in kanji_learning_order";
    $DIFF{$2} = $1+0;
}
close DIFF;

#####################################################################
# Phase 1                                                           #
#####################################################################

# For communication between the phases
my @PHASE_OUT;

my $line;
while (defined ($line = <>)) {
    chomp $line;
    my @e = split /\t/, $line;
    if(@e == 2) {
        $e[1] =~ s/\[([^\|\]]{2,})\|(.*?)\]/furi_optimize($1,$2)/eg;
    } elsif (@e == 3) {
            @e = ($e[0], furi_optimize($e[1],$e[2]));
    }
    push @PHASE_OUT, [@e];
}

sub furi_optimize {
    my ($kanji, $furi) = @_;
    my $res = "";
    my $res2 = "";

    my $move_leading_kana = sub {
        # $res, $kanji, $furi - function-scope
        my $mod = 0;
        while(1) {
#        print "LK: ($kanji) ($furi)\n";
            last if $kanji eq "";
            my $ks = substr $kanji,0,1;
            my $kr = substr $kanji,1;
            if($ks eq "～" or $ks eq "~") {
                $kanji = $kr;
                $res  .= "{$ks}";
                $mod=1;
                next;
            }
            if($ks eq substr $furi,0,1) {
                $res  .= $ks;
                $kanji = $kr;
                $furi  = substr $furi,1;
                $mod=1;
                next;
            }
            last;
        }
        return $mod;
    };
    my $move_trailing_kana = sub {
        # $res2, $kanji, $furi - function-scope
        my $mod = 0;
        while(1) {
        #print "TK: ($kanji) ($furi)\n";
            last if $kanji eq "";
            my $ke = substr $kanji,-1;
            my $kb = substr $kanji,0,-1;
            if($ke eq "～" or $ke eq "~") {
                $kanji = $kb;
                $res2 = "{$ke}".$res2;
                next;
            }
            if($ke eq substr $furi,-1) {
                $kanji = $kb;
                $furi  = substr $furi,0,-1;
                $res2  = $ke.$res2;
                next;
            }
            last;
        }
        return $mod;
    };

    # Move trailing *X out
    if ($kanji =~ /(.*)(\*.)$/) {
            $kanji = $1;
            $res2 .= $2;
    }
    LOOP: while(1) {
        #print "LOOP: ($kanji) ($furi)\n";

        last if $kanji eq "";
        $move_leading_kana->();

        last if $kanji eq "";
        $move_trailing_kana->();
        # At this point the kanji has no leading or trailing kana
        # It may still have some kana in the middle

        # The next operations makes sense only for simplifying multikanji furigana
        # If the furigana is for a single kanji already, don't run it

        # It's safer to start from the end
        last if $kanji eq "";
        my $ke = substr $kanji,-1;
        my $kb = substr $kanji,0,-1;
        last if $kb eq "";
        for my $hatsuon(@{$common_kanji_hatsuon{$ke}}) {
            if($hatsuon eq substr $furi, -length($hatsuon)) {
                $res2  = "[$ke|$hatsuon]" . $res2;
                $kanji = $kb;
                $furi  = substr $furi, 0, -length($hatsuon);
                # Rerun the loop if something got stripped
                next LOOP;
            }
        }

        last if $kanji eq "";
        my $ks = substr $kanji,0,1;
        my $kr = substr $kanji,1;
        last if $kr eq "";
        for my $hatsuon(@{$common_kanji_hatsuon{$ks}}) {
            if($hatsuon eq substr $furi, 0, length($hatsuon)) {
                $res  .= "[$ks|$hatsuon]";
                $kanji = $kr;
                $furi  = substr $furi, length($hatsuon);
                # Rerun the loop if something got stripped
                next LOOP;
            }
        }

        # Well, we failed
        last;
    };
    # If only one of them is nonempty, it's a bug
    return "$res$res2" if $kanji eq "" and $furi eq "";
    return ($res."[$kanji|$furi]$res2") if $kanji ne "" and $furi ne "";
    die("Only one of (kanji|furigana) is nonempty - $res"."[$kanji|$furi]$res2)");
}

###########################################################
# Phase 2 - add partially furiganized kanji               #
###########################################################

our @RESULTS;

sub difficulty_equiv {
    # Furiganized kanji's difficulty to unfuriganized kanji difficulty converter
    # B(furi-A) = unfuri

    my $magical_factor_a = 50;
    my $magical_factor_b = 0.75;

    my ($level, $hardest_base, $hardest_furi) = @_;
    # (0.0001*$hardest_furi) just to get sane ordering of the first 50
    100*$level + max($hardest_base+0.0001*$hardest_furi, ($hardest_furi-$magical_factor_a)*$magical_factor_b);
}

# Just filter out thing we've seen on previous levels
my %seen = ();
for(@PHASE_OUT)
{
    my @e = @$_;
    $_ = join("\t",@e); # Blah
    my $seen_key = join("\t",@e[1..$#e]);
    if($seen{$seen_key}){
        #print STDERR "@e filtered out\n";
        next;
    }
    $seen{$seen_key}=1;

    my($level,$kanji,@readings) = @e;
    $level -= 3; # To start from 0, $level = 3 or 4 or 5

    # @RESULTS is [difficulty, subsumed_by, line] list

    if(@readings) {
    # Has multiple readings, can't be divided
        my $diff = diff(split //, $kanji);
        push @RESULTS, [$diff, -1, join("\t",$kanji,@readings)];
    } else {
        $kanji =~ s/(.)\|([^\]]+)\]\[々/$1|$2][々#$1/g;
        die "Weird 々 in $_" if $kanji =~ /々[^#]/;
        # type(@res) = (switch, hard, easy) list
        my @res = ();
        # Difficulty of all [X|Y] fragments, to decide what to furiganize
        my %dsw = ();
        # Difficulty of the hardest *potentially* furiganized kanji in the word
        my $diff_furi = 0;
        while($kanji ne "") {
            if ($kanji =~ s/^(\{.*?\})//) {
                push @res, [0, $1, $1];
            } elsif ($kanji =~ s/^(\((.*?)\|.*?\))//) {
                my ($frag, $kj) = ($1, $2);
                my $d = diff($kj);
                push @res, [$d, $frag, $frag];
                $dsw{$d} = 1;
                $diff_furi = max($diff_furi,$d);
                # Support pre-furiganized kanjis too
            } elsif ($kanji =~ s/^\[(.*?)\|(.*?)\]//) {
                my ($kj, $furi) = ($1, $2);
                my $d = diff($kj =~ /(?:々#)?(.)/g);
                $kj =~ s/#.//g;
                push @res, [$d, "[$kj|$furi]", "($kj|$furi)"];
                $dsw{$d} = 1;
                $diff_furi = max($diff_furi,$d);
            } elsif ($kanji =~ s/^(.)//) {
                push @res, [0, $1, $1];
            }
        }
        my $last_diff = -1;
        # Do not generate 2 kanjis at the same difficulty
        # For example if the word is [X 5][Y 200][Z 10]
        # Then difficulties are:
        # [X](Y)(Z) 100 - useless
        # [X](Y)[Z] 100
        # [X][Y](Z) 200
        # And there's no reason to generate the first one

        # Table of per-fragment difficulty
        my @dsws   = sort {$a <=> $b} keys %dsw;

        # Real bountary difficulties
        my @dswsfd = map { difficulty_equiv($level,$_,$diff_furi) } @dsws;

        for my $i(0..$#dsws) {
            my $diff = $dsws[$i];
            my $final_diff = $dswsfd[$i];
            next if ($i != $#dsws and $final_diff == $dswsfd[$i+1]);
            my $r = "";
            for(@res) {
                $r .= ($diff >= $_->[0]) ? $_->[1] : $_->[2];
            }
            my $subsumed_by = ($i == $#dsws) ? -1 : scalar(@RESULTS)+1;
            push @RESULTS, [$final_diff, $subsumed_by, $r];
#            print "$final_diff ($diff) | $subsumed_by | $r\n"; # @@@
        }
    }
}

sub diff
{
    my $diff = 0;
    for(@_) {
        # Lone 々 exists only in multi-meaning words (方々 かたがた ほうぼう)
        my $cd = defined $DIFF{$_}         ? $DIFF{$_} :
                 /\p{Hiragana}/            ?     0     :
                 /\p{Katakana}/            ?     0     :
                 ($_ eq "～" or $_ eq "々") ?     0     :
                                             10000;
        $diff = $cd if $cd > $diff;
    }
    return $diff;
}

###########################################################
# Phase 3 - sort and print everything out                 #
###########################################################

my @RESULTS_LOC = sort { $RESULTS[$a]->[0] <=> $RESULTS[$b]->[0] } (0..$#RESULTS);
my @REVERSE_RESULTS_LOC;
for(0..$#RESULTS) {
    $REVERSE_RESULTS_LOC[$RESULTS_LOC[$_]] = $_;
}
for(@RESULTS_LOC) {
    my @obj = @{$RESULTS[$_]};
    my $subsumed_by = $obj[1];
    $subsumed_by = $subsumed_by == -1 ? "" : ("\t#" . $REVERSE_RESULTS_LOC[$subsumed_by]);

    print "3\t", $obj[2], "$subsumed_by\n";
}
