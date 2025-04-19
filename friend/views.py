from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Value, CharField, Case, When, F
from user.models import Profile
from .models import Friend
from AinoteProject.utils import disp_qr_code
import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

@login_required
def list_view(request, page=1):
    logger.debug('start Friend list_view')

    PAGE_SIZE = 48 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    try:
        login_profile = Profile.objects.get(user1=request.user)
        logger.debug(f'login_profile={login_profile}')
        object_list = Friend.objects.filter(
            Q(profile1=login_profile) | Q(profile2=login_profile)
        ).annotate(
            nick_name=Case(
                When(profile1=login_profile, then=F('profile2__nick_name')),
                When(profile2=login_profile, then=F('profile1__nick_name')),
                default=Value(''),  # 念のため
                output_field=CharField()
            )
        )
        logger.debug(f'object_list={object_list}')
    except Profile.DoesNotExist:
        logger.warning(f'Profile not found for user: {request.user}')
        login_profile = None
        object_list = Friend.objects.none()

     # フリーワード検索用
    search_str = request.GET.get("search_str", "")
    logger.debug(f'Searching for: {search_str}')
    if search_str:
        object_list = object_list.filter(nick_name__icontains=search_str)

    # 並び替え処理
    sort_options = {
        "created_desc": "-created_at",
        "created_asc": "created_at",
        "nick_name_asc": "nick_name",
        "nick_name_desc": "-nick_name",
    }
    sort_by = request.GET.get("sort_by", "created_desc")
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
        'login_profile': login_profile,
        'search_str': search_str,
        'sort_by': sort_by,
    }

    logger.info('return render friend/list.html')
    return render(request, 'friend/list.html', context)


@login_required
def create_view(request):
    logger.info('start Friend create_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # profile_with = friend target
    try:
        profile_id = int(request.GET.get("profile_id", 1)) # get profile_id from URL query
        profile_with = get_object_or_404(Profile, id=profile_id) # get target profile instance
        logger.debug(f'profile_with={profile_with}')
    except ValueError:
        logger.debug('couldnt catch target profile_id')
        logger.error(f'couldnt get target profile_with id={profile_id}: {e}')
        profile_id = 1

    context = {'profile_own': profile_own, 'profile_with': profile_with}

    # 既存Friendチェック
    if Friend.objects.filter(profile1=profile_own, profile2=profile_with).exists() or Friend.objects.filter(profile1=profile_with, profile2=profile_own).exists():
        context.update({'errors': f'You two are already friends'})
        logger.info('friend already exists')
        return render(request, 'friend/create.html', context)
    else:
        earn_points = profile_own.get_earn_points_for_make_friend(profile_with)
        context.update({'points': f'You get points for this make-frined. Your [Status Point]: {profile_own.status_points:,} + {earn_points} pt'}) # 1日に1ポイント獲得後のメッセージ表示

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報から2つのProfileを取得(ACCEPTを押下されたもののみ)
        profile1_id = request.POST["profile_own_id"]
        logger.debug(f'POST profile_own_id={profile1_id}')
        profile1 = get_object_or_404(Profile, id=profile1_id)
        logger.debug(f'POST profile_own={profile1}')

        profile2_id = request.POST["profile_with_id"]
        logger.debug(f'POST profile_with_id={profile2_id}')
        profile2 = get_object_or_404(Profile, id=profile2_id)
        logger.debug(f'POST profile_with={profile2}')

        pic_data = request.user.profile

        try:
            # 順序を考慮して登録
            if profile1.id < profile2.id:
                friend = Friend.objects.create(profile1=profile1, profile2=profile2, created_pic = pic_data)
            else:
                friend = Friend.objects.create(profile1=profile2, profile2=profile1, created_pic = pic_data)
            logger.debug(f"{friend.profile1} - {friend.profile2}")

            earn_points = profile1.earn_points_for_make_friend(profile2)
            context.update({'points': f'You got points for make-frined. Your [Status Point]: {profile_own.status_points:,}(+{earn_points}) pt'}) # 1日に1ポイント獲得後のメッセージ表示

        except Exception as e:
            logger.error(f'couldnt create friend object profile1={profile1} profile2={profile2}: {e}')

        logger.info('return redirect user:detail')
        return redirect('user:detail', profile_with.id)
    else:
        logger.info('GET method')
        pass

    logger.info('return render friend/create.html')
    return render(request, 'friend/create.html', context)

@login_required
def delete_view(request, pk):
    logger.info('start Friend delete_view')

    logger.debug('get Friend object(pk)')
    friend = get_object_or_404(Friend, pk=pk)
    profile_own = request.user.profile

    if friend.profile1 == profile_own:
        profile_with = friend.profile2
    elif friend.profile2 == profile_own:
        profile_with = friend.profile1
    else:
        logger.info('not include request user.')

        logger.info('return redirect friend:list')
        return redirect('friend:list')
    
    form = Friend() # 取得はするが使用しない
    
    context = {'profile_own': profile_own, 'profile_with': profile_with}

    # 既存Friendチェック
    if Friend.objects.filter(profile1=profile_own, profile2=profile_with).exists() or Friend.objects.filter(profile1=profile_with, profile2=profile_own).exists():
        lose_points = profile_own.get_lose_points_for_remove_friend(profile_with)
        context.update({'points': f'You lose points for this remove-frined. Your [Status Point]: {profile_own.status_points:,} - {lose_points} pt'}) # 1日に1ポイント獲得後のメッセージ表示
    else:
        context.update({'errors': f'You two are already friends'})
        logger.info('friend already exists')
        return render(request, 'friend/create.html', context)

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報から2つのProfileを取得(REMOVEを押下されたもののみ)
        profile1_id = request.POST["profile_own_id"]
        logger.debug(f'POST profile_own_id={profile1_id}')
        profile1 = get_object_or_404(Profile, id=profile1_id)
        logger.debug(f'POST profile_own={profile1}')

        profile2_id = request.POST["profile_with_id"]
        logger.debug(f'POST profile_with_id={profile2_id}')
        profile2 = get_object_or_404(Profile, id=profile2_id)
        logger.debug(f'POST profile_with={profile2}')

        try:
            # 順序を考慮して登録
            if profile1.id < profile2.id:
                friend = Friend.objects.get(profile1=profile1, profile2=profile2)
            else:
                friend = Friend.objects.get(profile1=profile2, profile2=profile1)
            logger.debug(f"{friend.profile1} - {friend.profile2}")
            friend.delete()

            lose_points = profile1.lose_points_for_remove_friend(profile2)
            context.update({'points': f'You got points for make-frined. Your [Status Point]: {profile_own.status_points:,}(+{lose_points}) pt'}) # 1日に1ポイント獲得後のメッセージ表示

        except Exception as e:
            logger.error(f'couldnt delete friend object profile1={profile1} profile2={profile2}: {e}')

        logger.info('return redirect friend:list')
        return redirect('friend:list')
    
    else:
        logger.info('GET method')
        pass

    logger.info('return render friend/delete.html')
    return render(request, 'friend/delete.html', context)


@login_required
def disp_friend_qr_view(request):
    logger.info('start Friend disp_qr_view')

    profile_id = request.GET.get("profile_id")
    base_url = f"{settings.SITE_DOMAIN}/friend/create/?profile_id="
    url_for_qr = f"{base_url}{profile_id}"
    logger.info(f'url_for_qr={ url_for_qr }')
    
    return disp_qr_code(url_for_qr)
