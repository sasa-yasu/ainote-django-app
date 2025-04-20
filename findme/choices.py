from collections import OrderedDict

class ChoiceMixin:
    @classmethod
    def choices(cls):
        return [
            (value, label)
            for key, value in cls.__dict__.items()
            if isinstance(value, tuple) and len(value) == 2  # valueがタプルかつ長さが2であることを確認
            if not key.startswith('__') and not callable(value) and value is not None
            for value, label in [value]  # value を (value, label) として分解
        ]

class GenderChoice(ChoiceMixin):
    SECRET = ('O', '🌈秘密🤫')
    MALE = ('M', '👦男性👔')
    FEMALE = ('F', '👧女性👠')

class PrefectureChoice(ChoiceMixin):
    NONE = ('-', '-')
    HOKKAIDO = ('hokkaido', '❄️北海道🐄')
    AOMORI = ('aomori', '🍎青森県🌊')
    IWATE = ('iwate', '⛰️岩手県🏞️')
    MIYAGI = ('miyagi', '🐟宮城県🏯')
    AKITA = ('akita', '🐶秋田県🌾')
    YAMAGATA = ('yamagata', '🍒山形県🌸')
    FUKUSHIMA = ('fukushima', '🏔️福島県🧴')
    IBARAKI = ('ibaraki', '🥬茨城県🏖️')
    TOCHIGI = ('tochigi', '🍓栃木県🚗')
    GUNMA = ('gunma', '♨️群馬県🐴')
    SAITAMA = ('saitama', '🌻埼玉県🚉')
    CHIBA = ('chiba', '🐬千葉県🛫')
    TOKYO = ('tokyo', '🗼東京都🎌')
    KANAGAWA = ('kanagawa', '⚓神奈川県🏖️')
    NIIGATA = ('niigata', '🌾新潟県🎿')
    TOYAMA = ('toyama', '🏔️富山県🐟')
    ISHIKAWA = ('ishikawa', '🏯石川県🎨')
    FUKUI = ('fukui', '🦖福井県🏞️')
    YAMANASHI = ('yamanashi', '🍇山梨県🗻')
    NAGANO = ('nagano', '❄️長野県🥢')
    GIFU = ('gifu', '🏯岐阜県🍡')
    SHIZUOKA = ('shizuoka', '🗻静岡県🐟')
    AICHI = ('aichi', '🚄愛知県🏯')
    MIE = ('mie', '⛩️三重県🐚')
    SHIGA = ('shiga', '🌊滋賀県🦢')
    KYOTO = ('kyoto', '🎋京都府🏯')
    OSAKA = ('osaka', '🍜大阪府🎭')
    HYOGO = ('hyogo', '🦌兵庫県⛴️')
    NARA = ('nara', '🦌奈良県🏺')
    WAKAYAMA = ('wakayama', '🍊和歌山県🐼')
    TOTTORI = ('tottori', '🐪鳥取県⛱️')
    SHIMANE = ('shimane', '🦀島根県🏮')
    OKAYAMA = ('okayama', '🍑岡山県🏞️')
    HIROSHIMA = ('hiroshima', '🕊️広島県⛩️')
    YAMAGUCHI = ('yamaguchi', '🐡山口県🏯')
    TOKUSHIMA = ('tokushima', '🎵徳島県🌀')
    KAGAWA = ('kagawa', '🍜香川県🧂')
    EHIME = ('ehime', '🍊愛媛県⛴️')
    KOUCHI = ('kouchi', '🏞️高知県🐎')
    FUKUOKA = ('fukuoka', '🍜福岡県🎉')
    SAGA = ('saga', '🛤️佐賀県🍵')
    NAGASAKI = ('nagasaki', '⚓長崎県⛪')
    KUMAMOTO = ('kumamoto', '🐻熊本県🏯')
    OITA = ('oita', '♨️大分県🐵')
    MIYAZAKI = ('miyazaki', '🌴宮崎県🐓')
    KAGOSHIMA = ('kagoshima', '🌋鹿児島県🛳️')
    OKINAWA = ('okinawa', '🏖️沖縄県🥁')

