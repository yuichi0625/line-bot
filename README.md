# LINE Bot（集合場所くん）
集合場所となる駅を提案してくれるLINE Botです。  
コロナ禍の運動不足対策に、少人数で集まって散歩しよう、という思いで作成しました。

## 目次
- [準備](#準備)
    - [データの取得](#データの取得)
    - [LINE DevelopersとHerokuの登録・設定](#LINE-DevelopersとHerokuの登録・設定)
    - [データをHeroku Postgresに投入](#データをHeroku-Postgresに投入)
- [使い方](#使い方)
    - [路線一覧の表示](#路線一覧の表示)
    - [駅のランダム選択](#駅のランダム選択)
    - [中間地点の取得](#中間地点の取得)
- [TODO](#TODO)

## 準備
### データの取得
路線・駅のデータは[駅データ.jp](http://www.ekidata.jp/)からダウンロードします。  
`データダウンロード`から以下のデータをダウンロードしてください。  
- 都道府県データ：e.g. `pref.csv`
- 路線データ：e.g. `line20200619free.csv`
- 駅データ： e.g. `station20200619free.csv`

### LINE DevelopersとHerokuの登録・設定
以下のサイトを参考に行います。
- [Python + HerokuでLINE BOTを作ってみた](https://qiita.com/shimajiri/items/cf7ccf69d184fdb2fb26)
- [HerokuにRailsアプリをデプロイする手順](https://qiita.com/NaokiIshimura/items/eee473675d624a17310f)
- [PythonでLine botを作ってみた](https://qiita.com/kro/items/67f7510b36945eb9689b)
- [Heroku操作 CLI](https://qiita.com/ntkgcj/items/9e812220881d671b6bff)

### データをHeroku Postgresに投入
1. Heroku add-onsのHeroku Postgresをインストールします。  
    （参照）[Herokuのアドオン「Heroku Postgres」を使ってみる](https://kin29.info/heroku%E3%81%AE%E3%82%A2%E3%83%89%E3%82%AA%E3%83%B3%E3%80%8Cheroku-postgres%E3%80%8D%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E3%81%BF%E3%82%8B/)

1. `tools`配下に、`データの取得`で取得した3つの駅データを置きます。

1. 下記コマンドでcsvファイルをsqlファイルに変換します。  
    引数の日付は、ダウンロードしたcsvファイルに合わせてください。
    ```
    python convert_csv2sql.py -c 20200619
    ```

1. Heroku Postgresにログインして、テーブル作成 -> データ読み込みをします。  
    （参照）[Heroku PostgresにSQLファイルを読み込ます](https://rowingfan.hatenablog.jp/entry/2018/09/10/174500)  
    ※WindowsではUTF-8が読み込めませんでした。WSLで行ってください。
    ```
    # sqlファイルがあるディレクトリに移動
    cd tools

    # postgresqlをインストール
    sudo apt-get install postgresql

    # Heroku Postgresにログイン
    heroku pg:psql

    # stationsテーブルを作成
    \i create_table.sql

    # stationsテーブルに先ほどのデータを挿入
    \i insert_into_stations.sql

    # データが無事挿入されたか確認
    select * from stations where pref_name = '東京都';

    # Heroku Postgresからログアウト
    \q
    ```

## 使い方
カルーセルテンプレートを使っているため、パソコンのLINEでは表示できません。  
スマートフォンのLINEアプリを使用してください。

まず、`集合場所`と入力すると、項目の一覧が表示されます。  
![0](images/0.jpg)

### 路線一覧の表示
1. カルーセル一番左`路線一覧`の`都道府県を入力`を押します。  
![1](images/1.jpg)

1. 都道府県名を入力すると、その都道府県にある路線の一覧が表示されます。  
![2](images/2.jpg)

### 駅のランダム選択
1. カルーセル真ん中`駅名選択`の`都道府県／路線を入力`を押します。  
![3](images/3.jpg)

1. 都道府県名もしくは路線名を入力すると、そこに属する全駅名からランダムに一つを表示します。  
![4](images/4.jpg)

1. 路線名が重複する場合は、重複確認画面が出るので、意図した路線名を選択します。  
![5](images/5.jpg)

### 中間地点の取得
1. カルーセル一番右`中間地点`の`駅を入力`を押します。  
![6](images/6.jpg)

1. 駅名を複数入力すると、それらの中間地点にある駅を計算し、上位5つを表示します。  
![7](images/7.jpg)

1. 駅名が複数の都道府県に存在する場合は、重複確認画面が出るので、意図した都道府県名を選択します。  
![8](images/8.jpg)

## TODO
- 1人もしくは1グループでしか使えない。  
    （状態を1つしか保存していないため、複数で使うとおかしなことになります。）
