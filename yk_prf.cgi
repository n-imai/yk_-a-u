#! /usr/local/bin/perl
#
# 雪色のｶﾚｲﾄﾞｽｺｰﾌﾟ by b-Yak-38
#

$topfile = './index.html'; # トップページ
$datfile = './yk_dat.cgi'; # データファイル
$gdatfile = './yk_gdat.cgi'; # グローバルデータファイル
$advfile = './yk_adv.cgi'; # ADVスクリプトファイル
$bbsfile = './yk_bbs0.log'; # BBSログファイル
$autofile = './yk_auto.cgi'; # AUTOメッセージファイル
$lckfile = '../lck/yk_.lck'; # ロックファイル # +a
$ipath = '/ic'; # imode絵文字変換用画像格納ディレクトリー

$bgcolor = "#ffffff"; # バックグラウンドカラー
$htmlcolor = "<body bgcolor=\"$bgcolor\">\n";
$maxln = 128; # BBS最大保存行数
$auto_rate = 1; # AUTOメッセージ出現率
$max_entry = 100; # 最大登録可能人数
@gm_name = (		 # デバグ用キャラクター名
	     '',	 # +a
	     '',	 # 複数設定可能
	   );		 #
			 # +a
$CR = 1;		 # ｸﾘﾃｨｶﾙﾋｯﾄのon(1)･off(0)
$RE = 1;		 # 敗北時回復のon(1)･off(0)
			 # 盗賊系・僧侶系の強化のための機能。必要を感じなければoffにすれば良い。
#-------- コマンド関連 --------

# 冒険リスト
@adv_lst = ('ｺﾞﾌﾞﾘﾝの洞窟','西風の谷','地下共同墓地','廃村の怪奇');
@adv_t = (6,6,6,6); # 所用時間
@adv_n = (6,6,6,8); # 最大パーティー人数

# 依頼リスト
@wrk_lst = ('鉄鉱石採掘','聖水作成','呪文書写本','雑貨屋のﾊﾞｰｹﾞﾝ','一攫千金！');
@wrk_t = (8,8,8,8,8); # 所用時間
@wrk_n = (1,1,1,1,1); # 最大パーティー人数

# 移動リスト
@twn_lst = (''); # +a
@twn_t = (0); # 所用時間
@twn_url = ('http://bya.lib.net/yk_/');
$my_url = 'http://bya.lib.net/yk_/'; # 自サーバーURL

#-------- 休息関連 --------

# 時間当たりの回復量は宿屋を1とすると2,3…倍となっていく。
# 野宿ではほとんど回復しない。

@rst_lst = ('野宿','宿屋','病院');
@rst_gp = (0,1,10);
@rst_msg = (
    '野宿することにした…',
    '「いらっしゃいませ。宿代は1時間1Gpとなっております」',
    '「当ｸﾘﾆｯｸへようこそ。ご宿泊は1時間10Gpでございます」');

#-------- 道具屋関連 --------

# 名称に","と"/"は使用不可。
# 武器、防具ともそれぞれ9種類まで。

# 武器
@shp_wn = ('ﾀﾞｶﾞｰ','ｼｮｰﾄｿｰﾄﾞ','ﾛﾝｸﾞｿｰﾄﾞ','ﾌﾞﾛｰﾄﾞｿｰﾄﾞ','ﾊﾞｽﾀｰﾄﾞｿｰﾄﾞ'); # 名称
@shp_wg = (10,50,100,200,500); # 値段
@shp_wp = (1,2,3,4,5); # 攻撃力
@shp_wb = (20,20,20,20,20); # 耐久力
@shp_wmsg = (
	'短剣でーす。非力ですが使い勝手はまずまずでーす。',
	'小剣でーす。それほど重くもなく剣の修行に最適でーす。',
	'長剣でーす。一般的な剣で最も多用されていまーす。',
	'幅広剣でーす。破壊力はありますが、重いのが欠点でーす。',
	'片手半剣でーす。両手でも片手でも使え、状況に合わせた使い方ができまーす。'); # 説明