class HobbyChoice(ChoiceMixin):
    MUSIC = 'music', '🎧音楽鑑賞🎶'
    MOVIE = 'movie', '🎬映画鑑賞🍿'
    TRAVEL = 'travel', '✈️旅行🌍'
    SPORTS = 'sports', '⚽スポーツ🏃'
    READING = 'reading', '📚読書📖'
    COOKING = 'cooking', '🍳料理🧂'

class FoodChoice(ChoiceMixin):
    JAPANESE = "japanese", "🍱和食🍚"
    WESTERN = "western", "🍔洋食🥩"
    CHINESE = "chinese", "🥡中華料理🥢"
    KOREAN = "korean", "🌶️韓国料理🥘"
    ITALIAN = "italian", "🍝イタリアン🍕"
    FRENCH = "french", "🥖フレンチ🍷"
    THAI = "thai", "🍜タイ料理🌶️"
    INDIAN = "indian", "🍛インド料理🧄"
    SWEETS = "sweets", "🍰スイーツ🍩"
    FASTFOOD = "fastfood", "🍟ファストフード🍔"
    HEALTHY = "healthy", "🥗健康志向料理🍵"
    HOME = "home", "🏠家庭料理🍳"
    OTHER = "other", "❓その他🍽️"

class MusicChoice(ChoiceMixin):
    POP = "pop", "🎤ポップス🎶"
    ROCK = "rock", "🎸ロック🤘"
    JAZZ = "jazz", "🎷ジャズ🕶️"
    CLASSICAL = "classical", "🎻クラシック🎼"
    HIPHOP = "hiphop", "🧢ヒップホップ/ラップ🎧"
    EDM = "edm", "🎚️EDM/ダンス💃"
    RNB = "rnb", "🎙️R&B/ソウル❤️"
    ANIME = "anime", "🌟アニメソング🎵"
    GAME = "game", "🎮ゲーム音楽🕹️"
    KPOP = "kpop", "🇰🇷K-POP💫"
    ENKA = "enka", "🌸演歌🎤"
    IDOL = "idol", "💖アイドル🌟"
    FOLK = "folk", "🪕フォーク/カントリー🎶"
    METAL = "metal", "🤘メタル/ハードロック🔥"
    REGGAE = "reggae", "🟰レゲエ🧘"
    BLUES = "blues", "🎺ブルース💙"
    WORLD = "world", "🌍ワールドミュージック🎶"
    OTHER = "other", "❓その他🎼"

class MovieChoice(ChoiceMixin):
    ACTION = "action", "💥アクション🎯"
    ADVENTURE = "adventure", "🗺️アドベンチャー🧭"
    COMEDY = "comedy", "😂コメディ🎭"
    DRAMA = "drama", "🎬ドラマ🎟️"
    ROMANCE = "romance", "❤️恋愛/ラブロマンス💌"
    THRILLER = "thriller", "😱スリラー/サスペンス🔪"
    HORROR = "horror", "👻ホラー🧟"
    MYSTERY = "mystery", "🕵️ミステリー🔍"
    SCIFI = "sci-fi", "🚀SF/サイエンスフィクション👽"
    FANTASY = "fantasy", "🧙ファンタジー🦄"
    ANIMATION = "animation", "🎨アニメーション📽️"
    DOCUMENTARY = "documentary", "📚ドキュメンタリー🎞️"
    MUSICAL = "musical", "🎤ミュージカル🎶"
    HISTORY = "history", "🏛️歴史📜"
    BIOGRAPHY = "biography", "👤伝記🖋️"
    WAR = "war", "⚔️戦争🪖"
    CRIME = "crime", "🚓犯罪/クライム🕶️"
    FAMILY = "family", "👨‍👩‍👧‍👦ファミリー🧸"
    SUPERHERO = "superhero", "🦸ヒーロー/特撮⚡"
    JAPANESE = "japanese", "🎌邦画🎥"
    FOREIGN = "foreign", "🌍洋画🌐"
    OTHER = "other", "❓その他🎬"

