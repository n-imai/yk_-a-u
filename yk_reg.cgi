#! /usr/local/bin/perl
#
# ��F�̶ڲ�޽���� by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

&set_date;
&get_params;

if($DAT{'nm'} eq ''){ &error("���O�����͂���Ă��܂���B"); }
if($DAT{'pw'} eq ''){ &error("�p�X���[�h�����͂���Ă��܂���B"); }
if($DAT{'nm'} =~ /([,;\x00-\x20])/){ &error("���O�ɕs���ȕ���($1)���܂܂�Ă��܂��B"); }
if($DAT{'nm'} =~ /(\x81\x40)/){ &error("���O�ɕs���ȕ���($1)���܂܂�Ă��܂��B"); }
if($DAT{'pw'} =~ /([,;\x00-\x20])/){ &error("�p�X���[�h�ɕs���ȕ���($1)���܂܂�Ă��܂��B"); }
if(length($DAT{'pw'})<6){ &error("�p�X���[�h���Z�����܂��B"); }
unless($DAT{'pw'} =~ /\d/){ &error("�p�X���[�h�ɂ͏��Ȃ��Ƃ�1�����ȏ�̐������K�v�ł�"); }
unless($DAT{'pw'} =~ /\D/){ &error("�p�X���[�h�ɂ͏��Ȃ��Ƃ�1�����ȏ�̐����ȊO�̕������K�v�ł�"); }

&file_lock;

if(!open(IN,$datfile)){ &error("�ް�̧�ق��J���܂���B"); }
@dat = <IN>;
close(IN);

$dat[0] = "$time\n";
for($i=1;$i<=$#dat;$i++){
    &get_header($dat[$i]);
    if($DAT{'nm'} eq $nm){ &error("���̖��O�͂��łɎg�p����Ă��܂��B"); }
    if($la < $time-15*24*60*60){ # +a # 15�����������ŷ�׍폜
	splice(@dat,$i,1);
	$i--;
    }
}
if($i>$max_entry){ &error("���ݒ�����ާ��ׁ̈A�V�K��t�ł��܂���B"); }

$cl = $DAT{'cl'};
if($cl<0){ $cl = 0; }
elsif($cl>3){ $cl = 3; }
$lv = 1;
&set_max_point;

push(@dat,"$time,$DAT{'nm'},$DAT{'pw'},$cl,$lv,$mhp,$mmp,100,0,0,0,���,0,0,̸,0,0,,$time,$ad0,<br>\n");

if(!open(OUT,">$datfile")){ &error("�ް�̧�قɏ������߂܂���B"); }
print OUT @dat;
close(OUT);

&unlock;

$log = "���O:$DAT{'nm'}<br>�߽ܰ��:$DAT{'pw'}<br>�œo�^���܂����B<br>\n";

print "Content-type: text/html; charset=shift_jis\n\n";

print <<"_HTML_";
<html><head><title>��F�̶ڲ�޽����</title></head>
$htmlcolor
<center>��F�̶ڲ�޽����</center>
<hr>
$log
<hr>
<a href="$topfile">BACK</a>
</body></html>
_HTML_
exit;
