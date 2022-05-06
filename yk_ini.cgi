#! /usr/local/bin/perl
#
# ê·êFÇÃ∂⁄≤ƒﬁΩ∫∞Ãﬂ by b-Yak-38
#
$| = 1;

@cl_nm = ('Ãß≤¿∞','∏⁄ÿØ∏','ø∞ª◊∞','º∞Ã','€∞ƒﬁ','Ãﬂÿ∞Ωƒ','≥®ªﬁ∞ƒﬁ','±ªº›','Œ∞ÿ∞≈≤ƒ','ÀﬁºÆØÃﬂ','Ÿ∞›≈≤ƒ','∆›ºﬁ¨');
@cl_sy = ('F','C','S','T','L','P','W','A','H','B','R','N');
@cl_hpp = (3,2,1,2,4,2,1,3,3,2,3,2);
@cl_mpp = (1,2,3,1,1,3,4,1,2,3,2,2);

sub set_max_point{
    $mhp = 5+$cl_hpp[$cl]*$lv;
    $mmp = 5+$cl_mpp[$cl]*$lv;
    $hp = $mhp if($hp > $mhp);
    $mp = $mmp if($mp > $mmp);
}

sub get_data{
    local($dat) = @_;

    $dat =~ s/\n$//;
    ($la,$nm,$pw,$cl,$lv,$hp,$mp,$gp,$ex,$st,$pt,$wn,$wp,$wb,$an,$ap,$ab,$it,$nx,$ad,$lg) = split(/,/,$dat);
    if($st =~ s/\[(.*)\]//){ $op = $1; }
    else{ $op = ''; }
    &set_max_point;
}

sub get_header{
    local($dat) = @_;
    local($remainder);

    ($la,$nm,$pw,$remainder) = split(/,/,$dat,4);
}

sub set_data{
    local($n) = @_;

    if($op ne ''){ $st = "$st\[$op\]"; }
    $dat[$n] = "$time,$nm,$pw,$cl,$lv,$hp,$mp,$gp,$ex,$st,$pt,$wn,$wp,$wb,$an,$ap,$ab,$it,$nx,$ad,$lg\n";
}

sub set_date{
    $time = time;
    ($sec,$min,$hour,$mday,$month,$year,$wday,$yday,$isdst) = localtime($time);
    $min = "0$min" if($min<10);
    $sec = "0$sec" if($sec<10);
    $month++;
    $wday_str = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat') [$wday];
    $date = "$month/$mday $hour:$min:$sec";
    srand($time);
}

sub get_params{
    if($ENV{'REQUEST_METHOD'} eq "POST"){ read(STDIN,$param,$ENV{'CONTENT_LENGTH'}); }
    else{ $param = $ENV{'QUERY_STRING'}; }
    @pairs = split(/&/,$param);
    foreach $pairs (@pairs)
    {
	($key,$v) = split(/=/,$pairs);
	$v =~ tr/+/ /;
	$v =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
	$v =~ s/\t/ /g;
	$v =~ s/[\r\n]//g;
	$v =~ s/tel:\d*//ig;
	$v =~ s/</&lt;/g;
	$v =~ s/>/&gt;/g;
	if($key eq 'nm'){
	    $v =~ s/[\x00-\x20]//g;
	    $v =~ s/\x81\x40//g;
	}
	$DAT{$key} = $v;
    }
    $ad0 = $ENV{'REMOTE_ADDR'};
    $adn = gethostbyaddr(pack('C4',split(/\./,$ad0)),2);
    if($adn eq ''){ $adn = $ad0; }
    $ad0 = &encode_adr($ad0);

    $ua0 = $ENV{'HTTP_USER_AGENT'};
    $method = 'POST';
    $mode = '';
    if($ENV{'HTTP_X_JPHONE_MSNAME'} ne ''){
	$ua0 = $ENV{'HTTP_X_JPHONE_MSNAME'};
	$method = 'GET';
	$mode = 'j';
    }elsif($ua0 =~ /^DoCoMo/){
	($ua1,$ua2,$ua3,$ua4) = split(/\//,$ua0);
	$ua0 = $ua3;
	$mode = 'i';
    }
    $ua0 =~ s/</&lt;/g;
    $ua0 =~ s/>/&gt;/g;
    $ua0 =~ s/\&/&amp;/g;
}

sub escape_code{
    local($str) = @_;

    $str =~ s/(\W)/sprintf("%%%02lx",unpack('C',$1))/ge;
    $str;
}

sub unlock{
    rmdir($lckfile);
}

sub file_lock{
    local($mtime,$retry);

    if(-e $lckfile){
	$mtime = (stat($lckfile))[9];
	if($mtime > 0 && $mtime < time - 60){
	    &unlock;
	}
    }
    $retry = 3;
    while(!mkdir($lckfile,0755)){
	if(--$retry <= 0){
	    print "HTTP/1.0 200 OK\n" if($no_parse_header == 1);
	    print "Content-type: text/html; charset=shift_jis\n\n";
	    print "<html><head><title>CGI Error</title></head>\n";
	    print "<body><h1>CGI Error</h1>\n";
	    print "<p>Ãß≤ŸÇ™€Ø∏Ç≥ÇÍÇƒÇ¢Ç‹Ç∑ÅB<br>ÇµÇŒÇÁÇ≠Ç®ë“Çøâ∫Ç≥Ç¢ÅB\n";
	    print "</body></html>";
	    exit;
	}
	sleep(1);
    }
    $locked = 1;
}

sub emoji_decode{
    local(*lines) = @_;

    unless($ENV{'HTTP_USER_AGENT'} =~ /^DoCoMo/){
# é©ìÆäGï∂éöïœä∑ (f840-f84f,f89e-f8e4,f8f3-f8ff,f940-f9b0)
	for($i=0;$i<=$#lines;$i++){
	    $key = $lines[$i];
	    $lines[$i] ='';
	    while($key ne ''){
		if($key =~ /([\x00-\x80\xa0-\xdf\xf0-\xf7\xfa-\xff]*)([\x40-\xff].)(.*)/){
		    $v = $1.$2;
		    $key = $3;
		}else{
		    $v = $key;
		    $key = '';
		}
		while(($v =~ /\&\#(\d*);?/) && ($1 >= 63552) && ($1 <= 63999)){
		    $v =~ s/\&\#(\d*);?/<img src=$ipath\/$1.png>/;
		}
		$v =~ s/([\xf8-\xf9])([\x40-\xff])/'<img src='.$ipath.'\/'.unpack("S",$2.$1).'.png>'/eg;
		$lines[$i] .= $v;
	    }
	    $lines[$i] .= "\n";
	}
    }
}

sub error{
    print "HTTP/1.0 200 OK\n" if($no_parse_header == 1);
    print "Content-type: text/html; charset=shift_jis\n\n";
    print "<html><head><title>CGI Error</title></head>\n";
    print "<body><h1>CGI Error</h1>\n";
    print "<p>This program encountered an internal error.</p>";
    print "<p><b>Error:</b> $_[0]</p>\n";
    print "</body></html>";

    &unlock if($locked == 1);
    exit;
}
