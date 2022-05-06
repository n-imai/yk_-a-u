#! /usr/local/bin/perl
#
# 雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

&set_date;
&get_params;
&file_lock;

if(!open(IN,$datfile)){ &error("ﾃﾞｰﾀﾌｧｲﾙが開けません。"); }
@dat = <IN>;
close(IN);
if($dat[0] eq ''){ &error("ﾃﾞｰﾀﾌｧｲﾙの読み込みに失敗しました。"); }
for($i=1;$i<=$#dat;$i++){
    &get_header($dat[$i]);
    if($DAT{'nm'} eq $nm){
	if($DAT{'pw'} ne $pw){ &error("ﾊﾟｽﾜｰﾄﾞが間違っています。"); }
	$nm_ = $nm;
	$pw_ = $pw;
	$nm_e = &escape_code($nm);
	$pw_e = &escape_code($pw);
	$topfile = "yk_.cgi?nm=$nm_e&pw=$pw_e";
	last;
    }
}
if($i>$#dat){ &error("その名前では登録されていません。"); }

if($DAT{'tg'} eq ''){ $log = ''; }
elsif(length($DAT{'msg'}) > 100){ $log = "ﾒｯｾｰｼﾞが長すぎます。<br>\n"; }
else{
    for($i=1;$i<=$#dat;$i++){
	&get_header($dat[$i]);
	last if($DAT{'tg'} eq $nm);
    }
    if($i<=$#dat){
	&get_data($dat[$i]);
	$key = $nm_;
	$key =~ s/(\W)/\\$1/g;
	if($lg =~ /$key「.*」/){
	    $log = "前のﾒｯｾｰｼﾞがまだ読まれていません。<br>\n";
	}elsif($DAT{'msg'} ne ''){
	    $msg = $DAT{'msg'};
	    $msg =~ s/,/，/g;
	    $lg .= "$nm_「$msg」[$date]<br>";
	    &set_data($i);

	    $dat[0] = "$time\n";
	    if(!open(OUT,">$datfile")){ &error("ﾃﾞｰﾀﾌｧｲﾙに書き込めません。"); }
	    print OUT @dat;
	    close(OUT);

	    $log = "$nmにﾒｯｾｰｼﾞを送った。<br>\n";
	}else{
	    $log = "伝言を送れます。<br>\n";
	}
    }else{
	$log = "宛先不明です。<br>\n";
    }
}

&unlock;

&emoji_decode(*log);

print "Content-type: text/html; charset=shift_jis\n\n";
print <<"_HTML_";
<html><head><title>雪ｶﾚ</title></head>
$htmlcolor
$log
<hr>
[$date]<br>
<form action=yk_msg.cgi method=$method name=yk_msg>
<input type=hidden name=nm value=\"$nm_\">
<input type=hidden name=pw value=\"$pw_\">
名前<input type=text name=tg size=8><br>
ﾒｯｾｰｼﾞ<input type=text name=msg size=12 maxlength=64><br>
<input type=submit value="OK"><br></form>
<a href=\"$topfile">戻る</a>
</body></html>
_HTML_
exit;
