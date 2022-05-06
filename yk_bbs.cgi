#! /usr/local/bin/perl
#
# 雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

&set_date;
&get_params;
if(length($DAT{'nm'})>16){ &error("名前が長すぎます。"); }
if(length($DAT{'msg'})>100){ &error("入力が長すぎます。"); }
if($DAT{'ln'} eq ''){ $DAT{'ln'} = 5; }

if(!open(IN,$datfile)){ &error("ﾃﾞｰﾀﾌｧｲﾙが開けません。"); }
@dat = <IN>;
close(IN);
if($dat[0] eq ''){ &error("ﾃﾞｰﾀﾌｧｲﾙの読み込みに失敗しました。"); }
for($i=1;$i<=$#dat;$i++){
    &get_header($dat[$i]);
    if($DAT{'nm'} eq $nm){
	if($DAT{'pw'} eq ''){ &error("その名前は既に使われています。"); }
	if($DAT{'pw'} ne $pw){ &error("ﾊﾟｽﾜｰﾄﾞが間違っています。"); }
	$nm_e = &escape_code($nm);
	$pw_e = &escape_code($pw);
	$topfile = "yk_.cgi?nm=$nm_e&pw=$pw_e";
	last;
    }
}
if($i<=$#dat){
    &get_data($dat[$i]);
    $pwin = "<input type=hidden name=pw value=\"$pw\">";
}else{
    $pwin = '';
    if($DAT{'n'} ne ''){ &error("その名前では登録されていません。"); }
}

if($DAT{'n'} ne ''){
    $v = int($DAT{'n'});
    $bbsfile =~ s/\d\.log/$v\.log/i;
    $pwin .= "\n<input type=hidden name=n value=$v>";
}

if(!open(IN,$bbsfile)){ &error("BBSﾌｧｲﾙが開けません。"); }
@lines = <IN>;
close(IN);
if($lines[0] eq ''){ &error("BBSﾌｧｲﾙの読み込みに失敗しました。"); }

$buf = '';
if($DAT{'msg'} eq ''){
    if(($DAT{'n'} eq '') && rand(100)<$auto_rate){
	open(IN,$autofile);
	@tmp = <IN>;
	close(IN);
	($key,$v) = split(/,/,$tmp[rand($#tmp+1)]);
	$v =~ s/[\n\r]//g;
	$buf = "> $key<br> $v [$date (AUTO)]<br>\n";
	if($buf eq $lines[$#lines]){
	    $buf = '';
	}
    }
}else{
    if($DAT{'nm'} eq ''){ &error("名前を入れてください。"); }
    $buf = "> $DAT{'nm'} ";
    if($pwin eq ''){
	$buf .= "\(\?-Lv\?\)";
    }else{
	$buf .= "\($cl_sy[$cl]-Lv$lv\)";
    }
    $buf .= "<br> $DAT{'msg'}";
    $key = $lines[$#lines];
    $key =~ s/\s\[.*\]<br>\n//;
    if($buf eq $key){
	$buf = '';
    }else{
	if($mode ne ''){
	    $buf .= " [$date ($ua0)]<br>\n";
	}else{
	    $buf .= " [$date ($ad0)]<br>\n";
	}
    }
}

if($buf ne ''){
    @lines = @lines[($#lines-($maxln-1)) .. $#lines] if($#lines>=$maxln);
    push(@lines,$buf);
    open(OUT,">$bbsfile");
    print OUT @lines;
    close(OUT);
}

@lines = @lines[($#lines-($DAT{'ln'}-1)) .. $#lines] if($#lines>=$DAT{'ln'});

&emoji_decode(*lines);

if($mode eq 'i'){
    $msg_sz = "size=12";
}elsif($mode eq 'j'){
    $msg_sz = "size=12 maxlength=64";
}else{
    $msg_sz = "size=32";
}

print "Content-type: text/html; charset=shift_jis\n\n";
print <<"_HTML_";
<html><head><title>雪ｶﾚ</title></head>
$htmlcolor
@lines
<hr>
<form action=yk_bbs.cgi method=$method name=yk_bbs>
$pwin
名前<input type=text name=nm size=8 value="$DAT{'nm'}"><br>
ｺﾒﾝﾄ<input type=text name=msg $msg_sz><br>
行数<input type=text name=ln size=4 value=$DAT{'ln'}><br>
<input type=submit value="OK"></form>
<a href="$topfile">戻る</a>
</body></html>
_HTML_
exit;
