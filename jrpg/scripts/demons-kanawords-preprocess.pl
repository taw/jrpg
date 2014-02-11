#!/usr/bin/perl -w

use utf8;

sub geminate {
  my $word = shift;
  {
    # It's almost-regular
    last if $word =~ s/^ch/tch/;
    $word =~ s/^(.)/$1$1/ or die "Don't know how to geminate $word";
  }
  return $word;
}

sub convert {
  my ($word, $conv_table) = @_;
  my $result = "";
  LOOP: while($word ne "") {
    if(substr($word, 0, 1) eq "ー") {
      $word = substr $word, 1;
      $result .= substr $result, -1;
      next;
    }
    if(substr($word, 0, 1) eq "っ" or substr($word, 0, 1) eq "ッ") {
      my $first_char = substr($word, 0, 1);
      $word = substr $word, 1;
      for(@$conv_table)
      {
        #print "Trying $_->[0]\n";
        #print "Prefix: ", substr($word, 0, length($_->[0])), "\n";
        if(substr($word, 0, length($_->[0])) eq $_->[0]) {
          $word = substr $word, length($_->[0]);
          #print "Match $result | $_->[1] | ", geminate($_->[1]), "\n";
          $result .= geminate($_->[1]);
          next LOOP;
        }
      }
      die "Don't know what to do with ($result|$first_char$word)"
    }
    for(@$conv_table)
    {
      #print "Trying $_->[0]\n";
      #print "Prefix: ", substr($word, 0, length($_->[0])), "\n";
      if(substr($word, 0, length($_->[0])) eq $_->[0]) {
        $word = substr $word, length($_->[0]);
        $result .= $_->[1];
        next LOOP;
      }
    }
    die "Don't know what to do with ($result|$word)"
  }
  return $result;
}

my @CONVERSION = split /\s+/,
"きゃ kya kya
きゅ kyu kyu
きょ kyo kyo
しゃ sya sha
しゅ syu shu
しょ syo sho
ちゃ tya cha
ちゅ tyu chu
ちょ tyo cho
にゃ nya nya
にゅ nyu nyu
にょ nyo nyo
みゃ mya mya
みゅ myu myu
みょ myo myo
りゃ rya rya
りゅ ryu ryu
りょ ryo ryo
ぎゃ gya gya
ぎゅ gyu gyu
ぎょ gyo gyo
じゃ zya ja
じゅ zyu ju
じょ zyo jo
ぢゃ dya ja
ぢゅ dyu ju
ぢょ dyo jo
びゃ bya bya
びゅ byu byu
びょ byo byo
ぴゃ pya pya
ぴゅ pyu pyu
ぴょ pyo pyo
てぃ ti ti
ふぃ fi fi
ふぉ fo fo
あ a a
う u u
い i i
え e e
お o o
か ka ka
き ki ki
く ku ku
け ke ke
こ ko ko
さ sa sa
し si shi
す su su
せ se se
そ so so
た ta ta
ち ti chi
つ tu tsu
て te te
と to to
な na na
に ni ni
ぬ nu nu
ね ne ne
の no no
は ha ha
ひ hi hi
ふ hu fu
へ he he
ほ ho ho
ま ma ma
み mi mi
む mu mu
め me me
も mo mo
や ya ya
ゆ yu yu
よ yo yo
ら ra ra
り ri ri
る ru ru
れ re re
ろ ro ro
わ wa wa
を wo wo
が ga ga
ぎ gi gi
ぐ gu gu
げ ge ge
ご go go
ざ za za
じ zi ji
ず zu zu
ぜ ze ze
ぞ zo zo
だ da da
ぢ di ji
づ du du
で de de
ど do do
ば ba ba
び bi bi
ぶ bu bu
べ be be
ぼ bo bo
ぱ pa pa
ぴ pi pi
ぷ pu pu
ぺ pe pe
ぽ po po
ん n n";
our @CONV_K;
our @CONV_H;
my $kana_shift = ord("ア") - ord("あ");
while(@CONVERSION) {
  my $hiragana = shift @CONVERSION;
  my $kunrei   = shift @CONVERSION;
  my $hepburn  = shift @CONVERSION;
  my $katakana = $hiragana;
  $katakana =~ s/(.)/chr(ord($1)+$kana_shift)/eg;
  push @CONV_K, [$hiragana,$kunrei];
  push @CONV_K, [$katakana,$kunrei];
  push @CONV_H, [$hiragana,$hepburn];
  push @CONV_H, [$katakana,$hepburn];
}

sub convert_line
{
  ($kanaword, $trad) = split('\t', $_[0]);
  my $kunrei_word  = convert($kanaword, \@CONV_K);
  my $hepburn_word = convert($kanaword, \@CONV_H);
if ($kunrei_word eq $hepburn_word) {
    "$kanaword\t$kunrei_word\t$trad";
  } else {
    "$kanaword\t$kunrei_word\t$hepburn_word\t$trad";
  }
}

if (@ARGV and $ARGV[0] eq "--test") {
  my @test_cases = split(/\n/,
"あたらしい atarasii atarashii
バター bataa
がくせい gakusei
しゅくだい syukudai shukudai
いもうと imouto
かいもの kaimono
しつもん situmon shitsumon
こうえん kouen
ようふく youhuku youfuku
テレビ terebi
きっさてん kissaten
ベッド beddo
まっすぐ massugu
マッチ matti matchi");
  for(@test_cases) {
    chomp;
    /(.*?) /;
    my $expected = $_;
    my $actual = convert_line($1);
    $actual =~ s/\t/ /g;
    if($actual eq $expected) {
      print "OK\n";
    } else {
      print "Failed: '$expected' expected, was: '$actual'\n";
    }
  }
} else {
  for(<>) {
    chomp;
    my $line_out = convert_line($_);
    print "$line_out\n";
  }
}
