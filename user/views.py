import json
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes, format_millis_to_hhmm
from .forms import ProfileForm, UserCreateForm
from .models import Profile

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def get_mbti_name_choices(request):
    logger.debug('start Profile get_mbti_name_choices')
    
    mbti = request.GET.get('mbti')
    mbti_name_choices = Profile.MBTI_NAME_CHOICES.get(mbti, [])
    logger.debug(f'mbti_name_choices={mbti_name_choices}')

    return JsonResponse({'mbti_name_choices': list(mbti_name_choices)})

def list_view(request):
    logger.debug('start Profile list_view')

    PAGE_SIZE = 48 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    # フリーワード検索用
    search_str = request.GET.get("search_str", "")
    logger.debug(f'Searching for: {search_str}')
    if search_str:
        object_list = Profile.objects.filter(
            Q(nick_name__icontains=search_str)
        )
    else:
        object_list = Profile.objects.all()

    # 並び替え処理
    sort_options = {
        "updated_desc": "-updated_at",
        "updated_asc": "updated_at",
        "nick_name_asc": "nick_name",
        "nick_name_desc": "-nick_name",
        "created_desc": "-created_at",
        "created_asc": "created_at",
    }
    sort_by = request.GET.get("sort_by", "updated_desc")
    logger.debug(f'Sort by: {sort_by}')
    sort_field = sort_options.get(sort_by, "-id")  # デフォルトは -id
    object_list = object_list.order_by(sort_field)

    if object_list.exists():
        logger.debug('object_list exists')
        paginator = Paginator(object_list, PAGE_SIZE)
        try:
            display_object_list = paginator.page(page)
        except Exception as e:
            logger.warning(f'couldnt catch the display_object_list page={page}, error={e}')
            display_object_list = paginator.page(1)
        link_object_list = display_object_list.paginator.get_elided_page_range(
            page, on_each_side=PAGINATION_ON_EACH_SIDE, on_ends=PAGINATION_ON_ENDS
        )
    else:
        logger.debug('object_list not exists')
        display_object_list = []
        link_object_list = []

    context = {
        'display_object_list': display_object_list,
        'link_object_list': link_object_list,
        'search_str': search_str,
        'sort_by': sort_by,
    }

    logger.info('return render user/list.html')
    return render(request, 'user/list.html', context)


def detail_view(request, pk):
    logger.info('start detail_view')

    logger.debug('get Profile object(pk)')
    profile = get_object_or_404(Profile, pk=pk)

    # 最新の30件のチャットを取得
    recent_chats = profile.get_chats_by_count(30)

    # 最新の30件のチェックイン情報を取得
    recent_checkin_records = profile.get_recent_checkins(30)

    # 直近1ヶ月間のチェックイン情報を取得
    month_checkin_summary = profile.get_checkin_summary_last_month()

    # 直近1ヶ月間のチェックインサマリを取得
    month_checkins = profile.get_checkins_last_month()

    checkin_data = [
        {
            "title": f"[{checkin.get_diff_time()}]:{checkin.place.place}",
            "start": checkin.checkin_time.isoformat(),
            "end": checkin.checkout_time.isoformat() if checkin.checkout_time else None,
        }
        for checkin in month_checkins if checkin.checkin_time
    ]
    logger.debug(f'checkin_data={checkin_data}')

    checkin_data_json = json.dumps(checkin_data, default=str)
    logger.debug(f'checkin_data_json={checkin_data_json}')

    # 直近1ヶ月間の日別チェックイン時間を取得
    daily_checkins = profile.get_daily_checkin_summary_last_month()

    # Chart用データ作成
    bar_data_labels = []
    bar_data_values = []

    for date, duration_msec in daily_checkins:
        bar_data_labels.append(date.strftime('%m/%d'))  # X軸（日付）
        bar_data_values.append(round(duration_msec / 3600000, 2))  # Y軸（滞在時間（h））

    # 最新の30件のログイン情報を取得
    recent_login_records = profile.get_login_records(30)

    # 所属しているすべてのグループを取得
    joined_groups = profile.get_all_groups

    # すべてのFriendを取得
    friends = profile.get_friend_profiles

    context = {
                'object': profile, 'recent_chats': recent_chats, 'recent_checkin_records': recent_checkin_records, 
                'month_checkin_summary': month_checkin_summary, 'month_checkins': month_checkins, 
                'checkin_data_json': checkin_data_json,
                'bar_data_labels_json': json.dumps(bar_data_labels),
                'bar_data_values_json': json.dumps(bar_data_values),
                'recent_login_records': recent_login_records, 'joined_groups': joined_groups, 'friends': friends
    }

    logger.debug('return render user/detail.html')
    return render(request, 'user/detail.html', context)