class BookChoice(ChoiceMixin):
    NOVEL = "novel", "📖小説📝"
    MYSTERY = "mystery", "🕵️ミステリー🔍"
    ROMANCE = "romance", "💘恋愛/ラブストーリー💌"
    FANTASY = "fantasy", "🧝ファンタジー🦄"
    SCIFI = "sci-fi", "👽SF/サイエンスフィクション🚀"
    HISTORICAL = "historical", "🏯歴史小説📜"
    THRILLER = "thriller", "🔪スリラー/サスペンス😱"
    ESSAY = "essay", "📝エッセイ📄"
    POETRY = "poetry", "🖋️詩/短歌/俳句🌸"
    NONFICTION = "nonfiction", "📚ノンフィクション📘"
    BIOGRAPHY = "biography", "👤伝記🖊️"
    BUSINESS = "business", "💼ビジネス書📈"
    SELFHELP = "selfhelp", "🌟自己啓発💪"
    PSYCHOLOGY = "psychology", "🧠心理学🛋️"
    PHILOSOPHY = "philosophy", "🤔哲学/思想📚"
    SCIENCE = "science", "🔬科学/理系⚛️"
    RELIGION = "religion", "🕊️宗教/精神世界🛐"
    EDUCATION = "education", "🎓教育/子育て👶"
    COMIC = "comic", "📙漫画😂"
    LIGHTNOVEL = "lightnovel", "📘ライトノベル✨"
    LITERATURE = "literature", "📝純文学🏛️"
    CLASSIC = "classic", "🏺古典文学📖"
    OTHER = "other", "❓その他📗"

class PersonalityTypeChoice(ChoiceMixin):
    EASYGOING = "easygoing", "🌿おおらか☀️"
    SERIOUS = "serious", "📘真面目🧐"
    SOCIABLE = "sociable", "🤝社交的😄"
    CALM = "calm", "🧘‍♂️落ち着いている🌊"
    MY_PACE = "my_pace", "🐢マイペース🚶‍♂️"
    POSITIVE = "positive", "🌈ポジティブ💪"
    SENSITIVE = "sensitive", "🌸繊細💧"
    ENERGETIC = "energetic", "⚡元気・活発🏃‍♂️"
    QUIET = "quiet", "🤫おとなしい🌙"
    CURIOUS = "curious", "🔍好奇心旺盛🧠"
    LOGICAL = "logical", "🧩論理的🧠"
    EMOTIONAL = "emotional", "💖感情豊か😭"
    CHEERFUL = "cheerful", "😄明るい🌞"
    FRIENDLY = "friendly", "😊フレンドリー🤗"
    AMBITIOUS = "ambitious", "🚀向上心がある🎯"
    CONSIDERATE = "considerate", "🤝思いやりがある💐"
    INDEPENDENT = "independent", "🦅自立している🧍‍♂️"
    CAREFUL = "careful", "🔒慎重派🕵️‍♂️"
    ADAPTABLE = "adaptable", "🌊柔軟に対応できる🔄"
    LEADER = "leader", "👑リーダーシップがある🗣️"
    LISTENER = "listener", "👂聞き上手🤲"
    OTHER = "other", "❓その他💭"

