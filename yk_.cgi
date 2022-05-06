#! /usr/local/bin/perl
#
# 雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

@cmd_lst = ('このまま','休息','冒険','依頼','道具屋','移動');
@shp_lst = ('出る','武器','防具','ｱｲﾃﾑ','売る');

#&error("ただいまメンテナンス中です。しばらくお待ち下さい。");

# --- STATUS ---
# 0 : ready
# 1 : select rest -> 0|10-12
# 2 : select quest -> 0|24
# 3 : select work -> 0|31
# 4 : select shop-command -> 0|40-43
# 5 : select town -> 0|50

# 10-19 : resting -> 0

# 20 : quest -+-> 0|21-22
# 21 : y/n (equip) -> 0|23
# 22 : select item (drop) -> 0|23
# 23 : select class -> 0
# 25 : y/n (quest) -> 2|20

# 30 : work -+-> 0|21-22
# 35 : y/n (work) -> 3|30

# 40 : select weapon (buy) -> 4|44
# 41 : select armor (buy) -> 4|44
# 42 : select item (buy) -> 4|44
# 43 : select item (sell) -> 4|45
# 44 : y/n (buy) -> 4
# 45 : y/n (sell) -> 4

# 50 : server change/cancel -> 51
# 51 : moving -+-> 0

$log = '';

&set_date;
&get_params;
&file_lock;
&read_data;
if($time > $nx){
    if(&proceed == 0){ &cmd_analyze; }
    else{
	$log .= "<hr>\n";
	$update = 1;
    }
    &print_status;
}else{
    if($st == 20){
	$log .= "冒険中です。<br>";
	$f = 1;
    }elsif($st == 30){
	$log .= "仕事中です。<br>";
	$f = 1;
    }elsif($st == 51){
	$log .= "移動中です。<br>";
	$f = 1;
    }else{
	$f = 0;
    }
    if($f == 1){
	$i = $nx-$time;
	if($i<60){
	    $v = "$i\秒";
	}elsif($i<60*60){
	    $i = int($i/60);
	    $v = "$i\分";
	}else{
	    $j = int(($i%(60*60))/60);
	    $i = int($i/(60*60));
	    $v = "$i\時間$j\分";
	}
	$log .= "あと$v\。<hr>\n";
	$nm_e = &escape_code($nm);
	$pw_e = &escape_code($pw);
	$log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e\">酒場</a><br>\n";
	$log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e&n=1\">掲示板</a><br>\n";
	$log .= "<a href=\"yk_msg.cgi?nm=$nm_e&pw=$pw_e\">伝言</a><br>\n";
	$log .= "<a href=\"$topfile\">戻る</a>\n";
    }else{
	&cmd_analyze;
	&print_status;
    }
}
if($update == 1){ &write_data; }
&unlock;

@log = split(/\n/,$log);
&emoji_decode(*log);

print "Content-type: text/html; charset=shift_jis\n\n";
print <<"_HTML_";
<html><head><title>雪ｶﾚ</title></head>
$htmlcolor
@log
</body></html>
_HTML_
exit;

