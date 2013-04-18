#!/usr/bin/perl -w -C

use utf8;
use strict;

sub prepare_key_rx {
    my $key = shift @_;
    my $key_rx;
    if ($key =~ /^(.*)する$/) {
        $key_rx = "$1(する|します|して|した)";
    } elsif ($key =~ /^(.*)る$/) {
        # Should work with both godan and ichidan
        $key_rx = "$1(る|たら|なさい|た|て|よう|られた|られて|られる|られます|たがり|ない|なくて|ます|って|った|ろう|ります|られました|れば|れない|らない|えて|りました|りに|ましょう|られない|ません|りましょう|りたかった|りたい|れませんでした|りあわせた|れる|です|いません|ろ|ました|れません|らなかった|りません|りそう|に|らせよう|ちゃった|らなければ|らせた|らせて|なければ|ながら|なかった|っちゃった|っちゃって|させます|くだろう|なかった|けなければ|り|)";
    } elsif ($key =~ /^(.*)う$/) {
        $key_rx = "$1(う|った|って|いない|えません|えば|いました|おう|いましょう|えて|いたい|いしましょう|いに|いできる|いします|いして|われて|われる|われません|わない|います|えない|いしたい|わなかった|える|えた|います|わなければ|いなさい|われた|われました|わなくちゃ|わなく|わせた|わずに|わざる|えます|いません|いながら|いたく|いたかった|いたい|い)";
    } elsif ($key =~ /^(.*)く$/) {
        $key_rx = "$1(く|いた|いて|けば|ける|かなくて|かなければ|けなかった|きました|きなさい|きます|かれた|って|った|こう|けません|けます|けない|きません|きましょう|きながら|きたければ|きたく|きたがって|きたい|かなく|かなかった|かない|き)";
    } elsif ($key =~ /^(.*)す$/) {
        $key_rx = "$1(す|された|した|して|しましょう|せない|せば|せます|させよう|せません|しなさい|される|さない|そう|しません|します|しました|さなさい|しに|しながら|されて|されない|し)";
    } elsif ($key =~ /^(.*)む$/) {
        $key_rx = "$1(む|んだ|んで|みたい|める|まない|まなく|めば|みながら|みます|もう|みなさい|まなければ|まれた|みましょう|めます|めなかった|めません|めない|みません|みました|みたく|みたがって|みたかった|まれました|まれて|まなかった|ませた|ませて|み)";
    } elsif ($key =~ /^(.*)ぬ$/) {
        $key_rx = "$1(ぬ|んで|にます|にません|んだ|ななければ|に)";
    } elsif ($key =~ /^(.*)ぐ$/) {
        $key_rx = "$1(ぐ|いで|いだ)";
    } elsif ($key =~ /^(.*)ぶ$/) {
        $key_rx = "$1(ぶ|んだ|んで|べば|ばれる|べます|べる|びたい|ばれる|びましょう|びました|びます|びに|びなさい|びながら|ばれて|ばれた|ばなくて|ばない|ばせる|ばせた|び)";
    } elsif ($key =~ /^(.*)い$/) {
        $key_rx = "$1(い|くない|くなかった|かった|く|さ|)";
    } elsif ($key =~ /^(.*)つ$/) {
        $key_rx = "$1(つ|った|って|てば|てない|てた|とう|てなく|ちます|ちましょう|ちません|ちました|たない|ち)";
    } else {
        $key_rx = $key;
    }
    return $key_rx;
}

sub highlight_keys {
    my ($j, @keys) = @_;
    # @matches[3i] - keys that go unhighlighted at i
    # @matches[3i+1] - keys that go highlighted at i
    # @matches[3i+2] - ith character

    my @matches;
    for my $ki(0..$#keys) {
        my $k = $keys[$ki];
        my ($key, $key_pron) = @$k;

        my $key_rx = prepare_key_rx($key);
        my $got_match;

        while($j =~ /$key|$key_rx/g) {
            push @{$matches[3*$-[0]+1]}, "<$key+>";
            push @{$matches[3*$+[0]]}, "<$key->";
            #print "I have key NEEDED $key for sentence #", ($#sentence+1), "\n";
            #next;
            $got_match = 1;
        }
        # Proceed to kana keys only if kanji didn't match
        next if $got_match;

        if($key_pron) {
            my $key_rx2 = prepare_key_rx($key_pron);
            while($j =~ /$key_pron|$key_rx2/g) {
                push @{$matches[3*$-[0]+1]}, "<$key+>";
                push @{$matches[3*$+[0]]}, "<$key->";
            }
        }
    }
    while($j =~ /(.)/g) {
        push @{$matches[3*$-[0]+2]}, $1;
    }
    my $res;
    for(@matches) {
        next unless $_;
        $res .= join ("", sort @$_);
    }
    return $res;
}

