#!/usr/bin/perl -w -C

use utf8;

open A, "MAYBE_VERBS";
open B, "CHASEN_RESULTS";

our @MAYBE_VERBS=<A>;
our @CHASEN_RES=<B>;
our %FIX;

close A;
close B;

sub discard {
	shift @MAYBE_VERBS;	
}

sub ok {
	my ($base,$decl) = @_;
	my $end = $decl eq "5" ? "る" : $decl;
	my $mv = shift @MAYBE_VERBS;
#	print "$res <- $mv";
	# Blah, don't remove the ending if * is there
	$mv =~ /^(\d+)\s+(\d+)\s+$base(\*?)$end\t(.*?)((?:$end)?)$/ or die "Correction failure: $base*$decl !~ $mv";
	die "Big oops: $mv" if $3 and $5;
	$FIX{$1} = "$2\t$base*$decl\t$4\n";
}

for(@CHASEN_RES) {
#	print "CHECKING $_";
	chomp;
	s/\s+$//;
	s/\s+/ /g;
#	print "CHECKING $_\n";
	if (/^\S+ \S+ \S+ (?:名詞-一般|名詞-数|名詞-副詞可能|接頭詞-名詞接続|副詞-一般|連体詞)$/) {	
		discard();
	} elsif (/^(\S+)(む) \S+ム \1\2 動詞-自立 五段・マ行 基本形$/) {
		ok($1,$2);
	} elsif (/^(\S+)(う) \S+ウ \1\2 動詞-自立 五段・ワ行促音便 基本形$/) {
		ok($1,$2);
	} elsif (/^(\S+)(く) \S+ク \1\2 動詞-自立 五段・カ行イ音便 基本形$/) {
		ok($1,$2);
	} elsif (/^(\S+)(す) \S+ス \1\2 動詞-自立 五段・サ行 基本形$/) {
		ok($1,$2);
	} elsif (/^(\S+)(つ) \S+ツ \1\2 動詞-自立 五段・タ行 基本形$/) {
		ok($1,$2);
	} elsif (/^(\S+)(ぐ) \S+グ \1\2 動詞-自立 五段・ガ行 基本形$/) {
		ok($1,$2,);
	} elsif (/^(\S+)(ぶ) \S+ブ \1\2 動詞-自立 五段・バ行 基本形$/) {
		ok($1,$2);
	} elsif (/^(\S+)(る) \S+ル \1\2 動詞-自立 一段 基本形$/) {
		ok($1,$2); # 一段
	} elsif (/^(\S+)(る) \S+ル \1\2 動詞-自立 五段・ラ行 基本形$/) {
		ok($1,"5"); # 五段
	} else {
		#print "UNKNOWN: $_\n";
		discard();
	}
}

open DKS, "demons-kanji-source.txt";
while(<DKS>) {
	if(defined $FIX{$.}) {
		print $FIX{$.};	
	} else {
		print $_;
	}
}