class FavoriteDateChoice(ChoiceMixin):
    CAFE = "cafe", "☕カフェでゆっくり話す🧁"
    DINNER = "dinner", "🍷おしゃれなレストランでディナー🍽️"
    MOVIE = "movie", "🎬映画鑑賞デート🍿"
    PARK = "park", "🌳公園で散歩🚶‍♀️"
    AMUSEMENT_PARK = "amusement_park", "🎡遊園地・テーマパーク🎢"
    AQUARIUM = "aquarium", "🐠水族館デート🐧"
    ZOO = "zoo", "🦁動物園デート🐵"
    MUSEUM = "museum", "🖼️美術館・博物館巡り🏛️"
    SHOPPING = "shopping", "🛍️一緒にショッピング💳"
    DRIVE = "drive", "🚗ドライブデート🌆"
    BEACH = "beach", "🏖️海辺でのんびり🌅"
    PICNIC = "picnic", "🧺自然の中でピクニック🌼"
    HIKING = "hiking", "🥾ハイキング・登山⛰️"
    FESTIVAL = "festival", "🎆夏祭り・花火大会👘"
    HOT_SPRING = "hot_spring", "♨️温泉旅行🏞️"
    HOME_COOKING = "home_cooking", "🍳おうちで一緒に料理🥗"
    GAME_NIGHT = "game_night", "🎮おうちでゲーム・映画鑑賞📺"
    SPORTS = "sports", "🏀一緒にスポーツをする🏃‍♂️"
    CONCERT = "concert", "🎤ライブ・コンサート鑑賞🎶"
    SEASON_EVENT = "season_event", "🌸季節イベント（花見・紅葉など）🍁"
    TRAVEL = "travel", "🧳日帰りor泊まり旅行✈️"
    OTHER = "other", "❓その他💭"

class SenseOfValuesChoice(ChoiceMixin):
    TRUST = "trust", "🤝信頼関係🔒"
    HONESTY = "honesty", "🕊️正直さ🪞"
    COMMUNICATION = "communication", "🗣️しっかり話し合えること💬"
    RESPECT = "respect", "🙇‍♀️お互いを尊重すること🙇‍♂️"
    HUMOR = "humor", "😂ユーモア・笑いのセンス🤪"
    AFFECTION = "affection", "💞愛情表現💋"
    SHARED_VALUES = "shared_values", "🧠価値観の一致❤️"
    SUPPORT = "support", "🤗困った時に支え合えること🆘"
    FREEDOM = "freedom", "🕊️お互いの自由を尊重すること🛫"
    GROWTH = "growth", "🌱一緒に成長できること📈"
    PASSION = "passion", "🔥情熱・ドキドキ感❤️‍🔥"
    RELIABILITY = "reliability", "🛡️頼りがい🧍‍♂️"
    STABILITY = "stability", "⚖️安定感🧱"
    ROMANCE = "romance", "🌹ロマンチックな関係🌙"
    FUN = "fun", "🎉一緒にいて楽しいこと🥳"
    GOALS = "goals", "🎯将来の目標や夢の共有🚀"
    FAMILY_MIND = "family_mind", "🏡家庭的であること👨‍👩‍👧‍👦"
    OTHER = "other", "❓その他💭"

class FuturePlanChoice(ChoiceMixin):
    ENTREPRENEUR = "entrepreneur", "💼起業したい🚀"
    CAREER_UP = "career_up", "📈キャリアアップしたい🌟"
    EXPERT = "expert", "👨‍🔬専門分野で一流になりたい🎓"
    SIDE_JOB = "side_job", "💻副業をしたい💡"
    OVERSEAS = "overseas", "🌍海外で働きたい・暮らしたい✈️"
    CREATIVE = "creative", "🎨創作活動をしたい（音楽・アートなど）🎶"
    FREELANCE = "freelance", "🖥️フリーランスで働きたい👩‍💻"
    VOLUNTEER = "volunteer", "🤝社会貢献・ボランティア活動をしたい🌱"
    FAMILY = "family", "👨‍👩‍👧‍👦家庭を築きたい・子育てしたい🏡"
    COMMUNITY = "community", "🏘️地域活動に関わりたい🤝"
    RELAXED_LIFE = "relaxed_life", "🌿のんびりとした生活を送りたい🌅"
    FINANCIAL_FREEDOM = "financial_freedom", "💸経済的自由を得たい（脱サラなど）🏝️"
    STUDY = "study", "📚もう一度勉強したい・学び直したい🎓"
    ADVENTURE = "adventure", "🌎世界を旅したい・冒険したい🏞️"
    OTHER = "other", "❓その他💭"

