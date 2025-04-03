from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.models import Profile
from .models import Friend
from AinoteProject.utils import disp_qr_code
import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

@login_required
def list_view(request, page_cnt=1):
    logger.debug('start Friend list_view')

    page_size = 15 # disply page size
    onEachSide = 2 # display how many pages around current page
    onEnds = 2 # display how many pages on first/last edge
 
    try:
        page_cnt = int(request.GET.get("page_cnt", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page_cnt = 1
    
    try:
        login_profile = Profile.objects.get(user1=request.user)
        logger.debug(f'login_profile={login_profile}')
    except Profile.DoesNotExist:
        logger.warning(f'Profile not found for user: {request.user}')
        login_profile = None

    if login_profile:
        object_list = Friend.objects.filter( Q(profile1=login_profile) | Q(profile2=login_profile) ).order_by('-created_at')
        logger.debug(f'object_list={object_list}')
    else:
        object_list = Friend.objects.none()

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

    context = {'display_object_list': display_object_list, 'link_object_list': link_object_list, 'login_profile': login_profile}

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
    except ValueError:
        logger.debug('couldnt catch target profile_id')
        profile_id = 1

    try:
        profile_with = get_object_or_404(Profile, id=profile_id) # get target profile instance
        logger.debug(f'profile_with={profile_with}')
    except Exception as e:
        logger.error(f'couldnt get target profile_with id={profile_id}: {e}')

    context = {'profile_own': profile_own, 'profile_with': profile_with}

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

        try:
            # 順序を考慮して登録
            if profile1.id < profile2.id:
                friend = Friend.objects.create(profile1=profile1, profile2=profile2)
            else:
                friend = Friend.objects.create(profile1=profile2, profile2=profile1)
            logger.debug(f"{friend.profile1} - {friend.profile2}")
        except Exception as e:
            logger.error(f'couldnt create friend object profile1={profile1} profile2={profile2}: {e}')

        logger.info('return redirect friend:list')
        return redirect('friend:list')
    else:
        logger.info('GET method')
        pass

    logger.info('return render friend/create.html')
    return render(request, 'friend/create.html', context)

@login_required
def delete_view(request, pk):
    logger.info('start Friend delete_view')

    logger.debug('get Friend object(pk)')
    object = get_object_or_404(Friend, pk=pk)

    form = Friend() # 取得はするが使用しない
    context = {'object': object, 'form': form}

    logger.info('return render chat/delete.html')
    return render(request, 'chat/delete.html', context)


@login_required
def disp_friend_qr_view(request):
    logger.info('start Friend disp_qr_view')

    profile_id = request.GET.get("profile_id")
    base_url = f"{settings.SITE_DOMAIN}/friend/create/?profile_id="
    url_for_qr = f"{base_url}{profile_id}"
    logger.info(f'url_for_qr={ url_for_qr }')
    
    return disp_qr_code(url_for_qr)
