from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes
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
        object_list = Profile.objects.filter(
            Q(nick_name__icontains=search_str)
        )
    else:
        object_list = Profile.objects.all()

    # 並び替え処理
    sort_options = {
        "nick_name_asc": "nick_name",
        "nick_name_desc": "-nick_name",
        "created_asc": "created_at",
        "created_desc": "-created_at",
        "updated_asc": "updated_at",
        "updated_desc": "-updated_at",
    }
    sort_by = request.GET.get("sort_by", "nick_name_asc")
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
        'search_str': search_str,
        'sort_by': sort_by,
    }

    logger.info('return render user/list.html')
    return render(request, 'user/list.html', context)


def detail_view(request, pk):
    logger.info('start detail_view')

    logger.debug('get Profile object(pk)')
    object = get_object_or_404(Profile, pk=pk)

    # 最新の5件のチャットを取得
    recent_chats = object.get_chats_by_count(5)

    # 最新の5件のログイン情報を取得
    recent_login_records = object.get_login_records(5)

    # 所属しているすべてのグループを取得
    joined_groups = object.get_all_groups

    # すべてのFriendを取得
    friends = object.get_friend_profiles

    context = {'object': object, 'recent_chats': recent_chats, 'recent_login_records': recent_login_records, 'joined_groups': joined_groups, 'friends': friends}

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
            caretaker01_data = profile_form.cleaned_data["caretaker01"]
            caretaker02_data = profile_form.cleaned_data["caretaker02"]
            caretaker03_data = profile_form.cleaned_data["caretaker03"]
            caretaker04_data = profile_form.cleaned_data["caretaker04"]
            caretaker05_data = profile_form.cleaned_data["caretaker05"]
            pic_data = request.user.profile

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get("themes")

            try:
                object = Profile.objects.create(
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
                object.images = create_images(object, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                object.themes = create_themes(object, themes_data)

            try:
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data in Profile object: {e}')
            
            logger.info('return redirect user:list')
            return redirect('user:list')
        else:
            logger.error('user-form or profile_form is invalid.')
            print(user_form.errors)  # エラー内容をログに出力
            print(profile_form.errors)  # エラー内容をログに出力
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
    object = get_object_or_404(Profile, pk=pk)

    user_form = UserCreateForm({
        'id': object.user1.id,
        'username': object.user1.username,
    })
    
    if request.method == "POST":
        logger.info('POST method')

        # POSTデータから `mbti` を取得
        mbti_value = request.POST.get('mbti', object.mbti)
        
        profile_form = ProfileForm(request.POST, request.FILES)
        profile_form.fields['mbti_name'].choices = Profile.MBTI_NAME_CHOICES.get(mbti_value, [("", "---------")])
        
        context = {'object': object, 'user_form': user_form, 'profile_form': profile_form}

        if profile_form.is_valid():
            logger.debug('form.is_valid')

            object.memberid = profile_form.cleaned_data["memberid"]
            object.nick_name = profile_form.cleaned_data["nick_name"]
            object.badges = profile_form.cleaned_data["badges"]
            object.birth_year = profile_form.cleaned_data["birth_year"]
            if object.birth_year == '': object.birth_year = None
            object.birth_month_day = profile_form.cleaned_data["birth_month_day"]
            object.mbti = profile_form.cleaned_data["mbti"]
            object.mbti_name = profile_form.cleaned_data["mbti_name"]
            object.hobby = profile_form.cleaned_data["hobby"]
            object.sports = profile_form.cleaned_data["sports"]
            object.movie = profile_form.cleaned_data["movie"]
            object.music = profile_form.cleaned_data["music"]
            object.book = profile_form.cleaned_data["book"]
            object.event = profile_form.cleaned_data["event"]
            object.remarks = profile_form.cleaned_data["remarks"]
            object.caretaker01 = profile_form.cleaned_data["caretaker01"]
            object.caretaker02 = profile_form.cleaned_data["caretaker02"]
            object.caretaker03 = profile_form.cleaned_data["caretaker03"]
            object.caretaker04 = profile_form.cleaned_data["caretaker04"]
            object.caretaker05 = profile_form.cleaned_data["caretaker05"]
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
                logger.debug('save updated Profile object')
                object.save()
            except Exception as e:
                logger.error(f'couldnt save the Profile object: {e}')

            logger.info('return redirect user:list')
            return redirect('user:list')
        else:
            logger.error('form not is_valid')
            print(profile_form.errors)  # エラー内容をログに出力
    else:
        logger.info('GET method')  
        profile_form = ProfileForm(instance=object) # putback the form
        context = {'object': object, 'user_form': user_form, 'profile_form': profile_form}

    logger.info('return render user/update.html')
    return render(request, 'user/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Profile delete_view')
    
    logger.debug('get Profile object(pk)')
    object = get_object_or_404(Profile, pk=pk)

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
            logger.debug('delete old Profile object')
            object.delete()
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