# 防具
@shp_an = ('ﾛｰﾌﾞ','ﾚｻﾞｰﾀﾞﾌﾞﾚｯﾄ','ﾚｻﾞｰﾒｲﾙ','ﾌﾞﾚｽﾄﾌﾟﾚｰﾄ','ﾁｪｲﾝﾒｲﾙ'); # 名称
@shp_ag = (10,50,100,200,500); # 値段
@shp_ap = (1,2,3,4,5); # 防御力
@shp_ab = (10,20,30,40,30); # 耐久力
@shp_amsg = (
	'魔法使い向けのﾛｰﾌﾞでーす。防御力はほとんどありませーん。',
	'革のｼﾞｬｹｯﾄでーす。ちょっとした攻撃なら防げまーす。',
	'革の鎧でーす。一般的な戦士の鎧でーす。',
	'鉄の胸当てでーす。鉄の鎧にしては動きやすいのが利点でーす。',
	'鎖鎧でーす。かなりの攻撃を防いでくれますが、騒音と動きにくさが欠点でーす。'); # 説明

$shp_welcome = 'いらっしゃいませー。ご用件はなんでしょーかー？';
$shp_mihy = 'どれをご覧になりますかー？';
$shp_which = 'どれを見せて頂けるのでしょーかー？';
$shp_thanks = 'ありがとーございましたー';
$shp_ok = 'となりまーす。こちらでよろしいですかー？'; # 「…は…Gp」に続く
$shp_other = '他のものはいかがでしょー？';
$shp_nomoney = 'お金が足りないよーですがー？';
$shp_soldout = 'たった今売りきれてしまいましたー';
$shp_over = 'ｱｲﾃﾑは3つまでしか持てませーん';
$shp_noitem = '品物がないよーですがー？';

#-------- キャラクター転送関連 --------

# サーバー間の移動を可能にするには、自分のアクセスコードを設定し、
# それを接続したいサーバーのCGIの管理者に伝える。
# 相手のアクセスコードとIPアドレスを教えてもらい、%server_listに
#  ,'access-code','IP-address'
# の順に追加する。
# 同様に@url_listに
#  ,'URL'
# を追加する。
# アクセスコードは不正アクセスを防止するためのコードなので、
# いいかげんな（わかりやすい）文字列を設定してはならない。

$bakfile = './yk_bak.cgi'; # バックアップファイル

# 自サーバーの通信許可コード
$my_accesscode =  'DefaultAccessCode';

# 通信許可サーバーコード及びIPアドレスリスト
%server_list = (
    'DefaultAccessCode', '210.189.72.59'
);

# 通信許可サーバーURLリスト
@url_list = (
    'http://bya.lib.net/yk_/'
);

#-------- IPアドレス隠蔽用エンコードルーチン --------

sub encode_adr{
    local($ad) = @_;
    local($key,$v,@dt);

    $ad =~ s/(\d+)\.(\d+)\.(\d+)\.(\d+)$//;
    $ad = $1*256*256*256+$2*256*256+$3*256+$4;
    for(0..5){					  # +a
    $dt[$_] = int($ad/(52**(5-$_)));		  # 隠蔽ｺｰﾄﾞの
    $ad = $ad-int($ad/(52**(5-$_)))*(52**(5-$_)); # ｹﾀ下げのため
    if ($dt[$_]>=0 && $dt[$_]<26){		  # 英字に変換。
    $v = 65+$dt[$_];				  #
    $dt[$_] = chr($v);				  #
    }elsif($dt[$_]>=26 && $dt[$_]<52){		  #
    $v = 71+$dt[$_];				  #
    $dt[$_] = chr($v);				  #
    }else{					  #
    $dt[$_] = '';				  #
    }						  #
	     }					  #
    $ad = join('',@dt); 			  #
    $ad;
}