class RequestForPartnerChoice(ChoiceMixin):
    KIND = "kind", "💖思いやりがある🤗"
    HONEST = "honest", "🧐誠実で正直🙌"
    FUNNY = "funny", "😂ユーモアがある🤣"
    RELIABLE = "reliable", "💪頼りがいがある🛠️"
    CALM = "calm", "😌落ち着いている🌿"
    POSITIVE = "positive", "🌟ポジティブ思考✨"
    RESPECTFUL = "respectful", "🙏相手を尊重する🤝"
    EMPATHETIC = "empathetic", "💞共感力がある🤗"
    GOOD_COMMUNICATOR = "good_communicator", "🗣️コミュニケーション能力が高い📞"
    ROMANTIC = "romantic", "💘ロマンチック💐"
    INTELLECTUAL = "intellectual", "🧠知的で教養がある📚"
    ACTIVE = "active", "🏃‍♂️行動的・アウトドア派🏞️"
    CREATIVE = "creative", "🎨創造力がある💡"
    SIMILAR_VALUES = "similar_values", "💬価値観が似ている🤍"
    FAMILY_ORIENTED = "family_oriented", "👨‍👩‍👧‍👦家庭を大事にする🏡"
    FINANCIALLY_STABLE = "financially_stable", "💸経済的に安定している🏦"
    APPEARANCE = "appearance", "😍外見が好み💅"
    INDEPENDENT = "independent", "💼自立している💪"
    LISTENER = "listener", "👂話をしっかり聞いてくれる👂"
    AFFECTIONATE = "affectionate", "💋愛情表現が豊か💖"
    OTHER = "other", "❓その他💭"

class WeekendActivityChoice(ChoiceMixin):
    OUTDOOR = "outdoor", "🏞️アウトドア（登山・散歩・サイクリングなど）🚶‍♀️"
    MOVIE = "movie", "🎬映画鑑賞🍿"
    CAFE = "cafe", "☕カフェ巡り🍰"
    READING = "reading", "📚読書📖"
    SHOPPING = "shopping", "🛍️買い物👗"
    COOKING = "cooking", "🍳料理👨‍🍳"
    GAMING = "gaming", "🎮ゲーム🎲"
    ART = "art", "🎨アート・美術館巡り🖼️"
    STUDY = "study", "📘勉強・資格取得のための学習📝"
    MUSIC = "music", "🎶音楽を聴く・演奏する🎸"
    EXERCISE = "exercise", "💪ジム・ヨガなどの運動🧘‍♀️"
    TRAVEL = "travel", "✈️ひとり旅・日帰り旅行🗺️"
    RELAX = "relax", "🛋️自宅でのんびり・ゴロゴロする💤"
    PHOTO = "photo", "📸写真撮影・インスタ巡り🖼️"
    SOCIAL = "social", "💻SNS・ネットサーフィン🌐"
    HOBBY = "hobby", "🎨趣味に没頭する🧩"
    VOLUNTEER = "volunteer", "🤝ボランティア活動🌍"
    SPIRITUAL = "spiritual", "⛩️神社仏閣巡り・パワースポット巡り🕉️"
    OTHER = "other", "❓その他💭"

