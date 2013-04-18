#!/usr/bin/perl -w -C
# Merged into demons_kanji_preprocess.pl

use utf8;

our %DIFF;
open DIFF, "kanji_diff" or die "Can't open kanji_diff file: $!";
for(<DIFF>) {
    /^(\d+) (.)/ or die "Format error in kanji_diff";
    $DIFF{$2} = $1+0;
}
close DIFF;

our %EASY;
our @HARD;

# Furiganized kanji's difficulty to unfuriganized kanji difficulty converter
# B(furi-A) = unfuri
my $magical_factor_a = 50;
my $magical_factor_b = 0.75;

sub difficulty_equiv {
    my ($hardest_base, $hardest_furi) = @_;
    max($hardest_base, ($hardest_furi-$magical_factor_a)*$magical_factor_b);
}

for(<>)
{
    chomp;
    my($level,$kanji,@readings) = split /\s+/, $_;
    if($level <= 3)
    {
        $EASY{$level} .= "$_\n";
        next;
    }
    # We ignore $level for $level >= 4, it's an artifact from the old days

    # @HARD is [difficulty, subsumed_by, line] list

    if(@readings) {
    # Has multiple readings, can't be divided
        my $diff = diff(split //, $kanji);
        push @HARD, [$diff, -1, join("\t",$kanji,@readings)];
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
            } elsif ($kanji =~ s/^(\((.*?)|.*?\))//) {
                my $frag = $1;
                $diff_furi = max($diff_furi,diff($2));
                push @res, [0, $frag, $frag];
                die;
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
        my @dswsfd = map { difficulty_equiv($_,$diff_furi) } @dsws;

        for my $i(0..$#dsws) {
            my $diff = $dsws[$i];
            my $final_diff = $dswsfd[$i];
            next if ($i != $#dsws and $final_diff == $dswsfd[$i+1]);
            my $r = "";
            for(@res) {
                $r .= ($diff >= $_->[0]) ? $_->[1] : $_->[2];
            }
            my $subsumed_by = ($i == $#dsws) ? -1 : scalar(@HARD)+1;
            push @HARD, [$final_diff, $subsumed_by, $r];
#            print "$final_diff ($diff) | $subsumed_by | $r\n"; # @@@
        }
    }
}

for(sort keys %EASY) {
    print $EASY{$_};
}
my @HARD_LOC = sort { $HARD[$a]->[0] <=> $HARD[$b]->[0] } (0..$#HARD);
my @REVERSE_HARD_LOC;
for(0..$#HARD) {
    $REVERSE_HARD_LOC[$HARD_LOC[$_]] = $_;
}
for(@HARD_LOC) {
    my @obj = @{$HARD[$_]};
    my $subsumed_by = $obj[1];
    $subsumed_by = $subsumed_by == -1 ? "" : ("\t#" . $REVERSE_HARD_LOC[$subsumed_by]);

    print "4\t", $obj[2], "$subsumed_by\n";
}

sub max
{
    my $res = shift;
    for(@_) {
        $res = $_ if $_ > $res;
    }
    return $res;
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
