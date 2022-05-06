#! /usr/local/bin/perl
#
# ��F�̶ڲ�޽���� by b-Yak-38
#
require './yk_prf.cgi';
require './yk_ini.cgi';

@cmd_lst = ('���̂܂�','�x��','�`��','�˗�','���','�ړ�');
@shp_lst = ('�o��','����','�h��','����','����');

#&error("�������܃����e�i���X���ł��B���΂炭���҂��������B");

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
	$log .= "�`�����ł��B<br>";
	$f = 1;
    }elsif($st == 30){
	$log .= "�d�����ł��B<br>";
	$f = 1;
    }elsif($st == 51){
	$log .= "�ړ����ł��B<br>";
	$f = 1;
    }else{
	$f = 0;
    }
    if($f == 1){
	$i = $nx-$time;
	if($i<60){
	    $v = "$i\�b";
	}elsif($i<60*60){
	    $i = int($i/60);
	    $v = "$i\��";
	}else{
	    $j = int(($i%(60*60))/60);
	    $i = int($i/(60*60));
	    $v = "$i\����$j\��";
	}
	$log .= "����$v\�B<hr>\n";
	$nm_e = &escape_code($nm);
	$pw_e = &escape_code($pw);
	$log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e\">����</a><br>\n";
	$log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e&n=1\">�f����</a><br>\n";
	$log .= "<a href=\"yk_msg.cgi?nm=$nm_e&pw=$pw_e\">�`��</a><br>\n";
	$log .= "<a href=\"$topfile\">�߂�</a>\n";
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
<html><head><title>���</title></head>
$htmlcolor
@log
</body></html>
_HTML_
exit;

sub read_data{
    if(!open(IN,$datfile)){ &error("�ް�̧�ق��J���܂���B"); }
    @dat = <IN>;
    close(IN);
    if($dat[0] eq ''){ &error("�ް�̧�ق̓ǂݍ��݂Ɏ��s���܂����B"); }

    if(!open(IN,$gdatfile)){ &error("��۰����ް�̧�ق��J���܂���B"); }
    @gdat = <IN>;
    close(IN);
    if($gdat[0] eq ''){ &error("��۰����ް�̧�ق̓ǂݍ��݂Ɏ��s���܂����B"); }

    for($i=1;$i<=$#dat;$i++){
	&get_header($dat[$i]);
	if($DAT{'nm'} eq $nm){
	    if($DAT{'pw'} ne $pw){ &error("�߽ܰ�ނ��Ԉ���Ă��܂��B"); }
	    last;
	}
    }
    if($i>$#dat){ &error("���̖��O�ł͓o�^����Ă��܂���B"); }
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
    if($nm eq $gm_name[$_]){ $nx = $time-60*60; } # ���޸޷�ו����ݒ�
		 }				  #
}

sub write_data{
    $dat[0] = "$time\n";
    $ad = $adn;
    $ad =~ s/,//g;
    &set_data($n0);
    if(!open(OUT,">$datfile")){ &error("�ް�̧�قɏ������߂܂���B"); }
    print OUT @dat;
    close(OUT);

    if(!open(OUT,">$gdatfile")){ &error("��۰����ް�̧�قɏ������߂܂���B"); }
    print OUT @gdat;
    close(OUT);
}

sub proceed{
    if($st >= 10 && $st <= 19){
	$key = $st-10;
	$v = int(($time-$nx)/(60*60))+1;
	for($i=0;$i<$v;$i++){
	    if($gp<$rst_gp[$key]){
		$log .= "����������Ȃ�!<br>�ǂ��o���ꂽ!<br>\n";
		$st = 0;
		last;
	    }
	    $gp -= $rst_gp[$key];
	    $hp += $cl_hpp[$cl]*$key+int(rand(2));
	    $hp = $mhp if($hp>$mhp);
	    $mp += $cl_mpp[$cl]*$key+int(rand(2));
	    $mp = $mmp if($mp>$mmp);
	    if($hp==$mhp && $mp==$mmp){
		$log .= "���S�ɉ񕜂���!<br>\n";
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
	$log .= "�ړI�n�ɓ��������B<br>\n";
	$st = 0;
	$op = '';
	return 1;
    }
    return 0;
}

sub read_adv{
    if(!open(IN,$advfile)){ &error("��޳ު����̧�ق��J���܂���B"); }
    @script = <IN>;
    close(IN);

    $msg_lose = "�������A�r���ŗ͐s���Ă��܂����c<br>\n";
    $msg_timeup = "�������A���Ԃ����������Ă��܂����̂ň�U�߂邱�Ƃɂ����c<br>\n";
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
	$log .= "�ړI�n��������Ȃ������c<br>\n";
	$st = 0;
	$op = '';
    }
    if($lv == 10 && $cl < 4 && $st == 0){
	$log .= "- �׽��ݼ�! -<br>\n";
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
		if(rand(100) < $v){ $f = 1; } # �m������2 �E�Ɗ֌W�Ȃ�
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
		($key,$v) = split(/,/,$v);	     # event����
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
	    ($Subject,$rep_log,$rep_file) = split(/,/,$1);	   # BBS����߰Ă�ųݽ����
	    if($Subject == 1){$rep_log = $nm.$rep_log;} 	   # $Subject:
	    $rep_log = "> Report:<br>$rep_log [$date (SYS)]<br>\n";#  player�̖��O����߰Ă̐擪�ɓ����(1)
	    if(!open(IN,$rep_file)){				   #  ����Ȃ�(0)
	    $log.="�ް�̧�ق��J���Ȃ������B<br>\n";		   # $rep_log:BBS�ɗ�����߰�
				   }				   # $rep_file:��߰Ă𗬂�BBŞ�ق̎w��
	    @daty = <IN>;					   #
	    if($daty[0] eq ''){ 				   #
	    $log.="�ް�̧�ق̓ǂݍ��݂Ɏ��s�����B<br>\n";	   #
			      } 				   #
	    close(IN);						   #
	    push(@daty,$rep_log);				   #
	    if(!open(OUT,">$rep_file")){			   #
	    $log.="�ް�̧�ق��J���Ȃ������B<br>\n";		   #
				       }			   #
	    print OUT @daty;					   #
	    close(OUT); 					   #
	}elsif( $line =~ /^\s*battle\s*\((.*)\)\s*{/ ){
	    ($adv_hp,$adv_wp,$adv_mp,$adv_ap,$adv_rp,$adv_un,$adv_ex,$adv_lg) = split(/,/,$1); # +a �ϐ�$adv_log�ǉ��B
	    $log .= &add_message;							       # 1:�퓬���O�\�� 0:��\��
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
		$log .= "$v"."Gp��ɓ��ꂽ�B<br>\n";
		$gp += $v;
	    }
	    $ex_ += $adv_ex;
	    &exp_up($ex_);
	    if($adv_it ne ''){
		($key,$v) = split(/,/,$adv_it,2);
		if($key eq 'i'){
		    @item_lst = split(/\//,$it);
		    if($#item_lst<2){
			$log .= "$v\����ɓ��ꂽ!<br>\n";
			$it .= '/' if($it ne '');
			$it .= $v;
		    }else{
			$log .= "$v\�����������A�������������ς��������c<br>\n";
			$log .= "- �ǂꂩ�̂Ă܂���? -<br>\n";
			$st = 22;
			$op = "$key/$v";
		    }
		}elsif(($key eq 'w') || ($key eq 'a')){
		    ($v,$j,$k) = split(/,/,$v);
		    if($key eq 'w'){ $log .= "����:$v\[$j".'x'."$k\]��������!<br>\n"; } # +a
		    else{ $log .= "�h��:$v\[$j".'x'."$k\]��������!<br>\n"; }		  # ����h��\�\��
		    $log .= "- �������܂���? -<br>\n";
		    $st = 21;
		    $op = "$key/$v/$j/$k";
		}
	    }
	    return 1;
		}elsif( $line =~ /^\s*event\s*\((.*)\)\s*{/ ){		# +a
		  ($ev,$ev_e,$ev_log1,$ev_log0,$ev_v) = split(/,/,$1);	# $ev : ����Ă̎��
		   $log .= &add_message;				# $ev_e : ����Ă̌���
	    if($ev eq 'gp'){						# $ev_v : ������׸ނ̓Y��
		       if($gp+$ev_e<=0){				# (@ev_flg : ������׸�)
					$log .="$ev_log0";		# �w�肵�Ȃ�����׸ނ�$ev_flg[0]
					$ev_flg[$ev_v]=-1;		# $ev_log0 : ����Ď��s۸�
		       }else{						# $ev_log1 : ����Đ���۸�
					$log .="$ev_log1";		# = gp�l��(�r��)����� =
					$ev_flg[$ev_v]=1;		# $ev_e(���̒l��)�̒l��$gp�ɉ�����B
					$gp += $ev_e;			# $ev_e+$gp��0�ȉ��Ȃ玸�s
		       }						# �׸ނ�-1�ɂ���
			   }						# 0�ȏ�Ȃ琬��$ev_e�������A�׸ނ�1�ɂ���
									# ���l�ɐF��ȕϐ��ɑ΂��Ĳ���Ă��쐬�\
									#
		}elsif( $line =~ /^\s*trap\s*\((.*)\)\s*{/ ){		# +a
		    ($trap,$t_rate,$t_pow,$protec_item) = split(/,/,$1);# $trap : �ׯ�߂̎��
		     if($t_rate >= 1){$t_rate = 1;}			# $t_rate : �ׯ�߂̔�����(0.00 �` 1.00)
		     if($t_rate <= 0){$t_rate = 0;}			# $t_pow : �ׯ�߂̈З́A
 #		     if($t_pow >= 1){$t_pow = 1;}			# hp���~$trap�������� (0.00 �` 1.00)
 #		     if($t_pow <= 0){$t_pow = 0;}			# $protec_item : �ׯ�߉���юw��
	    $log .= &add_message;					#
    if($trap eq 'A'){							#
     &chk_protec_item($protec_item);					#
     if($flg == 1){							# �ׯ�ߐݒ�B
      &use_item($v);							# �u��P�v
      $log.="������$v�̗͂Ŕ����邱�Ƃ��o����!<br>";			# ������Ұ�ޕt�^���
      $log.="$v�͉��Ă��܂�����<hr>"; 				# $t_rate : 㩂��󂯂�m���B
     }elsif($pt_cl =~/[TAN]/ && (rand(1)>$t_rate/2)){			# �����n������Ɣ����B
      $log.="�����������̂Ƃ����̔��f�ŁA�����邱�Ƃ��o����<hr>";	# $dmg0_ �搧�U����Ұ��
     }elsif(rand(1)>$t_rate){						#
      $log.="�������K�^�ɂ������邱�Ƃ��o����<hr>";			#
     }else{								#
      $v=int($pt_hp*$t_pow);						#
      $pt_hp-=$v;							#
      $hp-=$v;								#
      $log.="$v����Ұ�ނ��󂯂Ă��܂���!<hr>";				#
	  }								#
    }elsif($trap eq 'W'){						#
     &chk_protec_item($protec_item);					#
     if($flg >= 1){							# �ׯ�ߐݒ�B
      &use_item($v);							# �u�㉻�v
      $log.="������$v�̗͂Ŕ����邱�Ƃ��o����!<br>";			# �����U���͂�0�ɂȂ��Ă��܂��
      $log.="$v�͉��Ă��܂�����<hr>"; 				# $t_rate : 㩂��󂯂�m���B
     }elsif(rand(1)>$t_rate){						# $t_pow : 㩂̌p������m���B
      $log.="�������K�^�ɂ������邱�Ƃ��o����<hr>";			#
     }else{								#
      $t_weak=1;							#
      $t_pow_1 = $t_pow;						#
      $log.="���U�������Ă��܂���!<hr>";				#
	  }								#
    }elsif($trap eq 'S'){						#
     &chk_protec_item($protec_item);					#
     if($flg >= 1){							# �ׯ�ߐݒ�B
      &use_item($v);							# �u���فv
      $log.="������$v�̗͂Ŕ����邱�Ƃ��o����!<br>";			# ���@�U����0�ɂȂ��Ă��܂��
      $log.="$v�͉��Ă��܂�����<hr>"; 				# $t_rate : 㩂��󂯂�m���B
     }elsif(rand(1)>$t_rate){						# $t_pow : 㩂̌p������m���B
      $log.="�������K�^�ɂ������邱�Ƃ��o����<hr>";			#
     }else{								#
      $t_silent=1;							#
      $t_pow_2 = $t_pow;						#
      $log.="���U�������Ă��܂���!<hr>";				#
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
    $log.="Enemy HP:$adv_hp<br>"; # �퓬۸ޕ\��
    $log.="Your HP:$pt_hp<br>";   # �퓬�O�̓G������
		  }		  # HP�MP��\��
    $j=0;				     # +a
    if($pt_cl =~ /A/){ $j = 33; }	     # ��è��˯Ă̐ݒ� A�̂Ƃ�33%
    elsif($pt_cl =~ /[NT]/){ $j = 20; }      # NT�̂Ƃ�20%
    elsif($pt_cl =~ /[FHLR]/){ $j = 5; }     # ��m�n��5%
    else{$j = 0; }			     # ���̑���0%
    $atp = $pt_atp-$adv_ap;
    if($t_weak == 1){		       # +a
    $atp0 = $atp;		       # �㉻�̐ݒ�
    $atp = 0;			       #
		    }		       #
    $atp = 0 if($atp<0);
    $mgp = $pt_mgp-$adv_rp;
    if($t_silent == 1){ 	       # +a
    $mgp0 = $mgp;		       # ���ق̐ݒ�
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
    if (rand(1)>$t_pow_1){	       # �㉻�̉���
    $log.="���U���߂���! ";	       #
    $atp = $atp0;		       #
    $t_weak = 0;		       #
				     } #
		    }		       #
    if($t_silent == 1){ 	       # +a
    if (rand(1)>$t_pow_2){	       # ���ق̉���
    $log.="���U���߂���! ";	       #
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
	    $dmg = $dmg+$k;	    # �퓬۸ޕ\��on�w��̎���
	    if($adv_lg==1){	    # ��������G�ւ�
	    $log.="\>\>$k\ ";	    # ���U��Ұ�ނ� >>n �ŕ\��
			  }	    #
	}else{
    if(rand(100)<$j && $CR==1 && $t_weak ==0){		      # +a
	    $k=int($pt_atp*1.5)+int(rand(2)),$v=1;	      # ��è�ق͖h�䖳���~1.5
    }else{$k = $atp+int(rand(2)),$v=0;			      #
			      } 			      #
	    $dmg = $dmg+$k;				      # ��������G��
	    if($adv_lg==1){				      # ��è��˯Ă����܂����Ƃ��A
	    $log.="\>$k";				      # �퓬۸ޕ\��on�w��̎���
	    if($v == 1){$log.="!";}			      # ��Ұ�ނ� >n! �ŕ\��
	    $log.="\ "; 				      #
			  }				      #
	}
	$k = $atp_+$adv_mp+int(rand(2)); # +a
	$dmg_ = $dmg_+$k;		 # �퓬۸ޕ\��on�w��̎���
	    if($adv_lg==1){		 # �G���疡���ւ�
	    $log.="$k\<\ ";		 # ��Ұ�ނ� n< �ŕ\��
			  }		 #

	if($wb > 1){ $wb--; }
	elsif($wb == 1){
	    if($wn ne '���'){
		$log .= "$wn\����ꂽ!<br>\n";
		$wn = '���';
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
	    if($an ne '̸'){
		$log .= "$an\����ꂽ!<br>\n";
		$an = '̸';
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
	  $hp = int($pt_hp/3);	      # �m���Ȃ�����Ȃ�
	  $hp = 1 if($pt_hp<1);       # �ŏI�퓬�O��1/3��hp�Emp���c��
	  $mp = int($pt_mp/3);	      #
	  if($hp == 1 && $mp ==0){    #
	  if($adv_lg==1){ # +a
	  $log .="<hr>";  # �퓬۸ޕ\��
			} #
	  $log .="$msg_lose";
	  }else{						  #
	  $log .="<hr>�͐s�������A���Ȃ�͂ŏ����񕜂������<br>"; #
	       }						  #
	}elsif($pt_cl =~ /[CPBH]/ && $RE == 1){ 		  #
	  $hp = int($pt_hp/4);	      # �m�����߰è��ɂ���ΐ����Ȃ�
	  $hp = 1 if($pt_hp<1);       # �ŏI�퓬�O��1/4��hp�Emp���c��
	  $mp = int($pt_mp/4);	      #
	  if($hp == 1 && $mp ==0){    #
	  if($adv_lg==1){ # +a
	  $log .="<hr>";  # �퓬۸ޕ\��
			} #
	  $log .="$msg_lose";
	  }else{							  #
	  $log .="<hr>�͐s�������A���Ȃ�͂ŏ����񕜂��Ă���������<br>"; #
	       }							  #
	}else{
	  if($adv_lg==1){ # +a
	  $log .="<hr>";  # �퓬۸ޕ\��
			} #
	  $log .="$msg_lose";
	  $hp = 1;
	  $mp = 0;
				  }
	    last;
	}elsif($dmg>=$adv_hp){
	    if($adv_lg==1){ # +a
	    $log .="<hr>";  # �퓬۸ޕ\��
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
 if($adv_un != 0 && $adv_lg != 0){$log .="$adv_un\+\ ";} # +a # �퓬۸ޕ\��on�̂Ƃ�
	$dmg = 0 if($dmg<0);				 # �G���ޯ�ނ̉񕜂� n+ �ŕ\��
    }
    if($adv_lt == 0){
	if($adv_lg==1){ # +a
	$log .="<hr>";	# �퓬۸ޕ\��
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
	$log .= "$ex_"."Exp��ɓ��ꂽ�B<br>\n";
	$ex += $ex_;
	if($ex >= $lv*$lv*10){
	    $log .= "���ق��オ����!<br>\n";
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
	    $log_ = "- �ǂ��ŋx�݂܂���? -<br>\n";
	    $st = 1;
	}elsif($DAT{'cmd'} == 2){
	    $log_ = "- �ǂ��֍s���܂���? -<br>\n";
	    $st = 2;
	}elsif($DAT{'cmd'} == 3){
	    $log_ = "- �ǂ�������󂯂܂���? -<br>\n";
	    $st = 3;
	}elsif($DAT{'cmd'} == 4){
	    $log_ = "�u$shp_welcome\�v<br>\n";
	    $st = 4;
	}elsif($DAT{'cmd'} == 5){
	    $log_ = "- �ǂ��֍s���܂���? -<br>\n";
	    $st = 5;
	}
    }elsif($st == 1){
	$v = $DAT{'cmd'};
	$v = 0 if($v<0 || $v>$#rst_lst || $v>9);
	$log_ = $rst_msg[$v]."<br>\n";
	$st = 10+$v;
	$nx = $time+60*60;
    }elsif($st == 2){
#	for($i=0;$i<=$#adv_lst;$i++){			    #uni���ɂ��듮��΍�
#	    last if($DAT{'cmd'} eq $adv_lst[$i]);	    #
#	}						    #
#	if($i <= $#adv_lst){				    #
       $i = $DAT{'cmd'};				    #
       if($DAT{'st'} == $st && 0 <= $i && $i <= $#adv_lst){ #
	    $v = $adv_t[$i];
	    $v = 1 if($v<1);
	    $log_ = "�ړI�n:$adv_lst[$i]<br>���v����:$v<br>�߰è��l��:$adv_n[$i]<hr>- �o�����܂���? -<br>\n";
	    $st = 25;
	    $op = $i;
	}else{
	    $log_ = "�������܂��������B<br>\n";
	    $st = 0;
	}
    }elsif($st == 3){
#	for($i=0;$i<=$#wrk_lst;$i++){			     #uni���ɂ��듮��΍�
#	    last if($DAT{'cmd'} eq $wrk_lst[$i]);	     #
#	}						     #
#	if($i <= $#wrk_lst){				     #
       $i = $DAT{'cmd'};				     #
       if($DAT{'st'} == $st && 0 <= $i && $i <= $#wrk_lst){  #
	    $v = $wrk_t[$i];
	    $v = 1 if($v<1);
	    $log_ = "�˗����e:$wrk_lst[$i]<br>���v����:$v<br>�߰è��l��:$wrk_n[$i]<hr>- �����󂯂܂���? -<br>\n";
	    $st = 35;
	    $op = $i;
	}else{
	    $log_ = "����ς��߂��B<br>\n";
	    $st = 0;
	}
    }elsif($st == 4){
	if($DAT{'cmd'} == 1){
	    $log_ = "�u$shp_mihy\�v<br>\n";
	    $st = 40;
	}elsif($DAT{'cmd'} == 2){
	    $log_ = "�u$shp_mihy\�v<br>\n";
	    $st = 41;
	}elsif($DAT{'cmd'} == 3){
	    $log_ = "�u$shp_mihy\�v<br>\n";
	    $st = 42;
	}elsif($DAT{'cmd'} == 4){
	    $log_ = "�u$shp_which\�v<br>\n";
	    $st = 43;
	}else{
	    $log_ = "�u$shp_thanks\�v<br>\n";
	    $st = 0;
	}
    }elsif($st == 5){
#	 for($i=0;$i<=$#twn_lst;$i++){			      #uni���ɂ��듮��΍�
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
		$log_ = "$key\�܂ł�$v"."���Ԃقǂ̓��̂肾�B<br>\n";
		$st = 50;
		$op = $i;
	    }else{
		$log_ = "������$key\���B<br>\n";
		$st = 0;
	    }
	}else{
	    $log_ = "�������܂��������B<br>\n";
	    $st = 0;
	}
    }elsif($st == 21){
	($key,$v,$i,$j) = split(/\//,$op);
	if($DAT{'cmd'} == 0){
	    $log_ = "$v\��������߂�<br>\n";
	}else{
	    $log_ = "$v\�𑕔�����!<br>\n";
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
	    $log_ .= "- �׽��ݼ�! -<br>\n";
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
	    $log_ = "$item_lst[$i]\���̂Ă�$v\����ɓ��ꂽ!<br>\n";
	    $item_lst[$i] = $v;
	    $it = join('/',@item_lst);
	}else{
	    $log_ = "$v\��������߂�<br>\n";
	}
	if($lv == 10 && $cl < 4){
	    $log_ .= "- �׽��ݼ�! -<br>\n";
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
	    $log_ = "$cl_nm[$cl]�ɂȂ���!<br>\n";
	    $st = 0;
	}else{
	    $log_ .= "- �׽��ݼ�! -<br>\n";
	}
    }elsif($st == 25){
	if($DAT{'cmd'} == 0 || $op > $#adv_lst){
	    $log_ = "- �ǂ��֍s���܂���? -<br>\n";
	    $st = 2;
	    $op = '';
	}else{
	    $log_ = "�o��!<br>\n";
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
	    $log_ = "- �ǂ�������󂯂܂���? -<br>\n";
	    $st = 3;
	    $op = '';
	}else{
	    $log_ = "�d���J�n!<br>\n";
	    $i = int($op);
	    $v = $wrk_t[$i];
	    $v = 1 if($v<1);
	    $st = 30;
	    $op = $wrk_lst[$i];
	    $nx = $time + $v*60*60;
	    &update_party($op,$wrk_n[$i]);
	}
    }elsif($st == 40){
#	 for($i=0;$i<=$#shp_wn;$i++){			     #uni���ɂ��듮��΍�
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
	    $log_ = "�u$key\[$shp_wp[$i]x$shp_wb[$i]\]��$shp_wmsg[$i]<br>\n$v"."Gp$shp_ok\�v<br>\n";
	    $st = 44;
	    $op = "w/$key/$v";
	}else{
	    $log_ = "�u$shp_other\�v<br>\n";
	    $st = 4;
	}
    }elsif($st == 41){
#	 for($i=0;$i<=$#shp_an;$i++){			     #uni���ɂ��듮��΍�
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
	    $log_ = "�u$key\[$shp_ap[$i]x$shp_ab[$i]\]��$shp_amsg[$i]<br>\n$v"."Gp$shp_ok\�v<br>\n";
	    $st = 44;
	    $op = "a/$key/$v";
	}else{
	    $log_ = "�u$shp_other\�v<br>\n";
	    $st = 4;
	}
    }elsif($st == 42){
#	 $i = &search_item($DAT{'cmd'});	     #uni���ɂ��듮��΍�
	 $key = $DAT{'cmd'};			     #
	if($DAT{'st'} == $st && $key ne '-1'){	     #
	    $key =~ s/(..)/sprintf('%c',hex($1))/ge; #
	    $i = &search_item($key);		     #
	}else{					     #
	    $i = -1;				     #
	}					     #
	if($i<0){
	    $log_ = "�u$shp_other\�v<br>\n";
	    $st = 4;
	}else{
	    $v = &item_value($item_n);
	    $log_ = "�u$item_nm\��$v"."Gp$shp_ok\�v<br>\n";
	    $st = 44;
	    $op = "i/$item_nm/$v";
	}
    }elsif($st == 43){
	@item_lst = split(/\//,$it);
#	 for($i=0;$i<=$#item_lst;$i++){ 		       #uni���ɂ��듮��΍�
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
	    $log_ = "�u$key\��$v"."Gp$shp_ok\�v<br>\n";
	    $st = 45;
	    $op = "i/$key/$v";
	}else{
	    $log_ = "�u$shp_other\�v<br>\n";
	    $st = 4;
	}
    }elsif($st == 44){
	if($DAT{'cmd'} == 0){
	    $log_ = "�u$shp_other\�v<br>\n";
	}else{
	    $log_ = &buy_item;
	}
	$st = 4;
	$op = '';
    }elsif($st == 45){
	if($DAT{'cmd'} == 0){
	    $log_ = "�u$shp_other\�v<br>\n";
	}else{
	    $log_ = &sell_item;
	}
	$st = 4;
	$op = '';
    }elsif($st == 50){
	$log_ = "- �ǂ��֍s���܂���? -<br>\n";
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
	    next if($t < $nx-5*60); # +a �����\����10��
	    $nx = $t;
	    $pt = $v;
	    $pt =~ s/[\r\n]//g;
	    last;
	}
    }
$flg=0; 			# +a
for(0..$#gm_name){		# ���޸޷�ו����ݒ�
if($nm eq $gm_name[$_]){$flg=1} #
		 }		#
    if($i<=$#gdat && ($flg != 1)){
	($pt_n,$pt_cl,$pt_hp,$pt_mp,$pt_atp,$pt_mgp,$pt_dfp,$pt_it,$pt_mem) = split(/\//,$pt,9);
	$log .= "$pt_mem\���߰è��ɉ������!<br>\n";
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
for(0..$#gm_name){		# ���޸޷�ו����ݒ�
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
	    $lg .= "$nm_\���߰è��ɉ������!<br>";
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
	$log_ = "�u$shp_nomoney\�v<br>\n";
    }else{
	if($i eq 'w'){
	    for($i=0;$i<=$#shp_wn;$i++){ last if($key eq $shp_wn[$i]); }
	    if($i<=$#shp_wn){
		$log_ = "�u$shp_thanks\�v<br>\n";
		$wn = $key;
		$gp -= $v;
		$wp = $shp_wp[$i];
		$wb = $shp_wb[$i];
	    }else{
		$log_ = "�u$shp_soldout\�v<br>\n";
	    }
	}elsif($i eq 'a'){
	    for($i=0;$i<=$#shp_an;$i++){ last if($key eq $shp_an[$i]); }
	    if($i<=$#shp_an){
		$log_ = "�u$shp_thanks\�v<br>\n";
		$an = $key;
		$gp -= $v;
		$ap = $shp_ap[$i];
		$ab = $shp_ab[$i];
	    }else{
		$log_ = "�u$shp_soldout\�v<br>\n";
	    }
	}else{
	    @item_lst = split(/\//,$it);
	    if($#item_lst < 2){
		$i = &search_item($key);
		if($i<0){
		    $log_ = "�u$shp_soldout\�v<br>\n";
		}else{
		    $log_ = "�u$shp_thanks\�v<br>\n";
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
		$log_ .= "�u$shp_over\�v<br>\n";
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
	$log_ = "�u$shp_thanks\�v<br>\n";
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
	$log_ = "�u$shp_noitem\�v<br>\n";
    }
    $log_;
}

sub print_status{
    $v = int($time/(6*60*60));
    srand($v);
    $v=$nx-$time;		       # +a
    $i=int($v/60);		       # ���̉񕜂܂ł̎��Ԃ�\��
    $v=$v-$i*60;   #		       #
    if($i==0 && $v==0){ 	       #
    $v="";			       #
		      }else{	       #
    $v="<br>���̉񕜂܂�<br>$i��$v�b"; #
			   }	       #
    $log .= "- �x���� -$v<hr>\n" if($st >= 10 && $st <= 19);


    $log .= "���O:$nm<br>�׽:$cl_nm[$cl]\[Lv$lv\]<br>Exp:$ex<br>Gp:$gp<br>Hp:$hp/$mhp<br>Mp:$mp/$mmp<br>$wn\[$wp".'x'."$wb\]<br>$an\[$ap".'x'."$ab\]<br>$it<br>\n"; # +a ���ѕ\��
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
	$log .= "�����<select name=cmd size=1>\n";
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
#	     $log .= "<option>��߂�</option>\n";	      #uni���ɂ��듮��΍�
	    $log .= "<option value=\"-1\">��߂�</option>\n"; #
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
#		$log .= " value=\"$key\"" if($method eq 'GET'); #uni���ɂ��듮��΍�
		$key_e = $key;					#
		$key_e =~ s/(.)/ sprintf('%02x',ord($1)) /ge;	#
		$log .= " value=\"$key_e\"";			#
		$log .= ">$key</option>\n";
	    }
	}elsif($st == 22 || $st == 43){
#	    $log .= "<option>��߂�</option>\n";		#uni���ɂ��듮��΍�
	    $log .= "<option value=\"-1\">��߂�</option>\n";	#
	    @item_lst = split(/\//,$it);
	    for($i=0;$i<=$#item_lst;$i++){
		$log .= "<option";
#		$log .= " value=\"$item_lst[$i]\"" if($method eq 'GET'); #uni���ɂ��듮��΍�
		$log .= " value=\"$i\"";				 #
		$log .= ">$item_lst[$i]</option>\n";
	    }
	}elsif($st == 23){
	    if($cl == 0){ $log .= "<option value=0>$cl_nm[4]</option><option value=1>$cl_nm[8]</option><option value=2>$cl_nm[10]</option>\n"; }
	    elsif($cl == 1){ $log .= "<option value=0>$cl_nm[5]</option><option value=1>$cl_nm[8]</option><option value=2>$cl_nm[9]</option>\n"; }
	    elsif($cl == 2){ $log .= "<option value=0>$cl_nm[6]</option><option value=1>$cl_nm[10]</option><option value=2>$cl_nm[9]</option>\n"; }
	    elsif($cl == 3){ $log .= "<option value=0>$cl_nm[7]</option><option value=1>$cl_nm[11]</option>\n"; }
	}elsif($st == 21 || $st == 25 || $st == 35 || $st == 44 || $st == 45){
	    $log .= "<option value=0>���ł�</option><option value=1>����</option>\n";
	}else{
	    $log .= "<option value=0>�m�F</option>\n";
	}
	$log .= "</select><br>\n";
	$log .= "<input type=\"hidden\" name=\"st\" value=\"$st\">"; #uni���ɂ��듮��΍�
	$log .= "<input type=submit value=OK><br></form>\n";
    }
    $nm_e = &escape_code($nm);
    $pw_e = &escape_code($pw);
    $log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e\">����</a><br>\n";
    $log .= "<a href=\"yk_bbs.cgi?nm=$nm_e&pw=$pw_e&n=1\">�f����</a><br>\n";
    $log .= "<a href=\"yk_msg.cgi?nm=$nm_e&pw=$pw_e\">�`��</a><br>\n";
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
#   $log .= "<option>��߂�</option>\n";	      #uni���ɂ��듮��΍�
    $log .= "<option value=\"-1\">��߂�</option>\n"; #
    for($i=0;$i<=$#lst;$i++){
	$log .= "<option";
#	$log .= " value=\"$lst[$i]\"" if($method eq 'GET'); #uni���ɂ��듮��΍�
	$log .= " value=\"$i\"";			    #
	$log .= ">$lst[$i]</option>\n";
    }
}