sub read_data{
    if(!open(IN,$datfile)){ &error("ﾃﾞｰﾀﾌｧｲﾙが開けません。"); }
    @dat = <IN>;
    close(IN);
    if($dat[0] eq ''){ &error("ﾃﾞｰﾀﾌｧｲﾙの読み込みに失敗しました。"); }

    if(!open(IN,$gdatfile)){ &error("ｸﾞﾛｰﾊﾞﾙﾃﾞｰﾀﾌｧｲﾙが開けません。"); }
    @gdat = <IN>;
    close(IN);
    if($gdat[0] eq ''){ &error("ｸﾞﾛｰﾊﾞﾙﾃﾞｰﾀﾌｧｲﾙの読み込みに失敗しました。"); }

    for($i=1;$i<=$#dat;$i++){
	&get_header($dat[$i]);
	if($DAT{'nm'} eq $nm){
	    if($DAT{'pw'} ne $pw){ &error("ﾊﾟｽﾜｰﾄﾞが間違っています。"); }
	    last;
	}
    }
    if($i>$#dat){ &error("その名前では登録されていません。"); }
    $n0 = $i;

    $t = int($time/(6*60*60));
    $i = int($gdat[0]/(6*60*60));
    if($t > $i){
	$v = $t-$i;
	$items = $gdat[1];
	$items =~ s/[\n\r]//g;
	@item_lst = split(/,/,$items);
	for($i=0;$i<=$#item_lst;$i++){
	    ($item_nm,$item_n) = split(/\//,$item_lst[$i]);
	    $item_n -= $v;
	    if($item_n>0){
		$item_lst[$i] = "$item_nm/$item_n";
	    }else{
		splice(@item_lst,$i,1);
		$i--;
	    }
	}
	$gdat[1] = join(',',@item_lst);
	$gdat[1] .= "\n";
	$t *= (6*60*60);
	$gdat[0] = "$t\n";
	$update = 1;
    }else{ $update = 0; }

    &get_data($dat[$n0]);
    if($lg ne ''){
	$log .= "$lg<hr>\n";
	$lg = '';
	$update = 1;
    }
for(0..$#gm_name){				  # +a
    if($nm eq $gm_name[$_]){ $nx = $time-60*60; } # ﾃﾞﾊﾞｸﾞｷｬﾗ複数設定
		 }				  #
}

sub write_data{
    $dat[0] = "$time\n";
    $ad = $adn;
    $ad =~ s/,//g;
    &set_data($n0);
    if(!open(OUT,">$datfile")){ &error("ﾃﾞｰﾀﾌｧｲﾙに書き込めません。"); }
    print OUT @dat;
    close(OUT);

    if(!open(OUT,">$gdatfile")){ &error("ｸﾞﾛｰﾊﾞﾙﾃﾞｰﾀﾌｧｲﾙに書き込めません。"); }
    print OUT @gdat;
    close(OUT);
}

sub proceed{
    if($st >= 10 && $st <= 19){
	$key = $st-10;
	$v = int(($time-$nx)/(60*60))+1;
	for($i=0;$i<$v;$i++){
	    if($gp<$rst_gp[$key]){
		$log .= "代金が払えない!<br>追い出された!<br>\n";
		$st = 0;
		last;
	    }
	    $gp -= $rst_gp[$key];
	    $hp += $cl_hpp[$cl]*$key+int(rand(2));
	    $hp = $mhp if($hp>$mhp);
	    $mp += $cl_mpp[$cl]*$key+int(rand(2));
	    $mp = $mmp if($mp>$mmp);
	    if($hp==$mhp && $mp==$mmp){
		$log .= "完全に回復した!<br>\n";
		$st = 0;
		last;
	    }
	}
	$nx = $time - int(($time-$nx)%(60*60)) + 60*60 if($st != 0);
	return 1;
    }elsif($st == 20 || $st == 30){
	srand($nx);
	($pt_n,$pt_cl,$pt_hp,$pt_mp,$pt_atp,$pt_mgp,$pt_dfp,$pt_it,$pt_mem) = split(/\//,$pt,9);
	&read_adv;
	$pt = '';
	return 1;
    }elsif($st == 51){
	$log .= "目的地に到着した。<br>\n";
	$st = 0;
	$op = '';
	return 1;
    }
    return 0;
}

sub read_adv{
    if(!open(IN,$advfile)){ &error("ｱﾄﾞｳﾞｪﾝﾁｬｰﾌｧｲﾙが開けません。"); }
    @script = <IN>;
    close(IN);

    $msg_lose = "しかし、途中で力尽きてしまった…<br>\n";
    $msg_timeup = "しかし、時間をかけすぎてしまったので一旦戻ることにした…<br>\n";
    $ex_ = 0;

    for($l=0;$l<=$#script;$l++){
	$line = $script[$l];
	next if( $line =~ /^\#/ );
	if( $line =~ /^\s*map\s*\((.*)\)\s*{/ ){
	    if($op eq $1){
		$st = 0;
		$op = '';
		&adv_result;
		last;
	    }else{ &skip_nest; }
	}
    }
    if($l>$#script){
	$log .= "目的地が見つからなかった…<br>\n";
	$st = 0;
	$op = '';
    }
    if($lv == 10 && $cl < 4 && $st == 0){
	$log .= "- ｸﾗｽﾁｪﾝｼﾞ! -<br>\n";
	$st = 23;
    }
}

sub adv_result{
    $l++;
    $l_ = $l;
    for(;$l<=$#script;$l++){
	$line = $script[$l];
	if( $l > $l_ && $line =~ /^\s*}/ ){ last; }
	elsif( $line =~ /\s*if\s*\((.*)\)\s*{/ ){
	    ($key,$v) = split(/,/,$1,2);
	    $f = 0;
	    if($key eq 'r'){
		if($pt_cl =~ /[N]/){ $v *= 3; }
		elsif($pt_cl =~ /[TA]/){ $v *= 2; }
		if(rand(100) < $v){ $f = 1; }
	    }elsif($key eq 'R'){	      # +a
		if(rand(100) < $v){ $f = 1; } # 確率分岐2 職業関係なし
	    }elsif($key eq 'i'){
		($key,$v) = split(/,/,$v);
		$key =~ s/([\x81-\x9f\xe0-\xff])([\x40\x5b-\x5e\x7b-\xff])/\\$1\\$2/g;
		$v = 1 if($v eq '');
		@item_lst = split(/\|/,$pt_it);
		for($i=0;$i<=$#item_lst;$i++){
		    if($item_lst[$i] =~ /$key/){ $v--; }
		}
		if($v<=0){ $f = 1; }
	    }elsif($key eq 'c'){
		if($pt_cl =~ /[$v]/i){ $f = 1; }
	    }elsif($key eq 'e'){		     # +a
		($key,$v) = split(/,/,$v);	     # event分岐
		if($ev_flg[$ev_v] eq $v){ $f = 1; }  #
	    }elsif($key eq 'n'){
		if($pt_n >= $v){ $f = 1; }
	    }

	    if($f == 1){
		if( &adv_result == 1 ){ return 1; }
		for(;$line =~ /else\s+if\s*\(.*\)\s*{/;){ &skip_nest; }
		if( $line =~ /else\s*{/ ){ &skip_nest; }
	    }else{
		&skip_nest;
		if( $line =~ /else\s+if\s*\(.*\)\s*{/ ){
		    $l_ = $l;
		    $l--;
		    next;
		}
		if( $line =~ /else\s*{/ ){
		    if( &adv_result == 1 ){ return 1; }
		}
	    }
	}elsif( $line =~ /^\s*start\s*\((.*)\)\s*{/ ){
	    $adv_lt = $1;
	    $log .= &add_message;
	}elsif( $line =~ /^\s*message\s*{/ ){
	    $log .= &add_message;
	}elsif( $line =~ /^\s*msg-lose\s*{/ ){
	    $msg_lose = &add_message;
	}elsif( $line =~ /^\s*msg-timeup\s*{/ ){
	    $msg_timeup = &add_message;
	}elsif( $line =~ /^\s*report\s*\((.*)\)\s*{/ ){ 	   # +a
	    ($Subject,$rep_log,$rep_file) = split(/,/,$1);	   # BBSにﾚﾎﾟｰﾄをｱﾅｳﾝｽする
	    if($Subject == 1){$rep_log = $nm.$rep_log;} 	   # $Subject:
	    $rep_log = "> Report:<br>$rep_log [$date (SYS)]<br>\n";#  playerの名前をﾚﾎﾟｰﾄの先頭に入れる(1)
	    if(!open(IN,$rep_file)){				   #  入れない(0)
	    $log.="ﾃﾞｰﾀﾌｧｲﾙが開けなかった。<br>\n";		   # $rep_log:BBSに流すﾚﾎﾟｰﾄ
				   }				   # $rep_file:ﾚﾎﾟｰﾄを流すBBSﾌｧｲﾙの指定
	    @daty = <IN>;					   #
	    if($daty[0] eq ''){ 				   #
	    $log.="ﾃﾞｰﾀﾌｧｲﾙの読み込みに失敗した。<br>\n";	   #
			      } 				   #
	    close(IN);						   #
	    push(@daty,$rep_log);				   #
	    if(!open(OUT,">$rep_file")){			   #
	    $log.="ﾃﾞｰﾀﾌｧｲﾙが開けなかった。<br>\n";		   #
				       }			   #
	    print OUT @daty;					   #
	    close(OUT); 					   #
	}elsif( $line =~ /^\s*battle\s*\((.*)\)\s*{/ ){
	    ($adv_hp,$adv_wp,$adv_mp,$adv_ap,$adv_rp,$adv_un,$adv_ex,$adv_lg) = split(/,/,$1); # +a 変数$adv_log追加。
	    $log .= &add_message;							       # 1:戦闘ログ表示 0:非表示
	    if( &battle == 0 ){ return 1; }
	}elsif( $line =~ /^\s*clear\s*\((.*)\)\s*{/ ){
	    ($adv_gp,$adv_ex,$adv_it) = split(/,/,$1,3);
	    $log .= &add_message;
	    if($pt_cl =~ /[TAN]/){
		$v = $adv_gp;
	    }else{
		$v = int($adv_gp/2);
		$v = int(rand($v+1))+$v;
	    }
	    $v = int($v/$pt_n);
	    if($v>0){
		$log .= "$v"."Gp手に入れた。<br>\n";
		$gp += $v;
	    }
	    $ex_ += $adv_ex;
	    &exp_up($ex_);
	    if($adv_it ne ''){
		($key,$v) = split(/,/,$adv_it,2);
		if($key eq 'i'){
		    @item_lst = split(/\//,$it);
		    if($#item_lst<2){
			$log .= "$v\を手に入れた!<br>\n";
			$it .= '/' if($it ne '');
			$it .= $v;
		    }else{
			$log .= "$v\を見つけたが、持ち物がいっぱいだった…<br>\n";
			$log .= "- どれか捨てますか? -<br>\n";
			$st = 22;
			$op = "$key/$v";
		    }
		}elsif(($key eq 'w') || ($key eq 'a')){
		    ($v,$j,$k) = split(/,/,$v);
		    if($key eq 'w'){ $log .= "武器:$v\[$j".'x'."$k\]を見つけた!<br>\n"; } # +a
		    else{ $log .= "防具:$v\[$j".'x'."$k\]を見つけた!<br>\n"; }		  # 武器防具性能表示
		    $log .= "- 装備しますか? -<br>\n";
		    $st = 21;
		    $op = "$key/$v/$j/$k";
		}
	    }
	    return 1;
		}elsif( $line =~ /^\s*event\s*\((.*)\)\s*{/ ){		# +a
		  ($ev,$ev_e,$ev_log1,$ev_log0,$ev_v) = split(/,/,$1);	# $ev : ｲﾍﾞﾝﾄの種類
		   $log .= &add_message;				# $ev_e : ｲﾍﾞﾝﾄの効果
	    if($ev eq 'gp'){						# $ev_v : ｲﾍﾞﾝﾄﾌﾗｸﾞの添字
		       if($gp+$ev_e<=0){				# (@ev_flg : ｲﾍﾞﾝﾄﾌﾗｸﾞ)
					$log .="$ev_log0";		# 指定しなければﾌﾗｸﾞは$ev_flg[0]
					$ev_flg[$ev_v]=-1;		# $ev_log0 : ｲﾍﾞﾝﾄ失敗ﾛｸﾞ
		       }else{						# $ev_log1 : ｲﾍﾞﾝﾄ成功ﾛｸﾞ
					$log .="$ev_log1";		# = gp獲得(喪失)ｲﾍﾞﾝﾄ =
					$ev_flg[$ev_v]=1;		# $ev_e(負の値可)の値を$gpに加える。
					$gp += $ev_e;			# $ev_e+$gpが0以下なら失敗
		       }						# ﾌﾗｸﾞを-1にする
			   }						# 0以上なら成功$ev_eを加え、ﾌﾗｸﾞを1にする
									# 同様に色んな変数に対してｲﾍﾞﾝﾄを作成可能
									#
		}elsif( $line =~ /^\s*trap\s*\((.*)\)\s*{/ ){		# +a
		    ($trap,$t_rate,$t_pow,$protec_item) = split(/,/,$1);# $trap : ﾄﾗｯﾌﾟの種類
		     if($t_rate >= 1){$t_rate = 1;}			# $t_rate : ﾄﾗｯﾌﾟの発生率(0.00 ～ 1.00)
		     if($t_rate <= 0){$t_rate = 0;}			# $t_pow : ﾄﾗｯﾌﾟの威力、
 #		     if($t_pow >= 1){$t_pow = 1;}			# hpが×$trap減少する (0.00 ～ 1.00)
 #		     if($t_pow <= 0){$t_pow = 0;}			# $protec_item : ﾄﾗｯﾌﾟ回避ｱｲﾃﾑ指定
	    $log .= &add_message;					#
    if($trap eq 'A'){							#
     &chk_protec_item($protec_item);					#
     if($flg == 1){							# ﾄﾗｯﾌﾟ設定。
      &use_item($v);							# 「奇襲」
      $log.="しかし$vの力で避けることが出来た!<br>";			# 強制ﾀﾞﾒｰｼﾞ付与の罠
      $log.="$vは壊れてしまった･･<hr>"; 				# $t_rate : 罠を受ける確率。
     }elsif($pt_cl =~/[TAN]/ && (rand(1)>$t_rate/2)){			# 盗賊系が居ると半減。
      $log.="しかし盗賊のとっさの判断で、避けることが出来た<hr>";	# $dmg0_ 先制攻撃ﾀﾞﾒｰｼﾞ
     }elsif(rand(1)>$t_rate){						#
      $log.="しかし幸運にも避けることが出来た<hr>";			#
     }else{								#
      $v=int($pt_hp*$t_pow);						#
      $pt_hp-=$v;							#
      $hp-=$v;								#
      $log.="$vのﾀﾞﾒｰｼﾞを受けてしまった!<hr>";				#
	  }								#
    }elsif($trap eq 'W'){						#
     &chk_protec_item($protec_item);					#
     if($flg >= 1){							# ﾄﾗｯﾌﾟ設定。
      &use_item($v);							# 「弱化」
      $log.="しかし$vの力で避けることが出来た!<br>";			# 物理攻撃力が0になってしまう罠
      $log.="$vは壊れてしまった･･<hr>"; 				# $t_rate : 罠を受ける確率。
     }elsif(rand(1)>$t_rate){						# $t_pow : 罠の継続する確率。
      $log.="しかし幸運にも避けることが出来た<hr>";			#
     }else{								#
      $t_weak=1;							#
      $t_pow_1 = $t_pow;						#
      $log.="物攻を失ってしまった!<hr>";				#
	  }								#
    }elsif($trap eq 'S'){						#
     &chk_protec_item($protec_item);					#
     if($flg >= 1){							# ﾄﾗｯﾌﾟ設定。
      &use_item($v);							# 「沈黙」
      $log.="しかし$vの力で避けることが出来た!<br>";			# 魔法攻撃が0になってしまう罠
      $log.="$vは壊れてしまった･･<hr>"; 				# $t_rate : 罠を受ける確率。
     }elsif(rand(1)>$t_rate){						# $t_pow : 罠の継続する確率。
      $log.="しかし幸運にも避けることが出来た<hr>";			#
     }else{								#
      $t_silent=1;							#
      $t_pow_2 = $t_pow;						#
      $log.="魔攻を失ってしまった!<hr>";				#
	  }								#
			      } 					#
	}elsif( $line =~ /^\s*use-item\s*\((.*)\)/ ){
	    $key = $1;
	    $key =~ s/([\x81-\x9f\xe0-\xff])([\x40\x5b-\x5e\x7b-\xff])/\\$1\\$2/g;
	    @item_lst = split(/\//,$it);
	    for($i=0;$i<=$#item_lst;$i++){
		if($item_lst[$i] =~ /$key/){
		    splice(@item_lst,$i,1);
		    $it = join('/',@item_lst);
		    last;
		}
	    }
	}elsif( $line =~ /^\s*}/ ){ last; }
    }
    return 0;
}

sub add_message{
    local($msg);
    $msg = '';
    for($l++;$l<=$#script;$l++){
	$line = $script[$l];
	last if($line =~ /^\s*}/);
	$line =~ s/^\s*//;
	$line =~ s/[\n\r]//g;
	if($line =~ /(<img\s+src\s+=\s+\".*\.)(gif)(\">)/i){
	    next if(($mode eq 'i') && ($ua0 !~ /it/));
	    $line = $1.'png'.$3 if($mode eq 'j');
	}
	$msg .= "$line<br>";
    }
    $msg .= "<hr>\n";
    $msg;
}
sub chk_protec_item{
    local($key) = @_;
    $flg = 0;
	    @item_lst = split(/\|/,$pt_it);
	    for($i=0;$i<=$#item_lst;$i++){
	    if($item_lst[$i] eq $key){
	    $flg = 1;
	    $v=$key;
	    last;
				     }
					 }
}
sub use_item{
    local($key) = @_;
	    @item_lst = split(/\//,$it);
	    for($i=0;$i<=$#item_lst;$i++){
		if($item_lst[$i] eq $key){
		    splice(@item_lst,$i,1);
		    $it = join('/',@item_lst);
		    last;
					   }
					 }
	    @item_lst = split(/\|/,$pt_it);
	    for($i=0;$i<=$#item_lst;$i++){
		if($item_lst[$i] eq $key){
		    splice(@item_lst,$i,1);
		    $pt_it = join('|',@item_lst);
		    last;
					   }
					 }
}
sub battle{
    if($adv_lg==1){		  # +a
    $log.="Enemy HP:$adv_hp<br>"; # 戦闘ﾛｸﾞ表示
    $log.="Your HP:$pt_hp<br>";   # 戦闘前の敵味方の
		  }		  # HP･MPを表示
    $j=0;				     # +a
    if($pt_cl =~ /A/){ $j = 33; }	     # ｸﾘﾃｨｶﾙﾋｯﾄの設定 Aのとき33%
    elsif($pt_cl =~ /[NT]/){ $j = 20; }      # NTのとき20%
    elsif($pt_cl =~ /[FHLR]/){ $j = 5; }     # 戦士系は5%
    else{$j = 0; }			     # その他は0%
    $atp = $pt_atp-$adv_ap;
    if($t_weak == 1){		       # +a
    $atp0 = $atp;		       # 弱化の設定
    $atp = 0;			       #
		    }		       #
    $atp = 0 if($atp<0);
    $mgp = $pt_mgp-$adv_rp;
    if($t_silent == 1){ 	       # +a
    $mgp0 = $mgp;		       # 沈黙の設定
    $mgp = 0;			       #
		      } 	       #
    $mgp = 0 if($mgp<0);
    if($pt_cl =~ /P/){ $adv_un = int($adv_un/4); }
    elsif($pt_cl =~ /[CBH]/){ $adv_un = int($adv_un/2); }

    $atp_ = $adv_wp-$pt_dfp;
    $atp_ = 0 if($atp_<0);

    $dmg = 0;
    $dmg_ = 0;
    for(;$adv_lt>0;$adv_lt--){
    if($t_weak == 1){		       # +a
    if (rand(1)>$t_pow_1){	       # 弱化の解除
    $log.="物攻が戻った! ";	       #
    $atp = $atp0;		       #
    $t_weak = 0;		       #
				     } #
		    }		       #
    if($t_silent == 1){ 	       # +a
    if (rand(1)>$t_pow_2){	       # 沈黙の解除
    $log.="魔攻が戻った! ";	       #
    $mgp = $mgp0;		       #
    $t_silent = 0;		       #
				     } #
		    }		       #
	$v = int(($mgp+1)/2);
	if($mgp>$atp && $pt_mp>=$v){
	    $pt_mp -= $v;
	    $mp -= $v;
	    $mp = 0 if($mp<0);
	    $k = $mgp+int(rand(2)); # +a
	    $dmg = $dmg+$k;	    # 戦闘ﾛｸﾞ表示on指定の時は
	    if($adv_lg==1){	    # 味方から敵への
	    $log.="\>\>$k\ ";	    # 魔攻ﾀﾞﾒｰｼﾞを >>n で表示
			  }	    #
	}else{
    if(rand(100)<$j && $CR==1 && $t_weak ==0){		      # +a
	    $k=int($pt_atp*1.5)+int(rand(2)),$v=1;	      # ｸﾘﾃｨｶﾙは防御無視×1.5
    }else{$k = $atp+int(rand(2)),$v=0;			      #
			      } 			      #
	    $dmg = $dmg+$k;				      # 味方から敵に
	    if($adv_lg==1){				      # ｸﾘﾃｨｶﾙﾋｯﾄが決まったとき、
	    $log.="\>$k";				      # 戦闘ﾛｸﾞ表示on指定の時は
	    if($v == 1){$log.="!";}			      # ﾀﾞﾒｰｼﾞを >n! で表示
	    $log.="\ "; 				      #
			  }				      #
	}
	$k = $atp_+$adv_mp+int(rand(2)); # +a
	$dmg_ = $dmg_+$k;		 # 戦闘ﾛｸﾞ表示on指定の時は
	    if($adv_lg==1){		 # 敵から味方への
	    $log.="$k\<\ ";		 # ﾀﾞﾒｰｼﾞを n< で表示
			  }		 #

	if($wb > 1){ $wb--; }
	elsif($wb == 1){
	    if($wn ne 'ｽﾃﾞ'){
		$log .= "$wn\が壊れた!<br>\n";
		$wn = 'ｽﾃﾞ';
	    }
	    $wp = 0;
	    $wb = 0;
	    if($pt_n == 1){
		$atp = 0;
		$pt_atp = 0;
	    }
	}
	if($ab > 1){ $ab--; }
	elsif($ab == 1){
	    if($an ne 'ﾌｸ'){
		$log .= "$an\が壊れた!<br>\n";
		$an = 'ﾌｸ';
	    }
	    $ap = 0;
	    $ab = 0;
	    if($pt_n == 1){
		$atp_ = $adv_wp;
		$pt_dfp = 0;
	    }
	}

      if($dmg_>=$pt_hp){
       if($cl_sy[$cl] =~ /[CPBH]/ && $RE == 1){ # +a
	  $hp = int($pt_hp/3);	      # 僧侶なら逝かない
	  $hp = 1 if($pt_hp<1);       # 最終戦闘前の1/3のhp・mpが残る
	  $mp = int($pt_mp/3);	      #
	  if($hp == 1 && $mp ==0){    #
	  if($adv_lg==1){ # +a
	  $log .="<hr>";  # 戦闘ﾛｸﾞ表示
			} #
	  $log .="$msg_lose";
	  }else{						  #
	  $log .="<hr>力尽きたが、聖なる力で少し回復した･･･<br>"; #
	       }						  #
	}elsif($pt_cl =~ /[CPBH]/ && $RE == 1){ 		  #
	  $hp = int($pt_hp/4);	      # 僧侶がﾊﾟｰﾃｨｰにいれば逝かない
	  $hp = 1 if($pt_hp<1);       # 最終戦闘前の1/4のhp・mpが残る
	  $mp = int($pt_mp/4);	      #
	  if($hp == 1 && $mp ==0){    #
	  if($adv_lg==1){ # +a
	  $log .="<hr>";  # 戦闘ﾛｸﾞ表示
			} #
	  $log .="$msg_lose";
	  }else{							  #
	  $log .="<hr>力尽きたが、聖なる力で少し回復してもらった･･･<br>"; #
	       }							  #
	}else{
	  if($adv_lg==1){ # +a
	  $log .="<hr>";  # 戦闘ﾛｸﾞ表示
			} #
	  $log .="$msg_lose";
	  $hp = 1;
	  $mp = 0;
				  }
	    last;
	}elsif($dmg>=$adv_hp){
	    if($adv_lg==1){ # +a
	    $log .="<hr>";  # 戦闘ﾛｸﾞ表示
			  } #
	    $pt_hp -= $dmg_;
	    $hp -= $dmg_;
	    $hp = 1 if($hp<1);
	    $ex_ += int($adv_ex/$pt_n);
	    if($pt_n<6){ $ex_ += $pt_n-1; }
	    else{ $ex_ += 5; }
	    return 1;
	}

	$dmg -= $adv_un;
 if($adv_un != 0 && $adv_lg != 0){$log .="$adv_un\+\ ";} # +a # 戦闘ﾛｸﾞ表示onのとき
	$dmg = 0 if($dmg<0);				 # 敵ｱﾝﾃﾞｯﾄﾞの回復を n+ で表示
    }
    if($adv_lt == 0){
	if($adv_lg==1){ # +a
	$log .="<hr>";	# 戦闘ﾛｸﾞ表示
		      } #
	$log .= $msg_timeup;
	$hp -= $dmg_;
	$hp = 1 if($hp<1);
    }
    $v = $dmg/$adv_hp;
    $v = 1 if($v>1);
    $ex_ += int($adv_ex*$v/$pt_n);
    if($pt_n<6){ $ex_ += $pt_n-1; }
    else{ $ex_ += 5; }
    &exp_up($ex_);
    return 0;
}

sub exp_up{
    local($ex_) = @_;

    if($ex_>0){
	$log .= "$ex_"."Exp手に入れた。<br>\n";
	$ex += $ex_;
	if($ex >= $lv*$lv*10){
	    $log .= "ﾚﾍﾞﾙが上がった!<br>\n";
	    $lv++;
	    &set_max_point;
	}
    }
}

sub skip_nest{
    for($l++;$l<=$#script;$l++){
	$line = $script[$l];
	if( $line =~ /^\s*}/ ){ last; }
	elsif( $line =~ /{.*}/ ){ next; }
	elsif( $line =~ /{[\s\r\n]/ ){
	    &skip_nest;
	    for(;$line =~ /else\s+if\s*\(.*\)\s*{/;){ &skip_nest; }
	    if( $line =~ /else\s*{/ ){ &skip_nest; }
	}
    }
}

sub cmd_analyze{
    local($log_);

    $log_ = '';
    if($st == 0 || ($st >= 10 && $st <=19)){
	if($DAT{'cmd'} == 1){
	    $log_ = "- どこで休みますか? -<br>\n";
	    $st = 1;
	}elsif($DAT{'cmd'} == 2){
	    $log_ = "- どこへ行きますか? -<br>\n";
	    $st = 2;
	}elsif($DAT{'cmd'} == 3){
	    $log_ = "- どれを引き受けますか? -<br>\n";
	    $st = 3;
	}elsif($DAT{'cmd'} == 4){
	    $log_ = "「$shp_welcome\」<br>\n";
	    $st = 4;
	}elsif($DAT{'cmd'} == 5){
	    $log_ = "- どこへ行きますか? -<br>\n";
	    $st = 5;
	}
    }elsif($st == 1){
	$v = $DAT{'cmd'};
	$v = 0 if($v<0 || $v>$#rst_lst || $v>9);
	$log_ = $rst_msg[$v]."<br>\n";
	$st = 10+$v;
	$nx = $time+60*60;
    }elsif($st == 2){
#	for($i=0;$i<=$#adv_lst;$i++){			    #uni氏による誤動作対策
#	    last if($DAT{'cmd'} eq $adv_lst[$i]);	    #
#	}						    #
#	if($i <= $#adv_lst){				    #
       $i = $DAT{'cmd'};				    #
       if($DAT{'st'} == $st && 0 <= $i && $i <= $#adv_lst){ #
	    $v = $adv_t[$i];
	    $v = 1 if($v<1);
	    $log_ = "目的地:$adv_lst[$i]<br>所要時間:$v<br>ﾊﾟｰﾃｨｰ人数:$adv_n[$i]<hr>- 出発しますか? -<br>\n";
	    $st = 25;
	    $op = $i;
	}else{
	    $log_ = "準備がまだだった。<br>\n";
	    $st = 0;
	}
    }elsif($st == 3){
#	for($i=0;$i<=$#wrk_lst;$i++){			     #uni氏による誤動作対策
#	    last if($DAT{'cmd'} eq $wrk_lst[$i]);	     #
#	}						     #
#	if($i <= $#wrk_lst){				     #
       $i = $DAT{'cmd'};				     #
       if($DAT{'st'} == $st && 0 <= $i && $i <= $#wrk_lst){  #
	    $v = $wrk_t[$i];
	    $v = 1 if($v<1);
	    $log_ = "依頼内容:$wrk_lst[$i]<br>所要時間:$v<br>ﾊﾟｰﾃｨｰ人数:$wrk_n[$i]<hr>- 引き受けますか? -<br>\n";
	    $st = 35;
	    $op = $i;
	}else{
	    $log_ = "やっぱりやめた。<br>\n";
	    $st = 0;
	}
    }elsif($st == 4){
	if($DAT{'cmd'} == 1){
	    $log_ = "「$shp_mihy\」<br>\n";
	    $st = 40;
	}elsif($DAT{'cmd'} == 2){
	    $log_ = "「$shp_mihy\」<br>\n";
	    $st = 41;
	}elsif($DAT{'cmd'} == 3){
	    $log_ = "「$shp_mihy\」<br>\n";
	    $st = 42;
	}elsif($DAT{'cmd'} == 4){
	    $log_ = "「$shp_which\」<br>\n";
	    $st = 43;
	}else{
	    $log_ = "「$shp_thanks\」<br>\n";
	    $st = 0;
	}
    }elsif($st == 5){
#	 for($i=0;$i<=$#twn_lst;$i++){			      #uni氏による誤動作対策
#	     if($DAT{'cmd'} eq $twn_lst[$i]){		      #
#		 $key = $twn_lst[$i];			      #
#		 last;					      #
#	     }						      #
#	 }						      #
#	 if($i <= $#twn_lst){				      #
	 $i = $DAT{'cmd'};				      #
	 $key = $twn_lst[$i];				      #
	 if($DAT{'st'} == $st && 0 <= $i && $i <= $#twn_lst){ #
	    $v = $twn_t[$i];
	    if($v > 0){
		$log_ = "$key\までは$v"."時間ほどの道のりだ。<br>\n";
		$st = 50;
		$op = $i;
	    }else{
		$log_ = "ここが$key\だ。<br>\n";
		$st = 0;
	    }
	}else{
	    $log_ = "準備がまだだった。<br>\n";
	    $st = 0;
	}
    }elsif($st == 21){
	($key,$v,$i,$j) = split(/\//,$op);
	if($DAT{'cmd'} == 0){
	    $log_ = "$v\をあきらめた<br>\n";
	}else{
	    $log_ = "$v\を装備した!<br>\n";
	    if($key eq 'w'){
		$wn = $v;
		$wp = $i;
		$wb = $j;
	    }elsif($key eq 'a'){
		$an = $v;
		$ap = $i;
		$ab = $j;
	    }
	}
	if($lv == 10 && $cl < 4){
	    $log_ .= "- ｸﾗｽﾁｪﾝｼﾞ! -<br>\n";
	    $st = 23;
	}else{
	    $st = 0;
	}
	$op = '';
    }elsif($st == 22){
	($key,$v) = split(/\//,$op);
	@item_lst = split(/\//,$it);
#	for($i=0;$i<=$#item_lst;$i++){			    # ???
#	    last if($DAT{'cmd'} eq $item_lst[$i]);	    #
#	}						    #
#	if($i <= $#item_lst){				    #
      $i = $DAT{'cmd'}; 				    #
      $key = $item_lst[$i];				    #
      if($DAT{'st'} == $st && 0 <= $i && $i <= $#item_lst){ #
	    $log_ = "$item_lst[$i]\を捨てて$v\を手に入れた!<br>\n";
	    $item_lst[$i] = $v;
	    $it = join('/',@item_lst);
	}else{
	    $log_ = "$v\をあきらめた<br>\n";
	}
	if($lv == 10 && $cl < 4){
	    $log_ .= "- ｸﾗｽﾁｪﾝｼﾞ! -<br>\n";
	    $st = 23;
	}else{
	    $st = 0;
	}
	$op = '';
    }elsif($st == 23){
	if($DAT{'cmd'} ne ''){
	    if($DAT{'cmd'} == 1){
		if($cl == 0){ $cl = 8; }
		elsif($cl == 1){ $cl = 8; }
		elsif($cl == 2){ $cl = 10; }
		elsif($cl == 3){ $cl = 11; }
	    }elsif($DAT{'cmd'} == 2 && $cl<3){
		if($cl == 0){ $cl = 10; }
		elsif($cl == 1){ $cl = 9; }
		elsif($cl == 2){ $cl = 9; }
	    }else{
		$cl += 4;
	    }
	    &set_max_point;
	    $log_ = "$cl_nm[$cl]になった!<br>\n";
	    $st = 0;
	}else{
	    $log_ .= "- ｸﾗｽﾁｪﾝｼﾞ! -<br>\n";
	}
    }elsif($st == 25){
	if($DAT{'cmd'} == 0 || $op > $#adv_lst){
	    $log_ = "- どこへ行きますか? -<br>\n";
	    $st = 2;
	    $op = '';
	}else{
	    $log_ = "出発!<br>\n";
	    $i = int($op);
	    $v = $adv_t[$i];
	    $v = 1 if($v<1);
	    $st = 20;
	    $op = $adv_lst[$i];
	    $nx = $time + $v*60*60;
	    &update_party($op,$adv_n[$i]);
	}
    }elsif($st == 35){
	if($DAT{'cmd'} == 0 || $op > $#wrk_lst){
	    $log_ = "- どれを引き受けますか? -<br>\n";
	    $st = 3;
	    $op = '';
	}else{
	    $log_ = "仕事開始!<br>\n";
	    $i = int($op);
	    $v = $wrk_t[$i];
	    $v = 1 if($v<1);
	    $st = 30;
	    $op = $wrk_lst[$i];
	    $nx = $time + $v*60*60;
	    &update_party($op,$wrk_n[$i]);
	}
    }elsif($st == 40){
#	 for($i=0;$i<=$#shp_wn;$i++){			     #uni氏による誤動作対策
#	     if($DAT{'cmd'} eq $shp_wn[$i]){		     #
#		 $key = $shp_wn[$i];			     #
#		 last;					     #
#	     }						     #
#	 }						     #
#	 if($i <= $#shp_wn){				     #
	 $i = $DAT{'cmd'};				     #
	 $key = $shp_wn[$i];				     #
	 if($DAT{'st'} == $st && 0 <= $i && $i <= $#shp_wn){ #
	    $v = $shp_wg[$i];
	    $log_ = "「$key\[$shp_wp[$i]x$shp_wb[$i]\]は$shp_wmsg[$i]<br>\n$v"."Gp$shp_ok\」<br>\n";
	    $st = 44;
	    $op = "w/$key/$v";
	}else{
	    $log_ = "「$shp_other\」<br>\n";
	    $st = 4;
	}
    }elsif($st == 41){
#	 for($i=0;$i<=$#shp_an;$i++){			     #uni氏による誤動作対策
#	     if($DAT{'cmd'} eq $shp_an[$i]){		     #
#		 $key = $shp_an[$i];			     #
#		 last;					     #
#	     }						     #
#	 }						     #
#	 if($i <= $#shp_an){				     #
	  $i = $DAT{'cmd'};				     #
	 $key = $shp_an[$i];				     #
	 if($DAT{'st'} == $st && 0 <= $i && $i <= $#shp_an){ #
	    $v = $shp_ag[$i];
	    $log_ = "「$key\[$shp_ap[$i]x$shp_ab[$i]\]は$shp_amsg[$i]<br>\n$v"."Gp$shp_ok\」<br>\n";
	    $st = 44;
	    $op = "a/$key/$v";
	}else{
	    $log_ = "「$shp_other\」<br>\n";
	    $st = 4;
	}
    }elsif($st == 42){
#	 $i = &search_item($DAT{'cmd'});	     #uni氏による誤動作対策
	 $key = $DAT{'cmd'};			     #
	if($DAT{'st'} == $st && $key ne '-1'){	     #
	    $key =~ s/(..)/sprintf('%c',hex($1))/ge; #
	    $i = &search_item($key);		     #
	}else{					     #
	    $i = -1;				     #
	}					     #
	if($i<0){
	    $log_ = "「$shp_other\」<br>\n";
	    $st = 4;
	}else{
	    $v = &item_value($item_n);
	    $log_ = "「$item_nm\は$v"."Gp$shp_ok\」<br>\n";
	    $st = 44;
	    $op = "i/$item_nm/$v";
	}
    }elsif($st == 43){
	@item_lst = split(/\//,$it);
#	 for($i=0;$i<=$#item_lst;$i++){ 		       #uni氏による誤動作対策
#	     last if($DAT{'cmd'} eq $item_lst[$i]);	       #
#	 }						       #
#	 if($i <= $#item_lst){				       #
#	     $i = &search_item($DAT{'cmd'});		       #
	 $i = -1;					       #
	 $i = $DAT{'cmd'} if($DAT{'cmd'} ne '');	       #
	 if($DAT{'st'} == $st && 0 <= $i && $i <= $#item_lst){ #
	    $key = $item_lst[$i];			       #
	   $i = &search_item($key);			       #??
	    $v = &item_value($item_n);
	    $v = int($v/2);
#	    $key = $DAT{'cmd'}; 			       #??
	    $log_ = "「$key\は$v"."Gp$shp_ok\」<br>\n";
	    $st = 45;
	    $op = "i/$key/$v";
	}else{
	    $log_ = "「$shp_other\」<br>\n";
	    $st = 4;
	}
    }elsif($st == 44){
	if($DAT{'cmd'} == 0){
	    $log_ = "「$shp_other\」<br>\n";
	}else{
	    $log_ = &buy_item;
	}
	$st = 4;
	$op = '';
    }elsif($st == 45){
	if($DAT{'cmd'} == 0){
	    $log_ = "「$shp_other\」<br>\n";
	}else{
	    $log_ = &sell_item;
	}
	$st = 4;
	$op = '';
    }elsif($st == 50){
	$log_ = "- どこへ行きますか? -<br>\n";
	$st = 5;
	$op = '';
    }
    if($log_ ne ''){
	$log .= "$log_<hr>\n";
	$update = 1;
    }
}

sub update_party{
    local($target,$max_n) = @_;

    for($i=2;$i<=$#gdat;$i++){
	($t,$key,$v) = split(/\t/,$gdat[$i]);
	if($key eq $target){
	    splice(@gdat,$i,1);
	    $i--;
	    next if($t < $nx-5*60); # +a 合流可能時間10分
	    $nx = $t;
	    $pt = $v;
	    $pt =~ s/[\r\n]//g;
	    last;
	}
    }
$flg=0; 			# +a
for(0..$#gm_name){		# ﾃﾞﾊﾞｸﾞｷｬﾗ複数設定
if($nm eq $gm_name[$_]){$flg=1} #
		 }		#
    if($i<=$#gdat && ($flg != 1)){
	($pt_n,$pt_cl,$pt_hp,$pt_mp,$pt_atp,$pt_mgp,$pt_dfp,$pt_it,$pt_mem) = split(/\//,$pt,9);
	$log .= "$pt_mem\のﾊﾟｰﾃｨｰに加わった!<br>\n";
	if($it ne ''){
	    $pt_it .= "\|" if($pt_it ne '');
	    $pt_it .= $it;
	}
	$pt_mem .= "/$nm";
    }else{
	$pt_n = 0;
	$pt_cl = '';
	$pt_hp = 0;
	$pt_mp = 0;
	$pt_atp = 0;
	$pt_mgp = 0;
	$pt_dfp = 0;
	$pt_it = $it;
	$pt_mem = $nm;
    }
    $pt_it =~ s/\//\|/g;

    $pt_n++;
    $pt_cl .= $cl_sy[$cl];
    $pt_hp = $hp if($hp>$pt_hp);
    $pt_mp = $mp if($mp>$pt_mp);

    if($cl_sy[$cl] =~ /[SWB]/){ $atp = int(($wp+1)/3); }
    elsif($cl_sy[$cl] =~ /[CTPN]/){ $atp = int(($wp*2+1)/3); }
    else{ $atp = $wp; }
    $pt_atp = $atp if($atp>$pt_atp);

    $v = int(sqrt($lv)*2);
    $v -= $wp-1 if($wp>1);
    $v -= $ap-1 if($ap>1);
    if($wp>0 && $v>0){
	if($cl_sy[$cl] =~ /[FTLA]/){ $mgp = int(($v+1)/3); }
	elsif($cl_sy[$cl] =~ /[CPHN]/){ $mgp = int(($v*2+1)/3); }
	else{ $mgp = $v; }
    }else{ $mgp = 0; }
    $pt_mgp = $mgp if($mgp>$pt_mgp);

    $pt_dfp = $ap if($ap>$pt_dfp);

    $pt = "$pt_n/$pt_cl/$pt_hp/$pt_mp/$pt_atp/$pt_mgp/$pt_dfp/$pt_it/$pt_mem";
$flg=0; 			# +a
for(0..$#gm_name){		# ﾃﾞﾊﾞｸﾞｷｬﾗ複数設定
if($nm eq $gm_name[$_]){$flg=1} #
		 }		#
    return if($flg == 1);	#
    push(@gdat,"$nx\t$target\t$pt\n") if($pt_n<$max_n);

    $nm_ = $nm;
    $pt_ = $pt;
    &set_data($n0);
    @pt_mem = split(/\//,$pt_mem);
    for($i=0;$i<$#pt_mem;$i++){
	for($j=1;$j<=$#dat;$j++){
	    &get_header($dat[$j]);
	    last if($pt_mem[$i] eq $nm);
	}
	if($j<=$#dat){
	    &get_data($dat[$j]);
	    $pt = $pt_;
	    $lg .= "$nm_\がﾊﾟｰﾃｨｰに加わった!<br>";
	    &set_data($j);
	}
    }
    &get_data($dat[$n0]);
}

sub search_item{
    local($key) = @_;
    local($items);

    $items = $gdat[1];
    $items =~ s/[\n\r]//g;
    @item_lst = split(/,/,$items);
    for($i=0;$i<=$#item_lst;$i++){
	($item_nm,$item_n) = split(/\//,$item_lst[$i]);
	last if($key eq $item_nm);
    }
    if($i>$#item_lst){
	$i = -1;
	$item_nm = '';
	$item_n = 0;
    }
    $i;
}

sub item_value{
    local($n) = @_;

    if($n<0){ $n = 0; }
    elsif($n>99){ $n = 99; }
    $rv = int(110-sqrt($n+1)*10);
    $rv;
}

sub buy_item{
    local($log_);

    ($i,$key,$v) = split(/\//,$op);
    if($gp < $v){
	$log_ = "「$shp_nomoney\」<br>\n";
    }else{
	if($i eq 'w'){
	    for($i=0;$i<=$#shp_wn;$i++){ last if($key eq $shp_wn[$i]); }
	    if($i<=$#shp_wn){
		$log_ = "「$shp_thanks\」<br>\n";
		$wn = $key;
		$gp -= $v;
		$wp = $shp_wp[$i];
		$wb = $shp_wb[$i];
	    }else{
		$log_ = "「$shp_soldout\」<br>\n";
	    }
	}elsif($i eq 'a'){
	    for($i=0;$i<=$#shp_an;$i++){ last if($key eq $shp_an[$i]); }
	    if($i<=$#shp_an){
		$log_ = "「$shp_thanks\」<br>\n";
		$an = $key;
		$gp -= $v;
		$ap = $shp_ap[$i];
		$ab = $shp_ab[$i];
	    }else{
		$log_ = "「$shp_soldout\」<br>\n";
	    }
	}else{
	    @item_lst = split(/\//,$it);
	    if($#item_lst < 2){
		$i = &search_item($key);
		if($i<0){
		    $log_ = "「$shp_soldout\」<br>\n";
		}else{
		    $log_ = "「$shp_thanks\」<br>\n";
		    $it .= '/' if($it ne '');
		    $it .= $key;
		    $gp -= $v;
		    if($item_n > 1){
			$item_n--;
			$item_lst[$i] = "$item_nm/$item_n";
		    }else{
			splice(@item_lst,$i,1);
		    }
		    $gdat[1] = join(',',@item_lst);
		    $gdat[1] .= "\n";
		}
	    }else{
		$log_ .= "「$shp_over\」<br>\n";
	    }
	}
    }
    $log_;
}

sub sell_item{
    local($log_);

    ($i,$key,$v) = split(/\//,$op);
    @item_lst = split(/\//,$it);
    for($i=0;$i<=$#item_lst;$i++){
	last if($key eq $item_lst[$i]);
    }
    if($i<=$#item_lst){
	$log_ = "「$shp_thanks\」<br>\n";
	splice(@item_lst,$i,1);
	$it = join('/',@item_lst);
	$gp += $v;
	$i = &search_item($key);
	if($i<0){
	    push(@item_lst,"$key/1");
	}else{
	    $item_n++;
	    $item_n = 99 if($item_n>99);
	    $item_lst[$i] = "$item_nm/$item_n";
	}
	$gdat[1] = join(',',@item_lst);
	$gdat[1] .= "\n";
    }else{
	$log_ = "「$shp_noitem\」<br>\n";
    }
    $log_;
}

sub print_status{
    $v = int($time/(6*60*60));
    srand($v);
    $v=$nx-$time;		       # +a
    $i=int($v/60);		       # 次の回復までの時間を表示
    $v=$v-$i*60;   #		       #
    if($i==0 && $v==0){ 	       #
    $v="";			       #
		      }else{	       #
    $v="<br>次の回復まで<br>$i分$v秒"; #
			   }	       #
    $log .= "- 休息中 -$v<hr>\n" if($st >= 10 && $st <= 19);


    $log .= "名前:$nm<br>ｸﾗｽ:$cl_nm[$cl]\[Lv$lv\]<br>Exp:$ex<br>Gp:$gp<br>Hp:$hp/$mhp<br>Mp:$mp/$mmp<br>$wn\[$wp".'x'."$wb\]<br>$an\[$ap".'x'."$ab\]<br>$it<br>\n"; # +a ｱｲﾃﾑ表示
    if($st == 50){
	$log .= "<form action=\"$twn_url[$op]nph-yk_srv.cgi\" method=GET name=yk_srv>\n";
	$log .= "<input type=hidden name=URL value=\"$my_url\">\n";
	$log .= "<input type=hidden name=nm value=\"$nm\">\n<input type=hidden name=pw value=\"$pw\">\n";
	$log .= "<input type=submit value=GO><br></form>\n";

	$log .= "<form action=yk_.cgi method=$method name=yk_>\n";
	$log .= "<input type=hidden name=nm value=\"$nm\">\n<input type=hidden name=pw value=\"$pw\">\n";
	$log .= "<input type=submit value=CANCEL><br></form>\n";
    }else{
	$log .= "<form action=yk_.cgi method=$method name=yk_>\n";
	$log .= "<input type=hidden name=nm value=\"$nm\">\n<input type=hidden name=pw value=\"$pw\">\n";
	$log .= "ｺﾏﾝﾄﾞ<select name=cmd size=1>\n";
	if($st == 0 || ($st >= 10 && $st <= 19)){
	    for($i=0;$i<=$#cmd_lst;$i++){ $log .= "<option value=$i>$cmd_lst[$i]</option>\n"; }
	}elsif($st == 1){
	    for($i=0;$i<=$#rst_lst;$i++){ $log .= "<option value=$i>$rst_lst[$i]</option>\n"; }
	}elsif($st == 2){
	    &select_list(*adv_lst);
	}elsif($st == 3){
	    &select_list(*wrk_lst);
	}elsif($st == 4){
	    for($i=0;$i<=$#shp_lst;$i++){ $log .= "<option value=$i>$shp_lst[$i]</option>\n"; }
	}elsif($st == 5){
	    &select_list(*twn_lst);
	}elsif($st == 40){
	    &select_list(*shp_wn);
	}elsif($st == 41){
	    &select_list(*shp_an);
	}elsif($st == 42){
#	     $log .= "<option>やめる</option>\n";	      #uni氏による誤動作対策
	    $log .= "<option value=\"-1\">やめる</option>\n"; #
	    $items = $gdat[1];
	    $items =~ s/[\n\r]//g;
	    @item_lst = split(/,/,$items);
	    if($#item_lst>18){
		$i = $#item_lst-18;
		for(;$i>0;$i--){
		    $j = int(rand($#item_lst+1));
		    splice(@item_lst,$j,1);
		}
	    }
	    for($i=0;$i<=$#item_lst;$i++){
		($key,$v) = split(/\//,$item_lst[$i]);
		$log .= "<option";
#		$log .= " value=\"$key\"" if($method eq 'GET'); #uni氏による誤動作対策
		$key_e = $key;					#
		$key_e =~ s/(.)/ sprintf('%02x',ord($1)) /ge;	#
		$log .= " value=\"$key_e\"";			#
		$log .= ">$key</option>\n";
	    }
	}elsif($st == 22 || $st == 43){
#	    $log .= "<option>やめる</option>\n";		#uni氏による誤動作対策
	    $log .= "<option value=\"-1\">やめる</option>\n";	#
	    @item_lst = split(/\//,$it);
	    for($i=0;$i<=$#item_lst;$i++){
		$log .= "<option";
#		$log .= " value=\"$item_lst[$i]\"" if($method eq 'GET'); #uni氏による誤動作対策
		$log .= " value=\"$i\"";				 #
		$log .= ">$item_lst[$i]</option>\n";
	    }
	}elsif($st == 23){
	    if($cl == 0){ $log .= "<option value=0>$cl_nm[4]</option><option value=1>$cl_nm[8]</option><option value=2>$cl_nm[10]</option>\n"; }
	    elsif($cl == 1){ $log .= "<option value=0>$cl_nm[5]</option><option value=1>$cl_nm[8]</option><option value=2>$cl_nm[9]</option>\n"; }
	    elsif($cl == 2){ $log .= "<option value=0>$cl_nm[6]</option><option value=1>$cl_nm[10]</option><option value=2>$cl_nm[9]</option>\n"; }
	    elsif($cl == 3){ $log .= "<option value=0>$cl_nm[7]</option><option value=1>$cl_nm[11]</option>\n"; }
	}elsif($st == 21 || $st == 25 || $st == 35 || $st == 44 || $st == 45){
	    $log .= "<option value=0>嫌です</option><option value=1>了承</option>\n";
	}else{
	    $log .= "<option value=0>確認</option>\n";
	}
	$log .= "</select><br>\n";
	$log .= "<input type=\"hidden\" name=\"st\" value=\"$st\">"; #uni氏による誤動作対策
	$log .= "<input type=submit value=OK><br></form>\n";
    }
    $nm_e = &escape_code($nm);
    $pw_e = &escape_code($pw);
    $log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e\">酒場</a><br>\n";
    $log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e&n=1\">掲示板</a><br>\n";
    $log .= "<a href=\"yk_msg.cgi?nm=$nm_e&pw=$pw_e\">伝言</a><br>\n";
}

sub select_list{
    local(*lst) = @_;

    if($#lst>18){
	$i = $#lst-18;
	for(;$i>0;$i--){
	    $j = int(rand($#lst-8))+9;
	    splice(@lst,$j,1);
	}
    }
#   $log .= "<option>やめる</option>\n";	      #uni氏による誤動作対策
    $log .= "<option value=\"-1\">やめる</option>\n"; #
    for($i=0;$i<=$#lst;$i++){
	$log .= "<option";
#	$log .= " value=\"$lst[$i]\"" if($method eq 'GET'); #uni氏による誤動作対策
	$log .= " value=\"$i\"";			    #
	$log .= ">$lst[$i]</option>\n";
    }
}