sub test_highlight_keys {
    my @test_cases = (
        ["〆切に<間に合う+>間に合います<間に合う->か。", "〆切に間に合いますか。", ["間に合う", undef]],

        # Highlighter isn't supposed to know word boundaries, so it's going ho highlight 彼 in 彼女 also
        ["「５<日+>日<日-><前+>前<前->に<彼+><彼女+>彼<彼->女<彼女->にあった」と<彼+>彼<彼->は<言う+>言った<言う->。", "「５日前に彼女にあった」と彼は言った。", ["日", undef], ["前", undef], ["彼女", undef], ["彼", undef], ["言う", undef]],
        # Order of keys shouldn't affect nested highlighting
        ["「５<日+>日<日-><前+>前<前->に<彼+><彼女+>彼<彼->女<彼女->にあった」と<彼+>彼<彼->は<言う+>言った<言う->。", "「５日前に彼女にあった」と彼は言った。", ["日", undef], ["前", undef], ["彼", undef], ["彼女", undef], ["言う", undef]],

    );
    for(@test_cases) {
        my $expected = shift @$_;
        my $actual = highlight_keys(@$_);
        if($expected eq $actual) {
            print "Test OK\n";
        } else {
            print "Expected: $expected\n";
            print "Actual:   $actual\n";
        }
    }
}

# TEST MODE
#test_highlight_keys();
#exit;
# END TEST MODE

open TANAKA, ">", "data/tanaka.txt";

my %needed;
open DEMONS_KANJI, "<", "data/demons-kanji.txt";
while(<DEMONS_KANJI>)
{
        chomp;
        s!^\d+\s+!!;
        s!\s.*!!;
        s!\{～\}!!g;
        s!～!!g;
        s!\((.*?)\|.*?\)!$1!g;
        s!\[(.*?)\|.*?\]!$1!g;
        s!\*5!る!g;
        s!\*!!g;
        $needed{$_}++;
}
close DEMONS_KANJI;

our $TANAKA_RAW;
open $TANAKA_RAW, "<", "data/tanaka_raw.u8";

sub get_tanaka_raw_line {
    while(1) {
        my $tanaka_raw = <$TANAKA_RAW>;
        return unless defined $tanaka_raw;
        chomp $tanaka_raw;
        return $tanaka_raw unless $tanaka_raw =~ /^#/;
    }
}

# word -> offsets to sentences in TAKANA
my %key_to_ofs;

# FIXME: Multiple [[ protection
while(1) {
    my $a = get_tanaka_raw_line;
    last unless defined $a;
    my $b = get_tanaka_raw_line;
    last unless defined $b;

    die "Formatting error (A): $a" unless $a =~ m!^A: (.*)!;
    my $s = $1;

    die "Formatting error (B): $b" unless $b =~ m!^B: ?(.*)!;
    my (@keys);
    for(split /\s+/, $1) {
        # A few lame hand fixes
        s/\Q(かみあわせ/(かみあわせ)/;
        s/\Q留める(とどめる0/留める(とどめる)/;
        s/\Q着く(つく)(つく)/着く(つく)/;
        # These are edict indexes, ignore
        s/\[\d+\]//;
        # Get rid of reading
        my $reading = undef;
        $reading = $1 if s/\((\p{Hiragana}+)\)//;
        # Useless, but will be filtered out anyway
        next if m!^(\p{Hiragana}|\p{Katakana}|ー)*$!;
        if ($needed{$_}) {
            push @keys, [$_, $reading];
        } else {
            #print "I have key USELESS $_ for sentence #", ($#sentence+1), "\n";
        }
    }
    next unless @keys;
    # @keys should be uniq
    # Perl sucks by not having a generic (non-scalar) uniq
    my @keys_orig = @keys;
    @keys = ();
    my %keys_seen_nopron;
    my %keys_seen_pron;
    for(@keys_orig) {
        if (defined $_->[1]) {
            next if($keys_seen_pron{$_->[0]}{$_->[1]});
            $keys_seen_pron{$_->[0]}{$_->[1]} = 1;
        } else {
            next if($keys_seen_nopron{$_->[0]});
            $keys_seen_nopron{$_->[0]} = 1;
        }
        push @keys, $_;
    }

    my ($j, $e) = split /\t/, $s;

    my $highlighted = highlight_keys($j, @keys);

    my $sentence_ofs = tell TANAKA;
    #print TANAKA "$highlighted\t$e\n";
    # jrpg.py doesn't understand highlighting information yet
    print TANAKA "$j\t$e\n";
    $key_to_ofs{$_->[0]}{$sentence_ofs} = 1 for @keys;
}

open TANAKA_IDX, ">", "data/tanaka_idx.txt";
for my $key(keys %key_to_ofs) {
    my @ofs = sort {$a <=> $b} keys %{$key_to_ofs{$key}};
    print TANAKA_IDX "$key\t", join("\t", @ofs), "\n";
}
