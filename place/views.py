from django.conf import settings
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from AinoteProject.utils import haversine, disp_qr_code
from AinoteProject.utils import create_images, update_images, delete_images, create_themes, update_themes, delete_themes, safe_json_post
from user.models import Profile
from .forms import PlaceForm
from .models import Place, CheckinRecord

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')


def list_view(request, page=1):
    logger.debug('start Place list_view')

    PAGE_SIZE = 15 # disply page size
    PAGINATION_ON_EACH_SIDE = 2 # display how many pages around current page
    PAGINATION_ON_ENDS = 2 # display how many pages on first/last edge
 
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        logger.debug('couldnt catch the page cnt')
        page = 1
    
    object_list = Place.objects.order_by('-id')

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

    context = {'display_object_list': display_object_list, 'link_object_list': link_object_list}

    logger.info('return render place/list.html')
    return render(request, 'place/list.html', context)


def detail_view(request, pk):
    logger.info('start detail_view')

    logger.debug('get Place object(pk)')
    place = get_object_or_404(Place, pk=pk)

    # 現座のログイン状態ログインを取得
    recent_checkin_statuses = place.get_checkin_status

    # 最新の100件のログインを取得
    recent_checkin_records = place.get_checkin_records_by_count(100)

    context = {'object': place, 'recent_checkin_statuses': recent_checkin_statuses, 'recent_checkin_records': recent_checkin_records}

    logger.debug('return render place/detail.html')
    return render(request, 'place/detail.html', context)

@login_required
def create_view(request): 
    logger.info('start Place create_view')

    if request.method == "POST":
        logger.info('POST method')

        form = PlaceForm(request.POST, request.FILES)
        context = {'form': form}

        if form.is_valid():
            logger.debug('Place form.is_valid')

            place_data = form.cleaned_data["place"]

            images_data = request.FILES.get("images")
            themes_data = request.FILES.get('themes')
            
            area_data = form.cleaned_data["area"]
            overview_data = form.cleaned_data["overview"]
            address_data = form.cleaned_data["address"]
            tel_data = form.cleaned_data["tel"]
            url_data = form.cleaned_data["url"]
            context_data = form.cleaned_data["context"]
            remarks_data = form.cleaned_data["remarks"]
            schedule_monthly_data = form.cleaned_data['schedule_monthly']
            schedule_weekly_data = form.cleaned_data['schedule_weekly']
            latitude_data = form.cleaned_data["latitude"]
            longitude_data = form.cleaned_data["longitude"]
            googlemap_url_data = form.cleaned_data["googlemap_url"]
            pic_data = request.user.profile

            try:
                place = Place.objects.create(
                    place = place_data,
                    images = None, # 画像はまだ保存しない
                    themes = None, # 画像はまだ保存しない
                    area = area_data,
                    overview = overview_data,
                    address = address_data,
                    tel = tel_data,
                    url = url_data,
                    context = context_data,
                    remarks = remarks_data,
                    schedule_monthly = schedule_monthly_data,
                    schedule_weekly = schedule_weekly_data,
                    latitude = latitude_data,
                    longitude = longitude_data,
                    googlemap_url = googlemap_url_data,
                    created_pic = pic_data,
                    updated_pic = pic_data,
                )
            except Exception as e:
                logger.error(f'couldnt create the Place Object: {e}')
                logger.info('return render place/create.html')
                return render(request, 'place/create.html', context)

            if images_data:
                logger.debug('images_data exists')
                place.images = create_images(place, images_data)

            if themes_data:
                logger.debug('themes_data exists')
                place.themes = create_themes(place, themes_data)

            try:
                place.save()
            except Exception as e:
                logger.error(f'couldnt save the images_data / themes_data in Place object: {e}')
            
            logger.info('return redirect place:list')
            return redirect('place:list')
        else:
            logger.error('form is invalid.')
            logger.error(form.errors)
    else:
        logger.info('GET method')
        form = PlaceForm()
        context = {'form': form}

    logger.info('return render place/create.html')
    return render(request, 'place/create.html', context)
    