class OngoingProjectChoice(ChoiceMixin):
    CAREER_DEVELOPMENT = "career_development", "💼キャリアの成長・スキルアップ📈"
    STARTUP = "startup", "🚀起業・スタートアップ💡"
    FREELANCE = "freelance", "💻フリーランスの仕事🏠"
    RESEARCH = "research", "🔬研究・調査📊"
    SIDE_PROJECT = "side_project", "💼副業プロジェクト📅"
    HOBBY_PROJECT = "hobby_project", "🎨趣味でのプロジェクト（アート、音楽、写真など）📸"
    LEARNING = "learning", "📚新しい技術や言語の学習🖥️"
    FITNESS = "fitness", "🏋️‍♀️健康・フィットネス（ジム、ダイエット、ヨガなど）🧘‍♂️"
    VOLUNTEERING = "volunteering", "🤝ボランティア活動🌍"
    COMMUNITY_BUILDING = "community_building", "🏘️コミュニティ作り・参加👥"
    TRAVEL = "travel", "✈️旅行計画・実行🌍"
    PERSONAL_GROWTH = "personal_growth", "🌱自己成長・心理学の学習🧠"
    WRITING = "writing", "✍️執筆（ブログ、小説、詩など）📖"
    CREATIVE_WORK = "creative_work", "🎨創作活動（絵画、音楽、映像制作など）🎬"
    EVENT_ORGANIZING = "event_organizing", "🎉イベントの企画・運営📅"
    PRODUCTIVITY = "productivity", "⏰生産性向上の取り組み（習慣化、時間管理など）📈"
    INNOVATION = "innovation", "💡イノベーション・新しいアイディアの実現🚀"
    SOCIAL_PROJECT = "social_project", "🌍社会貢献活動（環境保護、社会問題解決など）♻️"
    FAMILY = "family", "👨‍👩‍👧‍👦家庭や育児に関連する活動🏡"
    OTHER = "other", "❓その他💭"

class SocialActivityChoice(ChoiceMixin):
    ENVIRONMENTAL_PROTECTION = "environmental_protection", "🌱環境保護活動（リサイクル、植樹、環境教育など）🌍"
    ANIMAL_WELFARE = "animal_welfare", "🐾動物福祉活動（動物保護団体、保護施設支援など）🐶"
    DISASTER_RELIEF = "disaster_relief", "🚨災害支援活動（被災地支援、募金活動など）💖"
    EDUCATION_SUPPORT = "education_support", "📚教育支援活動（子どもの学習支援、教育普及活動など）👩‍🏫"
    HEALTHCARE = "healthcare", "🩺医療支援活動（病院支援、医療ボランティアなど）💉"
    POVERTY_ALLEVIATION = "poverty_alleviation", "🍞貧困救済活動（食料支援、物資配布など）🏘️"
    ELDERLY_SUPPORT = "elderly_support", "👵高齢者支援活動（訪問介護、シニア向けプログラムなど）👴"
    COMMUNITY_DEVELOPMENT = "community_development", "🏡地域社会開発（地域イベントの企画、地域活性化など）🌆"
    REFUGEE_SUPPORT = "refugee_support", "🌍難民支援活動（難民キャンプの支援、物資提供など）🆘"
    HUMAN_RIGHTS = "human_rights", "✊人権活動（平等、自由の促進、LGBTQ+支援など）🏳️‍🌈"
    GENDER_EQUALITY = "gender_equality", "♀️ジェンダー平等活動（女性の権利向上、性別に関する教育など）♂️"
    YOUTH_MENTORSHIP = "youth_mentorship", "👩‍🏫若者支援（メンターとして活動、若者向けプログラムなど）👨‍🏫"
    COMMUNITY_HEALTH = "community_health", "💪地域の健康推進活動（予防接種、健康診断など）🏥"
    ARTS_AND_CULTURE = "arts_and_culture", "🎨アート・文化活動（地域の文化祭支援、アートプロジェクトなど）🎭"
    SPORTS_AND_RECREATION = "sports_and_recreation", "⚽スポーツ・レクリエーション支援（地域スポーツイベントの開催など）🏅"
    CLEAN_UP = "clean_up", "🧹地域清掃活動（ビーチクリーンアップ、街のゴミ拾いなど）🗑️"
    SOCIAL_INCLUSION = "social_inclusion", "🤝社会的包摂活動（マイノリティ支援、孤立を防ぐ活動など）🌍"
    MENTAL_HEALTH = "mental_health", "🧠メンタルヘルス支援（カウンセリング、精神的支援活動など）💙"
    TECH_FOR_GOOD = "tech_for_good", "💻テクノロジーを活用した社会貢献（IT教育、オンライン支援プラットフォームなど）🌐"
    OTHER = "other", "❓その他の社会活動💬"

