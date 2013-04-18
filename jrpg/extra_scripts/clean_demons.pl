#!/usr/bin/perl -w -C

for(<>) {
    unless (m!^(\d+)\t(\S+)\t(\S+)$!) {
	print;
	next;
    }
    my ($n,$kj,$kn)=($1,$2,$3);
    my $cp="";
    my $cs="";
    while($kn ne "" and $kj ne "") {
	if (substr($kj,0,1) eq substr($kn,0,1)) {
	    $cp .= substr($kn,0,1);
	    $kj  = substr $kj,1;
	    $kn  = substr $kn,1;
	} elsif (substr($kj,0,1) eq "~") {
	    $cp .= "{~}";
	    $kj  = substr $kj,1;
	} else {
	    last;
	}
    }
    while($kn ne "" and $kj ne "") {
	if(substr($kj,-1) eq substr($kn,-1)) {
	    $cs = substr($kn,-1).$cs;
	    $kj = substr$kj,0,-1;
	    $kn = substr$kn,0,-1;
	} elsif (substr($kj,-1) eq "~") {
	    $cs = "{~}".$cs;
	    $kj = substr$kj,0,-1;
	} else {
	    last;
	}
    }
    print "$n\t$cp","[$kj|$kn]$cs\n";
}
