#! /usr/local/bin/perl
#
# 雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ by b-Yak-38
#

require './yk_prf.cgi';
require './yk_ini.cgi';

$no_parse_header = 1;

&set_date;
&get_params;

$ra = $ENV{'REMOTE_ADDR'};
$sc = $ENV{'HTTP_BYA_YK_SERVER_CODE'};
if($sc ne ''){
    if($server_list{$sc} eq $ra){ &send_data; }
    else{ &error("Access denied."); }
}

&file_lock;
&open_data;
&check_conflict;

if($DAT{'URL'} eq ''){ &HTMLdie("Server URL required."); }
for($i=0;$i<=$#url_list;$i++){
    last if($url_list[$i] eq $DAT{'URL'});
}
if($i>$#url_list){ &HTMLdie("Server URL permission denied."); }

$URL = $DAT{'URL'} . 'nph-yk_srv.cgi';

#---------------------------------------------------------------------

use Socket qw(AF_INET SOCK_STREAM) ;
$AF_INET= AF_INET ; $SOCK_STREAM= SOCK_STREAM ;

sub proxy_encode {
    local($URL)= @_ ;
    $URL=~ s#^([\w+.-]+)://#$1/# ;		   # http://xxx -> http/xxx
#    $URL=~ s/(.)/ sprintf('%02x',ord($1)) /ge ;   # each char -> 2-hex
#    $URL=~ tr/a-zA-Z/n-za-mN-ZA-M/ ;		   # rot-13
    return $URL ;
}

sub proxy_decode {
    local($PATH_INFO)= @_ ;
#    $PATH_INFO=~ tr/a-zA-Z/n-za-mN-ZA-M/ ;	   # rot-13
#    $PATH_INFO=~ s/([0-9A-Fa-f]{2})/ sprintf("%c",hex($1)) /ge ;
    $PATH_INFO=~ s#^([\w+.-]+)/#$1://# ;	   # http/xxx -> http://xxx
    return $PATH_INFO ;
}

$SIG{'ALRM'} = 'timeexit' ;
alarm(600);

sub timeexit { exit 1 }

$ENV{'SCRIPT_NAME'}=~ s#^/?#/# ;

$env_accept= $ENV{'HTTP_ACCEPT'} || '*/*' ;	# may be modified later

binmode STDOUT ;

if($ENV{'QUERY_STRING'} ne ''){
    $URL=~ s/(\?.*)?$/?$ENV{'QUERY_STRING'}/;
}

($scheme, $authority, $path)=
    ($URL=~ m#^([\w+.-]+)://([^/?]*)(.*)$#i) ;
$scheme=~ tr/A-Z/a-z/ ;
$path= "/$path" if $path!~ m#^/# ;   # if path is '' or contains only query

$is_html= $path=~ /\.html?(\?|$)/i ;

&unsupported_warning($URL) unless ($scheme=~ /^(http)$/) ;

&HTMLdie('The target URL cannot contain an empty host name.')
    unless $authority=~ /^\w/ ;

$*= 1 ;     # allow multi-line matching

$this_url= join('', 'http://', $ENV{'SERVER_NAME'},
		   ($ENV{'SERVER_PORT'}==80  ? ''  : ':'.$ENV{'SERVER_PORT'} ),
		    $ENV{'SCRIPT_NAME'}, '/') ;

$base_url= $URL ;
&fix_base_vars ;   # must be called whenever $base_url is set

$stripped_data = '';

&http_get;

if($stripped_data ne ''){
    push(@dat,"$stripped_data\n");
    &close_data;
}
&unlock;

if ( $is_html  && ($body[0] ne '') ) {

    foreach (@body) {
	s/<bya completed>/<a href=$topfile>ﾄｯﾌﾟへ<\/a>/i;
    }	# foreach (@body)

    $headers=~ s/^Content-Length:.*\012/
		 'Content-Length: ' . length(join('',@body)) . "\015\012"/ie ;

}

if ($ENV{'REQUEST_METHOD'} eq 'HEAD') {
    print $status, $headers ;
} elsif ($is_html) {
    print $status, $headers, @body ;
} else {
    print $status, $headers, $body ;
}

exit ;

sub fix_base_vars {
    $base_url=~ s#^([\w+.-]+://[^/?]+)/?#$1/# ;

    ($base_scheme)= $base_url=~ m#^([\w+.-]+:)//# ;
    ($base_host)=   $base_url=~ m#^([\w+.-]+://[^/?]+)# ; # no ending slash
    ($base_path)=   $base_url=~ m#^([^?]*/)# ;		  # use greedy matching
}

sub http_get {
    local($portst, $realhost, $realport, $request_uri,
	  $cookie_to_server, $lefttoget, $postbody, $rin, $dummy) ;
    local($/)= "\012" ;

    ($host,$port)= $authority=~ /^([^:]*):?(.*)$/ ;
    $host=~ tr/A-Z/a-z/ ;
    $port= 80 if $port eq '' ;

    $portst= ($port==80)  ? ''	: ":$port" ;

    $realhost= $host ;
    $realport= $port ;
    $request_uri= $path ;

    if ($ENV{'http_proxy'}) {
	local($dont_proxy) ;
	foreach (split(/\s*,\s*/, $ENV{'no_proxy'})) {
	    $dont_proxy= 1, last if $host=~ /$_$/ ;
	}
	unless ($dont_proxy) {
	    ($dummy,$realhost,$realport)=
		$ENV{'http_proxy'}=~ m#^(http://)?([^/?:]*):?([^/?]*)#i ;
	    $realport= 80 if $realport eq '' ;
	    $request_uri= $URL ;
	}
    }

    &newsocketto(*S, $realhost, $realport) ;
    binmode S ;   # see note with "binmode STDOUT", above

    print S $ENV{'REQUEST_METHOD'}, ' ', $request_uri, " HTTP/1.0\015\012",
	    'Host: ', $host, $portst, "\015\012",    # being a good netizen
	    'Accept: ', $env_accept, "\015\012",	# possibly modified
	    'Bya-Yk-Server-Code: ', $my_accesscode, "\015\012";

    if ($ENV{'REQUEST_METHOD'} eq 'POST') {
	$lefttoget= $ENV{'CONTENT_LENGTH'} ;
	print S 'Content-type: ', $ENV{'CONTENT_TYPE'}, "\015\012",
		'Content-length: ', $lefttoget, "\015\012\015\012" ;
	do {
	    $lefttoget-= read(STDIN, $postbody, $lefttoget) ;
	    print S $postbody ;
	} while $lefttoget && length($postbody) ;

    } else {
	print S "\015\012" ;
    }

    vec($rin= '', fileno(S), 1)= 1 ;
    select($rin, undef, undef, 60)
	|| &HTMLdie("No response from $realhost:$realport") ;

    $status= <S> ;  # first line, which is the status line in HTTP 1.x

    if ($status=~ m#^HTTP/#) {
	do {
	    $headers.= $_= <S> ;    # $headers includes last blank line
	} until (/^(\015\012|\012)$/) ;   # lines may end with LF or CRLF

	$headers=~ s/(\015\012|\012)[ \t]/ /g ;

	if	  ($headers=~ m#^Content-Base:\s*([\w+.-]+://\S+)#i) {
	    $base_url= $1, &fix_base_vars ;
	} elsif   ($headers=~ m#^Content-Location:\s*([\w+.-]+://\S+)#i) {
	    $base_url= $1, &fix_base_vars ;
	} elsif   ($headers=~ m#^Location:\s*([\w+.-]+://\S+)#i) {
	    $base_url= $1, &fix_base_vars ;
	} elsif   ($headers=~ m#^Bya-Yk-Stripped-Data:\s*\"(.*)\"#i) {
	    $stripped_data = $1;
	    $headers =~ s/^Bya-Yk-Stripped-Data:(.*)$//gi;
	}

	&http_fix ;

	$is_html= $is_html || ($headers=~ m#^Content-type:\s*text/html\b#i) ;

	if ($ENV{'REQUEST_METHOD'} ne 'HEAD') {
	    if ($is_html) {
		$/= '>' ;
		@body= <S> ;
	    } else {
		undef $/ ;
		$body= <S> ;
	    }
	} else {
	    $body= ''; @body= () ;
	}

    } else {
	$is_html= 1 ;	# HTTP 0.9 by definition implies an HTML response
	undef $/ ;
	$body= $status . <S> ;
	$status= '' ;

	# split $body into @body; with each element ending in ">" or EOstring
	@body= $body=~ /([^>]*>?)/g ;
    }

    close(S) ;

}  # sub http_get()

sub http_fix {
    $headers=~ s/^Set-Cookie:.*\012//gi;
}

sub newsocketto {
    local(*S, $host, $port)= @_ ;
    local($hostaddr, $remotehost) ;

    $hostaddr= ($host=~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/)
		  ?  pack('c4', $1, $2, $3, $4)     # for IP address
		  :  ( (gethostbyname($host))[4]    # for alpha host name
		       || &HTMLdie("Couldn't find address for $host: $!") ) ;
    $remotehost= pack('S n a4 x8', $AF_INET, $port, $hostaddr) ;

    socket(S, $AF_INET, $SOCK_STREAM, (getprotobyname('tcp'))[2])
	|| &HTMLdie("Couldn't create socket: $!") ;
    connect(S, $remotehost)
	|| &HTMLdie("Couldn't connect to $host:$port: $!") ;
    select((select(S), $|=1)[0]) ;	# unbuffer the socket
}

sub HTMLescape {
    local($s)= @_ ;
    $s=~ s/&/&amp;/g ;	    # must be before all others
    $s=~ s/"/&quot;/g ;
    $s=~ s/</&lt;/g ;
    $s=~ s/>/&gt;/g ;
    return $s ;
}

sub HTMLunescape {
    local($s)= @_ ;
    $s=~ s/&quot;/"/g ;
    $s=~ s/&lt;/</g ;
    $s=~ s/&gt;/>/g ;
    $s=~ s/&amp;/&/g ;	    # must be after all others
    return $s ;
}

sub unsupported_warning {
    print <<EOF ;
HTTP/1.0 200 OK
Content-type: text/html; charset=shift_jis

<html>
<head><title>WARNING</title></head>
<body>Warning: $_[0]</body>
</html>
EOF
    &unlock;
    exit ;
}

sub nontextdie {
    print "HTTP/1.0 403 Forbidden\n\n";
    &unlock;
    exit ;
}

sub skip_image {
    if ($RETURN_EMPTY_GIF) {
	print <<EOF ;
HTTP/1.0 200 OK
Content-Type: image/gif
Content-Length: 43

GIF89a\x01\0\x01\0\x80\0\0\0\0\0\xff\xff\xff\x21\xf9\x04\x01\0\0\0\0\x2c\0\0\0\0\x01\0\x01\0\x40\x02\x02\x44\x01\0\x3b
EOF
    } else {
	print "HTTP/1.0 404 Not Found\n\n" ;
    }
    &unlock;
    exit ;
}

sub HTMLdie {
    local($msg)= @_ ;
    print <<EOF ;
HTTP/1.0 200 OK
Content-Type: text/html; charset=shift_jis

<html>
<head><title>ERROR</title></head>
<body>Error: $msg</body>
</html>
EOF
    &unlock;
    exit ;
}

#---------------------------------------------------

sub open_data {
    if(!open(IN,$datfile)){ &error("ﾃﾞｰﾀﾌｧｲﾙが開けません。"); }
    @dat = <IN>;
    close(IN);
    if($dat[0] eq ''){ &error("ﾃﾞｰﾀﾌｧｲﾙの読み込みに失敗しました。"); }
}

sub close_data {
    $dat[0] = "$time\n";
    if(!open(OUT,">$datfile")){ &error("ﾃﾞｰﾀﾌｧｲﾙに書き込めません。"); }
    print OUT @dat;
    close(OUT);
}

sub check_conflict {
    for($i=1;$i<=$#dat;$i++){
	&get_header($dat[$i]);
	if($DAT{'nm'} eq $nm){ &error("同じ名前の人がいるので移動できません。"); }
	if($la < $time-15*24*60*60){ # +a # 15日ｱｸｾｽ無しでｷｬﾗ削除
	    splice(@dat,$i,1);
	    $i--;
	}
    }
    if($i>$max_entry){ &error("現在、移動先が定員ｵｰｳﾞｧｰの為、移動できません。"); }
}

sub send_data {
    &file_lock;
    &open_data;
    for($i=1;$i<=$#dat;$i++){
	&get_header($dat[$i]);
	if($DAT{'nm'} eq $nm){
	    if($DAT{'pw'} ne $pw){ &error("ﾊﾟｽﾜｰﾄﾞが間違っています。"); }
	    $n0 = $i;
	    last;
	}
    }
    if($i>$#dat){ &error("その名前では登録されていません。"); }

    &get_data($dat[$n0]);
    if($st != 50){ &error("移動先が指定されていません。"); }
    $st = 51;
    $nx = $time + $twn_t[$op]*60*60;
    &set_data($n0);

    &backup_data($dat[$n0]);
    $tmp = &HTMLescape($dat[$n0]);
    $tmp =~ s/[\n\r]//g;
    splice(@dat,$n0,1);
    &close_data;

    print <<EOF ;
HTTP/1.0 200 OK
Content-Type: text/html; charset=shift_jis
Bya-Yk-Stripped-Data: "$tmp"

<html>
<head><title>雪ｶﾚ</title></head>
$htmlcolor
他の街へ移動します。<br>
<br>
<font color="#ff000">注：ﾄｯﾌﾟのｱﾄﾞﾚｽが変わります。記録するのを忘れないで下さい。</font><br>
<bya completed>
</body>
</html>
EOF
    &unlock;
    exit;
}

sub backup_data{
    local($bdat) = @_;

    if(!open(IN,$bakfile)){ &error("ﾊﾞｯｸｱｯﾌﾟﾌｧｲﾙが開けません。"); }
    @bak = <IN>;
    close(IN);

    for($i=0;$i<=$#bak;$i++){
	&get_header($bak[$i]);
	if($DAT{'nm'} eq $nm){
	    splice(@bak,$i,1);
	    $i--;
	}elsif($la < $time-10*24*60*60){ # +a # 10日後 ﾊﾞｯｸｱｯﾌﾟﾌｧｲﾙからｷｬﾗ削除
	 splice(@bak,$i,1);
	    $i--;
	}
    }
    push(@bak,$bdat);

    if(!open(OUT,">$bakfile")){ &error("ﾊﾞｯｸｱｯﾌﾟﾌｧｲﾙに書きこめません。"); }
    print OUT @bak;
    close(OUT);
}