class FreeDayChoice(ChoiceMixin):
    NATURE_ESCAPE = "nature_escape", "🏞️自然の中で過ごす（ハイキング、キャンプ、ビーチでリラックスなど）🌳"
    CITY_EXPLORATION = "city_exploration", "🏙️街を散策する（カフェ巡り、観光名所巡りなど）🏙️"
    CREATIVE_HOBBY = "creative_hobby", "🎨クリエイティブな趣味を楽しむ（絵を描く、音楽を作る、料理するなど）🎶"
    ADVENTURE = "adventure", "🧗‍♂️冒険的な体験をする（スポーツ、バンジージャンプ、旅行など）🌍"
    SPA_AND_RELAX = "spa_and_relax", "💆‍♀️スパやリラックスする時間を過ごす（温泉、マッサージ、瞑想など）🛁"
    FAMILY_TIME = "family_time", "👨‍👩‍👧‍👦家族と過ごす（みんなで料理、ゲーム、外食など）🍽️"
    FRIENDS_GATHERING = "friends_gathering", "🍻友達と過ごす（ピクニック、飲み会、カラオケなど）🎤"
    READING_AND_STUDY = "reading_and_study", "📚読書や学びの時間を持つ（本を読む、新しいスキルを学ぶなど）🖋️"
    INDOOR_RELAX = "indoor_relax", "🎮家でのんびり過ごす（映画鑑賞、ゲーム、ネットサーフィンなど）🛋️"
    VOLUNTEERING = "volunteering", "🤝社会貢献活動に参加する（ボランティア活動、地域イベント支援など）🌍"
    SPORTS_AND_FITNESS = "sports_and_fitness", "🏋️‍♂️スポーツやフィットネスに挑戦する（ジム、ヨガ、ジョギングなど）🏃‍♀️"
    CULINARY_EXPERIENCE = "culinary_experience", "🍣美味しい食事を楽しむ（グルメ巡り、料理教室など）🍷"
    TRAVEL_ABROAD = "travel_abroad", "✈️海外旅行に行く（異文化交流、観光など）🌏"
    LUXURY_EXPERIENCE = "luxury_experience", "💎贅沢な体験をする（高級レストラン、リゾート地など）🍽️"
    WATCHING_PERFORMANCE = "watching_performance", "🎭演劇やライブを観る（コンサート、映画、演劇など）🎶"
    SILENT_RETREAT = "silent_retreat", "🧘‍♀️静かな場所で過ごす（リトリート、瞑想、静寂な場所でのひとときなど）🌿"
    OTHER = "other", "❓その他の過ごし方💬"

