#!/usr/bin/perl -w

system q[
cat demons-kanji-source.txt
|
perl -C -nle 'use utf8; next unless(/^\d+\t.*(\p{Hiragana})\t.*/); $h=$1; next if $h =~ /[γγγγγγγ«γγΏγγγ‘γ¦γγγ¨γγ©γ­γΉγΌγ½γΎγγγγγγγ³γγγͺγ°γ γγ―γ§γγ]/; print' >MAYBE_VERBS
];

system q[
cat MAYBE_VERBS
|
perl -ple 's/\d+\t//; s/\t.*//; s/\*//'
|
u2e
|
chasen
|
e2u
|
perl -w -nle 'if($_ eq "EOS"){print join(" =||= ", @a); @a=()}else {push @a,$_}' >CHASEN_RESULTS
];