@login_required
def create_view(request): 
    logger.info('start Profile create_view')

    if request.method == "POST":
        logger.info('POST method')

        # POSTデータから `mbti` を取得
        mbti_value = request.POST.get('mbti')

        user_form = UserCreateForm(request.POST, request.FILES)
        profile_form = ProfileForm(request.POST, request.FILES)
        profile_form.fields['mbti_name'].choices = Profile.MBTI_NAME_CHOICES.get(mbti_value, [("", "---------")])

        context = {'user_form': user_form, 'profile_form': profile_form}

        if user_form.is_valid() and profile_form.is_valid():
            logger.debug('User Profile form.is_valid')

            try:
                # Userモデルの処理。ログインできるようis_activeをTrueにし保存
                user = user_form.save(commit=True)
                user.is_active = True
                user.save()
            except Exception as e:
                logger.error(f'couldnt create the User Object: {e}')
                logger.info('return render user/create.html')
                return render(request, 'user/create.html', context)

            memberid_data = profile_form.cleaned_data["memberid"]
            nick_name_data = profile_form.cleaned_data["nick_name"]
            badges_data = profile_form.cleaned_data["badges"]
            birth_year_data = profile_form.cleaned_data["birth_year"]
            if birth_year_data == '': birth_year_data = None
            birth_month_day_data = profile_form.cleaned_data["birth_month_day"]
            mbti_data = profile_form.cleaned_data["mbti"]
            mbti_name_data = profile_form.cleaned_data["mbti_name"]
            hobby_data = profile_form.cleaned_data["hobby"]
            sports_data = profile_form.cleaned_data["sports"]
            movie_data = profile_form.cleaned_data["movie"]
            music_data = profile_form.cleaned_data["music"]
            book_data = profile_form.cleaned_data["book"]
            event_data = profile_form.cleaned_data["event"]
            remarks_data = profile_form.cleaned_data["remarks"]
            contract_course_data = profile_form.cleaned_data["contract_course"]
            caretaker01_data = profile_form.cleaned_data["caretaker01"]
            caretaker02_data = profile_form.cleaned_data["caretaker02"]
            caretaker03_data = profile_form.cleaned_data["caretaker03"]
            caretaker04_data = profile_form.cleaned_data["caretaker04"]
            caretaker05_data = profile_form.cleaned_data["caretaker05"]
            pic_data = request.user.profile

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get("themes")

            try:
                profile = Profile.objects.create(
                    user1 = user,
                    memberid = memberid_data,
                    nick_name = nick_name_data,
                    badges = badges_data,
                    birth_year = birth_year_data,
                    birth_month_day = birth_month_day_data,
                    mbti = mbti_data,
                    mbti_name = mbti_name_data,
                    hobby = hobby_data,
                    sports = sports_data,
                    movie = movie_data,
                    music = music_data,
                    book = book_data,
                    event = event_data,
                    remarks = remarks_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    contract_course = contract_course_data,
                    caretaker01 = caretaker01_data,
                    caretaker02 = caretaker02_data,
                    caretaker03 = caretaker03_data,
                    caretaker04 = caretaker04_data,
                    caretaker05 = caretaker05_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Profile Object: {e}')
                logger.info('return render user/create.html')
                return render(request, 'user/create.html', context)

            if images_data:
                logger.debug('images_data exists')
                profile.images = create_images(profile, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                profile.themes = create_themes(profile, themes_data)

            try:
                profile.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data in Profile object: {e}')
            
            logger.info('return redirect user:list')
            return redirect('user:list')
        else:
            logger.error('user-form or profile_form is invalid.')
            logger.error(user_form.errors)
            logger.error(profile_form.errors)
    else:
        logger.info('GET method')
        user_form = UserCreateForm()
        profile_form = ProfileForm()
        context = {'user_form': user_form, 'profile_form': profile_form}

    logger.info('return render user/create.html')
    return render(request, 'user/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Profile update_view')

    logger.debug('get Profile object(pk)')
    profile = get_object_or_404(Profile, pk=pk)

    user_form = UserCreateForm({
        'id': profile.user1.id,
        'username': profile.user1.username,
    })
    
    if request.method == "POST":
        logger.info('POST method')

        # POSTデータから `mbti` を取得
        mbti_value = request.POST.get('mbti', object.mbti)
        
        profile_form = ProfileForm(request.POST, request.FILES)
        profile_form.fields['mbti_name'].choices = Profile.MBTI_NAME_CHOICES.get(mbti_value, [("", "---------")])
        
        context = {'object': profile, 'user_form': user_form, 'profile_form': profile_form}

        if profile_form.is_valid():
            logger.debug('form.is_valid')

            profile.memberid = profile_form.cleaned_data["memberid"]
            profile.nick_name = profile_form.cleaned_data["nick_name"]
            profile.badges = profile_form.cleaned_data["badges"]
            profile.birth_year = profile_form.cleaned_data["birth_year"]
            if profile.birth_year == '': profile.birth_year = None
            profile.birth_month_day = profile_form.cleaned_data["birth_month_day"]
            profile.mbti = profile_form.cleaned_data["mbti"]
            profile.mbti_name = profile_form.cleaned_data["mbti_name"]
            profile.hobby = profile_form.cleaned_data["hobby"]
            profile.sports = profile_form.cleaned_data["sports"]
            profile.movie = profile_form.cleaned_data["movie"]
            profile.music = profile_form.cleaned_data["music"]
            profile.book = profile_form.cleaned_data["book"]
            profile.event = profile_form.cleaned_data["event"]
            profile.remarks = profile_form.cleaned_data["remarks"]
            profile.contract_course = profile_form.cleaned_data["contract_course"]
            profile.caretaker01 = profile_form.cleaned_data["caretaker01"]
            profile.caretaker02 = profile_form.cleaned_data["caretaker02"]
            profile.caretaker03 = profile_form.cleaned_data["caretaker03"]
            profile.caretaker04 = profile_form.cleaned_data["caretaker04"]
            profile.caretaker05 = profile_form.cleaned_data["caretaker05"]
            profile.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            delete_images_flg = profile_form.cleaned_data.get('delete_images_flg')
            themes_data = request.FILES.get("themes")
            delete_themes_flg = profile_form.cleaned_data.get('delete_themes_flg')

            if images_data: # File Selected
                logger.debug('images_data exists')
                profile.images = update_images(profile, images_data)
            elif delete_images_flg and profile.images:
                logger.debug('delete_images exists')
                delete_images(profile)
                profile.images = None

            if themes_data: # File Selected
                logger.debug(f'themes_data exists={themes_data}')
                profile.themes = update_themes(profile, themes_data)
            elif delete_themes_flg and profile.themes:
                logger.debug('delete_themes exists')
                delete_themes(profile)
                profile.themes = None

            try:
                logger.debug('save updated Profile object')
                profile.save()
            except Exception as e:
                logger.error(f'couldnt save the Profile object: {e}')

            logger.info('return redirect user:list')
            return redirect('user:list')
        else:
            logger.error('form not is_valid')
            logger.error(profile_form.errors)
    else:
        logger.info('GET method') 
        profile_form = ProfileForm(instance=profile) # putback the form
        context = {'object': profile, 'user_form': user_form, 'profile_form': profile_form}

    logger.info('return render user/update.html')
    return render(request, 'user/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Profile delete_view')
    
    logger.debug('get Profile object(pk)')
    profile = get_object_or_404(Profile, pk=pk)

    context = {'object': profile}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if profile.images:
            logger.debug('old images_data exists')
            profile = delete_images(profile)

        # **古いファイルを削除**
        if profile.themes:
            logger.debug('old themes_data exists')
            profile = delete_themes(profile)

        try:
            logger.debug('delete old Profile object')
            profile.delete()
        except Exception as e:
            logger.error(f'couldnt delete Profile object: {e}')

        logger.info('return redirect user:list')
        return redirect('user:list')
    else:
        logger.info('GET method')

    logger.info('return render user/delete.html')
    return render(request, 'user/delete.html', context)

@csrf_exempt  # 関数デコレータに変更
@login_required
def given_likes(request, pk):
    logger.info('start User given_likes')

    if request.method == 'POST':
        logger.info('POST method')

        user = get_object_or_404(User, id=pk)
        logger.debug(f'get User object(pk)={user}')

        # いいね処理を実行
        user.given_likes(request)

        # Ajaxにいいね数を返す
        logger.info(f'return likes:({user.likes})')
        return JsonResponse({'likes': f'({user.likes})'})

    logger.info(f'return Invalid request:status=400')
    return JsonResponse({'error': 'Invalid request'}, status=400)

def checkin_calendar_view(request):
    from place.models import CheckinRecord

    profile = request.user.profile
    now = timezone.now()
    one_month_ago = now - timezone.timedelta(days=30)

    # チェックイン履歴を取得
    records = (
        CheckinRecord.objects
        .filter(profile=profile, checkin_time__gte=one_month_ago)
        .order_by('checkin_time')
    )

    events = []
    for record in records:
        checkin = record.checkin_time
        checkout = record.checkout_time or now
        events.append({
            "title": f"Check-in at {record.place.place}",
            "start": checkin.isoformat(),
            "end": checkout.isoformat()
        })

    return render(request, "profile/checkin_visual.html", {
        "events_json": json.dumps(events)
    })