class ProudestAchievementChoice(ChoiceMixin):
    ACADEMIC_SUCCESS = "academic_success", "🎓学業や資格取得（大学の卒業、資格試験の合格など）📚"
    CAREER_ACHIEVEMENT = "career_achievement", "💼キャリアの達成（昇進、プロジェクトの成功、起業など）🚀"
    PERSONAL_GROWTH = "personal_growth", "🌱自己成長（新しいスキルの習得、マインドセットの変化など）💡"
    FAMILY_RELATIONSHIP = "family_relationship", "👨‍👩‍👧‍👦家族との関係（親との絆を深めた、子供の育成など）❤️"
    VOLUNTEERING_CONTRIBUTION = "volunteering_contribution", "🤝社会貢献（ボランティア活動、コミュニティへの貢献など）🌍"
    OVERCOMING_ADVERSITY = "overcoming_adversity", "💪困難の克服（健康問題、経済的困難などを乗り越えた経験）🛠️"
    ARTISTIC_CREATIVITY = "artistic_creativity", "🎨芸術的な成果（絵を描いた、音楽を作った、演技をしたなど）🎶"
    SPORTS_ACHIEVEMENT = "sports_achievement", "🏅スポーツの成果（大会での優勝、自己記録の更新など）🏆"
    TRAVEL_EXPERIENCE = "travel_experience", "✈️旅行で得た経験（海外一人旅、異文化交流など）🌏"
    RELATIONSHIPS = "relationships", "🤗人間関係の構築（友人との絆、恋愛関係などの成功）💑"
    FINANCIAL_SUCCESS = "financial_success", "💰経済的成功（貯金、投資での成功、マイホーム購入など）🏠"
    PERSONAL_PROJECT = "personal_project", "💼個人的なプロジェクト（自分で始めた事業や活動など）🛠️"
    HELPING_OTHERS = "helping_others", "🤗他人を助けた経験（他人の成功に貢献した、自分が助けた話など）🙌"
    MILESTONE_EVENT = "milestone_event", "🎉人生の節目となる出来事（結婚、子供の誕生、大きな旅行など）💍"
    OTHER = "other", "❓その他の誇りに思うこと💬"

class MostImportantValuesChoice(ChoiceMixin):
    FAMILY = "family", "👨‍👩‍👧‍👦家族（家族との絆、親子関係など）🧑‍👧‍👦"
    FRIENDSHIP = "friendship", "🤝友情（友人との関係、信頼や支え合い）👬"
    HEALTH = "health", "💪健康（身体的・精神的な健康を維持すること）🏋️‍♀️"
    HONESTY = "honesty", "🕊️正直（誠実であること、嘘をつかないこと）⚖️"
    CAREER = "career", "💼キャリア（仕事の成長や目標達成）📈"
    FINANCIAL_STABILITY = "financial_stability", "💰経済的安定（お金の管理や将来のための準備）🏦"
    SELF_DEVELOPMENT = "self_development", "📚自己成長（新しいスキルを学ぶこと、人生の経験から学ぶこと）🧠"
    COMPASSION = "compassion", "💖思いやり（他者への優しさや助け合いの精神）🤗"
    INTEGRITY = "integrity", "🔒誠実さ（道徳的・倫理的に正しいことをする）🛡️"
    ADVENTURE = "adventure", "🌍冒険心（新しいことに挑戦すること、未知の経験をすること）🧭"
    CREATIVITY = "creativity", "🎨創造性（芸術や新しいアイデアを生み出すこと）💡"
    PEACE_OF_MIND = "peace_of_mind", "☮️心の平穏（ストレスの少ない生活、精神的な安定）🧘‍♂️"
    FREEDOM = "freedom", "🕊️自由（自分らしく生きること、制約からの解放）🚀"
    JUSTICE = "justice", "⚖️正義（公平で公正な社会を目指すこと）🕊️"
    LOVE = "love", "❤️愛（愛情を持ち続けること、関係性の深さ）💑"
    ENVIRONMENT = "environment", "🌿環境（自然保護や持続可能な生活）🌍"
    OTHER = "other", "❓その他の大切にしていること❕"

class ImageCategoryChoice(ChoiceMixin):
    SMILE = ('smile', '😊笑顔😄')
    FASHION = ('fashion', '👗オシャレ🕶️')
    HOBBY_ACTION = ('hobby_action', '🎨趣味🎸')
    PET_LOVE = ('pet_love', '🐶ペット🐱')
    OUTDOOR = ('outdoor', '🌄自然・お出かけ🚴')
    SPORTS_POSE = ('sports_pose', '🏋️‍♂️スポーツ・健康美💪')
    FOODIE = ('foodie', '🍳手料理・グルメ🍰')
    CULTURE = ('culture', '📚知的・文化的🧠')
    MYSTERY = ('mystery', '🎭ミステリアス🌙')
    FUNNY = ('funny', '😂ユーモア🤪')