@login_required
def update_view(request, pk):
    logger.info('start Place update_view')

    logger.debug('get Place object(pk)')
    place = get_object_or_404(Place, pk=pk)

    if request.method == "POST":
        logger.info('POST method')

        form = PlaceForm(request.POST, request.FILES)
        context = {'object': place, 'form': form}

        if form.is_valid():
            logger.debug('form.is_valid')

            place.place = form.cleaned_data["place"]
            place.area = form.cleaned_data["area"]
            place.overview = form.cleaned_data["overview"]
            place.address = form.cleaned_data["address"]
            place.tel = form.cleaned_data["tel"]
            place.url = form.cleaned_data["url"]
            place.context = form.cleaned_data["context"]
            place.remarks = form.cleaned_data["remarks"]
            place.schedule_monthly = form.cleaned_data['schedule_monthly']
            place.schedule_weekly = form.cleaned_data['schedule_weekly']
            place.latitude = form.cleaned_data["latitude"]
            place.longitude = form.cleaned_data["longitude"]
            place.googlemap_url = form.cleaned_data["googlemap_url"]
            place.updated_pic = request.user.profile

            images_data = request.FILES.get("images")
            delete_images_flg = form.cleaned_data.get('delete_images_flg')
            themes_data = request.FILES.get('themes')
            delete_themes_flg = form.cleaned_data.get('delete_themes_flg')
            
            if images_data: # File Selected
                logger.debug('images_data exists')
                place.images = update_images(place, images_data)
            elif delete_images_flg and place.images:
                logger.debug('delete_images exists')
                delete_images(place)
                place.images = None
            
            if themes_data: # File Selected
                logger.debug('themes_data exists')
                place.themes = update_themes(place, themes_data)
            elif delete_themes_flg and place.themes:
                logger.debug('delete_themes exists')
                delete_themes(place)
                place.themes = None

            try:
                logger.debug('save updated Place object')
                place.save()
            except Exception as e:
                logger.error(f'couldnt save the Place object: {e}')

            logger.info('return redirect place:list')
            return redirect('place:list')
        else:
            logger.error('form not is_valid')
            logger.error(form.errors)
    else:
        logger.info('GET method')  
        form = PlaceForm(instance=place) # putback the form
        context = {'object': place, 'form': form}

    logger.info('return render place/update.html')
    return render(request, 'place/update.html', context)


@login_required
def delete_view(request, pk):
    logger.info('start Place delete_view')
    
    logger.debug('get Place object(pk)')
    place = get_object_or_404(Place, pk=pk)

    context = {'object': place}

    if request.method == "POST":
        logger.info('POST method')

        # **古いファイルを削除**
        if place.images:
            logger.debug('old images_data exists')
            place = delete_images(place)

        # **古いファイルを削除**
        if place.themes:
            logger.debug('old themes_data exists')
            place = delete_themes(place)

        try:
            logger.debug('delete old Place object')
            place.delete()
        except Exception as e:
            logger.error(f'couldnt delete Place object: {e}')

        logger.info('return redirect place:list')
        return redirect('place:list')
    else:
        logger.info('GET method')

    logger.info('return render place/delete.html')
    return render(request, 'place/delete.html', context)

@login_required
def push_likes(request, pk):
    logger.info('start Place push_likes')
    return safe_json_post(request, lambda: _push_likes_logic(request, pk))

def _push_likes_logic(request, pk):
    place = get_object_or_404(Place, id=pk)
    logger.debug(f'get Place object(pk)={place}')

    place.push_likes(request)

    logger.info(f'return likes:{place.likes}')
    return JsonResponse({'likes': f'({place.likes})'})


@login_required
def disp_checkin_qr_view(request):
    logger.info('start Place disp_checkin_qr_view')

    place_id = request.GET.get("place_id")
    base_url = f"{settings.SITE_DOMAIN}/place/checkin/?place_with_id="
    url_for_qr = f"{base_url}{place_id}"
    logger.info(f'url_for_qr={ url_for_qr }')
    
    return disp_qr_code(url_for_qr)

