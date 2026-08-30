const DESTINATIONS_DATA = [
  {
    group: "北海道",
    options: [
      { value: "新千歳", en: "NEW CHITOSE", lat: "42.775", lon: "141.692", code: "CTS" },
      { value: "函館", en: "HAKODATE", lat: "41.770", lon: "140.822", code: "HKD" },
      { value: "旭川", en: "ASAHIKAWA", lat: "43.670", lon: "142.448", code: "AKJ" },
      { value: "釧路", en: "KUSHIRO", lat: "43.041", lon: "144.180", code: "KUH" },
      { value: "女満別", en: "MEMANBETSU", lat: "43.880", lon: "144.164", code: "MMB" },
      { value: "帯広", en: "OBIHIRO", lat: "42.735", lon: "143.213", code: "OBO" },
      { value: "稚内", en: "WAKKANAI", lat: "45.405", lon: "141.802", code: "WKJ" },
      { value: "中標津", en: "NAKASHIBETSU", lat: "43.577", lon: "144.965", code: "SHB" },
      { value: "奥尻", en: "OKUSHIRI", lat: "42.072", lon: "139.431", code: "OIR" },
      { value: "利尻", en: "RISHIRI", lat: "45.406", lon: "141.183", code: "RIS" },
      { value: "丘珠", en: "OKADAMA", lat: "43.116", lon: "141.378", code: "OKD" }
    ]
  },
  {
    group: "東北",
    options: [
      { value: "青森", en: "AOMORI", lat: "40.725", lon: "140.690", code: "AOJ" },
      { value: "三沢", en: "MISAWA", lat: "40.704", lon: "141.369", code: "MSJ" },
      { value: "花巻", en: "HANAMAKI", lat: "39.431", lon: "141.130", code: "HNA" },
      { value: "仙台", en: "SENDAI", lat: "38.139", lon: "140.917", code: "SDJ" },
      { value: "山形", en: "YAMAGATA", lat: "38.411", lon: "140.372", code: "GAJ" },
      { value: "庄内", en: "SHONAI", lat: "38.811", lon: "139.789", code: "SYO" },
      { value: "秋田", en: "AKITA", lat: "39.615", lon: "140.218", code: "AXT" },
      { value: "大館能代", en: "ODATE NOSHIRO", lat: "40.187", lon: "140.375", code: "ONJ" },
      { value: "福島", en: "FUKUSHIMA", lat: "37.225", lon: "140.432", code: "FKS" }
    ]
  },
  {
    group: "関東・甲信越",
    options: [
      { value: "東京（羽田）", en: "TOKYO HANEDA", lat: "35.549", lon: "139.779", code: "HND", selected: true },
      { value: "東京（成田）", en: "TOKYO NARITA", lat: "35.771", lon: "140.392", code: "NRT" },
      { value: "茨城", en: "IBARAKI", lat: "36.182", lon: "140.414", code: "IBR" },
      { value: "新潟", en: "NIIGATA", lat: "37.956", lon: "139.117", code: "KIJ" },
      { value: "松本", en: "MATSUMOTO", lat: "36.165", lon: "137.922", code: "MMJ" },
      { value: "佐渡", en: "SADO", lat: "38.069", lon: "138.406", code: "SDS" }
    ]
  },
  {
    group: "中部・北陸",
    options: [
      { value: "名古屋（中部）", en: "CENTRAIR", lat: "34.858", lon: "136.805", code: "NGO" },
      { value: "名古屋（小牧）", en: "NAGOYA KOMAKI", lat: "35.255", lon: "136.923", code: "NKM" },
      { value: "静岡", en: "SHIZUOKA", lat: "34.796", lon: "138.190", code: "FSZ" },
      { value: "富山", en: "TOYAMA", lat: "36.648", lon: "137.187", code: "TOY" },
      { value: "小松", en: "KOMATSU", lat: "36.393", lon: "136.407", code: "KMQ" },
      { value: "能登", en: "NOTO", lat: "37.294", lon: "136.963", code: "NTQ" },
      { value: "福井", en: "FUKUI", lat: "36.142", lon: "136.222", code: "FKJ" }
    ]
  },
  {
    group: "関西",
    options: [
      { value: "大阪（伊丹）", en: "OSAKA ITAMI", lat: "34.785", lon: "135.438", code: "ITM" },
      { value: "大阪（関西）", en: "KANSAI", lat: "34.434", lon: "135.244", code: "KIX" },
      { value: "神戸", en: "KOBE", lat: "34.632", lon: "135.224", code: "UKB" },
      { value: "南紀白浜", en: "NANKI SHIRAHAMA", lat: "33.664", lon: "135.362", code: "SHM" },
      { value: "コウノトリ但馬", en: "TAJIMA", lat: "35.509", lon: "134.787", code: "TJH" }
    ]
  },
  {
    group: "中国・四国",
    options: [
      { value: "広島", en: "HIROSHIMA", lat: "34.436", lon: "132.919", code: "HIJ" },
      { value: "岡山", en: "OKAYAMA", lat: "34.757", lon: "133.855", code: "OKJ" },
      { value: "鳥取", en: "TOTTORI", lat: "35.515", lon: "134.164", code: "TTJ" },
      { value: "米子", en: "YONAGO", lat: "35.503", lon: "133.147", code: "YGJ" },
      { value: "出雲", en: "IZUMO", lat: "35.411", lon: "132.890", code: "IZO" },
      { value: "山口宇部", en: "YAMAGUCHI UBE", lat: "33.931", lon: "131.279", code: "UBJ" },
      { value: "岩国", en: "IWAKUNI", lat: "34.145", lon: "132.238", code: "IWK" },
      { value: "萩・石見", en: "HAGI IWAMI", lat: "34.680", lon: "131.783", code: "IWJ" },
      { value: "高松", en: "TAKAMATSU", lat: "34.214", lon: "134.012", code: "TAK" },
      { value: "松山", en: "MATSUYAMA", lat: "33.828", lon: "132.700", code: "MYJ" },
      { value: "高知", en: "KOCHI", lat: "33.546", lon: "133.674", code: "KCZ" },
      { value: "徳島", en: "TOKUSHIMA", lat: "34.296", lon: "134.609", code: "TKS" }
    ]
  },
  {
    group: "九州・沖縄",
    options: [
      { value: "福岡", en: "FUKUOKA", lat: "33.585", lon: "130.450", code: "FUK" },
      { value: "北九州", en: "KITAKYUSHU", lat: "33.845", lon: "131.034", code: "KKJ" },
      { value: "佐賀", en: "SAGA", lat: "33.151", lon: "130.303", code: "HSG" },
      { value: "長崎", en: "NAGASAKI", lat: "32.916", lon: "129.913", code: "NGS" },
      { value: "福江", en: "FUKUE", lat: "32.668", lon: "128.831", code: "FUJ" },
      { value: "対馬", en: "TSUSHIMA", lat: "34.283", lon: "129.325", code: "TSJ" },
      { value: "壱岐", en: "IKI", lat: "33.748", lon: "129.789", code: "IKI" },
      { value: "熊本", en: "KUMAMOTO", lat: "32.837", lon: "130.855", code: "KMJ" },
      { value: "大分", en: "OITA", lat: "33.479", lon: "131.737", code: "OIT" },
      { value: "宮崎", en: "MIYAZAKI", lat: "31.877", lon: "131.445", code: "KMI" },
      { value: "鹿児島", en: "KAGOSHIMA", lat: "31.801", lon: "130.719", code: "KOJ" },
      { value: "種子島", en: "TANEGASHIMA", lat: "30.601", lon: "130.985", code: "TGM" },
      { value: "屋久島", en: "YAKUSHIMA", lat: "30.387", lon: "130.658", code: "KUM" },
      { value: "奄美", en: "AMAMI", lat: "28.431", lon: "129.711", code: "ASJ" },
      { value: "喜界", en: "KIKAI", lat: "28.322", lon: "129.932", code: "KKX" },
      { value: "徳之島", en: "TOKUNOSHIMA", lat: "27.836", lon: "128.883", code: "TKN" },
      { value: "沖永良部", en: "OKINOERABU", lat: "27.429", lon: "128.707", code: "OKE" },
      { value: "与論", en: "YORON", lat: "27.045", lon: "128.411", code: "RNJ" },
      { value: "沖縄（那覇）", en: "OKINAWA", lat: "26.204", lon: "127.645", code: "OKA" },
      { value: "久米島", en: "KUMEJIMA", lat: "26.363", lon: "126.711", code: "UEO" },
      { value: "宮古", en: "MIYAKO", lat: "24.783", lon: "125.295", code: "MMY" },
      { value: "下地島", en: "SHIMOJISHIMA", lat: "24.827", lon: "125.145", code: "SHI" },
      { value: "石垣", en: "ISHIGAKI", lat: "24.401", lon: "124.243", code: "ISG" },
      { value: "与那国", en: "YONAGUNI", lat: "24.469", lon: "122.977", code: "OGN" }
    ]
  },
  {
    group: "海外（東アジア・東南アジア）",
    options: [
      { value: "ソウル（仁川）", en: "SEOUL INCHEON", lat: "37.469", lon: "126.451", code: "ICN" },
      { value: "ソウル（金浦）", en: "SEOUL GIMPO", lat: "37.558", lon: "126.790", code: "GMP" },
      { value: "釜山", en: "BUSAN", lat: "35.179", lon: "128.938", code: "PUS" },
      { value: "台北（桃園）", en: "TAIPEI TAOYUAN", lat: "25.079", lon: "121.234", code: "TPE" },
      { value: "台北（松山）", en: "TAIPEI SONGSHAN", lat: "25.069", lon: "121.552", code: "TSA" },
      { value: "高雄", en: "KAOHSIUNG", lat: "22.577", lon: "120.350", code: "KHH" },
      { value: "香港", en: "HONG KONG", lat: "22.308", lon: "113.914", code: "HKG" },
      { value: "上海（浦東）", en: "SHANGHAI PUDONG", lat: "31.144", lon: "121.808", code: "PVG" },
      { value: "上海（虹橋）", en: "SHANGHAI HONGQIAO", lat: "31.197", lon: "121.336", code: "SHA" },
      { value: "北京（首都）", en: "BEIJING CAPITAL", lat: "40.080", lon: "116.584", code: "PEK" },
      { value: "北京（大興）", en: "BEIJING DAXING", lat: "39.509", lon: "116.410", code: "PKX" },
      { value: "シンガポール", en: "SINGAPORE", lat: "1.364", lon: "103.991", code: "SIN" },
      { value: "バンコク", en: "BANGKOK", lat: "13.690", lon: "100.750", code: "BKK" },
      { value: "クアラルンプール", en: "KUALA LUMPUR", lat: "2.745", lon: "101.709", code: "KUL" },
      { value: "マニラ", en: "MANILA", lat: "14.508", lon: "121.019", code: "MNL" },
      { value: "ジャカルタ", en: "JAKARTA", lat: "-6.125", lon: "106.655", code: "CGK" },
      { value: "ホーチミン", en: "HO CHI MINH CITY", lat: "10.818", lon: "106.651", code: "SGN" },
      { value: "ハノイ", en: "HANOI", lat: "21.221", lon: "105.807", code: "HAN" }
    ]
  },
  {
    group: "海外（北米・ハワイ）",
    options: [
      { value: "ホノルル", en: "HONOLULU", lat: "21.318", lon: "-157.922", code: "HNL" },
      { value: "ロサンゼルス", en: "LOS ANGELES", lat: "33.942", lon: "-118.408", code: "LAX" },
      { value: "サンフランシスコ", en: "SAN FRANCISCO", lat: "37.621", lon: "-122.379", code: "SFO" },
      { value: "ニューヨーク", en: "NEW YORK JFK", lat: "40.641", lon: "-73.778", code: "JFK" },
      { value: "シカゴ", en: "CHICAGO", lat: "41.974", lon: "-87.907", code: "ORD" },
      { value: "シアトル", en: "SEATTLE", lat: "47.450", lon: "-122.308", code: "SEA" },
      { value: "バンクーバー", en: "VANCOUVER", lat: "49.196", lon: "-123.181", code: "YVR" }
    ]
  },
  {
    group: "海外（欧州・中東・オセアニア）",
    options: [
      { value: "ロンドン", en: "LONDON HEATHROW", lat: "51.470", lon: "-0.454", code: "LHR" },
      { value: "パリ", en: "PARIS CHARLES DE GAULLE", lat: "49.009", lon: "2.547", code: "CDG" },
      { value: "フランクフルト", en: "FRANKFURT", lat: "50.033", lon: "8.570", code: "FRA" },
      { value: "ヘルシンキ", en: "HELSINKI", lat: "60.317", lon: "24.963", code: "HEL" },
      { value: "ドバイ", en: "DUBAI", lat: "25.253", lon: "55.365", code: "DXB" },
      { value: "ドーハ", en: "DOHA", lat: "25.273", lon: "51.608", code: "DOH" },
      { value: "シドニー", en: "SYDNEY", lat: "-33.946", lon: "151.177", code: "SYD" },
      { value: "メルボルン", en: "MELBOURNE", lat: "-37.673", lon: "144.843", code: "MEL" }
    ]
  }
];
