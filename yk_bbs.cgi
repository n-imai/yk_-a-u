#! /usr/local/bin/perl
#
# ��F�̶ڲ�޽���� by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

&set_date;
&get_params;
if(length($DAT{'nm'})>16){ &error("���O���������܂��B"); }
if(length($DAT{'msg'})>100){ &error("���͂��������܂��B"); }
if($DAT{'ln'} eq ''){ $DAT{'ln'} = 5; }

if(!open(IN,$datfile)){ &error("�ް�̧�ق��J���܂���B"); }
@dat = <IN>;
close(IN);
if($dat[0] eq ''){ &error("�ް�̧�ق̓ǂݍ��݂Ɏ��s���܂����B"); }
for($i=1;$i<=$#dat;$i++){
    &get_header($dat[$i]);
    if($DAT{'nm'} eq $nm){
	if($DAT{'pw'} eq ''){ &error("���̖��O�͊��Ɏg���Ă��܂��B"); }
	if($DAT{'pw'} ne $pw){ &error("�߽ܰ�ނ��Ԉ���Ă��܂��B"); }
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
    if($DAT{'n'} ne ''){ &error("���̖��O�ł͓o�^����Ă��܂���B"); }
}

if($DAT{'n'} ne ''){
    $v = int($DAT{'n'});
    $bbsfile =~ s/\d\.log/$v\.log/i;
    $pwin .= "\n<input type=hidden name=n value=$v>";
}

if(!open(IN,$bbsfile)){ &error("BBŞ�ق��J���܂���B"); }
@lines = <IN>;
close(IN);
if($lines[0] eq ''){ &error("BBŞ�ق̓ǂݍ��݂Ɏ��s���܂����B"); }

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
    if($DAT{'nm'} eq ''){ &error("���O�����Ă��������B"); }
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
<html><head><title>���</title></head>
$htmlcolor
@lines
<hr>
<form action=yk_bbs.cgi method=$method name=yk_bbs>
$pwin
���O<input type=text name=nm size=8 value="$DAT{'nm'}"><br>
����<input type=text name=msg $msg_sz><br>
�s��<input type=text name=ln size=4 value=$DAT{'ln'}><br>
<input type=submit value="OK"></form>
<a href="$topfile">�߂�</a>
</body></html>
_HTML_
exit;