@login_required
def checkin_view(request): 
    logger.info('start Place checkin_view')

    # profile_own = operator
    try:
        profile_own = get_object_or_404(Profile, user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # place_with = target checkin place
    try:
        place_with_id = int(request.GET.get("place_with_id", 1)) # get place_with_id from URL query
        place_with = get_object_or_404(Place, pk=place_with_id) # get target place instance
        logger.debug(f'place_with={place_with}')
    except Exception as e:
        logger.error(f'couldnt get target place_with id={place_with_id}: {e}')
        place_with = None

    # checkin_record = latest CheckinRecord
    try:
        checkin_record = CheckinRecord.objects.filter(place=place_with, profile=profile_own).latest('pk')
        logger.debug(f'checkin_record={checkin_record}')
    except Exception as e:
        # 初回チェックイン時
        logger.info(f'couldnt get target checkin_record place={place_with} profile={profile_own}: {e}')
        checkin_record = None
    
    context = {'profile_own': profile_own, 'place_with': place_with, 'checkin_record': checkin_record}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報からProfile＆Place＆CheckinRecordを取得(POSTされたもののみ採用)
        profile_own_id_data = request.POST["profile_own_id"]
        profile_own = get_object_or_404(Profile, pk=profile_own_id_data)

        place_with_id_data = request.POST["place_with_id"]
        place_with = get_object_or_404(Place, pk=place_with_id_data)

        # GPS座標を取得して保存
        latitude_data = float(request.POST.get('latitude'))
        longitude_data = float(request.POST.get('longitude'))

        logger.debug(f'place_with.latitude={place_with.latitude}')
        logger.debug(f'latitude_data={latitude_data}')
        logger.debug(f'place_with.longitude={place_with.longitude}')
        logger.debug(f'longitude_data={longitude_data}')

        if not haversine(latitude_data, longitude_data, place_with.latitude, place_with.longitude):

            # チェックインする場所と操作者がGPS情報上近くにいない場合
            context.update({'errors': f'Not around by GPS Geolocation. Should more close to target'})

            logger.info('return render place/checkin.html')
            return render(request, 'place/checkin.html', context)
            
        # 初回ログイン時の処理
        if not checkin_record:
            logger.info('First checkin: No previous record found.')


            try:
                # 初回チェックインを作成
                checkin_record = CheckinRecord.objects.create(
                    place=place_with,
                    profile=profile_own,
                    checkin_time=now()
                )
                if place_with.is_profile_not_checked_in_today(profile_own):
                    earn_points = place_with.earn_points_for_checkin(profile_own)
                    context.update({'points': f'You got points for today checkin. Your [Status Point]: {profile_own.status_points:,}(+{earn_points}) pt'}) # 1日に1ポイント獲得後のメッセージ表示
                context.update({'messages': f'Successfully Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})
                context.update({'checkin_record': checkin_record})

                # send the checkin email to parents
                place_with.send_checkin_email(profile_own)
                
            except Exception as e:
                logger.error(f'Failed to create CheckinRecord: {e}')
                context.update({'errors': 'Failed to create CheckinRecord.'})

        else:
            # 既にチェックイン済みでチェックアウトされていない場合はエラー
            if checkin_record.checkin_time and not checkin_record.checkout_time:
                logger.warning(f'Already checked in. Last Checked-In: {checkin_record.checkin_time}')
                context.update({'errors': f'Already Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})
            
            # チェックアウト済みなら新規チェックイン作成
            else:
                try:
                    new_checkin = CheckinRecord.objects.create(
                        place=place_with,
                        profile=profile_own,
                        checkin_time=now()
                    )
                    if place_with.is_profile_not_checked_in_today(profile_own):
                        earn_points = place_with.earn_points_for_checkin(profile_own)
                        context.update({'points': f'You got points for today checkin. Your [Status Point]: {profile_own.status_points:,}(+{earn_points}) pt'}) # 1日に1ポイント獲得後のメッセージ表示
                    context.update({'messages': f'Successfully Checked-In at {new_checkin.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})
                    context.update({'checkin_record': new_checkin})

                    # send the checkin email to parents
                    place_with.send_checkin_email(profile_own)

                except Exception as e:
                    logger.error(f'Failed to create new CheckinRecord: {e}')
                    context.update({'errors': 'Failed to create new CheckinRecord.'})
        
    else:
        logger.info('GET method')

        # チェックイン済みでチェックアウトがまだの場合はエラーメッセージを表示
        if checkin_record and checkin_record.checkin_time and not checkin_record.checkout_time:
            context.update({'errors': f'Already Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}'})

        else:
            if place_with.is_profile_not_checked_in_today(profile_own):
                # 1日に1ポイント獲得のメッセージ表示
                earn_points = place_with.get_earn_points_for_checkin()
                contract_pt = profile_own.get_contract_pt()
                used_pt = profile_own.get_total_checkin_days_this_month()
                remain_points = contract_pt - used_pt
                context.update({'points': f'1 day get {earn_points} points. Your [Status Point]: {profile_own.status_points:,} + {earn_points} pt'})
                if 0 < remain_points:
                    context.update({'infos': f'You have still {remain_points:,} points as of yesterday. [contact: {contract_pt:,},  used: {used_pt:,} pt]'})
                else:
                    context.update({'errors': f'Your available credit is {remain_points:,} points as of yesterday. [contact: {contract_pt:,},  used: {used_pt:,} pt]'})
            else:
                context.update({'points': f'You already checked-in today. Your [Status Point]: {profile_own.status_points:,} pt'})
        
    logger.info('return render place/checkin.html')
    return render(request, 'place/checkin.html', context)


@login_required
def disp_checkout_qr_view(request):
    logger.info('start Place disp_checkout_qr_view')

    place_id = request.GET.get("place_id")
    base_url = f"{settings.SITE_DOMAIN}/place/checkout/?place_with_id="
    url_for_qr = f"{base_url}{place_id}"
    logger.info(f'url_for_qr={ url_for_qr }')
    
    return disp_qr_code(url_for_qr)

@login_required
def checkout_view(request): 
    logger.info('start Place checkout_view')

    # profile_own = operator
    try:
        profile_own = Profile.objects.get(user1=request.user) # get login profile object
        logger.debug(f'profile_own={profile_own}')
    except Exception as e:
        logger.error(f'couldnt get my request.user={request.user}: {e}')
        profile_own = None

    # place_with = target checkin place
    place_with_id = int(request.GET.get("place_with_id", 1)) # get place_with_id from URL query
    place_with = get_object_or_404(Place, pk=place_with_id) # get target place instance
    logger.debug(f'place_with={place_with}')

    # checkin_record = latest CheckinRecord
    checkin_record = CheckinRecord.objects.filter(place=place_with, profile=profile_own).latest('pk')
    logger.debug(f'checkin_record={checkin_record}')

    context = {'profile_own': profile_own, 'place_with': place_with, 'checkin_record': checkin_record}

    if request.method == "POST":
        logger.info('POST method')

        # GETの情報ではなく、POSTの情報からProfile＆Placeを取得(POSTされたもののみ採用)
        profile_own_id_data = request.POST["profile_own_id"]
        profile_own = get_object_or_404(Profile, pk=profile_own_id_data)

        place_with_id_data = request.POST["place_with_id"]
        place_with = get_object_or_404(Place, pk=place_with_id_data)

        checkin_record_id_data = request.POST["checkin_record_id"]
        checkin_record = CheckinRecord.objects.get(pk=checkin_record_id_data)

        if checkin_record:
            # チェックアウト処理
            # place&profileが一致していて、チェックアウト時間が入っていないもののみ
            if checkin_record.profile == profile_own and checkin_record.place == place_with and not checkin_record.checkout_time:
                try:
                    checkin_record.checkout_time = now()
                    checkin_record.save()
                    if checkin_record.checkin_time.strftime("%Y/%m/%d") < now().strftime("%Y/%m/%d"):
                        deduct_points = place_with.deduct_points_for_checkin(profile_own)
                        context.update({'errors': f'We deducted {deduct_points} points from your Status and Available.'})
                    context.update({'messages': f'Successfully Checked-Out at {checkin_record.checkout_time.strftime("%Y/%m/%d %H:%M:%S")}.'})

                    # send the checkout email to parents
                    place_with.send_checkout_email(profile_own)

                except Exception as e:
                    checkin_record = CheckinRecord()
                    logger.error(f'couldnt update the Place CheckinRecord Object: {e}')
                    context.update({'errors': f'Couldnt Checked-Out.'})
            else:
                logger.error(f'couldnt update the Place CheckinRecord Object')
                context.update({'errors': f'Already Checked-Out at {checkin_record.checkout_time.strftime("%Y/%m/%d %H:%M:%S")}.'})
        else:
            context.update({'errors': 'No check-in record found. Please check-in first.'})

    else:
        logger.info('GET method')

        # 既にチェックアウト時間が設定されている場合はエラーメッセージを表示
        if checkin_record and checkin_record.checkout_time:
                context.update({'errors': f'Already Checked-Out at {checkin_record.checkout_time.strftime("%Y/%m/%d %H:%M:%S")}.'})
        elif checkin_record:
                context.update({'infos': f'Check-Out for Last Checked-In at {checkin_record.checkin_time.strftime("%Y/%m/%d %H:%M:%S")}.'} )
                if checkin_record.checkin_time.strftime("%Y/%m/%d") < now().strftime("%Y/%m/%d"):
                    reduce_points = place_with.earn_points_for_checkin(profile_own)
                    context.update({'errors': f'Last Check-In doesnt have Check-Out record. After Check-Out, we deduct {reduce_points:,} points.'} )                
        else:
            context.update({'errors': 'No previous check-in records found. Please check-in first.'})

    logger.info('return render place/checkout.html')
    return render(request, 'place/checkout.html', context)
