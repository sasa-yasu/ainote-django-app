import logging
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.db.models import Q
from user.models import Profile
from middleware.current_request import get_current_request
from AinoteProject.utils import crop_square_image, crop_16_9_image, get_mbti_compatibility, get_mbti_detail_url

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

class FindMe(models.Model):
    """Find-Me"""

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='findmes')

    ##### 基本情報 #####
    # 名前
    name = models.CharField('Name', max_length=100, null=True, blank=True)
    # 性別
    GENDER_CHOICES = [
        ('O', '🌈秘密🤫'),
        ('M', '👦男性👔'),
        ('F', '👧女性👠'),
    ]
    gender = models.CharField('Gender', max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    # アイコン画像＆背景画像
    images = models.ImageField('Images', upload_to='findme', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='findme', null=True, blank=True)
    #  生年月日
    default_year = timezone.now().year  # 当年を基準にして選択肢を作成
    years_choice = [(year, str(year)) for year in range(default_year - 130, default_year + 1)]  # 過去130年分の年をリストとして作成
    birth_year = models.PositiveIntegerField('Birthday(Y)', choices=years_choice, null=True, blank=True)  # 年を保存
    birth_month_day = models.DateField('Birth(M/D))', null=True, blank=True)  # 月日を保存、デフォルトは12月31日

    # 居住地(都道府県)
    PREFECTURE_CHOICES = [
        ('-', '-'),
        ('hokkaido', '❄️北海道🐄'),
        ('aomori', '🍎青森県🌊'),
        ('iwate', '⛰️岩手県🏞️'),
        ('miyagi', '🐟宮城県🏯'),
        ('akita', '🐶秋田県🌾'),
        ('yamagata', '🍒山形県🌸'),
        ('fukushima', '🏔️福島県🧴'),
        ('ibaraki', '🥬茨城県🏖️'),
        ('tochigi', '🍓栃木県🚗'),
        ('gunma', '♨️群馬県🐴'),
        ('saitama', '🌻埼玉県🚉'),
        ('chiba', '🐬千葉県🛫'),
        ('tokyo', '🗼東京都🎌'),
        ('kanagawa', '⚓神奈川県🏖️'),
        ('niigata', '🌾新潟県🎿'),
        ('toyama', '🏔️富山県🐟'),
        ('ishikawa', '🏯石川県🎨'),
        ('fukui', '🦖福井県🏞️'),
        ('yamanashi', '🍇山梨県🗻'),
        ('nagano', '❄️長野県🥢'),
        ('gifu', '🏯岐阜県🍡'),
        ('shizuoka', '🗻静岡県🐟'),
        ('aichi', '🚄愛知県🏯'),
        ('mie', '⛩️三重県🐚'),
        ('shiga', '🌊滋賀県🦢'),
        ('kyoto', '🎋京都府🏯'),
        ('osaka', '🍜大阪府🎭'),
        ('hyogo', '🦌兵庫県⛴️'),
        ('nara', '🦌奈良県🏺'),
        ('wakayama', '🍊和歌山県🐼'),
        ('tottori', '🐪鳥取県⛱️'),
        ('shimane', '🦀島根県🏮'),
        ('okayama', '🍑岡山県🏞️'),
        ('hiroshima', '🕊️広島県⛩️'),
        ('yamaguchi', '🐡山口県🏯'),
        ('tokushima', '🎵徳島県🌀'),
        ('kagawa', '🍜香川県🧂'),
        ('ehime', '🍊愛媛県⛴️'),
        ('kouchi', '🏞️高知県🐎'),
        ('fukuoka', '🍜福岡県🎉'),
        ('saga', '🛤️佐賀県🍵'),
        ('nagasaki', '⚓長崎県⛪'),
        ('kumamoto', '🐻熊本県🏯'),
        ('oita', '♨️大分県🐵'),
        ('miyazaki', '🌴宮崎県🐓'),
        ('kagoshima', '🌋鹿児島県🛳️'),
        ('okinawa', '🏖️沖縄県🥁'),
    ]
    living_pref = models.CharField('Living Pref.', max_length=10, choices=PREFECTURE_CHOICES, null=True, blank=True)
    # 居住地
    living_area = models.CharField('Living Area', max_length=255, null=True, blank=True)
    # MBTI
    mbti = models.CharField('MBTI Type', max_length=4, choices=Profile.MBTI_CHOICES, null=True, blank=True)
    mbti_name = models.CharField(max_length=100, null=True, blank=True)

    ##### 自己紹介 #####
    # 短い自己紹介文
    overview = models.CharField('Overview', max_length=255, null=True, blank=True)
    # 長文の自己紹介
    introduce = models.TextField('Introduce', null=True, blank=True)

    ##### 趣味・興味 #####
    # 趣味（例：映画鑑賞、読書、旅行、スポーツ、音楽など） 
    HOBBY_CHOICES = [
        ('music', '🎧音楽鑑賞🎶'),
        ('movie', '🎬映画鑑賞🍿'),
        ('travel', '✈️旅行🌍'),
        ('sports', '⚽スポーツ🏃'),
        ('reading', '📚読書📖'),
        ('cooking', '🍳料理🧂'),
    ]
    hobby_choice = MultiSelectField('Hobby Choice', max_length=200, choices=HOBBY_CHOICES, null=True, blank=True)
    hobby = models.TextField('Hobby', null=True, blank=True)
    # 好きな食べ物：共通の好みがあれば話題作りに使えます。
    FOOD_CHOICES = [
        ("japanese", "🍱和食🍚"),
        ("western", "🍔洋食🥩"),
        ("chinese", "🥡中華料理🥢"),
        ("korean", "🌶️韓国料理🥘"),
        ("italian", "🍝イタリアン🍕"),
        ("french", "🥖フレンチ🍷"),
        ("thai", "🍜タイ料理🌶️"),
        ("indian", "🍛インド料理🧄"),
        ("sweets", "🍰スイーツ🍩"),
        ("fastfood", "🍟ファストフード🍔"),
        ("healthy", "🥗健康志向料理🍵"),
        ("home", "🏠家庭料理🍳"),
        ("other", "❓その他🍽️"),
    ]
    food_choice = MultiSelectField('Food Choice', max_length=200, choices=FOOD_CHOICES, null=True, blank=True)
    food = models.TextField('Food', null=True, blank=True)
    # 好きな音楽：自分の好みを伝えることで、相性の良い相手を見つけやすくなります。
    MUSIC_CHOICES = [
        ('pop', '🎤ポップス🎶'),
        ('rock', '🎸ロック🤘'),
        ('jazz', '🎷ジャズ🕶️'),
        ('classical', '🎻クラシック🎼'),
        ('hiphop', '🧢ヒップホップ/ラップ🎧'),
        ('edm', '🎚️EDM/ダンス💃'),
        ('rnb', '🎙️R&B/ソウル❤️'),
        ('anime', '🌟アニメソング🎵'),
        ('game', '🎮ゲーム音楽🕹️'),
        ('kpop', '🇰🇷K-POP💫'),
        ('enka', '🌸演歌🎤'),
        ('idol', '💖アイドル🌟'),
        ('folk', '🪕フォーク/カントリー🎶'),
        ('metal', '🤘メタル/ハードロック🔥'),
        ('reggae', '🟰レゲエ🧘'),
        ('blues', '🎺ブルース💙'),
        ('world', '🌍ワールドミュージック🎶'),
        ('other', '❓その他🎼'),
    ]
    music_choice = MultiSelectField('Music Choice', max_length=200, choices=MUSIC_CHOICES, null=True, blank=True)
    music = models.TextField('Music', null=True, blank=True)
    # 好きな映画：自分の好みを伝えることで、相性の良い相手を見つけやすくなります。
    MOVIE_CHOICES = [
        ('action', '💥アクション🎯'),
        ('adventure', '🗺️アドベンチャー🧭'),
        ('comedy', '😂コメディ🎭'),
        ('drama', '🎬ドラマ🎟️'),
        ('romance', '❤️恋愛/ラブロマンス💌'),
        ('thriller', '😱スリラー/サスペンス🔪'),
        ('horror', '👻ホラー🧟'),
        ('mystery', '🕵️ミステリー🔍'),
        ('sci-fi', '🚀SF/サイエンスフィクション👽'),
        ('fantasy', '🧙ファンタジー🦄'),
        ('animation', '🎨アニメーション📽️'),
        ('documentary', '📚ドキュメンタリー🎞️'),
        ('musical', '🎤ミュージカル🎶'),
        ('history', '🏛️歴史📜'),
        ('biography', '👤伝記🖋️'),
        ('war', '⚔️戦争🪖'),
        ('crime', '🚓犯罪/クライム🕶️'),
        ('family', '👨‍👩‍👧‍👦ファミリー🧸'),
        ('superhero', '🦸ヒーロー/特撮⚡'),
        ('japanese', '🎌邦画🎥'),
        ('foreign', '🌍洋画🌐'),
        ('other', '❓その他🎬'),
    ]
    movie_choice = MultiSelectField('Movie Choice', max_length=200, choices=MOVIE_CHOICES, null=True, blank=True)
    movie = models.TextField('Movie', null=True, blank=True)
    # 好きな本：自分の好みを伝えることで、相性の良い相手を見つけやすくなります。
    BOOK_CHOICES = [
        ('novel', '📖小説📝'),
        ('mystery', '🕵️ミステリー🔍'),
        ('romance', '💘恋愛/ラブストーリー💌'),
        ('fantasy', '🧝ファンタジー🦄'),
        ('sci-fi', '👽SF/サイエンスフィクション🚀'),
        ('historical', '🏯歴史小説📜'),
        ('thriller', '🔪スリラー/サスペンス😱'),
        ('essay', '📝エッセイ📄'),
        ('poetry', '🖋️詩/短歌/俳句🌸'),
        ('nonfiction', '📚ノンフィクション📘'),
        ('biography', '👤伝記🖊️'),
        ('business', '💼ビジネス書📈'),
        ('selfhelp', '🌟自己啓発💪'),
        ('psychology', '🧠心理学🛋️'),
        ('philosophy', '🤔哲学/思想📚'),
        ('science', '🔬科学/理系⚛️'),
        ('religion', '🕊️宗教/精神世界🛐'),
        ('education', '🎓教育/子育て👶'),
        ('comic', '📙漫画😂'),
        ('lightnovel', '📘ライトノベル✨'),
        ('literature', '📝純文学🏛️'),
        ('classic', '🏺古典文学📖'),
        ('other', '❓その他📗'),
    ]
    book_choice = MultiSelectField('Book Choice', max_length=200, choices=BOOK_CHOICES, null=True, blank=True)
    book = models.TextField('Book', null=True, blank=True)

    ##### 性格や価値観 #####
    # 自分の性格タイプ（例：おおらか、真面目、社交的、落ち着いている、マイペースなど）
    PERSONALITY_TYPE_CHOICES = [
        ('easygoing', '🌿おおらか☀️'),
        ('serious', '📘真面目🧐'),
        ('sociable', '🤝社交的😄'),
        ('calm', '🧘‍♂️落ち着いている🌊'),
        ('my_pace', '🐢マイペース🚶‍♂️'),
        ('positive', '🌈ポジティブ💪'),
        ('sensitive', '🌸繊細💧'),
        ('energetic', '⚡元気・活発🏃‍♂️'),
        ('quiet', '🤫おとなしい🌙'),
        ('curious', '🔍好奇心旺盛🧠'),
        ('logical', '🧩論理的🧠'),
        ('emotional', '💖感情豊か😭'),
        ('cheerful', '😄明るい🌞'),
        ('friendly', '😊フレンドリー🤗'),
        ('ambitious', '🚀向上心がある🎯'),
        ('considerate', '🤝思いやりがある💐'),
        ('independent', '🦅自立している🧍‍♂️'),
        ('careful', '🔒慎重派🕵️‍♂️'),
        ('adaptable', '🌊柔軟に対応できる🔄'),
        ('leader', '👑リーダーシップがある🗣️'),
        ('listener', '👂聞き上手🤲'),
        ('other', '❓その他💭'),
    ]
    personality_type_choice = MultiSelectField('Favorite Type Choice', max_length=200, choices=PERSONALITY_TYPE_CHOICES, null=True, blank=True)
    personality_type = models.TextField('Favorite Type', null=True, blank=True)
    # 理想のデート：どんなデートが好きか、またはどんな相手と一緒に楽しみたいかを記載。
    FAVORITE_DATE_CHOICES = [
        ('cafe', '☕カフェでゆっくり話す🧁'),
        ('dinner', '🍷おしゃれなレストランでディナー🍽️'),
        ('movie', '🎬映画鑑賞デート🍿'),
        ('park', '🌳公園で散歩🚶‍♀️'),
        ('amusement_park', '🎡遊園地・テーマパーク🎢'),
        ('aquarium', '🐠水族館デート🐧'),
        ('zoo', '🦁動物園デート🐵'),
        ('museum', '🖼️美術館・博物館巡り🏛️'),
        ('shopping', '🛍️一緒にショッピング💳'),
        ('drive', '🚗ドライブデート🌆'),
        ('beach', '🏖️海辺でのんびり🌅'),
        ('picnic', '🧺自然の中でピクニック🌼'),
        ('hiking', '🥾ハイキング・登山⛰️'),
        ('festival', '🎆夏祭り・花火大会👘'),
        ('hot_spring', '♨️温泉旅行🏞️'),
        ('home_cooking', '🍳おうちで一緒に料理🥗'),
        ('game_night', '🎮おうちでゲーム・映画鑑賞📺'),
        ('sports', '🏀一緒にスポーツをする🏃‍♂️'),
        ('concert', '🎤ライブ・コンサート鑑賞🎶'),
        ('season_event', '🌸季節イベント（花見・紅葉など）🍁'),
        ('travel', '🧳日帰りor泊まり旅行✈️'),
        ('other', '❓その他💭'),
    ]
    favorite_date_choice = MultiSelectField('Favorite Date Choice', max_length=200, choices=FAVORITE_DATE_CHOICES, null=True, blank=True)
    favorite_date = models.TextField('Favorite Date', null=True, blank=True)
    # 重視する価値観（例：誠実、家族重視、成長志向、自由を大切にするなど）
    SENSE_OF_VALUES_CHOICES = [
        ('trust', '🤝信頼関係🔒'),
        ('honesty', '🕊️正直さ🪞'),
        ('communication', '🗣️しっかり話し合えること💬'),
        ('respect', '🙇‍♀️お互いを尊重すること🙇‍♂️'),
        ('humor', '😂ユーモア・笑いのセンス🤪'),
        ('affection', '💞愛情表現💋'),
        ('shared_values', '🧠価値観の一致❤️'),
        ('support', '🤗困った時に支え合えること🆘'),
        ('freedom', '🕊️お互いの自由を尊重すること🛫'),
        ('growth', '🌱一緒に成長できること📈'),
        ('passion', '🔥情熱・ドキドキ感❤️‍🔥'),
        ('reliability', '🛡️頼りがい🧍‍♂️'),
        ('stability', '⚖️安定感🧱'),
        ('romance', '🌹ロマンチックな関係🌙'),
        ('fun', '🎉一緒にいて楽しいこと🥳'),
        ('goals', '🎯将来の目標や夢の共有🚀'),
        ('family_mind', '🏡家庭的であること👨‍👩‍👧‍👦'),
        ('other', '❓その他💭'),
    ]
    sense_of_values_choice = MultiSelectField('Sense of Values Choice', max_length=200, choices=SENSE_OF_VALUES_CHOICES, null=True, blank=True)
    sense_of_values = models.TextField('Sense of Values', null=True, blank=True)

    ##### 目標・将来のビジョン #####
    # 今後のキャリアや人生でやりたいこと：将来のビジョンや計画について簡単に触れる。
    FUTURE_PLAN_CHOICES = [
        ('entrepreneur', '💼起業したい🚀'),
        ('career_up', '📈キャリアアップしたい🌟'),
        ('expert', '👨‍🔬専門分野で一流になりたい🎓'),
        ('side_job', '💻副業をしたい💡'),
        ('overseas', '🌍海外で働きたい・暮らしたい✈️'),
        ('creative', '🎨創作活動をしたい（音楽・アートなど）🎶'),
        ('freelance', '🖥️フリーランスで働きたい👩‍💻'),
        ('volunteer', '🤝社会貢献・ボランティア活動をしたい🌱'),
        ('family', '👨‍👩‍👧‍👦家庭を築きたい・子育てしたい🏡'),
        ('community', '🏘️地域活動に関わりたい🤝'),
        ('relaxed_life', '🌿のんびりとした生活を送りたい🌅'),
        ('financial_freedom', '💸経済的自由を得たい（脱サラなど）🏝️'),
        ('study', '📚もう一度勉強したい・学び直したい🎓'),
        ('adventure', '🌎世界を旅したい・冒険したい🏞️'),
        ('other', '❓その他💭'),
    ]
    future_plan_choice = MultiSelectField('Future Plan Choice', max_length=200, choices=FUTURE_PLAN_CHOICES, null=True, blank=True)
    future_plan = models.TextField('Future Plan', null=True, blank=True)
    # 理想のパートナー像：どんな性格や価値観のパートナーを求めているかを伝える。
    REQUEST_FOR_PARTNER_CHOICES = [
        ('kind', '💖思いやりがある🤗'),
        ('honest', '🧐誠実で正直🙌'),
        ('funny', '😂ユーモアがある🤣'),
        ('reliable', '💪頼りがいがある🛠️'),
        ('calm', '😌落ち着いている🌿'),
        ('positive', '🌟ポジティブ思考✨'),
        ('respectful', '🙏相手を尊重する🤝'),
        ('empathetic', '💞共感力がある🤗'),
        ('good_communicator', '🗣️コミュニケーション能力が高い📞'),
        ('romantic', '💘ロマンチック💐'),
        ('intellectual', '🧠知的で教養がある📚'),
        ('active', '🏃‍♂️行動的・アウトドア派🏞️'),
        ('creative', '🎨創造力がある💡'),
        ('similar_values', '💬価値観が似ている🤍'),
        ('family_oriented', '👨‍👩‍👧‍👦家庭を大事にする🏡'),
        ('financially_stable', '💸経済的に安定している🏦'),
        ('appearance', '😍外見が好み💅'),
        ('independent', '💼自立している💪'),
        ('listener', '👂話をしっかり聞いてくれる👂'),
        ('affectionate', '💋愛情表現が豊か💖'),
        ('other', '❓その他💭'),
    ]
    request_for_partner_choice = MultiSelectField('Request for partner Choice', max_length=200, choices=REQUEST_FOR_PARTNER_CHOICES, null=True, blank=True)
    request_for_partner = models.TextField('Request for partner', null=True, blank=True)

    ##### 興味のある活動 #####
    # 週末の過ごし方：どのように週末を過ごすのが好きか（例：アウトドア、映画、カフェ巡りなど）。
    WEEKEND_ACTIVITY_CHOICES = [
        ('outdoor', '🏞️アウトドア（登山・散歩・サイクリングなど）🚶‍♀️'),
        ('movie', '🎬映画鑑賞🍿'),
        ('cafe', '☕カフェ巡り🍰'),
        ('reading', '📚読書📖'),
        ('shopping', '🛍️買い物👗'),
        ('cooking', '🍳料理👨‍🍳'),
        ('gaming', '🎮ゲーム🎲'),
        ('art', '🎨アート・美術館巡り🖼️'),
        ('study', '📘勉強・資格取得のための学習📝'),
        ('music', '🎶音楽を聴く・演奏する🎸'),
        ('exercise', '💪ジム・ヨガなどの運動🧘‍♀️'),
        ('travel', '✈️ひとり旅・日帰り旅行🗺️'),
        ('relax', '🛋️自宅でのんびり・ゴロゴロする💤'),
        ('photo', '📸写真撮影・インスタ巡り🖼️'),
        ('social', '💻SNS・ネットサーフィン🌐'),
        ('hobby', '🎨趣味に没頭する🧩'),
        ('volunteer', '🤝ボランティア活動🌍'),
        ('spiritual', '⛩️神社仏閣巡り・パワースポット巡り🕉️'),
        ('other', '❓その他💭'),
    ]
    weekend_activity_choice = MultiSelectField('Weekend Activity Choice', max_length=200, choices=WEEKEND_ACTIVITY_CHOICES, null=True, blank=True)
    weekend_activity = models.TextField('Weekend Activity', null=True, blank=True)
    # 今やっている活動／プロジェクト：仕事やプライベートで挑戦していること、趣味でやっていること。
    ONGOING_PROJECT_CHOICES = [
        ('career_development', '💼キャリアの成長・スキルアップ📈'),
        ('startup', '🚀起業・スタートアップ💡'),
        ('freelance', '💻フリーランスの仕事🏠'),
        ('research', '🔬研究・調査📊'),
        ('side_project', '💼副業プロジェクト📅'),
        ('hobby_project', '🎨趣味でのプロジェクト（アート、音楽、写真など）📸'),
        ('learning', '📚新しい技術や言語の学習🖥️'),
        ('fitness', '🏋️‍♀️健康・フィットネス（ジム、ダイエット、ヨガなど）🧘‍♂️'),
        ('volunteering', '🤝ボランティア活動🌍'),
        ('community_building', '🏘️コミュニティ作り・参加👥'),
        ('travel', '✈️旅行計画・実行🌍'),
        ('personal_growth', '🌱自己成長・心理学の学習🧠'),
        ('writing', '✍️執筆（ブログ、小説、詩など）📖'),
        ('creative_work', '🎨創作活動（絵画、音楽、映像制作など）🎬'),
        ('event_organizing', '🎉イベントの企画・運営📅'),
        ('productivity', '⏰生産性向上の取り組み（習慣化、時間管理など）📈'),
        ('innovation', '💡イノベーション・新しいアイディアの実現🚀'),
        ('social_project', '🌍社会貢献活動（環境保護、社会問題解決など）♻️'),
        ('family', '👨‍👩‍👧‍👦家庭や育児に関連する活動🏡'),
        ('other', '❓その他💭'),
    ]
    ongoing_project_choice = MultiSelectField('On-Going Project Choice', max_length=200, choices=ONGOING_PROJECT_CHOICES, null=True, blank=True)
    ongoing_project = models.TextField('On-Going Project', null=True, blank=True)

    ##### 社会的な活動・ボランティア #####
    # 参加している社会活動やボランティア：自分の社会貢献やコミュニティ活動を記載（相手に共感を呼びやすい）。
    SOCIAL_ACTIVITY_CHOICES = [
        ('environmental_protection', '🌱環境保護活動（リサイクル、植樹、環境教育など）🌍'),
        ('animal_welfare', '🐾動物福祉活動（動物保護団体、保護施設支援など）🐶'),
        ('disaster_relief', '🚨災害支援活動（被災地支援、募金活動など）💖'),
        ('education_support', '📚教育支援活動（子どもの学習支援、教育普及活動など）👩‍🏫'),
        ('healthcare', '🩺医療支援活動（病院支援、医療ボランティアなど）💉'),
        ('poverty_alleviation', '🍞貧困救済活動（食料支援、物資配布など）🏘️'),
        ('elderly_support', '👵高齢者支援活動（訪問介護、シニア向けプログラムなど）👴'),
        ('community_development', '🏡地域社会開発（地域イベントの企画、地域活性化など）🌆'),
        ('refugee_support', '🌍難民支援活動（難民キャンプの支援、物資提供など）🆘'),
        ('human_rights', '✊人権活動（平等、自由の促進、LGBTQ+支援など）🏳️‍🌈'),
        ('gender_equality', '♀️ジェンダー平等活動（女性の権利向上、性別に関する教育など）♂️'),
        ('youth_mentorship', '👩‍🏫若者支援（メンターとして活動、若者向けプログラムなど）👨‍🏫'),
        ('community_health', '💪地域の健康推進活動（予防接種、健康診断など）🏥'),
        ('arts_and_culture', '🎨アート・文化活動（地域の文化祭支援、アートプロジェクトなど）🎭'),
        ('sports_and_recreation', '⚽スポーツ・レクリエーション支援（地域スポーツイベントの開催など）🏅'),
        ('clean_up', '🧹地域清掃活動（ビーチクリーンアップ、街のゴミ拾いなど）🗑️'),
        ('social_inclusion', '🤝社会的包摂活動（マイノリティ支援、孤立を防ぐ活動など）🌍'),
        ('mental_health', '🧠メンタルヘルス支援（カウンセリング、精神的支援活動など）💙'),
        ('tech_for_good', '💻テクノロジーを活用した社会貢献（IT教育、オンライン支援プラットフォームなど）🌐'),
        ('other', '❓その他の社会活動💬'),
    ]
    social_activity_choice = MultiSelectField('Social Activity Choice', max_length=200, choices=SOCIAL_ACTIVITY_CHOICES, null=True, blank=True)
    social_activity = models.TextField('Social Activity', null=True, blank=True)

    ##### ユニークな質問 #####
    # もしも自由に過ごせる1日があったら何をしたいか？
    FREE_DAY_CHOICES = [
        ('nature_escape', '🏞️自然の中で過ごす（ハイキング、キャンプ、ビーチでリラックスなど）🌳'),
        ('city_exploration', '🏙️街を散策する（カフェ巡り、観光名所巡りなど）🏙️'),
        ('creative_hobby', '🎨クリエイティブな趣味を楽しむ（絵を描く、音楽を作る、料理するなど）🎶'),
        ('adventure', '🧗‍♂️冒険的な体験をする（スポーツ、バンジージャンプ、旅行など）🌍'),
        ('spa_and_relax', '💆‍♀️スパやリラックスする時間を過ごす（温泉、マッサージ、瞑想など）🛁'),
        ('family_time', '👨‍👩‍👧‍👦家族と過ごす（みんなで料理、ゲーム、外食など）🍽️'),
        ('friends_gathering', '🍻友達と過ごす（ピクニック、飲み会、カラオケなど）🎤'),
        ('reading_and_study', '📚読書や学びの時間を持つ（本を読む、新しいスキルを学ぶなど）🖋️'),
        ('indoor_relax', '🎮家でのんびり過ごす（映画鑑賞、ゲーム、ネットサーフィンなど）🛋️'),
        ('volunteering', '🤝社会貢献活動に参加する（ボランティア活動、地域イベント支援など）🌍'),
        ('sports_and_fitness', '🏋️‍♂️スポーツやフィットネスに挑戦する（ジム、ヨガ、ジョギングなど）🏃‍♀️'),
        ('culinary_experience', '🍣美味しい食事を楽しむ（グルメ巡り、料理教室など）🍷'),
        ('travel_abroad', '✈️海外旅行に行く（異文化交流、観光など）🌏'),
        ('luxury_experience', '💎贅沢な体験をする（高級レストラン、リゾート地など）🍽️'),
        ('watching_performance', '🎭演劇やライブを観る（コンサート、映画、演劇など）🎶'),
        ('silent_retreat', '🧘‍♀️静かな場所で過ごす（リトリート、瞑想、静寂な場所でのひとときなど）🌿'),
        ('other', '❓その他の過ごし方💬'),
    ]
    free_day_choice = MultiSelectField('Free Day Choice', max_length=200, choices=FREE_DAY_CHOICES, null=True, blank=True)
    free_day = models.TextField('What if Free Day', null=True, blank=True)
    # 今までの人生で最も誇りに思うことは何か？
    PROUDEST_ACHIEVEMENTS_CHOICES = [
        ('academic_success', '🎓学業や資格取得（大学の卒業、資格試験の合格など）📚'),
        ('career_achievement', '💼キャリアの達成（昇進、プロジェクトの成功、起業など）🚀'),
        ('personal_growth', '🌱自己成長（新しいスキルの習得、マインドセットの変化など）💡'),
        ('family_relationship', '👨‍👩‍👧‍👦家族との関係（親との絆を深めた、子供の育成など）❤️'),
        ('volunteering_contribution', '🤝社会貢献（ボランティア活動、コミュニティへの貢献など）🌍'),
        ('overcoming_adversity', '💪困難の克服（健康問題、経済的困難などを乗り越えた経験）🛠️'),
        ('artistic_creativity', '🎨芸術的な成果（絵を描いた、音楽を作った、演技をしたなど）🎶'),
        ('sports_achievement', '🏅スポーツの成果（大会での優勝、自己記録の更新など）🏆'),
        ('travel_experience', '✈️旅行で得た経験（海外一人旅、異文化交流など）🌏'),
        ('relationships', '🤗人間関係の構築（友人との絆、恋愛関係などの成功）💑'),
        ('financial_success', '💰経済的成功（貯金、投資での成功、マイホーム購入など）🏠'),
        ('personal_project', '💼個人的なプロジェクト（自分で始めた事業や活動など）🛠️'),
        ('helping_others', '🤗他人を助けた経験（他人の成功に貢献した、自分が助けた話など）🙌'),
        ('milestone_event', '🎉人生の節目となる出来事（結婚、子供の誕生、大きな旅行など）💍'),
        ('other', '❓その他の誇りに思うこと💬'),
    ]
    proudest_achievements_choice = MultiSelectField('Proudest Achievement Choice', max_length=200, choices=PROUDEST_ACHIEVEMENTS_CHOICES, null=True, blank=True)
    proudest_achievements = models.TextField('Proudest Achieve.', null=True, blank=True)
    # 最も大切にしていることは？
    MOST_IMPORTANT_VALUES_CHOICES = [
        ('family', '👨‍👩‍👧‍👦家族（家族との絆、親子関係など）🧑‍👧‍👦'),
        ('friendship', '🤝友情（友人との関係、信頼や支え合い）👬'),
        ('health', '💪健康（身体的・精神的な健康を維持すること）🏋️‍♀️'),
        ('honesty', '🕊️正直（誠実であること、嘘をつかないこと）⚖️'),
        ('career', '💼キャリア（仕事の成長や目標達成）📈'),
        ('financial_stability', '💰経済的安定（お金の管理や将来のための準備）🏦'),
        ('self_development', '📚自己成長（新しいスキルを学ぶこと、人生の経験から学ぶこと）🧠'),
        ('compassion', '💖思いやり（他者への優しさや助け合いの精神）🤗'),
        ('integrity', '🔒誠実さ（道徳的・倫理的に正しいことをする）🛡️'),
        ('adventure', '🌍冒険心（新しいことに挑戦すること、未知の経験をすること）🧭'),
        ('creativity', '🎨創造性（芸術や新しいアイデアを生み出すこと）💡'),
        ('peace_of_mind', '☮️心の平穏（ストレスの少ない生活、精神的な安定）🧘‍♂️'),
        ('freedom', '🕊️自由（自分らしく生きること、制約からの解放）🚀'),
        ('justice', '⚖️正義（公平で公正な社会を目指すこと）🕊️'),
        ('love', '❤️愛（愛情を持ち続けること、関係性の深さ）💑'),
        ('environment', '🌿環境（自然保護や持続可能な生活）🌍'),
        ('other', '❓その他の大切にしていること❕'),
    ]
    most_important_values_choice = MultiSelectField('Most important Values Choice', max_length=200, choices=MOST_IMPORTANT_VALUES_CHOICES, null=True, blank=True)
    most_important_values = models.TextField('Most important Values', null=True, blank=True)

    contacts = models.TextField('Contact', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='findme_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='findme_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    class Meta:
        pass

    def __str__(self):
        return f'<FindMe:name={self.name}, {self.profile.nick_name}>'

    def get_mbti_choices(self):
        """選択した MBTI に応じた表示名称の選択肢を返す"""
        return self.profile.MBTI_NAME_CHOICES.get(self.mbti, [])

    def get_mbti_name_display(self):
        """mbti_name のラベルを取得する"""
        for choices in self.profile.MBTI_NAME_CHOICES.values():
            for key, label in choices:
                if key == self.mbti_name:
                    return label
        return ""

    @property
    def get_mbti_url(self):
        """選択した MBTI に応じた詳細説明画面URLを返す"""
        return get_mbti_detail_url(self.mbti)

    @property
    def get_mbti_comp(self):
        request = get_current_request()  # 現在のリクエストを取得
        logger.debug(f'request={request}')
        logger.debug(f'hasattr(request, "user")={hasattr(request, "user")}')
        logger.debug(f'hasattr(request.user, "profile")={hasattr(request.user, "profile")}')
        if request and hasattr(request, 'user') and hasattr(request.user, 'profile'):
            user_profile = request.user.profile
            logger.debug(f'user_profile.mbti={user_profile.mbti}')
            logger.debug(f'self.mbti={self.mbti}')
            if user_profile.mbti and self.mbti:
                logger.debug(f'get_mbti_compatibility')
                return get_mbti_compatibility(user_profile.mbti, self.mbti)
        return None, None
    
    @classmethod
    def get_all_choices(cls, context):
        context.update({'GENDER_CHOICES': FindMe.GENDER_CHOICES})
        context.update({'HOBBY_CHOICES': FindMe.HOBBY_CHOICES})
        context.update({'FOOD_CHOICES': FindMe.FOOD_CHOICES})
        context.update({'MUSIC_CHOICES': FindMe.MUSIC_CHOICES})
        context.update({'MOVIE_CHOICES': FindMe.MOVIE_CHOICES})
        context.update({'BOOK_CHOICES': FindMe.BOOK_CHOICES})
        context.update({'PERSONALITY_TYPE_CHOICES': FindMe.PERSONALITY_TYPE_CHOICES})
        context.update({'FAVORITE_DATE_CHOICES': FindMe.FAVORITE_DATE_CHOICES})
        context.update({'SENSE_OF_VALUES_CHOICES': FindMe.SENSE_OF_VALUES_CHOICES})
        context.update({'FUTURE_PLAN_CHOICES': FindMe.FUTURE_PLAN_CHOICES})
        context.update({'REQUEST_FOR_PARTNER_CHOICES': FindMe.REQUEST_FOR_PARTNER_CHOICES})
        context.update({'WEEKEND_ACTIVITY_CHOICES': FindMe.WEEKEND_ACTIVITY_CHOICES})
        context.update({'ONGOING_PROJECT_CHOICES': FindMe.ONGOING_PROJECT_CHOICES})
        context.update({'SOCIAL_ACTIVITY_CHOICES': FindMe.SOCIAL_ACTIVITY_CHOICES})
        context.update({'FREE_DAY_CHOICES': FindMe.FREE_DAY_CHOICES})
        context.update({'PROUDEST_ACHIEVEMENTS_CHOICES': FindMe.PROUDEST_ACHIEVEMENTS_CHOICES})
        context.update({'MOST_IMPORTANT_VALUES_CHOICES': FindMe.MOST_IMPORTANT_VALUES_CHOICES})

        return context
    
    @classmethod
    def filter_findme_object(cls, object_list, object_field, field_name, choices):
        
        if not object_field: return object_list
        # 選択肢のバリデーション
        valid_choices = [choice[0] for choice in choices]
        logger.debug(f'valid_choices: {valid_choices}')

        object = [choice for choice in object_field if choice in valid_choices]
        logger.debug(f'object: {object}')
        # フィルタ処理
        if object:
            q = Q()
            for choice in object:
                logger.debug(f'field_name: {field_name} include choice={choice}')
                q |= Q(**{f"{field_name}__icontains": choice})
            logger.debug(f'object_list: {object_list}')
            object_list = object_list.filter(q)
        return object_list

    def save(self, *args, **kwargs):
        if self.images and self.images != self.__class__.objects.get(pk=self.pk).images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.images = crop_square_image(self.images, 300) # Update the images size

        if self.themes and self.themes != self.__class__.objects.get(pk=self.pk).themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

        """mbti_name が現在の mbti に対応しているかチェック"""
        if self.mbti and self.mbti_name:
            valid_choices = dict(self.profile.MBTI_NAME_CHOICES.get(self.mbti, []))
            if self.mbti_name not in valid_choices:
                self.mbti_name = None  # 無効な場合はクリア

        super().save(*args, **kwargs)

    # 受け取った Poke数 を表示
    @property
    def poke_count(self):
        return self.received_pokes.count()
    
    @property
    def get_all_notifications(self):
        """ すべての通知を取得 """
        return self.recipient_notifications.all().order_by("-created_at")

class FindMeImage(models.Model):
    """FindMe に紐づく画像（複数可）"""
    findme = models.ForeignKey('FindMe', on_delete=models.CASCADE, related_name='findme_images')
    IMAGE_CATEGORY_CHOICES = [
        ('smile', '😊笑顔😄'),
        ('fashion', '👗オシャレ🕶️'),
        ('hobby_action', '🎨趣味🎸'),
        ('pet_love', '🐶ペット🐱'),
        ('outdoor', '🌄自然・お出かけ🚴'),
        ('sports_pose', '🏋️‍♂️スポーツ・健康美💪'),
        ('foodie', '🍳手料理・グルメ🍰'),
        ('culture', '📚知的・文化的🧠'),
        ('mystery', '🎭ミステリアス🌙'),
        ('funny', '😂ユーモア🤪'),
    ]
    image_category_choice = models.CharField('Image Category', max_length=100, choices=IMAGE_CATEGORY_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to='findme/images')
    caption = models.CharField(max_length=255, blank=True, null=True)  # 任意のキャプション

    is_theme = models.BooleanField(default=False)  # テーマ画像フラグ（Trueならテーマ画像として扱う）

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.findme.name or "Unknown"} (Theme: {self.is_theme})'


class Poke(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_pokes')
    receiver = models.ForeignKey(FindMe, on_delete=models.CASCADE, related_name='received_pokes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass

    def __str__(self):
        return f'{self.sender} poked {self.receiver} on {self.created_at}'

class Notification(models.Model):
    recipient = models.ForeignKey(FindMe, on_delete=models.CASCADE, related_name='recipient_notifications')
    sender = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='sender_notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
