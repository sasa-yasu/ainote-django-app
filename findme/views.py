from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes
from user.models import Profile
from .forms import FindMeForm
from .models import FindMe

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

    findme_own = FindMe.objects.filter(profile=request.user.profile).first()

    context = {
        'display_object_list': display_object_list,
        'link_object_list': link_object_list,
        'search_str': search_str,
        'sort_by': sort_by,
        'findme_own': findme_own,
    }

    logger.info('return render findme/list.html')
    return render(request, 'findme/list.html', context)


def detail_view(request, pk):
    logger.info('start detail_view')

    logger.debug('get FindMe object(pk)')
    object = get_object_or_404(FindMe, pk=pk)

    context = {'object': object}

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
            living_area_data = findme_form.cleaned_data["living_area"]
            mbti_data = findme_form.cleaned_data["mbti"]
            mbti_name_data = findme_form.cleaned_data["mbti_name"]
            overview_data = findme_form.cleaned_data["overview"]
            introduce_data = findme_form.cleaned_data["introduce"]
            hobby_data = findme_form.cleaned_data["hobby"]
            food_data = findme_form.cleaned_data["food"]
            music_data = findme_form.cleaned_data["music"]
            movie_data = findme_form.cleaned_data["movie"]
            book_data = findme_form.cleaned_data["book"]
            favorite_type_data = findme_form.cleaned_data["favorite_type"]
            favorite_date_data = findme_form.cleaned_data["favorite_date"]
            sense_of_values_data = findme_form.cleaned_data["sense_of_values"]
            future_plan_data = findme_form.cleaned_data["future_plan"]
            request_for_partner_data = findme_form.cleaned_data["request_for_partner"]
            weekend_activity_data = findme_form.cleaned_data["weekend_activity"]
            on_going_project_data = findme_form.cleaned_data["on_going_project"]
            on_going_event_data = findme_form.cleaned_data["on_going_event"]
            what_you_want_to_do_data = findme_form.cleaned_data["what_you_want_to_do"]
            most_proud_event_data = findme_form.cleaned_data["most_proud_event"]
            what_you_value_most_data = findme_form.cleaned_data["what_you_value_most"]
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
                    living_area = living_area_data,
                    mbti = mbti_data,
                    mbti_name = mbti_name_data,
                    overview = overview_data,
                    introduce = introduce_data,
                    hobby = hobby_data,
                    food = food_data,
                    music = music_data,
                    movie = movie_data,
                    book = book_data,
                    favorite_type = favorite_type_data,
                    favorite_date = favorite_date_data,
                    sense_of_values = sense_of_values_data,
                    future_plan = future_plan_data,
                    request_for_partner = request_for_partner_data,
                    weekend_activity = weekend_activity_data,
                    on_going_project = on_going_project_data,
                    on_going_event = on_going_event_data,
                    what_you_want_to_do = what_you_want_to_do_data,
                    most_proud_event = most_proud_event_data,
                    what_you_value_most = what_you_value_most_data,
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
            object.living_area = findme_form.cleaned_data["living_area"]
            object.mbti = findme_form.cleaned_data["mbti"]
            object.mbti_name = findme_form.cleaned_data["mbti_name"]

            object.overview = findme_form.cleaned_data["overview"]
            object.introduce = findme_form.cleaned_data["introduce"]

            object.hobby = findme_form.cleaned_data["hobby"]
            object.food = findme_form.cleaned_data["food"]
            object.music = findme_form.cleaned_data["music"]
            object.movie = findme_form.cleaned_data["movie"]
            object.book = findme_form.cleaned_data["book"]

            object.favorite_type = findme_form.cleaned_data["favorite_type"]
            object.favorite_date = findme_form.cleaned_data["favorite_date"]
            object.sense_of_values = findme_form.cleaned_data["sense_of_values"]

            object.future_plan = findme_form.cleaned_data["future_plan"]
            object.request_for_partner = findme_form.cleaned_data["request_for_partner"]

            object.weekend_activity = findme_form.cleaned_data["weekend_activity"]
            object.on_going_project = findme_form.cleaned_data["on_going_project"]
            object.on_going_event = findme_form.cleaned_data["on_going_event"]

            object.what_you_want_to_do = findme_form.cleaned_data["what_you_want_to_do"]
            object.most_proud_event = findme_form.cleaned_data["most_proud_event"]
            object.what_you_value_most = findme_form.cleaned_data["what_you_value_most"]

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

    logger.info('return render findme/delete.html')
    return render(request, 'findme/delete.html', context)
