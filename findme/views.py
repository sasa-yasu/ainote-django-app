from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes
from user.models import Profile
from .forms import FindMeForm
from .models import FindMe, Poke, Notification

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

def get_mbti_name_choices(request):
    logger.debug('start FindMe get_mbti_name_choices')
    
    mbti = request.GET.get('mbti')
    mbti_name_choices = Profile.MBTI_NAME_CHOICES.get(mbti, [])
    logger.debug(f'mbti_name_choices={mbti_name_choices}')

    return JsonResponse({'mbti_name_choices': list(mbti_name_choices)})

def list_view(request):
    logger.debug('start FindMe list_view')

    page_size = 48 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    # フリーワード検索用
    search_str = request.GET.get("search_str", "")
    logger.debug(f'Searching for: {search_str}')
    if search_str:
        object_list = FindMe.objects.filter(
            Q(name__icontains=search_str) |
            Q(living_area__icontains=search_str) |
            Q(overview__icontains=search_str)
        )
    else:
        object_list = FindMe.objects.all()

    # 検索条件オープン状態保持向け
    open_sections = request.GET.get("open_sections", "")
    logger.debug(f'open_sections: {open_sections}')

    # 性別フィルタ用
    search_gender = request.GET.getlist("search_gender", "")
    logger.debug(f'search_gender: {search_gender}')
    if search_gender: object_list = FindMe.filter_findme_object(object_list, search_gender, 'gender', FindMe.GENDER_CHOICES)

    # hobbyフィルタ用
    search_hobby = request.GET.getlist("search_hobby", "")
    logger.debug(f'search_hobby: {search_hobby}')
    if search_hobby: object_list = FindMe.filter_findme_object(object_list, search_hobby, 'hobby', FindMe.HOBBY_CHOICES)

    # foodフィルタ用
    search_food = request.GET.getlist("search_food", "")
    logger.debug(f'search_food: {search_food}')
    if search_food: object_list = FindMe.filter_findme_object(object_list, search_food, 'food', FindMe.FOOD_CHOICES)

    # musicフィルタ用
    search_music = request.GET.getlist("search_music", "")
    logger.debug(f'search_music: {search_music}')
    if search_music: object_list = FindMe.filter_findme_object(object_list, search_music, 'music', FindMe.MUSIC_CHOICES)

    # movieフィルタ用
    search_movie = request.GET.getlist("search_movie", "")
    logger.debug(f'search_movie: {search_movie}')
    if search_movie: object_list = FindMe.filter_findme_object(object_list, search_movie, 'movie', FindMe.MOVIE_CHOICES)

    # bookフィルタ用
    search_book = request.GET.getlist("search_book", "")
    logger.debug(f'search_book: {search_book}')
    if search_book: object_list = FindMe.filter_findme_object(object_list, search_book, 'book', FindMe.BOOK_CHOICES)

    # personality_typeフィルタ用
    search_personality_type = request.GET.getlist("search_personality_type", "")
    logger.debug(f'search_personality_type: {search_personality_type}')
    if search_personality_type: object_list = FindMe.filter_findme_object(object_list, search_personality_type, 'personality_type', FindMe.PERSONALITY_TYPE_CHOICES)

    # favorite_dateフィルタ用
    search_favorite_date = request.GET.getlist("search_favorite_date", "")
    logger.debug(f'search_favorite_date: {search_favorite_date}')
    if search_favorite_date: object_list = FindMe.filter_findme_object(object_list, search_favorite_date, 'favorite_date', FindMe.FAVORITE_DATE_CHOICES)

    # sense_of_valuesフィルタ用
    search_sense_of_values = request.GET.getlist("search_sense_of_values", "")
    logger.debug(f'search_sense_of_values: {search_sense_of_values}')
    if search_sense_of_values: object_list = FindMe.filter_findme_object(object_list, search_sense_of_values, 'sense_of_values', FindMe.SENSE_OF_VALUES_CHOICES)

    # future_planフィルタ用
    search_future_plan = request.GET.getlist("search_future_plan", "")
    logger.debug(f'search_future_plan: {search_future_plan}')
    if search_future_plan: object_list = FindMe.filter_findme_object(object_list, search_future_plan, 'future_plan', FindMe.FUTURE_PLAN_CHOICES)

    # request_for_partnerフィルタ用
    search_request_for_partner = request.GET.getlist("search_request_for_partner", "")
    logger.debug(f'search_request_for_partner: {search_request_for_partner}')
    if search_request_for_partner: object_list = FindMe.filter_findme_object(object_list, search_request_for_partner, 'request_for_partner', FindMe.REQUEST_FOR_PARTNER_CHOICES)

    # weekend_activityフィルタ用
    search_weekend_activity = request.GET.getlist("search_weekend_activity", "")
    logger.debug(f'search_weekend_activity: {search_weekend_activity}')
    if search_weekend_activity: object_list = FindMe.filter_findme_object(object_list, search_weekend_activity, 'weekend_activity', FindMe.WEEKEND_ACTIVITY_CHOICES)

    # ongoing_projectフィルタ用
    search_ongoing_project = request.GET.getlist("search_ongoing_project", "")
    logger.debug(f'search_ongoing_project: {search_ongoing_project}')
    if search_ongoing_project: object_list = FindMe.filter_findme_object(object_list, search_ongoing_project, 'ongoing_project', FindMe.ONGOING_PROJECT_CHOICES)

    # social_activityフィルタ用
    search_social_activity = request.GET.getlist("search_social_activity", "")
    logger.debug(f'search_social_activity: {search_social_activity}')
    if search_social_activity: object_list = FindMe.filter_findme_object(object_list, search_social_activity, 'social_activity', FindMe.SOCIAL_ACTIVITY_CHOICES)

    # free_dayフィルタ用
    search_free_day = request.GET.getlist("search_free_day", "")
    logger.debug(f'search_free_day: {search_free_day}')
    if search_free_day: object_list = FindMe.filter_findme_object(object_list, search_free_day, 'free_day', FindMe.FREE_DAY_CHOICES)

    # proudest_achievementsフィルタ用
    search_proudest_achievements = request.GET.getlist("search_proudest_achievements", "")
    logger.debug(f'search_proudest_achievements: {search_proudest_achievements}')
    if search_proudest_achievements: object_list = FindMe.filter_findme_object(object_list, search_proudest_achievements, 'proudest_achievements', FindMe.PROUDEST_ACHIEVEMENTS_CHOICES)

    # most_important_valuesフィルタ用
    search_most_important_values = request.GET.getlist("search_most_important_values", "")
    logger.debug(f'search_most_important_values: {search_most_important_values}')
    if search_most_important_values: object_list = FindMe.filter_findme_object(object_list, search_most_important_values, 'most_important_values', FindMe.MOST_IMPORTANT_VALUES_CHOICES)

    # 並び替え処理
    sort_options = {
        "name_asc": "name",
        "name_desc": "-name",
        "created_asc": "created_at",
        "created_desc": "-created_at",
        "updated_asc": "updated_at",
        "updated_desc": "-updated_at",
    }
    sort_by = request.GET.get("sort_by", "name_asc")
    logger.debug(f'Sort by: {sort_by}')
    sort_field = sort_options.get(sort_by, "-id")  # デフォルトは -id
    object_list = object_list.order_by(sort_field)

    if object_list.exists():
        logger.debug('object_list exists')
        paginator = Paginator(object_list, page_size)
        try:
            display_object_list = paginator.page(page_cnt)
        except:
            logger.warning('couldnt catch the display_object_list page_cnt=', page_cnt)
            display_object_list = paginator.page(1)        
        link_object_list = display_object_list.paginator.get_elided_page_range(
            page_cnt, on_each_side=onEachSide, on_ends=onEnds
        )
    else:
        logger.debug('object_list not exists')
        display_object_list = []
        link_object_list = []

    context = {
        'display_object_list': display_object_list,
        'link_object_list': link_object_list,
        'open_sections': open_sections,
        'search_gender': search_gender,
        'search_hobby': search_hobby,
        'search_food': search_food,
        'search_music': search_music,
        'search_movie': search_movie,
        'search_book': search_book,
        'search_personality_type': search_personality_type,
        'search_favorite_date': search_favorite_date,
        'search_sense_of_values': search_sense_of_values,
        'search_future_plan': search_future_plan,
        'search_request_for_partner': search_request_for_partner,
        'search_weekend_activity': search_weekend_activity,
        'search_ongoing_project': search_ongoing_project,
        'search_social_activity': search_social_activity,
        'search_free_day': search_free_day,
        'search_proudest_achievements': search_proudest_achievements,
        'search_most_important_values': search_most_important_values,
        'search_str': search_str,
        'sort_by': sort_by,
    }

    # add all CHOICES for input / display
    context = FindMe.get_all_choices(context)

    logger.info('return render findme/list.html')
    return render(request, 'findme/list.html', context)


