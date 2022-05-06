#! /usr/local/bin/perl
#
# 雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

&set_date;
&get_params;

if($DAT{'nm'} eq ''){ &error("名前が入力されていません。"); }
if($DAT{'pw'} eq ''){ &error("パスワードが入力されていません。"); }
if($DAT{'nm'} =~ /([,;\x00-\x20])/){ &error("名前に不正な文字($1)が含まれています。"); }
if($DAT{'nm'} =~ /(\x81\x40)/){ &error("名前に不正な文字($1)が含まれています。"); }
if($DAT{'pw'} =~ /([,;\x00-\x20])/){ &error("パスワードに不正な文字($1)が含まれています。"); }
if(length($DAT{'pw'})<6){ &error("パスワードが短すぎます。"); }
unless($DAT{'pw'} =~ /\d/){ &error("パスワードには少なくとも1文字以上の数字が必要です"); }
unless($DAT{'pw'} =~ /\D/){ &error("パスワードには少なくとも1文字以上の数字以外の文字が必要です"); }

&file_lock;

if(!open(IN,$datfile)){ &error("ﾃﾞｰﾀﾌｧｲﾙが開けません。"); }
@dat = <IN>;
close(IN);

$dat[0] = "$time\n";
for($i=1;$i<=$#dat;$i++){
    &get_header($dat[$i]);
    if($DAT{'nm'} eq $nm){ &error("その名前はすでに使用されています。"); }
    if($la < $time-15*24*60*60){ # +a # 15日ｱｸｾｽ無しでｷｬﾗ削除
	splice(@dat,$i,1);
	$i--;
    }
}
if($i>$max_entry){ &error("現在定員ｵｰｳﾞｧｰの為、新規受付できません。"); }

$cl = $DAT{'cl'};
if($cl<0){ $cl = 0; }
elsif($cl>3){ $cl = 3; }
$lv = 1;
&set_max_point;

push(@dat,"$time,$DAT{'nm'},$DAT{'pw'},$cl,$lv,$mhp,$mmp,100,0,0,0,ｽﾃﾞ,0,0,ﾌｸ,0,0,,$time,$ad0,<br>\n");

if(!open(OUT,">$datfile")){ &error("ﾃﾞｰﾀﾌｧｲﾙに書き込めません。"); }
print OUT @dat;
close(OUT);

&unlock;

$log = "名前:$DAT{'nm'}<br>ﾊﾟｽﾜｰﾄﾞ:$DAT{'pw'}<br>で登録しました。<br>\n";

print "Content-type: text/html; charset=shift_jis\n\n";

print <<"_HTML_";
<html><head><title>雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ</title></head>
$htmlcolor
<center>雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ</center>
<hr>
$log
<hr>
<a href="$topfile">BACK</a>
</body></html>
_HTML_
exit;
