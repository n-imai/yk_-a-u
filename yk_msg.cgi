#! /usr/local/bin/perl
#
# ��F�̶ڲ�޽���� by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

&set_date;
&get_params;
&file_lock;

if(!open(IN,$datfile)){ &error("�ް�̧�ق��J���܂���B"); }
@dat = <IN>;
close(IN);
if($dat[0] eq ''){ &error("�ް�̧�ق̓ǂݍ��݂Ɏ��s���܂����B"); }
for($i=1;$i<=$#dat;$i++){
    &get_header($dat[$i]);
    if($DAT{'nm'} eq $nm){
	if($DAT{'pw'} ne $pw){ &error("�߽ܰ�ނ��Ԉ���Ă��܂��B"); }
	$nm_ = $nm;
	$pw_ = $pw;
	$nm_e = &escape_code($nm);
	$pw_e = &escape_code($pw);
	$topfile = "yk_.cgi?nm=$nm_e&pw=$pw_e";
	last;
    }
}
if($i>$#dat){ &error("���̖��O�ł͓o�^����Ă��܂���B"); }

if($DAT{'tg'} eq ''){ $log = ''; }
elsif(length($DAT{'msg'}) > 100){ $log = "ү���ނ��������܂��B<br>\n"; }
else{
    for($i=1;$i<=$#dat;$i++){
	&get_header($dat[$i]);
	last if($DAT{'tg'} eq $nm);
    }
    if($i<=$#dat){
	&get_data($dat[$i]);
	$key = $nm_;
	$key =~ s/(\W)/\\$1/g;
	if($lg =~ /$key�u.*�v/){
	    $log = "�O��ү���ނ��܂��ǂ܂�Ă��܂���B<br>\n";
	}elsif($DAT{'msg'} ne ''){
	    $msg = $DAT{'msg'};
	    $msg =~ s/,/�C/g;
	    $lg .= "$nm_�u$msg�v[$date]<br>";
	    &set_data($i);

	    $dat[0] = "$time\n";
	    if(!open(OUT,">$datfile")){ &error("�ް�̧�قɏ������߂܂���B"); }
	    print OUT @dat;
	    close(OUT);

	    $log = "$nm��ү���ނ𑗂����B<br>\n";
	}else{
	    $log = "�`���𑗂�܂��B<br>\n";
	}
    }else{
	$log = "����s���ł��B<br>\n";
    }
}

&unlock;

&emoji_decode(*log);

print "Content-type: text/html; charset=shift_jis\n\n";
print <<"_HTML_";
<html><head><title>���</title></head>
$htmlcolor
$log
<hr>
[$date]<br>
<form action=yk_msg.cgi method=$method name=yk_msg>
<input type=hidden name=nm value=\"$nm_\">
<input type=hidden name=pw value=\"$pw_\">
���O<input type=text name=tg size=8><br>
ү����<input type=text name=msg size=12 maxlength=64><br>
<input type=submit value="OK"><br></form>
<a href=\"$topfile">�߂�</a>
</body></html>
_HTML_
exit;