def detail_view(request, pk):
    logger.info('start detail_view')

    logger.debug('get FindMe object(pk)')
    object = get_object_or_404(FindMe, pk=pk)

    context = {'object': object}

    # add all CHOICES for input / display
    context = FindMe.get_all_choices(context)

    context.update({'notifications': object.get_all_notifications})

    logger.debug('return render findme/detail.html')
    return render(request, 'findme/detail.html', context)

@login_required
def create_view(request): 
    logger.info('start FindMe create_view')

    logger.debug('get Profile object(pk)')
    login_profile = get_object_or_404(Profile, pk=request.user.profile.id)

    if request.method == "POST":
        logger.info('POST method')

        # POSTデータから `mbti` を取得
        mbti_value = request.POST.get('mbti')

        findme_form = FindMeForm(request.POST, request.FILES)
        findme_form.fields['mbti_name'].choices = Profile.MBTI_NAME_CHOICES.get(mbti_value, [("", "---------")])

        context = {'findme_form': findme_form}

        if findme_form.is_valid():
            logger.debug('FindMe form.is_valid')

            name_data = findme_form.cleaned_data["name"]
            gender_data = findme_form.cleaned_data["gender"]
            birth_year_data = findme_form.cleaned_data["birth_year"]
            if birth_year_data == '': birth_year_data = None
            birth_month_day_data = findme_form.cleaned_data["birth_month_day"]
            living_pref_data = findme_form.cleaned_data["living_pref"]
            living_area_data = findme_form.cleaned_data["living_area"]
            mbti_data = findme_form.cleaned_data["mbti"]
            mbti_name_data = findme_form.cleaned_data["mbti_name"]

            overview_data = findme_form.cleaned_data["overview"]
            introduce_data = findme_form.cleaned_data["introduce"]

            hobby_choice_data = findme_form.cleaned_data["hobby_choice"]
            hobby_data = findme_form.cleaned_data["hobby"]
            food_choice_data = findme_form.cleaned_data["food_choice"]
            food_data = findme_form.cleaned_data["food"]
            music_choice_data = findme_form.cleaned_data["music_choice"]
            music_data = findme_form.cleaned_data["music"]
            movie_choice_data = findme_form.cleaned_data["movie_choice"]
            movie_data = findme_form.cleaned_data["movie"]
            book_choice_data = findme_form.cleaned_data["book_choice"]
            book_data = findme_form.cleaned_data["book"]

            personality_type_choice_data = findme_form.cleaned_data["personality_type_choice"]
            personality_type_data = findme_form.cleaned_data["personality_type"]
            favorite_date_choice_data = findme_form.cleaned_data["favorite_date_choice"]
            favorite_date_data = findme_form.cleaned_data["favorite_date"]
            sense_of_values_choice_data = findme_form.cleaned_data["sense_of_values_choice"]
            sense_of_values_data = findme_form.cleaned_data["sense_of_values"]

            future_plan_choice_data = findme_form.cleaned_data["future_plan_choice"]
            future_plan_data = findme_form.cleaned_data["future_plan"]
            request_for_partner_choice_data = findme_form.cleaned_data["request_for_partner_choice"]
            request_for_partner_data = findme_form.cleaned_data["request_for_partner"]

            weekend_activity_choice_data = findme_form.cleaned_data["weekend_activity_choice"]
            weekend_activity_data = findme_form.cleaned_data["weekend_activity"]
            ongoing_project_choice_data = findme_form.cleaned_data["ongoing_project_choice"]
            ongoing_project_data = findme_form.cleaned_data["ongoing_project"]
            social_activity_choice_data = findme_form.cleaned_data["social_activity_choice"]
            social_activity_data = findme_form.cleaned_data["social_activity"]

            free_day_choice_data = findme_form.cleaned_data["free_day_choice"]
            free_day_data = findme_form.cleaned_data["free_day"]
            proudest_achievements_choice_data = findme_form.cleaned_data["proudest_achievements_choice"]
            proudest_achievements_data = findme_form.cleaned_data["proudest_achievements"]
            most_important_values_choice_data = findme_form.cleaned_data["most_important_values_choice"]
            most_important_values_data = findme_form.cleaned_data["most_important_values"]

            contacts_data = findme_form.cleaned_data["contacts"]
            remarks_data = findme_form.cleaned_data["remarks"]
            pic_data = request.user.profile

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get("themes")

            try:
                object = FindMe.objects.create(
                    profile = login_profile,
                    name = name_data,
                    gender = gender_data,
                    birth_year = birth_year_data,
                    birth_month_day = birth_month_day_data,
                    living_pref = living_pref_data,
                    living_area = living_area_data,
                    mbti = mbti_data,
                    mbti_name = mbti_name_data,

                    overview = overview_data,
                    introduce = introduce_data,

                    hobby_choice = hobby_choice_data,
                    hobby = hobby_data,
                    food_choice = food_choice_data,
                    food = food_data,
                    music_choice = music_choice_data,
                    music = music_data,
                    movie_choice = movie_choice_data,
                    movie = movie_data,
                    book_choice = book_choice_data,
                    book = book_data,

                    personality_type_choice = personality_type_choice_data,
                    personality_type = personality_type_data,
                    favorite_date_choice = favorite_date_choice_data,
                    favorite_date = favorite_date_data,
                    sense_of_values_choice = sense_of_values_choice_data,
                    sense_of_values = sense_of_values_data,

                    future_plan_choice = future_plan_choice_data,
                    future_plan = future_plan_data,
                    request_for_partner_choice = request_for_partner_choice_data,
                    request_for_partner = request_for_partner_data,

                    weekend_activity_choice = weekend_activity_choice_data,
                    weekend_activity = weekend_activity_data,
                    ongoing_project_choice = ongoing_project_choice_data,
                    ongoing_project = ongoing_project_data,
                    social_activity_choice = social_activity_choice_data,
                    social_activity = social_activity_data,

                    free_day_choice = free_day_choice_data,
                    free_day = free_day_data,
                    proudest_achievements_choice = proudest_achievements_choice_data,
                    proudest_achievements = proudest_achievements_data,
                    most_important_values_choice = most_important_values_choice_data,
                    most_important_values = most_important_values_data,

                    contacts = contacts_data,
                    remarks = remarks_data,

                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the FindMe Object: {e}')
                logger.info('return render findme/create.html')
                return render(request, 'findme/create.html', context)

            if images_data:
                logger.debug('images_data exists')
                object.images = create_images(object, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                object.themes = create_themes(object, themes_data)

            try:
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data in FindMe object: {e}')
            
            logger.info('return redirect findme:list')
            return redirect('findme:list')
        else:
            logger.error('findme_form is invalid.')
            print(findme_form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')
        findme_form = FindMeForm()
        context = {'findme_form': findme_form}

    # add all CHOICES for input / display
    context = FindMe.get_all_choices(context)

    logger.info('return render findme/create.html')
    return render(request, 'findme/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start FindMe update_view')

    logger.debug('get FindMe object(pk)')
    object = get_object_or_404(FindMe, pk=pk)

    if request.method == "POST":
        logger.info('POST method')

        # POSTデータから `mbti` を取得
        mbti_value = request.POST.get('mbti', object.mbti)
        
        findme_form = FindMeForm(request.POST, request.FILES)
        findme_form.fields['mbti_name'].choices = Profile.MBTI_NAME_CHOICES.get(mbti_value, [("", "---------")])
        
        context = {'object': object, 'findme_form': findme_form}

        if findme_form.is_valid():
            logger.debug('form.is_valid')

            object.name = findme_form.cleaned_data["name"]
            object.gender = findme_form.cleaned_data["gender"]
            object.birth_year = findme_form.cleaned_data["birth_year"]
            if object.birth_year == '': object.birth_year = None
            object.birth_month_day = findme_form.cleaned_data["birth_month_day"]
            object.living_pref = findme_form.cleaned_data["living_pref"]
            object.living_area = findme_form.cleaned_data["living_area"]
            object.mbti = findme_form.cleaned_data["mbti"]
            object.mbti_name = findme_form.cleaned_data["mbti_name"]

            object.overview = findme_form.cleaned_data["overview"]
            object.introduce = findme_form.cleaned_data["introduce"]

            object.hobby_choice = findme_form.cleaned_data["hobby_choice"]
            object.hobby = findme_form.cleaned_data["hobby"]
            object.food_choice = findme_form.cleaned_data["food_choice"]
            object.food = findme_form.cleaned_data["food"]
            object.music_choice = findme_form.cleaned_data["music_choice"]
            object.music = findme_form.cleaned_data["music"]
            object.movie_choice = findme_form.cleaned_data["movie_choice"]
            object.movie = findme_form.cleaned_data["movie"]
            object.book_choice = findme_form.cleaned_data["book_choice"]
            object.book = findme_form.cleaned_data["book"]

            object.personality_type_choice = findme_form.cleaned_data["personality_type_choice"]
            object.personality_type = findme_form.cleaned_data["personality_type"]
            object.favorite_date_choice = findme_form.cleaned_data["favorite_date_choice"]
            object.favorite_date = findme_form.cleaned_data["favorite_date"]
            object.sense_of_values_choice = findme_form.cleaned_data["sense_of_values_choice"]
            object.sense_of_values = findme_form.cleaned_data["sense_of_values"]

            object.future_plan_choice = findme_form.cleaned_data["future_plan_choice"]
            object.future_plan = findme_form.cleaned_data["future_plan"]
            object.request_for_partner_choice = findme_form.cleaned_data["request_for_partner_choice"]
            object.request_for_partner = findme_form.cleaned_data["request_for_partner"]

            object.weekend_activity_choice = findme_form.cleaned_data["weekend_activity_choice"]
            object.weekend_activity = findme_form.cleaned_data["weekend_activity"]
            object.ongoing_project_choice = findme_form.cleaned_data["ongoing_project_choice"]
            object.ongoing_project = findme_form.cleaned_data["ongoing_project"]
            object.social_activity_choice = findme_form.cleaned_data["social_activity_choice"]
            object.social_activity = findme_form.cleaned_data["social_activity"]

            object.free_day_choice = findme_form.cleaned_data["free_day_choice"]
            object.free_day = findme_form.cleaned_data["free_day"]
            object.proudest_achievements_choice = findme_form.cleaned_data["proudest_achievements_choice"]
            object.proudest_achievements = findme_form.cleaned_data["proudest_achievements"]
            object.most_important_values_choice = findme_form.cleaned_data["most_important_values_choice"]
            object.most_important_values = findme_form.cleaned_data["most_important_values"]

            object.contacts = findme_form.cleaned_data["contacts"]
            object.remarks = findme_form.cleaned_data["remarks"]
            object.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get("themes")

            if images_data: # File Selected
                logger.debug('images_data exists')
                object.images = update_images(object, images_data)

            if themes_data: # File Selected
                logger.debug(f'themes_data exists={themes_data}')
                object.themes = update_themes(object, themes_data)

            try:
                logger.debug('save updated FindMe object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the FindMe object: {e}')

            logger.info('return redirect findme:list')
            return redirect('findme:list')
        else:
            logger.error('form not is_valid')
            print(findme_form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')  
        findme_form = FindMeForm(instance=object) # putback the form
        context = {'object': object, 'findme_form': findme_form}

    # add all CHOICES for input / display
    context = FindMe.get_all_choices(context)

    logger.info('return render findme/update.html')
    return render(request, 'findme/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start FindMe delete_view')
    
    logger.debug('get FindMe object(pk)')
    object = get_object_or_404(FindMe, pk=pk)

    context = {'object': object}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if object.images:
            logger.debug('old images_data exists')
            object = delete_images(object)

        # **古いファイルを削除**
        if object.themes:
            logger.debug('old themes_data exists')
            object = delete_themes(object)

        try:
            logger.debug('delete old FindMe object')
            object.delete()
        except Exception as e:
            logger.error(f'couldnt delete FindMe object: {e}')

        logger.info('return redirect findme:list')
        return redirect('findme:list')
    else:
        logger.info('GET method')

    # add all CHOICES for input / display
    context = FindMe.get_all_choices(context)

    logger.info('return render findme/delete.html')
    return render(request, 'findme/delete.html', context)


def send_poke(request, pk):
    logger.info('start FindMe send_poke')
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        sender = request.user.profile
        receiver = get_object_or_404(FindMe, id=pk)

        # 今日の日付の開始時間を取得（00:00）
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 今日poke済みか確認
        already_poked_today = Poke.objects.filter(
            sender=sender,
            receiver=receiver,
            created_at__gte=today_start
        ).exists()

#        if already_poked_today:
        if 0>1:
            logger.debug(f'今日はすでにPoke済です。')
    #        messages.info(request, 'すでに Poke 済みです。')
        else:
            # 初めての poke
            logger.debug(f'Pokeしました！')
            Poke.objects.create(sender=sender, receiver=receiver)
    #        messages.success(request, 'Poke を送りました！')
            Notification.objects.create(
                recipient=receiver,
                sender=request.user.profile,
                message=f"{request.user.profile.nick_name} さんからPokeされました！"
            )

    logger.info(f'JsonResponse:{receiver.poke_count}')
    return JsonResponse({'poke_count': receiver.poke_count})
